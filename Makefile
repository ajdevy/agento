# Agento Makefile - Cross-platform build automation
#
# Usage:
#   make dev           Set up dev environment (creates venv)
#   make test          Run tests
#   make lint         Run linters
#   make format      Format code
#   make build       Build packages
#   make clean      Clean artifacts

.PHONY: help dev test lint format build clean check

help:
	@echo "Agento Build Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  make dev        - Set up dev environment (venv + deps)"
	@echo "  make test       - Run test suite"
	@echo "  make lint      - Run linters"
	@echo "  make format   - Format code"
	@echo "  make build     - Build packages"
	@echo "  make clean    - Clean artifacts"

# Create venv and install
dev:
	@echo "Creating virtual environment..."
	@python3 -m venv .venv
	@.venv/bin/pip install --upgrade pip
	@.venv/bin/pip install -e ".[dev]"
	@echo ""
	@echo "✓ Dev environment ready!"
	@echo "Run '.venv/bin/activate' to activate, then 'agento' to start"

# Run tests
test:
	@.venv/bin/pytest tests/ -q --cov=src/agento --cov-fail-under=95

# Run linters
lint:
	@.venv/bin/ruff check src/agento tests/

# Format code
format:
	@.venv/bin/ruff format src/agento tests/

# Build packages
build:
	@mkdir -p dist
	@.venv/bin/python -m build --wheel --sdist

# Clean
clean:
	@rm -rf build dist *.egg-info .pytest_cache .venv
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Quick test (no coverage)
quick-test:
	@.venv/bin/pytest tests/ -q --no-cov