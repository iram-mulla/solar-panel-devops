pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "solar-panel-api"
        DOCKER_TAG = "${env.BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo "Code checked out from GitHub"
            }
        }
        
        stage('Setup Python') {
            steps {
                bat '''
                    python -m venv venv
                    venv\\Scripts\\activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Code Quality') {
            steps {
                bat '''
                    venv\\Scripts\\activate
                    pip install flake8
                    flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}", "-f docker/Dockerfile .")
                }
            }
        }
        
        stage('Test Container') {
            steps {
                bat '''
                    docker run -d -p 8000:8000 --name test-container %DOCKER_IMAGE%:%DOCKER_TAG%
                    timeout /t 10
                    curl http://localhost:8000/health
                    docker stop test-container
                    docker rm test-container
                '''
            }
        }
        
        stage('Push to Docker Hub') {
            when {
                branch 'main'
            }
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', 'docker-hub-credentials') {
                        docker.image("${DOCKER_IMAGE}").push("${DOCKER_TAG}")
                        docker.image("${DOCKER_IMAGE}").push("latest")
                    }
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}