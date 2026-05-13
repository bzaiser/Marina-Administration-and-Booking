#!/bin/bash

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Start Gunicorn with multiple workers for better concurrency
echo "Starting Gunicorn with 3 workers"
exec gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 marina_project.wsgi:application
