#!/bin/bash
set -e

# Script to run tests with coverage reporting
echo "Starting tests..."

# Set up SQLite for testing (faster and no database setup required)
export TESTING=true
export USE_SQLITE=true

# For CI environments, set environment variables from .env.test if it exists
if [ "$CI" = "true" ] && [ -f ".env.test" ]; then
    echo "Using CI environment with .env.test"
    export $(grep -v '^#' .env.test | xargs)
fi

# Run the tests with coverage
echo "Running pytest with coverage..."
python -m pytest tests/ -v --cov=app --cov-report=term-missing

# Generate XML report for CI if needed
if [ "$CI" = "true" ]; then
    python -m pytest tests/ -v --cov=app --cov-report=xml
fi

TEST_EXIT_CODE=$?

# Check exit code
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "--------------------------------------"
    echo "✅ All tests passed successfully!"
    exit 0
else
    echo "--------------------------------------"
    echo "❌ Tests failed."
    exit 1
fi