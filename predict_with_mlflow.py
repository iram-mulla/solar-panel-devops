import mlflow
import torch
import torchvision.transforms as transforms
from PIL import Image
import argparse
from datetime import datetime
import os
import sys
import io

# Fix Unicode for Windows Jenkins
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os

mlflow.set_tracking_uri(
    os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
)

CLASS_NAMES = ['bird-drop', 'clean', 'dusty', 'electrical-damage', 'physical-damage', 'snow']

CLEANING_RECOMMENDATIONS = {
    'bird-drop': {'action': 'Water Clean', 'priority': 'HIGH', 'description': 'Bird droppings cause hot spots. Clean immediately.', 'energy_gain': '15-20%'},
    'dusty': {'action': 'Air Blast', 'priority': 'MEDIUM', 'description': 'Dust reduces light absorption. Schedule cleaning.', 'energy_gain': '8-12%'},
    'snow': {'action': 'Snow Removal', 'priority': 'MEDIUM', 'description': 'Snow blocks sunlight. Remove if persists.', 'energy_gain': '25-30%'},
    'electrical-damage': {'action': 'Emergency Repair', 'priority': 'CRITICAL', 'description': 'Electrical damage requires immediate repair.', 'energy_gain': 'N/A - Safety Hazard'},
    'physical-damage': {'action': 'Panel Replacement', 'priority': 'HIGH', 'description': 'Physical damage reduces output permanently.', 'energy_gain': 'Variable'},
    'clean': {'action': 'No Action Needed', 'priority': 'LOW', 'description': 'Panel is clean and functioning optimally.', 'energy_gain': '0%'}
}

def predict_image(image_path, model_path):
    with mlflow.start_run(run_name=f"prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}", nested=True):
        
        if not os.path.exists(model_path):
            print(f"ERROR: Model file not found at: {model_path}")
            return None, None, None
        
        print(f"Loading model from: {model_path}")
        model = torch.jit.load(model_path, map_location='cpu')
        model.eval()
        
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        print(f"Loading image: {image_path}")
        image = Image.open(image_path).convert('RGB')
        input_tensor = transform(image).unsqueeze(0)
        
        with torch.no_grad():
            output = model(input_tensor)
            probabilities = torch.softmax(output, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
        
        predicted_class = CLASS_NAMES[predicted.item()]
        confidence_score = confidence.item() * 100
        
        all_probs = {CLASS_NAMES[i]: round(probabilities[0][i].item() * 100, 2) for i in range(len(CLASS_NAMES))}
        
        mlflow.log_param("image_path", image_path)
        mlflow.log_metric("confidence", confidence_score)
        mlflow.log_param("predicted_class", predicted_class)
        
        rec = CLEANING_RECOMMENDATIONS[predicted_class]
        
        print("\n" + "="*50)
        print("SOLAR PANEL DEFECT DETECTION RESULT")
        print("="*50)
        print(f"Image: {os.path.basename(image_path)}")
        print(f"Predicted: {predicted_class}")
        print(f"Confidence: {confidence_score:.2f}%")
        print(f"Action: {rec['action']}")
        print(f"Priority: {rec['priority']}")
        print("="*50)
        
        return predicted_class, confidence_score, all_probs

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, "models", "solar_panel_android.pt")
    
    if not os.path.exists(model_path):
        model_path = r"D:\Engineering\6th sem\DevOps\solar-panel-devops\models\solar_panel_android.pt"
    
    parser = argparse.ArgumentParser(description='Predict solar panel defect')
    parser.add_argument('image_path', help='Path to the solar panel image')
    args = parser.parse_args()
    
    predict_image(args.image_path, model_path)