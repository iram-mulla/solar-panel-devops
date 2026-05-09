import mlflow
import os

# Set MLflow tracking URI
mlflow.set_tracking_uri("http://127.0.0.1:5000")

# Create experiment for solar panel project
experiment_name = "solar-panel-defect-detection"

try:
    experiment_id = mlflow.create_experiment(
        name=experiment_name,
        artifact_location="file:///D:/mlflow/artifacts"
    )
    print(f"Experiment created with ID: {experiment_id}")
except Exception as e:
    # Experiment might already exist
    experiment = mlflow.get_experiment_by_name(experiment_name)
    print(f"Experiment already exists with ID: {experiment.experiment_id}")

# List all experiments
print("\nAll experiments:")
experiments = mlflow.search_experiments()
for exp in experiments:
    print(f"  - {exp.name} (ID: {exp.experiment_id})")