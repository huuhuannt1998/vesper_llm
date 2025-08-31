#!/bin/bash
# Startup script for Virtual Thermostat Testbed

set -e  # Exit on error

echo "====================================="
echo "Virtual Thermostat Testbed Startup"
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

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "ERROR: docker-compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

# Determine docker-compose command
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo "Using Docker Compose command: $COMPOSE_CMD"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env <<EOF
# SmartThings Configuration
SMARTTHINGS_CLIENT_ID=your_client_id_here
SMARTTHINGS_CLIENT_SECRET=your_client_secret_here

# Ngrok Configuration
NGROK_AUTH_TOKEN=2yHxM6qbmy8ujxrCDpXXKlXztzH_9eYjhRNFXtdQ64PsgSoM

# Security
JWT_SECRET=your_jwt_secret_change_in_production
EOF
    echo "NOTE: Please update .env with your SmartThings credentials"
fi

# Clean up any existing containers
echo "Cleaning up existing containers..."
$COMPOSE_CMD down 2>/dev/null || true

# Build container images
echo "Building container images..."
if ! $COMPOSE_CMD build; then
    echo "ERROR: Failed to build container images"
    exit 1
fi

# Start services
echo "Starting services..."
if ! $COMPOSE_CMD up -d; then
    echo "ERROR: Failed to start services"
    exit 1
fi

# Wait for services to be ready
echo "Waiting for services to initialize..."
sleep 15

# Check service health
echo "Checking service health..."
$COMPOSE_CMD ps

# Get ngrok URL
echo ""
echo "Getting ngrok URL..."
sleep 5
NGROK_URL=$($COMPOSE_CMD logs cloud-server 2>&1 | grep "Ngrok tunnel established" | tail -1 | awk '{print $NF}' || echo "Not found")

# Display access information
echo ""
echo "====================================="
echo "Testbed Ready!"
echo "====================================="
echo "Backend Console: http://localhost:3000"
echo "Backend API: http://localhost:8088"
echo "HELICs API: http://localhost:8088/api/helics"
echo "Cloud Server: http://localhost:8080"
if [ "$NGROK_URL" != "Not found" ] && [ -n "$NGROK_URL" ]; then
    echo "Ngrok URL: $NGROK_URL"
    echo "Schema Endpoint: $NGROK_URL/schema"
    echo "OAuth Authorize: $NGROK_URL/oauth/authorize"
    echo "OAuth Token: $NGROK_URL/oauth/token"
else
    echo ""
    echo "NOTE: Ngrok URL not found. Check logs with:"
    echo "  $COMPOSE_CMD logs cloud-server"
fi
echo ""
echo "Default credentials:"
echo "Username: admin"
echo "Password: admin123"
echo ""
echo "To spawn devices, use the console at http://localhost:3000"
echo "To view logs: $COMPOSE_CMD logs -f"
echo "To stop: $COMPOSE_CMD down"
echo "====================================="
