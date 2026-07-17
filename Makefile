.PHONY: setup sample load build build-real test lint dashboard validate clean

setup:
	uv sync --all-groups

sample:
	uv run mobility-intel generate-sample

load:
	uv run mobility-intel load-raw --mode sample

build:
	uv run python scripts/run_pipeline.py --mode sample

build-real:
	uv run python scripts/run_pipeline.py --mode local

test:
	uv run pytest

lint:
	uv run ruff check src tests scripts
	uv run ruff format --check src tests scripts

dashboard:
	uv run mobility-intel export-dashboard

validate: build lint test
	node --check dashboard/app.js

clean:
	uv run python scripts/clean.py
