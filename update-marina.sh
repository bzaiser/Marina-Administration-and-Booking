#!/bin/bash

# MARINA SAMOS - UPDATE FOR macOS / LINUX
# This script uses Git to fetch the latest changes.

echo "=========================================="
echo "   MARINA SAMOS - UPDATE (Mac/Linux)"
echo "=========================================="
echo ""

# Check for Git
if ! command -v git &> /dev/null; then
    echo "[ERROR] Git is not installed. Cannot update via Git."
    exit 1
fi

echo "[1/3] Fetching latest version from GitHub..."
git pull

echo "[2/3] Updating dependencies..."
if [ -d "venv" ]; then
    ./venv/bin/pip install -r requirements.txt
else
    echo "[WARNING] venv not found. Please run setup-marina.sh first."
    exit 1
fi

echo "[3/3] Running migrations..."
./venv/bin/python manage.py migrate
./venv/bin/python manage.py update_vendor

echo ""
echo "=========================================="
echo "   UPDATE COMPLETE!"
echo "=========================================="
echo ""
