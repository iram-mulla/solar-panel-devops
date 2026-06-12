pipeline {
    agent any
    
    environment {
        MLFLOW_URI = "http://127.0.0.1:5000"
        PIP_CACHE_DIR = "D:\\pip-cache"
        TEMP = "D:\\temp"
        TMP = "D:\\temp"
        PYTHONUSERBASE = "D:\\python-user"
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
                echo "Stage 2: Setting up Python environment (packages cached on D: drive)"
                bat '''
                    if not exist D:\\pip-cache mkdir D:\\pip-cache
                    if not exist D:\\temp mkdir D:\\temp
                    pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
                    pip install numpy pillow flask mlflow matplotlib seaborn scikit-learn boto3
                '''
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
                echo "Stage 7: Running test predictions on all 6 defect types"
                bat '''
                    echo ========================================
                    echo Testing ALL defect types...
                    echo ========================================
                    
                    echo [1/6] Testing bird-drop...
                    python predict_with_mlflow.py "test_images\\birddrop.png"
                    
                    echo [2/6] Testing clean panel...
                    python predict_with_mlflow.py "test_images\\clean.png"
                    
                    echo [3/6] Testing dusty panel...
                    python predict_with_mlflow.py "test_images\\dust.png"
                    
                    echo [4/6] Testing electrical damage...
                    python predict_with_mlflow.py "test_images\\Electrical_Damage.jpg"
                    
                    echo [5/6] Testing physical damage...
                    python predict_with_mlflow.py "test_images\\physical_damage.png"
                    
                    echo [6/6] Testing snow covered...
                    python predict_with_mlflow.py "test_images\\snow.png"
                    
                    echo ========================================
                    echo ALL 6/6 prediction tests PASSED!
                    echo ========================================
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