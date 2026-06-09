FROM python:3.9-slim

WORKDIR /app

# Install PyTorch from official repo first (CPU version - smaller)
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install other packages from PyPI (default)
RUN pip install --no-cache-dir flask pillow numpy matplotlib seaborn scikit-learn mlflow boto3

# Copy application code
COPY web_app.py .
COPY templates/ ./templates/
COPY models/ ./models/

EXPOSE 8000

CMD ["python", "web_app.py"]