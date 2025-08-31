#!/bin/bash
# Cleanup script for Virtual Thermostat Testbed
# This script removes all containers, images, volumes, and networks related to the project

set -e  # Exit on error

echo "====================================="
echo "Virtual Thermostat Testbed Cleanup"
echo "====================================="

# Set working directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."
echo "Working directory: $(pwd)"

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "ERROR: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Determine docker-compose command
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo "Using Docker Compose command: $COMPOSE_CMD"

# Get the project name (usually the directory name)
PROJECT_NAME=$(basename "$(pwd)" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]//g')
echo "Project name: $PROJECT_NAME"

# Stop and remove containers
echo ""
echo "Stopping and removing containers..."
$COMPOSE_CMD down -v 2>/dev/null || true

# Get all container IDs for this project
echo ""
echo "Looking for any remaining containers..."
CONTAINERS=$(docker ps -a --filter "label=com.docker.compose.project=$PROJECT_NAME" -q)
if [ -n "$CONTAINERS" ]; then
    echo "Removing remaining containers..."
    docker rm -f $CONTAINERS 2>/dev/null || true
else
    echo "No remaining containers found."
fi

# Remove images
echo ""
echo "Removing Docker images..."
# Get all image names from docker-compose.yml
IMAGES=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep -E "(${PROJECT_NAME}|backend-console|cloud-server|environment-simulator|thermostat)" | grep -v "<none>" || true)
if [ -n "$IMAGES" ]; then
    echo "Found images to remove:"
    echo "$IMAGES"
    echo "$IMAGES" | xargs -r docker rmi -f 2>/dev/null || true
else
    echo "No project images found."
fi

# Remove dangling images
echo ""
echo "Removing dangling images..."
DANGLING=$(docker images -f "dangling=true" -q)
if [ -n "$DANGLING" ]; then
    docker rmi $DANGLING 2>/dev/null || true
    echo "Dangling images removed."
else
    echo "No dangling images found."
fi

# Remove volumes
echo ""
echo "Removing Docker volumes..."
VOLUMES=$(docker volume ls --filter "label=com.docker.compose.project=$PROJECT_NAME" -q)
if [ -n "$VOLUMES" ]; then
    echo "Removing project volumes..."
    docker volume rm $VOLUMES 2>/dev/null || true
else
    echo "No project volumes found."
fi

# Remove networks
echo ""
echo "Removing Docker networks..."
NETWORKS=$(docker network ls --filter "label=com.docker.compose.project=$PROJECT_NAME" -q)
if [ -n "$NETWORKS" ]; then
    echo "Removing project networks..."
    docker network rm $NETWORKS 2>/dev/null || true
else
    echo "No project networks found."
fi

# Alternative cleanup based on service names from docker-compose.yml
echo ""
echo "Performing additional cleanup based on service names..."

# Stop any containers with our service names
docker stop $(docker ps -q --filter "name=backend-console") 2>/dev/null || true
docker stop $(docker ps -q --filter "name=cloud-server") 2>/dev/null || true
docker stop $(docker ps -q --filter "name=environment-simulator") 2>/dev/null || true
docker stop $(docker ps -q --filter "name=thermostat") 2>/dev/null || true

# Remove any containers with our service names
docker rm $(docker ps -aq --filter "name=backend-console") 2>/dev/null || true
docker rm $(docker ps -aq --filter "name=cloud-server") 2>/dev/null || true
docker rm $(docker ps -aq --filter "name=environment-simulator") 2>/dev/null || true
docker rm $(docker ps -aq --filter "name=thermostat") 2>/dev/null || true

# Clean up build cache (optional, commented out by default)
# echo ""
# echo "Cleaning Docker build cache..."
# docker builder prune -f

# Final cleanup summary
echo ""
echo "====================================="
echo "Cleanup Complete!"
echo "====================================="
echo ""
echo "The following have been removed:"
echo "- All project containers"
echo "- All project images"
echo "- All project volumes"
echo "- All project networks"
echo ""
echo "To rebuild and start fresh, run:"
echo "  ./scripts/startup.sh"
echo ""
echo "To perform a more aggressive cleanup (including build cache):"
echo "  docker system prune -a --volumes"
echo "====================================="
