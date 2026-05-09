import mlflow
import mlflow.pytorch
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Set MLflow tracking URI
mlflow.set_tracking_uri("file:///D:/mlflow/mlruns")
mlflow.set_experiment("solar-panel-model-training")

def log_training_run(model, train_loader, val_loader, params, results):
    """Log a training run to MLflow"""
    
    with mlflow.start_run(run_name=f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
        # Log parameters
        mlflow.log_params({
            "epochs": params['epochs'],
            "batch_size": params['batch_size'],
            "learning_rate": params['learning_rate'],
            "optimizer": params['optimizer'],
            "model_architecture": "EfficientNet-B0"
        })
        
        # Log metrics
        mlflow.log_metrics({
            "train_accuracy": results['train_accuracy'],
            "val_accuracy": results['val_accuracy'],
            "final_train_loss": results['train_losses'][-1],
            "final_val_loss": results['val_losses'][-1]
        })
        
        # Log model
        mlflow.pytorch.log_model(model, "model")
        
        # Log training curves
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
        ax1.plot(results['train_losses'], label='Train Loss')
        ax1.plot(results['val_losses'], label='Val Loss')
        ax1.set_title('Loss Curves')
        ax1.legend()
        
        ax2.plot(results['train_accs'], label='Train Acc')
        ax2.plot(results['val_accs'], label='Val Acc')
        ax2.set_title('Accuracy Curves')
        ax2.legend()
        
        mlflow.log_figure(fig, "training_curves.png")
        plt.close()
        
        print(f"Run logged with ID: {mlflow.active_run().info.run_id}")

# Example usage (you would integrate this with your actual training code)
if __name__ == "__main__":
    print("MLflow Training Script Ready")
    print(f"Tracking URI: {mlflow.get_tracking_uri()}")
    print(f"Experiment: solar-panel-model-training")