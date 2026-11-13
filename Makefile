.PHONY: help setup up down migrate load test lint format check reset-db

help:  ## Show available commands
	@grep -E "^[a-z-]+:.*##" $(MAKEFILE_LIST) | awk -F ":.*## " "{printf \"  %-10s %s\n\", \$$1, \$$2}"

setup:  ## Install/check all tools and dependencies (safe to re-run)
	./scripts/setup.sh

up:  ## Start Postgres
	docker compose up -d --wait postgres

down:  ## Stop containers (keeps data)
	docker compose down

migrate: up  ## Apply database migrations
	uv run alembic -c backend/alembic.ini upgrade head

load: migrate  ## Load postings from data/raw/postings.csv
	uv run etl/load.py

test:  ## Run pytest
	uv run pytest -q

lint:  ## Check lint and formatting
	uv run ruff check .
	uv run ruff format --check .

format:  ## Auto-fix lint and formatting
	uv run ruff check --fix .
	uv run ruff format .

check: lint test  ## Everything CI runs locally (minus the DB steps)

reset-db:  ## DELETE the database volume and start fresh
	docker compose down -v
