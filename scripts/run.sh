#!/bin/bash
# Agento run script

set -e

# Load environment
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Run agento
agento "$@"
