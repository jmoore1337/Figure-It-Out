.PHONY: dev migrate seed test help

help:
	@echo "Figure It Out — available commands:"
	@echo "  make dev       Start DB + backend + frontend"
	@echo "  make migrate   Run Alembic migrations"
	@echo "  make seed      Seed demo data"
	@echo "  make test      Run backend tests"

dev:
	@cp -n .env.example .env 2>/dev/null || true
	docker compose up

migrate:
	@cp -n .env.example .env 2>/dev/null || true
	cd backend && alembic upgrade head

seed:
	@cp -n .env.example .env 2>/dev/null || true
	cd backend && python seed.py

test:
	cd backend && python -m pytest tests/ -v
