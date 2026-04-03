# Aceest Fitness DevOps Project

## Overview

This project demonstrates a DevOps CI/CD pipeline for ACEest Fitness & Gym.

## Technologies Used

- Python
- Flask
- Docker
- Git
- GitHub
- GitHub Actions
- Pytest
- Jenkins

## Project Structure

aceest-fitness/
│
├── app.py
├── test_app.py
├── requirements.txt
├── Dockerfile
├── README.md
├── versions/

## Running the Application

pip install -r requirements.txt  
python app.py  

Open in browser:  
http://localhost:5000  

## Running Tests

pytest  

## Docker

docker build -t aceest-app .  
docker run -p 5000:5000 aceest-app  

## CI/CD Pipeline

GitHub Actions automatically:
- Installs dependencies
- Runs pytest
- Builds Docker image

## Jenkins Integration

Jenkins was configured to validate the build process by:

- Pulling code from GitHub repository
- Executing build steps
- Building Docker image

Jenkins acts as a secondary quality gate to ensure code stability and integration.
