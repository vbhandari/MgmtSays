# =============================================================================
# MgmtSays Makefile
# =============================================================================
# Common commands for development, testing, and deployment
# =============================================================================

.PHONY: help install dev build test lint clean docker-up docker-down db-migrate

# Default target
help:
	@echo "MgmtSays Development Commands"
	@echo "=============================="
	@echo ""
	@echo "Setup:"
	@echo "  make install        Install all dependencies"
	@echo "  make setup          Full setup (install + db + env)"
	@echo ""
	@echo "Development:"
	@echo "  make dev            Start all services for development"
	@echo "  make dev-backend    Start backend only"
	@echo "  make dev-frontend   Start frontend only"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up      Start all Docker services"
	@echo "  make docker-down    Stop all Docker services"
	@echo "  make docker-build   Build Docker images"
	@echo "  make docker-logs    View Docker logs"
	@echo ""
	@echo "Database:"
	@echo "  make db-migrate     Run database migrations"
	@echo "  make db-seed        Seed database with sample data"
	@echo "  make db-reset       Reset database"
	@echo ""
	@echo "Testing:"
	@echo "  make test           Run all tests"
	@echo "  make test-unit      Run unit tests only"
	@echo "  make test-int       Run integration tests only"
	@echo "  make test-e2e       Run E2E tests only"
	@echo "  make test-cov       Run tests with coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint           Run linters"
	@echo "  make format         Format code"
	@echo "  make typecheck      Run type checking"
	@echo ""
	@echo "Build:"
	@echo "  make build          Build for production"
	@echo "  make clean          Clean build artifacts"

# =============================================================================
# Setup
# =============================================================================

install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -e ".[dev]"
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Done!"

setup: install
	@echo "Copying environment file..."
	cp -n .env.example .env || true
	@echo "Starting database..."
	docker-compose up -d db chromadb
	@echo "Waiting for database..."
	sleep 5
	@echo "Running migrations..."
	cd backend && alembic upgrade head
	@echo "Setup complete!"

# =============================================================================
# Development
# =============================================================================

dev:
	docker-compose up

dev-backend:
	cd backend && uvicorn src.main:app --reload --host 0.0.0.0 --port 8080

dev-frontend:
	cd frontend && npm run dev

# =============================================================================
# Docker
# =============================================================================

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-build:
	docker-compose build

docker-logs:
	docker-compose logs -f

docker-clean:
	docker-compose down -v --rmi local

# =============================================================================
# Database
# =============================================================================

db-migrate:
	cd backend && alembic upgrade head

db-revision:
	cd backend && alembic revision --autogenerate -m "$(msg)"

db-seed:
	cd backend && python -m scripts.seed_db

db-reset:
	cd backend && alembic downgrade base && alembic upgrade head

# =============================================================================
# Testing
# =============================================================================

test: test-backend test-frontend

test-backend:
	cd backend && pytest

test-frontend:
	cd frontend && npm test

test-unit:
	cd backend && pytest tests/unit -v
	cd frontend && npm test -- --run

test-int:
	cd backend && pytest tests/integration -v

test-e2e:
	cd frontend && npm run test:e2e

test-regression:
	cd backend && pytest tests/regression -v

test-cov:
	cd backend && pytest --cov=src --cov-report=html
	cd frontend && npm run test:coverage

# =============================================================================
# Code Quality
# =============================================================================

lint:
	cd backend && ruff check src tests
	cd frontend && npm run lint

lint-fix:
	cd backend && ruff check src tests --fix
	cd frontend && npm run lint:fix

format:
	cd backend && ruff format src tests
	cd frontend && npm run format

typecheck:
	cd backend && mypy src
	cd frontend && npm run typecheck

quality: lint typecheck test

# =============================================================================
# Build
# =============================================================================

build:
	cd frontend && npm run build
	docker-compose -f docker-compose.prod.yml build

clean:
	rm -rf backend/.pytest_cache
	rm -rf backend/.ruff_cache
	rm -rf backend/.mypy_cache
	rm -rf backend/htmlcov
	rm -rf backend/.coverage
	rm -rf frontend/dist
	rm -rf frontend/coverage
	rm -rf frontend/node_modules/.vite
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
