# servers/ai-gateway 四道质量门（uv + Python 3.12）。
PORT ?= 8001

.PHONY: install dev build test lint typecheck clean

install:
	uv sync

dev:
	uv run uvicorn app.main:app --reload --port $(PORT)

build:
	uv run python -m compileall app

test:
	uv run pytest -q

lint:
	uv run ruff check .

typecheck:
	uv run mypy app

clean:
	rm -rf .venv .pytest_cache .ruff_cache .mypy_cache __pycache__ app/__pycache__ tests/__pycache__
