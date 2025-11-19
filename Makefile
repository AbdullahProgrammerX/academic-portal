.PHONY: help setup install migrate test lint format clean docker-up docker-down

help:
	@echo "Editorial System - Development Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup          - Complete project setup (venv + dependencies + migrations)"
	@echo "  make install        - Install all dependencies (backend + frontend)"
	@echo ""
	@echo "Database:"
	@echo "  make migrate        - Run Django migrations"
	@echo "  make makemigrations - Create new migrations"
	@echo "  make resetdb        - Reset database (WARNING: deletes all data)"
	@echo ""
	@echo "Development:"
	@echo "  make run-backend    - Run Django development server"
	@echo "  make run-frontend   - Run Vue.js development server"
	@echo "  make run-celery     - Run Celery worker"
	@echo "  make run-all        - Run all services in parallel"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test           - Run all tests"
	@echo "  make test-backend   - Run backend tests"
	@echo "  make test-frontend  - Run frontend tests"
	@echo "  make lint           - Run linters"
	@echo "  make format         - Format code"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up      - Start all Docker containers"
	@echo "  make docker-down    - Stop all Docker containers"
	@echo "  make docker-build   - Build Docker images"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          - Clean temporary files"

# Setup
setup: install migrate
	@echo "✅ Project setup complete!"

install:
	@echo "📦 Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ Dependencies installed!"

# Database
migrate:
	cd backend && python manage.py migrate

makemigrations:
	cd backend && python manage.py makemigrations

resetdb:
	cd backend && python manage.py flush --no-input
	cd backend && python manage.py migrate

# Development
run-backend:
	cd backend && python manage.py runserver 8000

run-frontend:
	cd frontend && npm run dev

run-celery:
	cd backend && celery -A config worker --loglevel=info

# Testing
test: test-backend test-frontend

test-backend:
	cd backend && pytest

test-frontend:
	cd frontend && npm run test

# Code Quality
lint:
	cd backend && flake8 .
	cd frontend && npm run lint

format:
	cd backend && black .
	cd backend && isort .
	cd frontend && npm run format

# Docker
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-build:
	docker-compose build

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	rm -rf backend/staticfiles
	rm -rf frontend/dist
