FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ALL application code
COPY web_app.py .
COPY predict_with_mlflow.py .
COPY log_model_training.py .
COPY register_model.py .
COPY setup_mlflow_experiment.py .
COPY templates/ ./templates/
COPY models/ ./models/
COPY test_images/ ./test_images/
COPY mlflow_experiments/ ./mlflow_experiments/

# Create MLflow directories
RUN mkdir -p /tmp/mlflow/mlruns /tmp/mlflow/artifacts

# Expose ports for web app and MLflow
EXPOSE 8000 5000

# Start both MLflow server and web app
CMD ["sh", "-c", "mlflow server --backend-store-uri sqlite:///tmp/mlflow/mlflow.db --default-artifact-root file:///tmp/mlflow/artifacts --host 0.0.0.0 --port 5000 & python web_app.py"]