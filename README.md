\# Solar Panel Defect Detection - DevOps/MLOps Project



\## Project Overview

Automated solar panel defect detection system using EfficientNet-B0 with MLflow for experiment tracking and model management.



\## Architecture

┌─────────────┐ ┌──────────────┐ ┌─────────────┐

│ Web App │────▶│ ML Model │────▶│ Prediction │

│ (Flask) │ │ (PyTorch) │ │ Results │

└─────────────┘ └──────────────┘ └─────────────┘

│ │

▼ ▼

┌─────────────┐ ┌──────────────┐

│ MLflow │ │ Model │

│ Tracking │ │ Registry │

└─────────────┘ └──────────────┘





\## Technologies Used

\- \*\*ML Framework\*\*: PyTorch, EfficientNet-B0

\- \*\*Experiment Tracking\*\*: MLflow

\- \*\*Model Registry\*\*: MLflow Model Registry

\- \*\*Web Framework\*\*: Flask

\- \*\*Containerization\*\*: Docker

\- \*\*Version Control\*\*: Git/GitHub

\- \*\*Model Format\*\*: TorchScript (optimized for deployment)



\## Model Details

\- \*\*Architecture\*\*: EfficientNet-B0 (pretrained on ImageNet)

\- \*\*Classes\*\*: bird-drop, clean, dusty, electrical-damage, physical-damage, snow

\- \*\*Optimization\*\*: 30% Pruning + INT8 Quantization

\- \*\*Size\*\*: 16.76 MB

\- \*\*Accuracy\*\*: 96.49% (Test Set)

\- \*\*Inference Time\*\*: \~44.3ms per image



\## Setup Instructions



\### Prerequisites

\- Python 3.9+

\- Docker (optional)

\- Git



\### Installation

```bash

\# Clone repository

git clone https://github.com/YOUR\_USERNAME/solar-panel-devops.git

cd solar-panel-devops



\# Install dependencies

pip install -r requirements.txt



\# Place model file in models/ directory

\# solar\_panel\_android.pt should be in models/

