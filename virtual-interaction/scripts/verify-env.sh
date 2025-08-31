#!/bin/bash
# Script to verify environment variables are loaded

echo "====================================="
echo "Environment Variable Verification"
echo "====================================="

# Set working directory to project root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    exit 1
fi

echo "✓ .env file found at: $(pwd)/.env"
echo ""

# Source the .env file to load variables
set -a
source .env
set +a

echo "Current Environment Variables:"
echo "-----------------------------"
echo "SMARTTHINGS_CLIENT_ID: ${SMARTTHINGS_CLIENT_ID:-NOT SET}"
echo "SMARTTHINGS_CLIENT_SECRET: ${SMARTTHINGS_CLIENT_SECRET:-NOT SET}"
echo "SMARTTHINGS_CALLBACK_CLIENT_ID: ${SMARTTHINGS_CALLBACK_CLIENT_ID:-NOT SET}"
echo "SMARTTHINGS_CALLBACK_CLIENT_SECRET: ${SMARTTHINGS_CALLBACK_CLIENT_SECRET:-NOT SET}"
echo "NGROK_AUTH_TOKEN: ${NGROK_AUTH_TOKEN:-NOT SET}"
echo "NGROK_DOMAIN: ${NGROK_DOMAIN:-NOT SET}"
echo "JWT_SECRET: ${JWT_SECRET:-NOT SET}"
echo ""

# Check file modification time
echo "File Information:"
echo "-----------------"
echo ".env last modified: $(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" .env 2>/dev/null || stat -c "%y" .env 2>/dev/null)"
echo ""

# Verify Docker Compose will use these values
echo "Docker Compose Environment Variables:"
echo "------------------------------------"
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

$COMPOSE_CMD config | grep -E "(SMARTTHINGS|NGROK|JWT)" | grep -v "^#" | sort | uniq

echo ""
echo "====================================="
