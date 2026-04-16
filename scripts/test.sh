#!/bin/bash
# Agento test script

set -e

echo "Running tests with coverage..."

pytest tests/ \
    -v \
    --cov=src/agento \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-fail-under=95 \
    "$@"

echo ""
echo "Coverage report generated in htmlcov/"
