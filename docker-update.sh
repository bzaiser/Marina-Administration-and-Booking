#!/bin/bash
# Update Marina in Docker
git pull
docker-compose up -d --build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
echo "Marina updated and restarted."
