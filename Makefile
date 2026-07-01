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


# ── Terraform ──

TF_DIR := infra/terraform

tf-init:
	terraform -chdir=$(TF_DIR) init

tf-plan:
	terraform -chdir=$(TF_DIR) plan

tf-apply:
	terraform -chdir=$(TF_DIR) apply

tf-destroy:
	terraform -chdir=$(TF_DIR) destroy

tf-fmt:
	terraform -chdir=$(TF_DIR) fmt -recursive

tf-validate:
	terraform -chdir=$(TF_DIR) validate

tf-output:
	terraform -chdir=$(TF_DIR) output


# ── Load Testing (k6) ──

k6-smoke:
	k6 run tests/load/smoke.js

k6-health:
	k6 run tests/load/health.js

k6-chat:
	k6 run tests/load/chat.js

k6-tenants:
	k6 run tests/load/tenants.js

k6-webhooks:
	k6 run tests/load/webhooks.js

k6-all: k6-health k6-chat k6-tenants k6-webhooks


# ── Maintenance ──

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache .mypy_cache
