import mlflow 
mlflow.set_tracking_uri('file:///D:/mlflow/mlruns') 
mlflow.set_experiment('test-experiment') 
with mlflow.start_run(): 
    mlflow.log_param("test", "hello") 
    mlflow.log_metric("accuracy", 0.95) 
print("Test run logged successfully!") 
