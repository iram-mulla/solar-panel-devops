import os
import io
import time
import threading

# Redirect caches/temp to D: before heavy ML imports (keeps C: free)
def _use_d_drive_for_cache():
    d_temp = os.environ.get("TEMP", "D:\\temp")
    if not os.path.isabs(d_temp) or d_temp.upper().startswith("C:"):
        d_temp = "D:\\temp"
    for key in ("TEMP", "TMP", "TMPDIR"):
        os.environ.setdefault(key, d_temp)
    os.makedirs(d_temp, exist_ok=True)
    for key, path in (
        ("PIP_CACHE_DIR", "D:\\pip-cache"),
        ("TORCH_HOME", "D:\\torch-cache"),
        ("HF_HOME", "D:\\hf-cache"),
        ("PYTHONUSERBASE", "D:\\python-user"),
    ):
        os.makedirs(path, exist_ok=True)
        os.environ.setdefault(key, path)


_use_d_drive_for_cache()

from flask import Flask, render_template, request, jsonify
import mlflow
from datetime import datetime

app = Flask(__name__)

# MLflow setup — uses your existing server on port 5000
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000"))

# Default "false" for fast localhost testing; set "true" to log each prediction to MLflow
MLFLOW_LOG_PREDICTIONS = os.getenv("MLFLOW_LOG_PREDICTIONS", "false").lower() == "true"

# Downscale large uploads before 224x224 transform (speeds up PIL + tensor work)
MAX_IMAGE_EDGE = int(os.getenv("MAX_IMAGE_EDGE", "384"))

CLASS_NAMES = ['bird-drop', 'clean', 'dusty', 'electrical-damage', 'physical-damage', 'snow']

CLEANING_RECOMMENDATIONS = {
    'bird-drop': {
        'action': 'Water Clean',
        'priority': 'HIGH',
        'badge_class': 'bg-danger',
        'description': 'Bird droppings cause hot spots and reduce efficiency. Clean immediately with water.',
        'energy_gain': '15-20%'
    },
    'dusty': {
        'action': 'Air Blast',
        'priority': 'MEDIUM',
        'badge_class': 'bg-warning',
        'description': 'Dust accumulation reduces light absorption. Schedule cleaning within 1 week.',
        'energy_gain': '8-12%'
    },
    'snow': {
        'action': 'Snow Removal',
        'priority': 'MEDIUM',
        'badge_class': 'bg-warning',
        'description': 'Snow cover blocks all sunlight. Remove if snow persists more than 2 days.',
        'energy_gain': '25-30%'
    },
    'electrical-damage': {
        'action': 'Emergency Repair',
        'priority': 'CRITICAL',
        'badge_class': 'bg-danger',
        'description': 'Electrical damage requires immediate professional repair. Risk of fire!',
        'energy_gain': 'N/A - Safety Hazard'
    },
    'physical-damage': {
        'action': 'Panel Replacement',
        'priority': 'HIGH',
        'badge_class': 'bg-danger',
        'description': 'Physical damage reduces output permanently. Schedule replacement.',
        'energy_gain': 'Variable'
    },
    'clean': {
        'action': 'No Action Needed',
        'priority': 'LOW',
        'badge_class': 'bg-success',
        'description': 'Panel is clean and functioning optimally. Continue monitoring.',
        'energy_gain': '0%'
    }
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(BASE_DIR, 'models', 'solar_panel_android.pt'))

_model_lock = threading.Lock()
_model = None
_device = None
_image_transform = None
_model_ready = False
_model_loading = False
_model_error = None


def _load_model():
    """Load PyTorch model in background so Flask starts quickly on localhost."""
    global _model, _device, _image_transform, _model_ready, _model_loading, _model_error

    with _model_lock:
        if _model_ready or _model_loading:
            return
        _model_loading = True

    try:
        import torch
        import torchvision.transforms as transforms

        torch.set_num_threads(max(1, min(4, os.cpu_count() or 1)))

        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        image_transform = transforms.Compose([
            transforms.Resize((224, 224), interpolation=transforms.InterpolationMode.BILINEAR),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        model = torch.jit.load(MODEL_PATH, map_location=device)
        model.to(device)
        model.eval()

        with torch.inference_mode():
            warmup = torch.zeros(1, 3, 224, 224, device=device)
            model(warmup)

        with _model_lock:
            _model = model
            _device = device
            _image_transform = image_transform
            _model_ready = True
            _model_error = None
        print("Model loaded and warmed up successfully!")
    except Exception as exc:
        with _model_lock:
            _model_error = str(exc)
        print(f"Error loading model: {exc}")
    finally:
        with _model_lock:
            _model_loading = False


def _start_model_loader():
    thread = threading.Thread(target=_load_model, daemon=True)
    thread.start()


def _load_rgb_image(img_bytes):
    """Decode and downscale large images to reduce preprocessing time."""
    from PIL import Image

    image = Image.open(io.BytesIO(img_bytes))
    image.load()
    image = image.convert('RGB')
    if max(image.size) > MAX_IMAGE_EDGE:
        image.thumbnail((MAX_IMAGE_EDGE, MAX_IMAGE_EDGE), Image.Resampling.BILINEAR)
    return image


def _log_prediction_to_mlflow(predicted_class, confidence_score):
    """Log prediction in background so the HTTP response is not blocked."""
    try:
        with mlflow.start_run(
            run_name=f"web_prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            nested=True
        ):
            mlflow.log_metric("confidence", confidence_score)
            mlflow.log_param("predicted_class", predicted_class)
    except Exception as exc:
        print(f"MLflow logging skipped: {exc}")


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'model_loaded': _model_ready,
        'model_loading': _model_loading,
        'model_error': _model_error,
        'device': str(_device) if _device else None,
        'mlflow_uri': os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000"),
        'mlflow_logging': MLFLOW_LOG_PREDICTIONS
    })


@app.route('/predict', methods=['POST'])
def predict():
    if _model_loading and not _model_ready:
        return jsonify({
            'error': 'Model is still loading. Wait a few seconds and try again.',
            'model_loading': True
        }), 503

    if not _model_ready or _model is None:
        return jsonify({'error': _model_error or 'Model not loaded'}), 500

    try:
        import torch

        total_start = time.perf_counter()

        file = request.files['file']
        img_bytes = file.read()
        image = _load_rgb_image(img_bytes)
        preprocess_done = time.perf_counter()

        input_tensor = _image_transform(image).unsqueeze(0).to(_device)

        infer_start = time.perf_counter()
        with torch.inference_mode():
            output = _model(input_tensor)
            probabilities = torch.softmax(output, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
        infer_done = time.perf_counter()

        predicted_class = CLASS_NAMES[predicted.item()]
        confidence_score = round(confidence.item() * 100, 2)

        all_probs = {
            CLASS_NAMES[i]: round(probabilities[0][i].item() * 100, 2)
            for i in range(len(CLASS_NAMES))
        }
        sorted_probs = sorted(all_probs.items(), key=lambda x: x[1], reverse=True)
        rec = CLEANING_RECOMMENDATIONS.get(predicted_class, {})
        preprocess_ms = round((preprocess_done - total_start) * 1000, 1)
        model_ms = round((infer_done - infer_start) * 1000, 1)
        total_ms = round((infer_done - total_start) * 1000, 1)

        if MLFLOW_LOG_PREDICTIONS:
            threading.Thread(
                target=_log_prediction_to_mlflow,
                args=(predicted_class, confidence_score),
                daemon=True
            ).start()

        return jsonify({
            'success': True,
            'predicted_class': predicted_class,
            'confidence': confidence_score,
            'probabilities': sorted_probs,
            'recommendation': rec,
            'inference_ms': model_ms,
            'preprocess_ms': preprocess_ms,
            'total_ms': total_ms
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


_start_model_loader()

if __name__ == '__main__':
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    print("Web app starting on http://127.0.0.1:8000 (model loads in background)")
    app.run(debug=debug, host='0.0.0.0', port=8000)
