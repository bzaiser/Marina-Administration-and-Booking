#!/bin/bash

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Start Gunicorn
echo "Starting Gunicorn"
exec gunicorn --bind 0.0.0.0:8000 marina_project.wsgi:application
