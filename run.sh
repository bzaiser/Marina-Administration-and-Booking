#!/bin/bash

# Marina Samos - Startup Script for macOS and Linux

echo "-----------------------------------------------"
echo "   Marina Management System - Starting up...   "
echo "-----------------------------------------------"

# 1. Check for Python 3
if ! command -v python3 &> /dev/null
then
    echo "ERROR: Python 3 could not be found. Please install Python 3."
    exit
fi

# 2. Check for Virtual Environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    echo "Installing dependencies..."
    ./venv/bin/pip install --upgrade pip
    if [ -f "requirements.txt" ]; then
        ./venv/bin/pip install -r requirements.txt
    else
        echo "WARNING: requirements.txt not found. Installing base packages..."
        ./venv/bin/pip install django django-colorfield django-htmx django-extensions whitenoise
    fi
fi

# 3. Setup Database & Static Files
echo "Checking for database migrations..."
./venv/bin/python manage.py migrate

echo "Collecting static files..."
./venv/bin/python manage.py collectstatic --noinput

# 4. Start Server
echo "Starting server on http://127.0.0.1:8003"
echo "Press Ctrl+C to stop."
./venv/bin/python manage.py runserver 8003
