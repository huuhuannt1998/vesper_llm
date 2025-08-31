#!/bin/bash
# Simple shutdown script for Virtual Thermostat Testbed
# This just stops services without removing anything

echo "====================================="
echo "Shutting Down Virtual Thermostat Testbed"
echo "====================================="

# Set working directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."

# Determine docker-compose command
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo "Stopping services..."
$COMPOSE_CMD down

echo ""
echo "====================================="
echo "Services Stopped!"
echo "====================================="
echo ""
echo "To restart services: ./scripts/startup.sh"
echo "To completely clean up: ./scripts/cleanup.sh"
echo "====================================="
