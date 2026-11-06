.PHONY: install test run lint docker-build docker-run docker-health

install:
	pip install -r requirements-dev.txt

test:
	pytest --cov=src/detector --cov-report=term-missing

run:
	uvicorn detector.api:app --app-dir src --host 0.0.0.0 --port 8000 --reload

lint:
	ruff check src tests

docker-build:
	docker build -t fake-job-detector:latest .

docker-run:
	docker run --rm -p 8000:8000 fake-job-detector:latest

docker-health:
	curl -f http://localhost:8000/health
