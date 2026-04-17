# Agento Makefile - Cross-platform build automation
#
# Usage:
#   make install       Install dependencies
#   make dev           Set up dev environment
#   make test          Run tests
#   make lint          Run linters
#   make format        Format code
#   make build         Build packages
#   make clean         Clean artifacts
#   make all           Full CI pipeline (lint, test, build)

.PHONY: help install dev test lint format build clean all check

# Default target
help:
	@echo "Agento Build Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  make install    - Install all dependencies"
	@echo "  make dev        - Set up development environment"
	@echo "  make test       - Run test suite"
	@echo "  make lint       - Run linters (ruff, mypy)"
	@echo "  make format     - Format code (ruff, black)"
	@echo "  make build      - Build distribution packages"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make check      - Run all checks (lint + test)"
	@echo "  make all        - Full CI pipeline"

# Detect OS (for platform-specific commands)
UNAME_S := $(shell uname -s)
IS_DARWIN := $(filter Darwin,$(UNAME_S))
IS_LINUX := $(filter Linux,$(UNAME_S))
IS_WINDOWS := $(shell uname -o 2>/dev/null || echo "unknown")

# Python commands
PYTHON := python3
PIP := pip3
PYTEST := pytest
LINTER := ruff
FORMATTER := black

# Install dependencies
install:
	@echo "Installing dependencies..."
	@$(PIP) install -e ".[all]"

# Development setup
dev: install lint test
	@echo "Development environment ready!"
	@echo "Run 'source .venv/bin/activate' to activate virtualenv"
	@echo "Then run 'agento' to start the agent"

# Run tests
test:
	@echo "Running tests..."
	@$(PYTEST) tests/ -q --cov=src/agento --cov-report=term-missing --cov-fail-under=95

# Run linters
lint:
	@echo "Running linters..."
	@$(LINTER) check src/agento tests/
	@$(LINTER) check src/agento tests/ --output-format=text
	@mypy src/agento --ignore-missing-imports || true

# Format code
format:
	@echo "Formatting code..."
	@$(LINTER) format src/agento tests/
	@$(FORMATTER) src/agento tests/

# Build distribution packages
build:
	@echo "Building packages..."
	@mkdir -p dist
	@$(PYTHON) -m build --wheel
	@$(PYTHON) -m build --sdist
	@echo "Packages created in dist/"

# Clean artifacts
clean:
	@echo "Cleaning..."
	@rm -rf build dist *.egg-info .pytest_cache .venv
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name ".coverage" -delete
	@echo "Clean complete"

# Run all checks (lint + test)
check: lint test
	@echo "All checks passed!"

# Full CI pipeline
all: lint test build
	@echo ""
	@echo "========================================="
	@echo "  Full CI pipeline complete!"
	@echo "========================================="

# Quick test (no coverage)
quick-test:
	@$(PYTEST) tests/ -q --no-cov

# Install with specific extras
install-dev:
	@$(PIP) install -e ".[dev]"

install-all:
	@$(PIP) install -e ".[all]"

# Run with specific Python version (for testing)
py313:
	@python3.13 -m venv .venv
	@.venv/bin/pip install -e ".[dev]"
	@.venv/bin/pip install pytest pytest-asyncio pytest-cov pytest-mock

# Security check
security:
	@$(PIP) audit || true

# Type check only
types:
	@mypy src/agento --strict --ignore-missing-imports || true

# Run with coverage report
coverage:
	@$(PYTEST) tests/ --cov=src/agento --cov-report=html --cov-report=term
	@echo "Coverage report: htmlcov/index.html"

# Open coverage report
coverage-open: coverage
	@if [ "$(UNAME_S)" = "Darwin" ]; then open htmlcov/index.html; fi
	@if [ "$(UNAME_S)" = "Linux" ]; then xdg-open htmlcov/index.html 2>/dev/null || true; fi
