#!/bin/bash
# Update Marina in Docker
git pull
mkdir -p data
docker-compose up -d --build
echo "Marina updated and restarting. Entrypoint will handle migrations."
