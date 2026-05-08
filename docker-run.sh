#!/bin/bash
# Start Marina in Docker
docker-compose up -d --build
echo "Marina is starting on port $(grep WEB_PORT .env | cut -d '=' -f2 || echo 8004)"
