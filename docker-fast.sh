#!/bin/bash
# Start Marina in Docker FAST (no build check)

echo "Pulling latest changes from Git..."
git pull origin main

echo "Updating containers..."
docker compose --env-file .env up -d

echo "Applying database migrations across all tenants..."
docker compose --env-file .env exec -T web env DJANGO_SETTINGS_MODULE=marina_project.settings python -c "from django.core.management import call_command; import django; django.setup(); from django.conf import settings; [call_command('migrate', database=db) for db in settings.DATABASES]"

echo "Reloading Gunicorn gracefully (zero downtime)..."
docker compose --env-file .env exec -T web kill -HUP 1
