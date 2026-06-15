FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

WORKDIR /app

# Install additional packages
RUN pip install --no-cache-dir flask mlflow scikit-learn matplotlib seaborn

# Create MLflow directory with write permissions
RUN mkdir -p /mlflow_data && chmod 777 /mlflow_data

# Copy application code
COPY web_app.py .
COPY templates/ ./templates/
COPY models/ ./models/

EXPOSE 8000

CMD ["python", "web_app.py"]