from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import torch
import torchvision.transforms as transforms
from PIL import Image
import io
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Solar Panel Defect Detection API")

CLASS_NAMES = ['bird-drop', 'clean', 'dusty', 'electrical-damage', 'physical-damage', 'snow']

CLEANING_RECOMMENDATIONS = {
    'bird-drop': {
        'action': 'Water Clean',
        'priority': 'HIGH',
        'description': 'Bird droppings cause hot spots. Clean immediately with water.',
        'estimated_energy_gain': '15-20%'
    },
    'dusty': {
        'action': 'Air Blast',
        'priority': 'MEDIUM',
        'description': 'Dust reduces light absorption. Schedule cleaning within 1 week.',
        'estimated_energy_gain': '8-12%'
    },
    'snow': {
        'action': 'Snow Removal',
        'priority': 'MEDIUM',
        'description': 'Snow blocks sunlight. Remove if persists more than 2 days.',
        'estimated_energy_gain': '25-30%'
    },
    'electrical-damage': {
        'action': 'Emergency Repair',
        'priority': 'CRITICAL',
        'description': 'Electrical damage requires immediate professional repair.',
        'estimated_energy_gain': 'N/A - Safety Hazard'
    },
    'physical-damage': {
        'action': 'Panel Replacement',
        'priority': 'HIGH',
        'description': 'Physical damage reduces output permanently.',
        'estimated_energy_gain': 'Variable'
    },
    'clean': {
        'action': 'No Action Needed',
        'priority': 'LOW',
        'description': 'Panel is clean and functioning optimally.',
        'estimated_energy_gain': '0%'
    }
}

# Global model variable
model = None
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def load_model():
    """Load the TorchScript model"""
    global model
    try:
        model_path = os.getenv('MODEL_PATH', 'models/solar_panel_android.pt')
        if os.path.exists(model_path):
            model = torch.jit.load(model_path, map_location=device)
            model.eval()
            logger.info(f"Model loaded from {model_path}")
            return True
        else:
            logger.warning(f"Model not found at {model_path}")
            return False
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return False

def preprocess_image(image: Image.Image) -> torch.Tensor:
    """Preprocess image for model input"""
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    return transform(image).unsqueeze(0)

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    load_model()

@app.get("/")
async def root():
    return {"message": "Solar Panel Defect Detection API", "status": "running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "device": str(device)
    }

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Predict defect from uploaded image"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Read and preprocess image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')
        input_tensor = preprocess_image(image).to(device)
        
        # Run inference
        with torch.no_grad():
            output = model(input_tensor)
            probabilities = torch.softmax(output, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
        
        predicted_class = CLASS_NAMES[predicted.item()]
        confidence_score = confidence.item() * 100
        
        # Get all probabilities
        all_probs = {
            CLASS_NAMES[i]: round(probabilities[0][i].item() * 100, 2)
            for i in range(len(CLASS_NAMES))
        }
        
        # Get recommendation
        recommendation = CLEANING_RECOMMENDATIONS.get(predicted_class, {})
        
        logger.info(f"Prediction: {predicted_class} ({confidence_score:.2f}%)")
        
        return JSONResponse({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "prediction": {
                "class": predicted_class,
                "confidence": confidence_score,
                "probabilities": all_probs,
                "recommendation": recommendation
            }
        })
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)