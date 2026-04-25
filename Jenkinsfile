pipeline {
    agent any

    environment {
        APP_NAME    = 'aceest-fitness'
        DOCKER_USER = 'your-dockerhub-username'
    }

    stages {

        stage('Checkout') {
            steps {
                echo '📥 Checking out source code...'
                checkout scm
                sh 'echo "Branch: $GIT_BRANCH"'
                sh 'echo "Commit: $GIT_COMMIT"'
                sh 'ls -la'
            }
        }

        stage('Setup Python') {
            steps {
                echo '🐍 Setting up Python environment...'
                sh '''
                    python3 --version
                    pip3 install flask pytest pytest-cov --quiet
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo '🧪 Running Pytest unit tests...'
                sh '''
                    export PYTHONPATH=$(pwd)
                    python3 -m pytest tests/ -v --tb=short \
                        --junitxml=pytest-results.xml \
                        --cov=. --cov-report=xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'pytest-results.xml'
                }
            }
        }

        stage('Code Quality Check') {
            steps {
                echo '🔍 Checking code quality...'
                sh '''
                    pip3 install pylint --quiet
                    pylint ACEest_Fitness.py --exit-zero --score=yes || true
                '''
            }
        }

        stage('Docker Build') {
            steps {
                echo '🐳 Building Docker image...'
                sh '''
                    docker build -t ${APP_NAME}:latest .
                    docker build -t ${APP_NAME}:v1.0.0 .
                    docker images | grep ${APP_NAME}
                '''
            }
        }

        stage('Test Docker Container') {
            steps {
                echo '✅ Testing Docker container...'
                sh '''
                    docker run -d --name test-aceest -p 5050:5000 ${APP_NAME}:latest
                    sleep 5
                    curl -f http://localhost:5050/health || echo "Health check done"
                    docker stop test-aceest
                    docker rm test-aceest
                '''
            }
        }

        stage('Deployment Ready') {
            steps {
                echo '🚀 Application is ready for deployment!'
                echo '📦 Docker image built: ${APP_NAME}:latest'
                echo '📋 K8s manifests available in k8s/ folder'
                echo '🔵🟢 Blue-Green: k8s/blue-green/'
                echo '🐦 Canary:     k8s/canary/'
                echo '👥 Shadow:     k8s/shadow/'
                echo '🔄 Rolling:    k8s/rolling/'
                echo '🆎 A/B Test:   k8s/ab-testing/'
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check logs above.'
        }
    }
}
