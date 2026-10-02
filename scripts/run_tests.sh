#!/bin/bash
set -e

echo "Running BB-ARBITRAGE tests..."

cd backend

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running unit tests..."
pytest tests/ -v --tb=short

echo "Tests completed successfully!"
