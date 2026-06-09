# Solar Panel Defect Detection - DevOps/MLOps Project

## Project overview
This repository combines the Flask prediction app, MLflow tracking, Jenkins automation, Docker packaging, and an AWS deployment path. The main goal is to support the full DevOps/MLOps lifecycle while keeping your current Jenkins and MLflow run commands intact.

## Workflow and tool integration
1. The user uploads an image in the Flask app.
2. The model analyzes the image and returns the defect class and recommendation.
3. MLflow stores model metadata and prediction insights.
4. Jenkins runs the automated pipeline and validates the model workflow.
5. Docker packages the app for deployment and AWS hosting.

## Current local setup
- Jenkins: D:\Jenkins\jenkins.war --httpPort=8088
- MLflow: sqlite:///D:/mlflow/mlflow.db with artifacts in D:/mlflow/artifacts
- Web app: python web_app.py on port 8000

## Deployment plan
- AWS EC2: host the web app for real-time inference.
- AWS ECR: store the Docker image.
- AWS S3: keep model artifacts and training outputs.
- Optional ALB + Route 53: expose the application in production.

## Performance note
The image analysis time is governed mainly by the model runtime on the machine that executes the prediction. The app now follows the same MLflow server path you already use and uses a reusable image transform path to reduce overhead during local testing.
