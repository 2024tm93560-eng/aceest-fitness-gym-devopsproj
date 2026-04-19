#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# ACEest Fitness — Assignment 2 Setup Script
# Run this ONCE after cloning or updating your repo.
# Usage: bash setup.sh YOUR_DOCKERHUB_USERNAME
# ─────────────────────────────────────────────────────────────────────────────

set -e

DOCKER_USER=${1:-"your-dockerhub-username"}

echo ""
echo "=================================================="
echo "  ACEest Fitness — DevOps Assignment 2 Setup"
echo "  Docker Hub user: $DOCKER_USER"
echo "=================================================="
echo ""

# ── Step 1: Replace placeholder username in all files ─────────────────────
echo "[1/8] Patching Docker Hub username in all files..."
find . -type f \( -name "*.yaml" -o -name "*.yml" -o -name "Jenkinsfile" \) \
  -exec sed -i "s/your-dockerhub-username/$DOCKER_USER/g" {} +
echo "      ✅ Patched"

# ── Step 2: Install Python dependencies ───────────────────────────────────
echo "[2/8] Installing Python dependencies..."
pip install -r requirements.txt --quiet
echo "      ✅ Done"

# ── Step 3: Run tests ──────────────────────────────────────────────────────
echo "[3/8] Running Pytest..."
pytest tests/ -v --tb=short
echo "      ✅ Tests passed"

# ── Step 4: Build Docker images ────────────────────────────────────────────
echo "[4/8] Building Docker images..."
docker build -t $DOCKER_USER/aceest-fitness:v1.0.0 -t $DOCKER_USER/aceest-fitness:latest .
echo "      ✅ Image built"

# ── Step 5: Push to Docker Hub ─────────────────────────────────────────────
echo "[5/8] Pushing to Docker Hub (login required)..."
docker login
docker push $DOCKER_USER/aceest-fitness:v1.0.0
docker push $DOCKER_USER/aceest-fitness:latest
echo "      ✅ Pushed"

# ── Step 6: Git branches and tags ─────────────────────────────────────────
echo "[6/8] Creating Git branches and version tags..."
git checkout -b release 2>/dev/null || git checkout release
git push origin release 2>/dev/null || true
git checkout -b canary 2>/dev/null || git checkout canary
git push origin canary 2>/dev/null || true
git checkout main
git tag -a v1.0.0 -m "Version 1.0.0 - Core gym management" 2>/dev/null || true
git tag -a v2.0.0 -m "Version 2.0.0 - Attendance and diet plans" 2>/dev/null || true
git push --tags 2>/dev/null || true
echo "      ✅ Branches: main, release, canary | Tags: v1.0.0, v2.0.0"

# ── Step 7: Start Minikube and deploy ─────────────────────────────────────
echo "[7/8] Starting Minikube and deploying Rolling Update..."
minikube start --driver=docker 2>/dev/null || minikube start
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/rolling/
echo "      Waiting for pods to be ready..."
kubectl rollout status deployment/aceest-fitness -n aceest --timeout=120s
SERVICE_URL=$(minikube service aceest-service -n aceest --url 2>/dev/null)
echo ""
echo "      ✅ App running at: $SERVICE_URL"
echo "      ✅ Health check:   $SERVICE_URL/health"

# ── Step 8: Start local Jenkins + SonarQube ───────────────────────────────
echo "[8/8] Starting Jenkins + SonarQube via Docker Compose..."
docker compose up -d jenkins sonarqube sonar-db
echo ""
echo "      ✅ Jenkins:   http://localhost:8080"
echo "      ✅ SonarQube: http://localhost:9000  (admin / admin)"
echo ""

# ── Summary ───────────────────────────────────────────────────────────────
echo "=================================================="
echo "  SETUP COMPLETE"
echo "=================================================="
echo ""
echo "  App endpoint:   $SERVICE_URL"
echo "  Jenkins:        http://localhost:8080"
echo "  SonarQube:      http://localhost:9000"
echo "  Docker Hub:     hub.docker.com/r/$DOCKER_USER/aceest-fitness"
echo ""
echo "  Next steps:"
echo "  1. Open Jenkins → New Item → Pipeline → GitHub repo URL"
echo "  2. Add credentials: dockerhub-credentials, sonarqube-token, kubeconfig"
echo "  3. Build Now → verify all 9 stages are green"
echo "  4. Open SonarQube → Projects → aceest-fitness-gym → Quality Gate"
echo "  5. Apply other k8s strategies:"
echo "     kubectl apply -f k8s/blue-green/"
echo "     kubectl apply -f k8s/canary/"
echo ""
