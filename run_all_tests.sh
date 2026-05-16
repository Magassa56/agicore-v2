#!/bin/bash

# This script runs all automated tests for the AGIcore system.

# Exit immediately if a command exits with a non-zero status.
set -e

echo "--- Starting AGIcore Test Suite ---"

# Install dependencies exactly like the CI job.
echo "Installing development dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pip install -e .

# Run Unit Tests
echo "--- Running Unit Tests ---"
python -m pytest tests/unit/

# Run Integration Tests
echo "--- Running Integration Tests ---"
python -m pytest tests/integration/

echo "--- All tests passed successfully! ---"

