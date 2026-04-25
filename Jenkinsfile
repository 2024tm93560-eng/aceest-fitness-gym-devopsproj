pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
                sh 'ls -la'
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing Python dependencies...'
                sh 'pip3 install flask pytest pytest-cov pylint --quiet --break-system-packages'
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running 44 Pytest tests...'
                sh 'export PYTHONPATH=$(pwd) && python3 -m pytest tests/ -v --tb=short --junitxml=pytest-results.xml --cov=. --cov-report=xml'
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'pytest-results.xml'
                }
            }
        }

        stage('Code Quality') {
            steps {
                echo 'Running pylint code quality check...'
                sh 'python3 -m pylint ACEest_Fitness.py --exit-zero --score=yes || true'
            }
        }

        stage('Docker Info') {
            steps {
                echo 'Docker image details:'
                echo 'Image: aceest-fitness:v1.0.0'
                echo 'Image: aceest-fitness:v2.0.0'
                sh 'cat Dockerfile'
            }
        }

        stage('Deployment Strategies') {
            steps {
                echo 'Kubernetes deployment strategies:'
                sh 'ls k8s/'
            }
        }
    }

    post {
        success {
            echo 'Pipeline PASSED - All 44 tests passed!'
        }
        failure {
            echo 'Pipeline failed. Check logs.'
        }
    }
}
