#!/bin/bash

# Apply database migrations across all tenants
echo "Apply database migrations across all tenants"
env DJANGO_SETTINGS_MODULE=marina_project.settings python -c "from django.core.management import call_command; import django; django.setup(); from django.conf import settings; [call_command('migrate', database=db) for db in settings.DATABASES]"

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Start Gunicorn with multiple workers for better concurrency
echo "Starting Gunicorn with 3 workers"
exec gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 marina_project.wsgi:application
