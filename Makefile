# Makefile for agento

.PHONY: help install dev test clean build package binary lint format check

# Default target
help:
	@echo "agento - Makefile targets"
	@echo ""
	@echo "  make install    - Install in development mode"
	@echo "  make dev        - Same as install"
	@echo "  make test       - Run tests"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make build      - Build distribution packages"
	@echo "  make binary     - Build standalone binary"
	@echo "  make lint       - Run linter (ruff)"
	@echo "  make format     - Format code"
	@echo "  make check      - Run all checks (lint + typecheck + test)"
	@echo "  make run        - Run the agent"
	@echo "  make shell       - Open shell with venv activated"

# Development installation
install dev:
	@echo "Installing in development mode..."
	@if [ ! -d ".venv" ]; then python3 -m venv .venv; fi
	@.venv/bin/pip install --upgrade pip
	@.venv/bin/pip install -e ".[all]"
	@echo "Done! Activate with: source .venv/bin/activate"

# Run tests
test:
	@echo "Running tests..."
	@.venv/bin/python -m pytest tests/ --timeout=30 -q

# Clean
clean:
	@echo "Cleaning..."
	@rm -rf build/ dist/ *.egg-info .pytest_cache
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@echo "Clean complete"

# Build distribution packages
build package:
	@echo "Building distribution packages..."
	@mkdir -p dist
	@python3 -m build --sdist
	@python3 -m build --wheel
	@echo "Packages created:"
	@ls -lh dist/*.whl dist/*.tar.gz 2>/dev/null

# Build standalone binary
binary:
	@echo "Building standalone binary..."
	@if ! .venv/bin/pip show pyinstaller > /dev/null 2>&1; then .venv/bin/pip install pyinstaller; fi
	@mkdir -p dist
	@rm -f dist/agento 2>/dev/null || true
	@.venv/bin/pyinstaller --name=agento --onefile --console --clean src/agento/main.py
	@chmod +x dist/agento
	@echo "Binary created: dist/agento"

# Lint with ruff
lint:
	@echo "Running linter..."
	@.venv/bin/ruff check src/agento

# Format code
format:
	@echo "Formatting code..."
	@.venv/bin/ruff format src/agento tests/

# Type check
typecheck:
	@echo "Running type checker..."
	@.venv/bin/mypy src/agento

# All checks
check: lint typecheck test

# Run the agent
run:
	@echo "Starting agento..."
	@.venv/bin/agento run

# Open shell with venv
shell:
	@echo "Opening shell with venv activated..."
	@.venv/bin/python -c "print('agento v0.1.0')"
	@bash -c 'source .venv/bin/activate && echo "Venv activated. Run '\''agento run'\'' to start." && $$SHELL'
