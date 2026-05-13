#!/bin/bash
# Start Marina in Docker FAST (no build check)

echo "Marina is starting FAST on port $(grep WEB_PORT .env | cut -d '=' -f2 || echo 8004)"
echo "Updating containers..."
docker compose --env-file .env up -d
docker compose --env-file .env restart web
