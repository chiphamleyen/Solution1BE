dev:
	docker-compose up -d

dev-down:
	docker-compose down

start:
	uvicorn main:app --host 0.0.0.0 --port 8080

start-reload:
	python main-hotload.py