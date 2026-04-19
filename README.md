# ACEest Fitness & Gym — DevOps Assignment 2

## Overview
End-to-end DevOps CI/CD pipeline for the ACEest Fitness & Gym Management System.

## Technologies
Python/Flask · Git/GitHub · Jenkins · GitHub Actions · Pytest · SonarQube · Docker · Kubernetes/Minikube · Istio

## Project Structure
```
aceest-fitness-gym-devopsproj/
├── ACEest_Fitness.py          ← Flask app v1.0.0
├── ACEest_Fitness_v2.py       ← Flask app v2.0.0
├── app.py                     ← Original v0 (Assignment 1)
├── requirements.txt
├── Dockerfile                 ← Multi-stage build
├── docker-compose.yml         ← Local: App + Jenkins + SonarQube
├── Jenkinsfile                ← 9-stage CI/CD pipeline
├── tests/
│   ├── test_aceest.py         ← 40+ Pytest test cases
│   └── conftest.py
├── k8s/
│   ├── namespace.yaml
│   ├── rolling/               ← Rolling Update
│   ├── blue-green/            ← Blue-Green
│   ├── canary/                ← Canary Release
│   ├── shadow/                ← Shadow (Istio)
│   └── ab-testing/            ← A/B Testing (Istio)
├── sonarqube/
│   └── sonar-project.properties
├── report/
│   └── ACEest_DevOps_Assignment2_Report.docx
└── .github/workflows/main.yml ← GitHub Actions CI/CD
```

## Quick Start
```bash
pip install -r requirements.txt
python ACEest_Fitness.py
# http://localhost:5000
```

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | App info |
| GET | /health | Health check |
| GET/POST | /members | Members |
| GET/POST | /trainers | Trainers |
| GET/POST | /classes | Classes |
| POST | /classes/<id>/enroll | Enroll |
| GET | /plans | Membership plans |
| POST | /bmi | BMI calculator |
| POST | /attendance/checkin | Check-in (v2) |
| GET | /diet-plans | Diet plans (v2) |

## Tests
```bash
pytest tests/ -v --cov=. --cov-report=term-missing
```

## Docker
```bash
docker build -t YOUR_USERNAME/aceest-fitness:v1.0.0 .
docker run -p 5000:5000 YOUR_USERNAME/aceest-fitness:v1.0.0
docker push YOUR_USERNAME/aceest-fitness:v1.0.0
docker push YOUR_USERNAME/aceest-fitness:latest
```

## Local Jenkins + SonarQube
```bash
docker compose up -d
# Jenkins:   http://localhost:8080
# SonarQube: http://localhost:9000
```

## Kubernetes
```bash
minikube start
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/rolling/          # default
minikube service aceest-service -n aceest --url
# Rollback: kubectl rollout undo deployment/aceest-fitness -n aceest
```

## Deployment Strategies
| Strategy | Trigger Branch | Rollback |
|----------|---------------|---------|
| Rolling Update | main | kubectl rollout undo |
| Blue-Green | release | Patch service selector |
| Canary | canary | Scale canary to 0 |
| Shadow | — | Stop Istio mirroring |
| A/B Testing | — | Remove routing rule |

## GitHub Actions Secrets Needed
- DOCKERHUB_USERNAME
- DOCKERHUB_TOKEN
- SONAR_TOKEN
- SONAR_HOST_URL
