\# Aceest Fitness DevOps Project



This project demonstrates a simple Python application with a DevOps pipeline.



\## Technologies Used



\- Python

\- Flask

\- Docker

\- Git

\- GitHub

\- GitHub Actions

\- Pytest



\## Project Structure



aceest-fitness/

│

├── app.py

├── test\_app.py

├── requirements.txt

├── Dockerfile

├── README.md

├── versions/



\## Running the Application



Install dependencies:



pip install -r requirements.txt



Run the application:



python app.py



Open in browser:



http://localhost:5000



\## Running Tests



pytest



\## Docker Build



docker build -t aceest-app .



Run container:



docker run -p 5000:5000 aceest-app



\## CI/CD



CI pipeline is implemented using GitHub Actions which automatically runs tests when code is pushed to the main branch.

