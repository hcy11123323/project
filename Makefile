.PHONY: install dev test lint format run clean docs docs-build docs-deploy

# Install production dependencies
install:
	pip install -e .

# Install dev dependencies (includes test + lint tools)
dev:
	pip install -e ".[dev]"
	playwright install chromium

# Run tests
test:
	pytest

# Lint check (no modifications)
lint:
	ruff check .
	ruff format --check .

# Auto-fix lint issues
format:
	ruff check --fix .
	ruff format .

# Start MCP server
run:
	agentic-playwright-mcp

# Clean caches and temp files
clean:
	rm -rf __pycache__ src/__pycache__ src/*/__pycache__
	rm -rf .pytest_cache .ruff_cache
	rm -rf logs/*.png
	rm -rf build dist *.egg-info

# Start local docs server
docs:
	mkdocs serve

# Build static docs site
docs-build:
	mkdocs build

# Deploy docs to GitHub Pages
docs-deploy:
	mkdocs gh-deploy
