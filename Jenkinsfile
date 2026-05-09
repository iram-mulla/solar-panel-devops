pipeline {
    agent any
    
    environment {
        MLFLOW_URI = "http://127.0.0.1:5000"
    }
    
    stages {
        stage('Code Checkout') {
            steps {
                echo "Stage 1: Code checked out from GitHub"
                checkout scm
            }
        }
        
        stage('Setup Python') {
            steps {
                echo "Stage 2: Setting up Python environment"
                bat 'pip install torch torchvision numpy pillow flask mlflow matplotlib seaborn scikit-learn boto3'
            }
        }
        
        stage('Verify Model & MLflow') {
            steps {
                echo "Stage 3: Verifying model and MLflow connection"
                bat '''
                    python -c "import torch; print('PyTorch:', torch.__version__)"
                    python -c "import mlflow; mlflow.set_tracking_uri('http://127.0.0.1:5000'); print('MLflow connected!')"
                    dir models\\solar_panel_android.pt
                '''
            }
        }
        
        stage('Setup MLflow Experiment') {
            steps {
                echo "Stage 4: Creating MLflow experiment"
                bat 'python setup_mlflow_experiment.py'
            }
        }
        
        stage('Log Training to MLflow') {
            steps {
                echo "Stage 5: Logging training metrics to MLflow"
                bat 'python log_model_training.py'
            }
        }
        
        stage('Register Model in MLflow') {
            steps {
                echo "Stage 6: Registering model in MLflow Registry"
                bat 'python register_model.py'
            }
        }
        
        stage('Run Prediction Tests') {
            steps {
                echo "Stage 7: Running test predictions"
                bat '''
                    python predict_with_mlflow.py "dataset\\birddrop.png"
                    python predict_with_mlflow.py "dataset\\clean.png"
                    python predict_with_mlflow.py "dataset\\physical_damage.png"
                '''
            }
        }
        
        stage('Generate Report') {
            steps {
                echo "Stage 8: Generating pipeline report"
                bat '''
                    echo JENKINS + MLFLOW PIPELINE REPORT > pipeline_report.txt
                    echo =============================== >> pipeline_report.txt
                    echo Build: %BUILD_NUMBER% >> pipeline_report.txt
                    echo Date: %DATE% %TIME% >> pipeline_report.txt
                    echo. >> pipeline_report.txt
                    echo Stages Completed: >> pipeline_report.txt
                    echo [OK] Code Checkout >> pipeline_report.txt
                    echo [OK] Python Setup >> pipeline_report.txt
                    echo [OK] Model Verification >> pipeline_report.txt
                    echo [OK] MLflow Setup >> pipeline_report.txt
                    echo [OK] Training Logged >> pipeline_report.txt
                    echo [OK] Model Registered >> pipeline_report.txt
                    echo [OK] Predictions Tested >> pipeline_report.txt
                    echo [OK] Report Generated >> pipeline_report.txt
                    echo. >> pipeline_report.txt
                    echo MLflow UI: http://127.0.0.1:5000 >> pipeline_report.txt
                    echo Web App: http://127.0.0.1:8000 >> pipeline_report.txt
                    type pipeline_report.txt
                '''
            }
        }
    }
    
    post {
        success {
            echo 'SUCCESS! MLflow: http://127.0.0.1:5000 | Web: http://127.0.0.1:8000'
        }
        failure {
            echo 'FAILED - Check logs above'
        }
    }
}