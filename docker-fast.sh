#!/bin/bash
# Start Marina in Docker FAST (no build check)
mkdir -p data
docker-compose up -d
echo "Marina is starting FAST on port $(grep WEB_PORT .env | cut -d '=' -f2 || echo 8004)"
