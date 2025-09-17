#!/bin/bash

# Script to set up database and run tests

set -e

echo "Creating test database..."
# Using SQLite for tests so we don't need to create a PostgreSQL DB for testing

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running tests..."
pytest -v

echo "All tests completed successfully!"