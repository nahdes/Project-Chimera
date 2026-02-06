# Project Chimera - Makefile
# Standardized commands for development

.PHONY: help setup install test lint format clean run-orchestrator run-worker docker-up docker-down

# Default target
help:
	@echo "Project Chimera - Available Commands:"
	@echo ""
	@echo "  make setup          - Initial project setup (create .env, install deps)"
	@echo "  make install        - Install all dependencies"
	@echo "  make install-dev    - Install with dev dependencies"
	@echo "  make test           - Run all tests"
	@echo "  make test-unit      - Run unit tests only"
	@echo "  make test-integration - Run integration tests"
	@echo "  make test-cov       - Run tests with coverage report"
	@echo "  make lint           - Run linters (ruff, mypy)"
	@echo "  make format         - Format code (black, ruff)"
	@echo "  make clean          - Remove build artifacts"
	@echo "  make run-orchestrator - Start orchestrator service"
	@echo "  make run-worker     - Start worker service"
	@echo "  make docker-up      - Start all services with Docker Compose"
	@echo "  make docker-down    - Stop all Docker services"
	@echo "  make spec-check     - Verify implementation matches specs"
	@echo ""

# Setup
setup:
	@echo "Setting up Project Chimera..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env file"; fi
	@uv sync --all-extras
	@echo "Setup complete! Edit .env with your API keys."

# Installation
install:
	uv sync

install-dev:
	uv sync --all-extras

# Testing
test:
	uv run pytest

test-unit:
	uv run pytest tests/unit -v

test-integration:
	uv run pytest tests/integration -v -m integration

test-e2e:
	uv run pytest tests/e2e -v -m e2e

test-cov:
	uv run pytest --cov --cov-report=html --cov-report=term

test-watch:
	uv run pytest-watch

# Code Quality
lint:
	@echo "Running linters..."
	uv run ruff check src/ tests/
	uv run mypy src/

format:
	@echo "Formatting code..."
	uv run black src/ tests/
	uv run ruff check --fix src/ tests/

format-check:
	uv run black --check src/ tests/
	uv run ruff check src/ tests/

# Cleaning
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache .coverage htmlcov/
	rm -rf .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Running Services
run-orchestrator:
	uv run chimera-orchestrator

run-planner:
	uv run chimera-planner

run-worker:
	uv run chimera-worker

run-judge:
	uv run chimera-judge

# Docker
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-rebuild:
	docker-compose up -d --build

# Database
db-migrate:
	@echo "Running database migrations..."
	uv run alembic upgrade head

db-rollback:
	@echo "Rolling back database..."
	uv run alembic downgrade -1

db-reset:
	@echo "Resetting database..."
	docker-compose down -v
	docker-compose up -d postgres
	sleep 2
	uv run alembic upgrade head

# Spec Checking (future implementation)
spec-check:
	@echo "Checking implementation against specs..."
	@echo "TODO: Implement spec validation script"

# Pre-commit
install-hooks:
	uv run pre-commit install

run-hooks:
	uv run pre-commit run --all-files

# Documentation
docs-serve:
	uv run mkdocs serve

docs-build:
	uv run mkdocs build

# Development helpers
shell:
	uv run ipython

notebook:
	uv run jupyter notebook

# CI/CD helpers
ci-test:
	uv run pytest --cov --cov-report=xml --cov-report=term

ci-lint:
	uv run ruff check src/ tests/
	uv run mypy src/
	uv run black --check src/ tests/
