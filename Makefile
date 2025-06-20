.PHONY: install check format ci

install:
	uv pip install -e .

test:
	uv run pytest

check:
	uvx ruff check

format:
	uvx ruff format

check-format:
	uvx ruff format --check

ci: check check-format test