.PHONY: help install run test docker-build docker-run docker-stop clean

help:
	@echo "Harness Pipeline Agent - Available Commands"
	@echo "==========================================="
	@echo "Local Development:"
	@echo "  make install      - Install dependencies in virtual environment"
	@echo "  make run          - Run the application locally"
	@echo "  make test         - Run the test client"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run with Docker Compose"
	@echo "  make docker-stop  - Stop Docker containers"
	@echo "  make docker-logs  - View Docker logs"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean        - Clean up generated files"
	@echo "  make setup-env    - Create .env from example"
	@echo "==========================================="

setup-env:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✓ Created .env file from .env.example"; \
		echo "⚠ Please edit .env with your credentials"; \
	else \
		echo "⚠ .env file already exists"; \
	fi

install: setup-env
	@echo "Creating virtual environment..."
	python3 -m venv venv
	@echo "Installing dependencies..."
	./venv/bin/pip install -r requirements.txt
	@echo "✓ Installation complete"
	@echo ""
	@echo "To activate the virtual environment, run:"
	@echo "  source venv/bin/activate"

run:
	@if [ ! -d venv ]; then \
		echo "⚠ Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi
	@if [ ! -f .env ]; then \
		echo "⚠ .env file not found. Run 'make setup-env' first."; \
		exit 1; \
	fi
	@echo "Starting Harness Pipeline Agent..."
	./venv/bin/python main.py

test:
	@if [ ! -f .env ]; then \
		echo "⚠ .env file not found. Cannot run tests."; \
		exit 1; \
	fi
	@echo "Running test client..."
	@echo "Make sure the API is running first (make run or make docker-run)"
	./venv/bin/python test_client.py

docker-build:
	@if [ ! -f .env ]; then \
		echo "⚠ .env file not found. Run 'make setup-env' first."; \
		exit 1; \
	fi
	@echo "Building Docker image..."
	./build-docker.sh

docker-run:
	@if [ ! -f .env ]; then \
		echo "⚠ .env file not found. Run 'make setup-env' first."; \
		exit 1; \
	fi
	@echo "Starting containers with Docker Compose..."
	docker-compose up -d
	@echo ""
	@echo "✓ Containers started"
	@echo "API available at: http://localhost:8000"
	@echo "Docs available at: http://localhost:8000/docs"
	@echo ""
	@echo "To view logs: make docker-logs"

docker-stop:
	@echo "Stopping containers..."
	docker-compose down
	@echo "✓ Containers stopped"

docker-logs:
	docker-compose logs -f

clean:
	@echo "Cleaning up..."
	rm -rf __pycache__
	rm -rf venv
	rm -rf *.egg-info
	rm -rf build
	rm -rf dist
	rm -rf .pytest_cache
	rm -f *.pyc
	rm -f *.log
	@echo "✓ Cleanup complete"
