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

# Copy application code
COPY src/ ./src/
COPY models/ ./models/
COPY mlflow_experiments/ ./mlflow_experiments/

# Create MLflow directories
RUN mkdir -p /tmp/mlflow/mlruns /tmp/mlflow/artifacts

EXPOSE 8000 5000

# Start both MLflow server and API
CMD ["sh", "-c", "mlflow server --backend-store-uri file:///tmp/mlflow/mlruns --default-artifact-root file:///tmp/mlflow/artifacts --host 0.0.0.0 --port 5000 & python src/app.py"]