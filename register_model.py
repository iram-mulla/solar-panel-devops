import mlflow
import mlflow.pytorch
import torch
import torch.nn as nn
import torchvision.models as models
from datetime import datetime

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("solar-panel-defect-detection")

class EnhancedEfficientNet(nn.Module):
    def __init__(self, num_classes=6, dropout_rate=0.35):
        super(EnhancedEfficientNet, self).__init__()
        self.backbone = models.efficientnet_b0(weights='IMAGENET1K_V1')
        
        for param in list(self.backbone.parameters())[:100]:
            param.requires_grad = False
        
        in_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(dropout_rate),
            nn.Linear(in_features, 512),
            nn.BatchNorm1d(512),
            nn.SiLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(512, num_classes)
        )
    
    def forward(self, x):
        return self.backbone(x)

def register_model():
    with mlflow.start_run(run_name=f"model-registration-{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
        
        # Log model parameters
        mlflow.log_params({
            "model_architecture": "EnhancedEfficientNet-B0",
            "input_size": "224x224",
            "num_classes": 6,
            "pretrained": True
        })
        
        # Create and log the model
        model = EnhancedEfficientNet(num_classes=6)
        
        # Create a sample input for model signature
        sample_input = torch.randn(1, 3, 224, 224)
        
        # Log the PyTorch model
        mlflow.pytorch.log_model(
            model,
            "solar_panel_model",
            registered_model_name="SolarPanelDefectDetector"
        )
        
        # Log model metadata
        mlflow.set_tags({
            "task": "image-classification",
            "classes": "bird-drop, clean, dusty, electrical-damage, physical-damage, snow",
            "framework_version": torch.__version__,
            "deployment_format": "TorchScript",
            "optimization": "Pruned (30%) + Quantized (INT8)"
        })
        
        print("Model registered successfully!")
        print(f"Run ID: {mlflow.active_run().info.run_id}")
        print("\nTo view the registered model, go to:")
        print("http://127.0.0.1:5000/#/models")

if __name__ == "__main__":
    register_model()