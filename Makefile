.PHONY: dev build up down logs test lint typecheck clean

# ── Development ──

dev:
	uv run uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8080

test:
	uv run python -m pytest tests/ -v

lint:
	uv run ruff check .

typecheck:
	uv run mypy .


# ── Docker ──

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

ps:
	docker compose ps


# ── Maintenance ──

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache .mypy_cache
