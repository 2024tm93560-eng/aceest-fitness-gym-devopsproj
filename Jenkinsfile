pipeline {
    agent any

    // ── Build triggers ────────────────────────────────────────────────────
    triggers {
        pollSCM('H/5 * * * *')   // poll GitHub every 5 minutes
    }

    // ── Pipeline-wide environment variables ───────────────────────────────
    environment {
        APP_NAME          = 'aceest-fitness'
        DOCKER_HUB_USER   = 'your-dockerhub-username'          // ← update this
        DOCKER_IMAGE      = "${DOCKER_HUB_USER}/${APP_NAME}"
        DOCKER_TAG        = "${BUILD_NUMBER}"
        DOCKER_LATEST_TAG = 'latest'
        SONAR_HOST        = 'http://localhost:9000'
        SONAR_TOKEN       = credentials('sonarqube-token')
        KUBECONFIG        = credentials('kubeconfig')
        K8S_NAMESPACE     = 'aceest'
        REGISTRY_CRED     = 'dockerhub-credentials'
        GIT_COMMIT_SHORT  = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
    }

    // ── Build options ─────────────────────────────────────────────────────
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 45, unit: 'MINUTES')
        timestamps()
        disableConcurrentBuilds()
    }

    stages {

        // ── Stage 1: Checkout ─────────────────────────────────────────────
        stage('Checkout') {
            steps {
                echo '📥 Checking out source code from GitHub...'
                checkout scm
                sh 'git log --oneline -5'
            }
        }

        // ── Stage 2: Setup Python Environment ────────────────────────────
        stage('Setup Python Environment') {
            steps {
                echo '🐍 Setting up Python virtual environment...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        // ── Stage 3: Unit Tests (Pytest) ──────────────────────────────────
        stage('Unit Tests - Pytest') {
            steps {
                echo '🧪 Running Pytest unit tests...'
                sh '''
                    . venv/bin/activate
                    pytest tests/ \
                        --tb=short \
                        --junitxml=reports/pytest-results.xml \
                        --cov=app \
                        --cov-report=xml:reports/coverage.xml \
                        --cov-report=html:reports/htmlcov \
                        -v
                '''
            }
            post {
                always {
                    junit 'reports/pytest-results.xml'
                    publishHTML(target: [
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'reports/htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }

        // ── Stage 4: SonarQube Analysis ───────────────────────────────────
        stage('SonarQube Analysis') {
            steps {
                echo '🔍 Running SonarQube static code analysis...'
                withSonarQubeEnv('SonarQube') {
                    sh '''
                        sonar-scanner \
                            -Dsonar.projectKey=aceest-fitness \
                            -Dsonar.projectName="ACEest Fitness & Gym" \
                            -Dsonar.projectVersion=${BUILD_NUMBER} \
                            -Dsonar.sources=app \
                            -Dsonar.tests=tests \
                            -Dsonar.python.coverage.reportPaths=reports/coverage.xml \
                            -Dsonar.python.xunit.reportPath=reports/pytest-results.xml \
                            -Dsonar.host.url=${SONAR_HOST} \
                            -Dsonar.login=${SONAR_TOKEN}
                    '''
                }
            }
        }

        // ── Stage 5: Quality Gate ─────────────────────────────────────────
        stage('Quality Gate') {
            steps {
                echo '🚦 Waiting for SonarQube Quality Gate result...'
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        // ── Stage 6: Docker Build ─────────────────────────────────────────
        stage('Docker Build') {
            steps {
                echo '🐳 Building Docker image...'
                sh '''
                    docker build \
                        --build-arg BUILD_NUMBER=${BUILD_NUMBER} \
                        --build-arg GIT_COMMIT=${GIT_COMMIT_SHORT} \
                        -t ${DOCKER_IMAGE}:${DOCKER_TAG} \
                        -t ${DOCKER_IMAGE}:${DOCKER_LATEST_TAG} \
                        .
                '''
                sh 'docker images | grep ${APP_NAME}'
            }
        }

        // ── Stage 7: Docker Test in Container ────────────────────────────
        stage('Test in Container') {
            steps {
                echo '🧪 Running tests inside Docker container...'
                sh '''
                    docker run --rm \
                        -v $(pwd)/reports:/app/reports \
                        ${DOCKER_IMAGE}:${DOCKER_TAG} \
                        sh -c "pip install pytest pytest-cov && pytest tests/ --tb=short -v"
                '''
            }
        }

        // ── Stage 8: Push to Docker Hub ───────────────────────────────────
        stage('Push to Docker Hub') {
            steps {
                echo '📤 Pushing Docker image to Docker Hub...'
                withCredentials([usernamePassword(
                    credentialsId: "${REGISTRY_CRED}",
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push ${DOCKER_IMAGE}:${DOCKER_TAG}
                        docker push ${DOCKER_IMAGE}:${DOCKER_LATEST_TAG}
                        docker logout
                    '''
                }
            }
        }

        // ── Stage 9: Deploy to Kubernetes ────────────────────────────────
        stage('Deploy - Rolling Update (Default)') {
            when {
                branch 'main'
            }
            steps {
                echo '☸️ Deploying to Kubernetes (Rolling Update)...'
                sh '''
                    kubectl --kubeconfig=${KUBECONFIG} apply -f k8s/rolling/
                    kubectl --kubeconfig=${KUBECONFIG} set image deployment/aceest-fitness \
                        aceest-fitness=${DOCKER_IMAGE}:${DOCKER_TAG} \
                        -n ${K8S_NAMESPACE}
                    kubectl --kubeconfig=${KUBECONFIG} rollout status deployment/aceest-fitness \
                        -n ${K8S_NAMESPACE} --timeout=120s
                '''
            }
        }

        // ── Stage 10: Blue-Green Deployment ──────────────────────────────
        stage('Deploy - Blue-Green') {
            when {
                branch 'release'
            }
            steps {
                echo '🟢🔵 Executing Blue-Green Deployment...'
                sh '''
                    # Deploy Green environment
                    kubectl --kubeconfig=${KUBECONFIG} apply -f k8s/blue-green/green-deployment.yaml \
                        -n ${K8S_NAMESPACE}
                    kubectl --kubeconfig=${KUBECONFIG} set image deployment/aceest-green \
                        aceest-fitness=${DOCKER_IMAGE}:${DOCKER_TAG} \
                        -n ${K8S_NAMESPACE}
                    kubectl --kubeconfig=${KUBECONFIG} rollout status deployment/aceest-green \
                        -n ${K8S_NAMESPACE} --timeout=120s

                    # Switch service traffic to Green
                    kubectl --kubeconfig=${KUBECONFIG} patch service aceest-service \
                        -n ${K8S_NAMESPACE} \
                        -p '{"spec":{"selector":{"version":"green"}}}'

                    echo "✅ Traffic switched to Green. Blue remains as fallback."
                '''
            }
        }

        // ── Stage 11: Canary Release ──────────────────────────────────────
        stage('Deploy - Canary') {
            when {
                branch 'canary'
            }
            steps {
                echo '🐦 Executing Canary Release (10% traffic)...'
                sh '''
                    kubectl --kubeconfig=${KUBECONFIG} apply -f k8s/canary/ -n ${K8S_NAMESPACE}
                    kubectl --kubeconfig=${KUBECONFIG} set image deployment/aceest-canary \
                        aceest-fitness=${DOCKER_IMAGE}:${DOCKER_TAG} \
                        -n ${K8S_NAMESPACE}
                    kubectl --kubeconfig=${KUBECONFIG} rollout status deployment/aceest-canary \
                        -n ${K8S_NAMESPACE} --timeout=120s
                    echo "✅ Canary deployed. Monitor metrics before full rollout."
                '''
            }
        }
    }

    // ── Post-build actions ────────────────────────────────────────────────
    post {
        success {
            echo '✅ Pipeline completed successfully!'
            sh 'docker rmi ${DOCKER_IMAGE}:${DOCKER_TAG} || true'
        }
        failure {
            echo '❌ Pipeline failed! Initiating rollback...'
            sh '''
                kubectl --kubeconfig=${KUBECONFIG} rollout undo deployment/aceest-fitness \
                    -n ${K8S_NAMESPACE} || true
            '''
            mail(
                to: 'devops-team@aceest.com',
                subject: "BUILD FAILED: ${JOB_NAME} #${BUILD_NUMBER}",
                body: "Check Jenkins: ${BUILD_URL}"
            )
        }
        always {
            cleanWs()
        }
    }
}
