\# Solar Panel Defect Detection - DevOps/MLOps Project



\## Project Overview

Automated solar panel defect detection system using EfficientNet-B0 with MLflow for experiment tracking and model management. The current project already includes the Jenkins pipeline, Docker packaging, and MLflow workflow you asked for, so the existing local commands should remain unchanged.



\## Architecture

User upload -> Flask web app -> PyTorch/TorchScript model -> defect prediction + recommendation
                              -> MLflow tracking + model registry
                              -> Jenkins pipeline automation
                              -> Docker container for deployment

The current local setup is:
- Jenkins on port 8088
- MLflow on port 5000
- Flask app on port 8000

## DevOps setup notes
- Jenkins pipeline: already defined in Jenkinsfile and should stay as-is.
- MLflow server: already uses D:/mlflow as requested; the app now follows that same tracking URI.
- Docker: already containerized via Dockerfile. This is ready for deployment packaging.
- AWS plan: EC2 for the app, ECR for container image storage, and S3/MLflow artifacts for model outputs.

## Local setup on D: drive only
Use the project virtual environment under D:\Engineering\6th sem\DevOps\solar-panel-devops\.venv instead of installing packages into C:\.

```powershell
cd "D:\Engineering\6th sem\DevOps\solar-panel-devops"
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The existing run commands are already aligned with this setup, so there is no need to change the Jenkins or MLflow commands you are using today.





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

