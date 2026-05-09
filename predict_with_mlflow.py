import mlflow
import torch
import torchvision.transforms as transforms
from PIL import Image
import argparse
from datetime import datetime
import os

mlflow.set_tracking_uri("http://127.0.0.1:5000")

CLASS_NAMES = ['bird-drop', 'clean', 'dusty', 'electrical-damage', 'physical-damage', 'snow']

CLEANING_RECOMMENDATIONS = {
    'bird-drop': {
        'action': 'Water Clean',
        'priority': 'HIGH',
        'description': 'Bird droppings cause hot spots. Clean immediately.',
        'energy_gain': '15-20%'
    },
    'dusty': {
        'action': 'Air Blast',
        'priority': 'MEDIUM',
        'description': 'Dust reduces light absorption. Schedule cleaning.',
        'energy_gain': '8-12%'
    },
    'snow': {
        'action': 'Snow Removal',
        'priority': 'MEDIUM',
        'description': 'Snow blocks sunlight. Remove if persists.',
        'energy_gain': '25-30%'
    },
    'electrical-damage': {
        'action': 'Emergency Repair',
        'priority': 'CRITICAL',
        'description': 'Electrical damage requires immediate repair.',
        'energy_gain': 'N/A - Safety Hazard'
    },
    'physical-damage': {
        'action': 'Panel Replacement',
        'priority': 'HIGH',
        'description': 'Physical damage reduces output permanently.',
        'energy_gain': 'Variable'
    },
    'clean': {
        'action': 'No Action Needed',
        'priority': 'LOW',
        'description': 'Panel is clean and functioning optimally.',
        'energy_gain': '0%'
    }
}

def predict_image(image_path, model_path):
    """Predict defect type for a solar panel image"""
    
    with mlflow.start_run(run_name=f"prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}", nested=True):
        
        # Check if model exists
        if not os.path.exists(model_path):
            print(f"ERROR: Model file not found at: {model_path}")
            print(f"Please place your solar_panel_android.pt file in the models folder")
            return None, None, None
        
        # Load the TorchScript model
        print(f"Loading model from: {model_path}")
        model = torch.jit.load(model_path, map_location='cpu')
        model.eval()
        
        # Preprocess image
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        print(f"Loading image: {image_path}")
        image = Image.open(image_path).convert('RGB')
        input_tensor = transform(image).unsqueeze(0)
        
        # Predict
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
        
        # Log prediction to MLflow
        mlflow.log_param("image_path", image_path)
        mlflow.log_metric("confidence", confidence_score)
        mlflow.log_param("predicted_class", predicted_class)
        
        for class_name, prob in all_probs.items():
            mlflow.log_metric(f"prob_{class_name}", prob)
        
        # Get recommendation
        rec = CLEANING_RECOMMENDATIONS[predicted_class]
        
        # Print results
        print("\n" + "="*50)
        print("SOLAR PANEL DEFECT DETECTION RESULT")
        print("="*50)
        print(f"Image: {os.path.basename(image_path)}")
        print(f"Predicted: {predicted_class}")
        print(f"Confidence: {confidence_score:.2f}%")
        print(f"\nProbabilities:")
        for cls, prob in sorted(all_probs.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * int(prob / 2)
            print(f"  {cls:20s}: {prob:6.2f}% {bar}")
        print(f"\nRecommendation:")
        print(f"  Action: {rec['action']}")
        print(f"  Priority: {rec['priority']}")
        print(f"  {rec['description']}")
        print(f"  Energy Gain: {rec['energy_gain']}")
        print("="*50)
        
        return predicted_class, confidence_score, all_probs

if __name__ == "__main__":
    # Get the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Model path - use absolute path
    model_path = os.path.join(script_dir, "models", "solar_panel_android.pt")
    
    # Also look in the project root
    if not os.path.exists(model_path):
        model_path = r"D:\Engineering\6th sem\DevOps\solar-panel-devops\models\solar_panel_android.pt"
    
    parser = argparse.ArgumentParser(description='Predict solar panel defect')
    parser.add_argument('image_path', help='Path to the solar panel image')
    args = parser.parse_args()
    
    predict_image(args.image_path, model_path)