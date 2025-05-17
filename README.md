# BE for Bao's solution: URL classification

# 2 ways to run the project
## Using docker
Download docker for your machine: https://docs.docker.com/compose/install/

(Optional but recommend) Install docker and docker compose extension for your IDE

Start app: in terminal run "docker-compose up -d" or "make dev"
Stop app: in terminal run "docker-compose down" or "make dev-down"

Or use the docker compose extension function if you have it

## Run wihout docker

Download python3.11 and create and venv with it
Run "pip install -r requirements.txt"
Run "make start-reload" or "make start"

## Swagger
After app run, go to:
localhost:8000/docs for swagger ui
localhost:8000/redoc for redoc
