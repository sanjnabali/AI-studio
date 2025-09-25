#!/bin/bash

# Production deployment script

echo "Deploying AI Studio to production..."

# Build and deploy using Docker Compose
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

echo "Production deployment complete!"
echo "Access the application at your configured domain"