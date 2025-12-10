#!/bin/bash

# This script runs all automated tests for the AGIcore system.

# Exit immediately if a command exits with a non-zero status.
set -e

echo "--- Starting AGIcore Test Suite ---"

# Install dependencies for testing
echo "Installing testing dependencies..."
pip install pytest pytest-asyncio httpx requests

# Run Unit Tests
echo "--- Running Unit Tests ---"
pytest tests/unit/

# Run Integration Tests
echo "--- Running Integration Tests ---"
pytest tests/integration/

echo "--- All tests passed successfully! ---"

