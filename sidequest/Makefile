# Axiom developer entrypoints (docs/TECHNICAL.md section 6).
# `make dev` must work from a clean clone with only Docker and make installed.

.PHONY: dev test lint migrate evals evals-smoke fixtures-refresh

dev:
	docker compose up --build

test:
	cd backend && python -m pytest -q
	cd frontend && npm run test

lint:
	cd backend && python -m ruff check .
	cd frontend && npm run lint && npm run typecheck

migrate:
	docker compose exec backend alembic upgrade head

# Live evals cost real tokens (~$5-15 full, ~$1-3 smoke). Backend must be running.
evals:
	cd evals && python run.py --render

evals-smoke:
	cd evals && python run.py --smoke --render

fixtures-refresh:
	@echo "fixtures-refresh: not implemented until Phase 1" && exit 1
