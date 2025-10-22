#!/bin/bash
# Build script for Unified Theming

set -e

echo "Building Unified Theming..."

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

# Install build dependencies
echo "Installing build dependencies..."
pip install --upgrade build twine

# Run tests
echo "Running tests..."
python -m pytest tests/ -v

# Format code
echo "Formatting code..."
black unified_theming tests
isort unified_theming tests

# Type check
echo "Type checking..."
mypy unified_theming

# Lint
echo "Linting..."
flake8 unified_theming tests

# Build package
echo "Building package..."
python -m build

# Check package
echo "Checking package..."
twine check dist/*

echo "Build complete! Packages are in dist/"
echo "To upload to PyPI: twine upload dist/*"