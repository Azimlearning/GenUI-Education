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

# Live evals cost real tokens; they arrive with the Phase 1 eval harness.
evals:
	@echo "evals: not implemented until Phase 1 (see evals/run.py)" && exit 1

evals-smoke:
	@echo "evals-smoke: not implemented until Phase 1 (see evals/run.py)" && exit 1

fixtures-refresh:
	@echo "fixtures-refresh: not implemented until Phase 1" && exit 1
