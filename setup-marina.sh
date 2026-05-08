#!/bin/bash

# MARINA SAMOS - SETUP FOR macOS / LINUX
# This script mirrors the setup-marina.bat for Unix-based systems.

echo "=========================================="
echo "   MARINA SAMOS - SETUP (Mac/Linux)"
echo "   Automated installation & configuration"
echo "=========================================="
echo ""

# 1. Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed. Please install it first."
    exit 1
fi

# 2. Virtual Environment Setup
if [ ! -d "venv" ]; then
    echo "[1/4] Creating virtual environment..."
    python3 -m venv venv
else
    echo "[OK] Virtual environment already exists."
fi

# 3. Configuration (.env)
echo ""
echo "[2/4] Database Configuration..."
echo "Where should the database be stored?"
echo "  [1] Locally in the program folder (Standard)"
echo "  [2] Custom path (e.g., OneDrive, iCloud, Shared Drive)"
echo ""
read -p "Choice (1 or 2): " DB_CHOICE

DB_PATH_LINE=""
if [ "$DB_CHOICE" == "2" ]; then
    echo ""
    echo "Tip: You can drag and drop a folder into this terminal window."
    read -p "Full path to the database file (e.g. /Users/name/OneDrive/marina/db.sqlite3): " CUSTOM_PATH
    
    # Expand tilde if present
    CUSTOM_PATH="${CUSTOM_PATH/#\~/$HOME}"
    
    DB_PATH_LINE="DB_PATH=$CUSTOM_PATH"
    
    # Create directory if it doesn't exist
    DB_DIR=$(dirname "$CUSTOM_PATH")
    mkdir -p "$DB_DIR"
    echo "[OK] Database will be stored at: $CUSTOM_PATH"
else
    echo "[OK] Database will be stored locally."
fi

# Create .env file
echo "# Marina Configuration" > .env
echo "DB_ENGINE=django.db.backends.sqlite3" >> .env
if [ ! -z "$DB_PATH_LINE" ]; then
    echo "$DB_PATH_LINE" >> .env
fi
echo "DEBUG=True" >> .env
echo "ALLOWED_HOSTS=127.0.0.1,localhost" >> .env
echo "[OK] .env configuration file created."

# 4. Dependencies & Database
echo ""
echo "[3/4] Installing dependencies..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

echo "[4/4] Setting up database..."
./venv/bin/python manage.py migrate
./venv/bin/python manage.py update_vendor

echo ""
echo "=========================================="
echo "   SETUP COMPLETE!"
echo ""
echo "   To start the app:  ./run.sh"
echo "   To update:         ./update-marina.sh"
echo "=========================================="
echo ""

read -p "Start the app now? (y/n): " START_NOW
if [ "$START_NOW" == "y" ]; then
    open "http://127.0.0.1:8003"
    ./venv/bin/python manage.py runserver 8003
fi
