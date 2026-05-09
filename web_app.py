from flask import Flask, render_template, request, jsonify
import torch
import torchvision.transforms as transforms
from PIL import Image
import io
import os
import mlflow
from datetime import datetime

app = Flask(__name__)

# MLflow setup
mlflow.set_tracking_uri("http://127.0.0.1:5000")

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

# Load model at startup
MODEL_PATH = r"D:\Engineering\6th sem\DevOps\solar-panel-devops\models\solar_panel_android.pt"

try:
    model = torch.jit.load(MODEL_PATH, map_location='cpu')
    model.eval()
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None

def preprocess_image(image):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    return transform(image).unsqueeze(0)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        file = request.files['file']
        img_bytes = file.read()
        image = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        
        # Preprocess and predict
        input_tensor = preprocess_image(image)
        
        with torch.no_grad():
            output = model(input_tensor)
            probabilities = torch.softmax(output, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
        
        predicted_class = CLASS_NAMES[predicted.item()]
        confidence_score = round(confidence.item() * 100, 2)
        
        # Get all probabilities
        all_probs = {
            CLASS_NAMES[i]: round(probabilities[0][i].item() * 100, 2)
            for i in range(len(CLASS_NAMES))
        }
        
        # Sort by probability
        sorted_probs = sorted(all_probs.items(), key=lambda x: x[1], reverse=True)
        
        # Get recommendation
        rec = CLEANING_RECOMMENDATIONS.get(predicted_class, {})
        
        # Log to MLflow
        with mlflow.start_run(run_name=f"web_prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}", nested=True):
            mlflow.log_metric("confidence", confidence_score)
            mlflow.log_param("predicted_class", predicted_class)
        
        return jsonify({
            'success': True,
            'predicted_class': predicted_class,
            'confidence': confidence_score,
            'probabilities': sorted_probs,
            'recommendation': rec
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)