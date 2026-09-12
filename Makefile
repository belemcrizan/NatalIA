.PHONY: install run test lint e2e benchmark up down observe
install:
	python -m pip install -r requirements-dev.lock
	python -m pip install --no-deps -e .
run:
	python -m uvicorn natalia.api:create_app --factory --host 127.0.0.1 --port 8000 --workers 1
test:
	python -m pytest -q
lint:
	python -m ruff check .
e2e:
	python scripts/e2e.py
benchmark:
	python scripts/benchmark.py
up:
	docker compose up --build -d
down:
	docker compose down
observe:
	docker compose --profile observability up --build -d
