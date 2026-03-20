COMPOSE = docker compose -f docker/docker-compose.yml --env-file .env
POETRY = poetry run

.PHONY: help build up down restart logs ps install run-local test test-cov lint format pre-commit

help:
	@echo "Available targets:"
	@echo "  make build    - Build images"
	@echo "  make up       - Start services in background"
	@echo "  make down     - Stop and remove services"
	@echo "  make restart  - Restart services"
	@echo "  make logs     - Follow service logs"
	@echo "  make ps       - Show service status"
	@echo "  make install  - Install project dependencies (no package install)"
	@echo "  make run-local  - Run bot locally (without Docker)"
	@echo "  make test     - Run tests"
	@echo "  make test-cov - Run tests with coverage"
	@echo "  make lint     - Run lint checks (ruff + pylint)"
	@echo "  make format   - Auto-format code (isort + ruff format)"
	@echo "  make pre-commit   - Pre-commit checks (isort + ruff check + pylint)"

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

restart:
	$(COMPOSE) down
	$(COMPOSE) up -d --build

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

install:
	poetry install --no-root

run-local:
	$(POETRY) python src/main.py

test:
	$(POETRY) pytest

test-cov:
	$(POETRY) pytest --cov=src --cov-report=term-missing --cov-report=xml

lint:
	$(POETRY) ruff check .
	$(POETRY) pylint src

format:
	$(POETRY) isort src tests
	$(POETRY) ruff format .

pre-commit:
	$(POETRY) pre-commit run --all-files
