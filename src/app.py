from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import torch
import torchvision.transforms as transforms
from PIL import Image
import io
import os
import logging
from datetime import datetime
import mlflow
import mlflow.pytorch
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MLflow setup
MLFLOW_TRACKING_URI = "file:///D:/mlflow/mlruns"
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment("solar-panel-defect-detection")

# Class names and recommendations (same as before)
CLASS_NAMES = ['bird-drop', 'clean', 'dusty', 'electrical-damage', 'physical-damage', 'snow']

CLEANING_RECOMMENDATIONS = {
    'bird-drop': {
        'action': 'Water Clean',
        'priority': 'HIGH',
        'description': 'Bird droppings cause hot spots and reduce efficiency. Clean immediately with water.',
        'estimated_energy_gain': '15-20%'
    },
    'dusty': {
        'action': 'Air Blast',
        'priority': 'MEDIUM',
        'description': 'Dust accumulation reduces light absorption. Schedule cleaning within 1 week.',
        'estimated_energy_gain': '8-12%'
    },
    'snow': {
        'action': 'Snow Removal',
        'priority': 'MEDIUM',
        'description': 'Snow cover blocks all sunlight. Remove if snow persists more than 2 days.',
        'estimated_energy_gain': '25-30%'
    },
    'electrical-damage': {
        'action': 'Emergency Repair',
        'priority': 'CRITICAL',
        'description': 'Electrical damage requires immediate professional repair. Risk of fire.',
        'estimated_energy_gain': 'N/A - Safety Hazard'
    },
    'physical-damage': {
        'action': 'Panel Replacement',
        'priority': 'HIGH',
        'description': 'Physical damage reduces output permanently. Schedule replacement.',
        'estimated_energy_gain': 'Variable'
    },
    'clean': {
        'action': 'No Action Needed',
        'priority': 'LOW',
        'description': 'Panel is clean and functioning optimally. Continue monitoring.',
        'estimated_energy_gain': '0%'
    }
}

# Global variables
model = None
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model_version = None

class SolarPanelModel(mlflow.pyfunc.PythonModel):
    """MLflow-compatible model wrapper"""
    
    def __init__(self, model_path=None):
        self.model = None
        self.model_path = model_path
        self.class_names = CLASS_NAMES
    
    def load_context(self, context):
        """Load the model from artifacts"""
        import torch
        model_file = context.artifacts["model"]
        self.model = torch.jit.load(model_file)
        self.model.eval()
    
    def predict(self, context, model_input):
        """Make predictions"""
        import torch
        import torchvision.transforms as transforms
        from PIL import Image
        
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        results = []
        for img in model_input:
            input_tensor = transform(img).unsqueeze(0)
            with torch.no_grad():
                output = self.model(input_tensor)
                probs = torch.softmax(output, dim=1)
                pred = torch.argmax(probs, dim=1)
            results.append({
                "class": self.class_names[pred[0]],
                "confidence": probs[0][pred[0]].item()
            })
        
        return results

def register_model_with_mlflow(model_path):
    """Register the model in MLflow Model Registry"""
    with mlflow.start_run(run_name="model-registration") as run:
        # Log model parameters
        mlflow.log_param("model_type", "EfficientNet-B0")
        mlflow.log_param("input_size", "224x224")
        mlflow.log_param("num_classes", 6)
        
        # Log the model
        artifacts = {"model": model_path}
        mlflow.pyfunc.log_model(
            artifact_path="solar_panel_model",
            python_model=SolarPanelModel(),
            artifacts=artifacts,
            registered_model_name="SolarPanelDefectDetector"
        )
        
        logger.info(f"Model registered with run_id: {run.info.run_id}")
        return run.info.run_id

def load_model_from_registry(model_name="SolarPanelDefectDetector", stage="Production"):
    """Load model from MLflow Model Registry"""
    global model, model_version
    
    try:
        model_uri = f"models:/{model_name}/{stage}"
        model = mlflow.pyfunc.load_model(model_uri)
        model_version = mlflow.register_model(model_uri, model_name)
        logger.info(f"Model loaded from registry: {model_name} ({stage})")
        return True
    except Exception as e:
        logger.error(f"Error loading model from registry: {e}")
        return False

def preprocess_image(image: Image.Image) -> torch.Tensor:
    """Preprocess image for model input"""
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    return transform(image).unsqueeze(0)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI"""
    # Startup: Load model
    model_path = os.getenv('MODEL_PATH', 'models/solar_panel_android.pt')
    
    # Try loading from MLflow registry first
    mlflow_loaded = load_model_from_registry()
    
    if not mlflow_loaded and os.path.exists(model_path):
        # Register model if not in registry
        run_id = register_model_with_mlflow(model_path)
        logger.info(f"Registered new model version with run_id: {run_id}")
        load_model_from_registry()
    
    yield  # Application runs here
    
    # Shutdown: Cleanup
    logger.info("Shutting down application")

app = FastAPI(
    title="Solar Panel Defect Detection API with MLflow",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {
        "message": "Solar Panel Defect Detection API",
        "status": "running",
        "mlflow_tracking": MLFLOW_TRACKING_URI
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "device": str(device),
        "mlflow_version": mlflow.__version__
    }

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Predict defect from uploaded image"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    with mlflow.start_run(run_name=f"prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}", nested=True):
        try:
            # Read image
            contents = await file.read()
            image = Image.open(io.BytesIO(contents)).convert('RGB')
            
            # Make prediction using MLflow model
            prediction = model.predict([image])[0]
            
            # Log metrics
            mlflow.log_metric("confidence", prediction["confidence"])
            
            # Get recommendation
            recommendation = CLEANING_RECOMMENDATIONS.get(prediction["class"], {})
            
            return JSONResponse({
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "prediction": {
                    "class": prediction["class"],
                    "confidence": prediction["confidence"],
                    "recommendation": recommendation
                }
            })
        
        except Exception as e:
            mlflow.log_param("error", str(e))
            logger.error(f"Prediction error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def list_models():
    """List registered models from MLflow"""
    try:
        client = mlflow.tracking.MlflowClient()
        models = client.search_registered_models()
        
        model_list = []
        for m in models:
            versions = client.search_model_versions(f"name='{m.name}'")
            model_list.append({
                "name": m.name,
                "versions": [
                    {
                        "version": v.version,
                        "stage": v.current_stage,
                        "status": v.status
                    }
                    for v in versions
                ]
            })
        
        return {"models": model_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/experiments")
async def list_experiments():
    """List MLflow experiments"""
    try:
        experiments = mlflow.search_experiments()
        exp_list = []
        for exp in experiments:
            exp_list.append({
                "id": exp.experiment_id,
                "name": exp.name,
                "artifact_location": exp.artifact_location
            })
        return {"experiments": exp_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Start MLflow tracking server in background
    import subprocess
    subprocess.Popen([
        "mlflow", "server",
        "--backend-store-uri", MLFLOW_TRACKING_URI,
        "--default-artifact-root", "file:///D:/mlflow/artifacts",
        "--host", "127.0.0.1",
        "--port", "5000"
    ])
    
    uvicorn.run(app, host="0.0.0.0", port=8000)