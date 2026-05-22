.PHONY: help db-up db-down db-wait db-migrate db-seed db-reset db-reseed db-truncate db-truncate-all minio-up minio-down minio-logs infra-up infra-down upload-default-image upload-card-images upload-card-images-offline install run-api run-frontend run-all

# docker compose (v2 plugin) или docker-compose (v1)
ifeq ($(shell docker compose version >/dev/null 2>&1 && echo yes),yes)
  DOCKER_COMPOSE := docker compose
else
  DOCKER_COMPOSE := docker-compose
endif

# После usermod -aG docker группа активна не во всех сессиях; sg docker обходит это.
DOCKER_RUN = sg docker -c "$(DOCKER_COMPOSE) $(1)"

help:
	@echo "Targets:"
	@echo "  make install       - pip install dependencies"
	@echo "  make db-up         - start PostgreSQL (Docker)"
	@echo "  make db-down       - stop PostgreSQL"
	@echo "  make db-check      - check local PostgreSQL (no Docker)"
	@echo "  make db-migrate    - apply Alembic migrations"
	@echo "  make db-seed       - insert demo users"
	@echo "  make db-reset      - downgrade + migrate + seed"
	@echo "  make db-reseed     - truncate all tables + seed (faster than reset)"
	@echo "  make db-truncate   - truncate table: make db-truncate TABLE=cards [CASCADE=1]"
	@echo "  make db-truncate-all - truncate all tables in current DB"
	@echo "  make minio-up      - start MinIO on :9000 and console on :9001"
	@echo "  make minio-down    - stop MinIO"
	@echo "  make minio-logs    - tail MinIO logs"
	@echo "  make infra-up      - start PostgreSQL + MinIO"
	@echo "  make infra-down    - stop all Docker infrastructure"
	@echo "  make upload-card-images DIR=assets/cards - upload images to cards by file name"
	@echo "  make run-api       - FastAPI on :8000"
	@echo "  make run-frontend  - Vite dev server on :5173"
	@echo "  make run-all       - run both API and frontend in parallel"

install:
	pip install -r requirements.txt

db-up:
	$(call DOCKER_RUN,up -d db)

minio-up:
	$(call DOCKER_RUN,up -d minio)

infra-up:
	$(call DOCKER_RUN,up -d db minio)

db-down:
	$(call DOCKER_RUN,down)

minio-down:
	$(call DOCKER_RUN,stop minio)

infra-down:
	$(call DOCKER_RUN,down)

minio-logs:
	$(call DOCKER_RUN,logs -f minio)

upload-default-image:
	@test -f assets/cards/default-image.png || (echo "File not found: assets/cards/default-image.png" && exit 1)
	PYTHONPATH=src python3 scripts/upload_default_image.py

upload-card-images:
	@test -n "$(DIR)" || (echo "Usage: make upload-card-images DIR=<folder> [API_BASE_URL=http://localhost:8000/api/v1]" && exit 1)
	API_BASE_URL=$(or $(API_BASE_URL),http://localhost:8000/api/v1) \
		bash scripts/upload_card_images.sh "$(DIR)"

db-wait:
	@echo "Waiting for PostgreSQL..."
	@for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do \
		sg docker -c "$(DOCKER_COMPOSE) exec -T db pg_isready -U cmb -d cool_magic_battles" >/dev/null 2>&1 && exit 0; \
		sleep 1; \
	done; \
	echo "PostgreSQL did not become ready in time"; exit 1

db-check:
	@psql -d cool_magic_battles -c "SELECT current_database(), current_user;" || \
		(echo "Local DB not ready. Create with: psql -d postgres -c \"CREATE DATABASE cool_magic_battles OWNER $$USER;\"" && exit 1)

db-migrate:
	PYTHONPATH=src python3 scripts/db.py upgrade

db-seed:
	PYTHONPATH=src python3 scripts/db.py seed

db-reset:
	PYTHONPATH=src python3 scripts/db.py downgrade
	PYTHONPATH=src python3 scripts/db.py upgrade
	$(MAKE) db-seed

db-reseed:
	PYTHONPATH=src .venv/bin/python scripts/db.py truncate-all
	PYTHONPATH=src .venv/bin/python scripts/db.py seed

db-fix-card-images:
	PYTHONPATH=src python3 scripts/db.py fix-card-images


	@test -n "$(TABLE)" || (echo "Usage: make db-truncate TABLE=<table> [CASCADE=1]" && exit 1)
	PYTHONPATH=src python3 scripts/db.py truncate "$(TABLE)" $(if $(CASCADE),--cascade)

db-truncate-all:
	PYTHONPATH=src python3 scripts/db.py truncate-all

# Если таблицы уже созданы вручную (create_all), но нет alembic_version:
db-stamp:
	PYTHONPATH=src python3 scripts/db.py stamp

run-api:
	PYTHONPATH=src uvicorn api.app:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	cd frontend && npm run dev

run-all:
	@echo "Starting API and Frontend in parallel..."
	@echo "API will be on http://localhost:8000"
	@echo "Frontend will be on http://localhost:5173"
	@echo "Press Ctrl+C to stop both"
	@trap 'kill 0' EXIT; \
		PYTHONPATH=src uvicorn api.app:app --reload --host 0.0.0.0 --port 8000 & \
		cd frontend && npm run dev
