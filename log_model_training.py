import mlflow
import mlflow.pytorch
import torch
import matplotlib
matplotlib.use('Agg')  # Fix for Jenkins - no display needed
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import sys
import io

# Fix Unicode for Windows Jenkins
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Set tracking URI
mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("solar-panel-defect-detection")

def log_training_results():
    """Log your training results from the notebook to MLflow"""
    
    run_name = f"efficientnet-b0-training-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    with mlflow.start_run(run_name=run_name):
        
        # Log model parameters
        mlflow.log_params({
            "model_type": "EfficientNet-B0",
            "input_size": "224x224",
            "num_classes": 6,
            "pretrained": True,
            "batch_size": 16,
            "learning_rate": 0.001,
            "optimizer": "AdamW",
            "weight_decay": 0.0001,
            "pruning_percentage": 0.30,
            "quantization": "INT8",
            "max_epochs": 10,
            "early_stopping_patience": 3
        })
        
        # Log training metrics from your notebook output
        epochs_data = [
            {"epoch": 1, "train_loss": 0.7958, "val_loss": 0.4844, "train_acc": 73.02, "val_acc": 84.21},
            {"epoch": 2, "train_loss": 0.3718, "val_loss": 0.4269, "train_acc": 87.47, "val_acc": 85.96},
            {"epoch": 3, "train_loss": 0.2778, "val_loss": 0.3026, "train_acc": 89.64, "val_acc": 91.23},
            {"epoch": 4, "train_loss": 0.2081, "val_loss": 0.3921, "train_acc": 94.15, "val_acc": 91.23},
            {"epoch": 5, "train_loss": 0.2234, "val_loss": 0.4139, "train_acc": 92.73, "val_acc": 85.96},
            {"epoch": 6, "train_loss": 0.1248, "val_loss": 0.2625, "train_acc": 96.41, "val_acc": 92.98},
            {"epoch": 7, "train_loss": 0.0535, "val_loss": 0.3308, "train_acc": 98.66, "val_acc": 92.11},
            {"epoch": 8, "train_loss": 0.0762, "val_loss": 0.3537, "train_acc": 96.91, "val_acc": 92.98},
            {"epoch": 9, "train_loss": 0.0737, "val_loss": 0.2583, "train_acc": 97.74, "val_acc": 93.86},
            {"epoch": 10, "train_loss": 0.0323, "val_loss": 0.2072, "train_acc": 99.16, "val_acc": 94.74},
        ]
        
        for epoch_data in epochs_data:
            mlflow.log_metrics({
                "train_loss": epoch_data["train_loss"],
                "val_loss": epoch_data["val_loss"],
                "train_accuracy": epoch_data["train_acc"],
                "val_accuracy": epoch_data["val_acc"]
            }, step=epoch_data["epoch"])
        
        # Log final metrics
        mlflow.log_metrics({
            "best_val_accuracy": 94.74,
            "test_accuracy": 96.49,
            "pruned_test_accuracy": 96.49,
            "quantized_test_accuracy": 96.49,
            "model_size_mb": 16.76,
            "inference_time_ms": 44.3
        })
        
        # Log class-wise performance
        class_metrics = {
            "bird_drop_precision": 1.0, "bird_drop_recall": 1.0, "bird_drop_f1": 1.0,
            "clean_precision": 0.6667, "clean_recall": 1.0, "clean_f1": 0.80,
            "dusty_precision": 1.0, "dusty_recall": 0.7778, "dusty_f1": 0.875,
            "electrical_damage_precision": 1.0, "electrical_damage_recall": 1.0, "electrical_damage_f1": 1.0,
            "physical_damage_precision": 1.0, "physical_damage_recall": 1.0, "physical_damage_f1": 1.0,
            "snow_precision": 1.0, "snow_recall": 1.0, "snow_f1": 1.0,
        }
        mlflow.log_metrics(class_metrics)
        
        # Create and log training plots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
        train_losses = [e["train_loss"] for e in epochs_data]
        val_losses = [e["val_loss"] for e in epochs_data]
        train_accs = [e["train_acc"] for e in epochs_data]
        val_accs = [e["val_acc"] for e in epochs_data]
        epochs = range(1, 11)
        
        ax1.plot(epochs, train_losses, 'b-', label='Train Loss')
        ax1.plot(epochs, val_losses, 'r-', label='Val Loss')
        ax1.set_title('Loss Curves')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Loss')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        ax2.plot(epochs, train_accs, 'b-', label='Train Acc')
        ax2.plot(epochs, val_accs, 'r-', label='Val Acc')
        ax2.set_title('Accuracy Curves')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Accuracy (%)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        mlflow.log_figure(fig, "training_curves.png")
        plt.close()
        
        # Log tags
        mlflow.set_tags({
            "project": "Solar Panel Defect Detection",
            "framework": "PyTorch",
            "deployment": "Android + API",
            "optimization": "Pruning + Quantization + TorchScript"
        })
        
        print(f"Run completed! Run ID: {mlflow.active_run().info.run_id}")

if __name__ == "__main__":
    log_training_results()
    print("Training results logged to MLflow!")