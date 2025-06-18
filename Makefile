APP_NAME=srex
DOCKER_IMAGE=srex
PY_SRC=cli core tests backend src

# Use pip/venv
VENV=.venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

.PHONY: all build run test lint shell clean help api test-api format check-format install-dev install-prod docker-clean docker-build docker-run docker-test docker-lint start-services

all: build

venv:
	python -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt -r requirements-rag.txt

build: venv
	docker build -t $(DOCKER_IMAGE) .

run:
	docker run --rm \
		-v ${PWD}/examples:/app/examples \
		-v ${PWD}/output:/app/output \
		-p 8000:8000 \
		$(DOCKER_IMAGE)

test:
	$(PYTHON) -m pytest --cov=$(APP_NAME) --cov-report=term --cov-report=xml tests/

test-api:
	$(PYTHON) -m pytest backend/tests/

test-watch:
	$(PYTHON) -m pytest-watch --cov=$(APP_NAME) --cov-report=term tests/

lint:
	$(PYTHON) -m ruff $(PY_SRC)
	$(PYTHON) -m black --check $(PY_SRC)
	$(PYTHON) -m mypy $(PY_SRC)

format:
	$(PYTHON) -m black $(PY_SRC)
	$(PYTHON) -m ruff --fix $(PY_SRC)
	$(PYTHON) -m isort $(PY_SRC)

check-format:
	$(PYTHON) -m black --check $(PY_SRC)
	$(PYTHON) -m ruff --check $(PY_SRC)
	$(PYTHON) -m isort --check-only $(PY_SRC)

api:
	$(PYTHON) -m backend.api.main

install-dev: venv
	$(PIP) install -r requirements.txt -r requirements-rag.txt
	$(PIP) install -e ".[dev]"

install-prod: venv
	$(PIP) install -r requirements.txt -r requirements-rag.txt
	$(PIP) install -e .

docker-clean:
	docker system prune -f
	docker image rm $(DOCKER_IMAGE) || true

docker-build: docker-clean
	docker build -t $(DOCKER_IMAGE) .

docker-run: docker-build
	docker run --rm \
		-v ${PWD}/examples:/app/examples \
		-v ${PWD}/output:/app/output \
		-p 8000:8000 \
		$(DOCKER_IMAGE)

docker-test: docker-build
	docker run --rm \
		-v ${PWD}/tests:/app/tests \
		$(DOCKER_IMAGE) pytest

docker-lint: docker-build
	docker run --rm \
		-v ${PWD}:/app \
		$(DOCKER_IMAGE) sh -c "ruff $(PY_SRC) && black --check $(PY_SRC)"

shell:
	docker run --rm -it -v ${PWD}:/app $(DOCKER_IMAGE) bash

clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .coverage coverage.xml output/*.json output/*.md debug/*.txt
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +

help:
	@echo "Makefile commands:"
	@echo "  make venv           - Create and setup virtual environment"
	@echo "  make build          - Build Docker image"
	@echo "  make run            - Run container with mounted input/output"
	@echo "  make test           - Run tests with coverage"
	@echo "  make test-api       - Run API tests"
	@echo "  make test-watch     - Run tests in watch mode"
	@echo "  make lint           - Run Ruff, Black, and MyPy checks"
	@echo "  make format         - Format code with Black, Ruff, and isort"
	@echo "  make check-format   - Check code formatting"
	@echo "  make api            - Run the API server"
	@echo "  make install-dev    - Install development dependencies"
	@echo "  make install-prod   - Install production dependencies"
	@echo "  make docker-clean   - Clean Docker images and containers"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run Docker container"
	@echo "  make docker-test    - Run tests in Docker"
	@echo "  make docker-lint    - Run linting in Docker"
	@echo "  make shell          - Open a shell in the container"
	@echo "  make clean          - Remove cache and output files"
	@echo "  make start-services - Start Flask metrics simulator and FastAPI backend"

start-services:
	-pid=$$(lsof -t -i :8000); if [ -n "$$pid" ]; then kill $$pid; fi
	-pid=$$(lsof -t -i :8001); if [ -n "$$pid" ]; then kill $$pid; fi
	cd devtools/metrics-simulator && nohup python3 app.py > flask.log 2>&1 &
	cd backend && nohup python3 run.py > fastapi.log 2>&1 &
	@echo "Flask metrics simulator started on port 8000."
	@echo "FastAPI backend started on port 8001."

stop-services:
	-pid=$$(lsof -t -i :8000); if [ -n "$$pid" ]; then kill $$pid; fi
	-pid=$$(lsof -t -i :8001); if [ -n "$$pid" ]; then kill $$pid; fi
	@echo "Stopped Flask and FastAPI services."