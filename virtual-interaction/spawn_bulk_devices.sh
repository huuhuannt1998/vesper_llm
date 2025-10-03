#!/bin/bash
# 
# Virtual Device Bulk Spawner CLI
# 
# Usage: ./spawn_bulk_devices.sh [number_of_devices] [username] [config_type]
#
# Example: ./spawn_bulk_devices.sh 1000 admin medium_house_efficient
#

# Default values
NUM_DEVICES=${1:-1}
USERNAME=${2:-"admin"}  
CONFIG_TYPE=${3:-"medium_house_efficient"}
BACKEND_URL="http://localhost:8088"

# Device endpoint
SPAWN_ENDPOINT="$BACKEND_URL/api/console/spawn"

echo "🚀 Virtual Device Bulk Spawner"
echo "================================="
echo "📊 Spawning $NUM_DEVICES devices"
echo "👤 Username: $USERNAME"
echo "⚙️  Config: $CONFIG_TYPE"
echo "🌐 Backend: $BACKEND_URL"
echo "================================="

# Check if backend is available
echo "🔍 Checking backend availability..."
if ! curl -s -f "$BACKEND_URL/health" > /dev/null; then
    echo "❌ Backend console not available at $BACKEND_URL"
    echo "   Make sure docker-compose is running: docker-compose up -d"
    exit 1
fi
echo "✅ Backend available"

# Counter variables
SUCCESS_COUNT=0
FAILED_COUNT=0
SPAWNED_SERIALS=()

# Function to spawn a single device
spawn_device() {
    local device_number=$1
    
    # JSON payload
    local payload="{\"device_type\":\"thermostat\",\"username\":\"$USERNAME\",\"environment_config\":\"$CONFIG_TYPE\"}"
    
    # Make API request with timeout
    local response
    response=$(curl -s -X POST "$SPAWN_ENDPOINT" \
        -H "Content-Type: application/json" \
        -d "$payload" \
        --connect-timeout 30 \
        --max-time 60 2>/dev/null)
    
    if [ $? -eq 0 ] && echo "$response" | grep -q "serial_number"; then
        # Extract serial number from response
        local serial=$(echo "$response" | grep -o '"serial_number":"[^"]*"' | cut -d'"' -f4)
        SPAWNED_SERIALS+=("$serial")
        ((SUCCESS_COUNT++))
        echo "✅ Device $device_number: $serial"
    else
        ((FAILED_COUNT++))
        echo "❌ Device $device_number: Failed"
    fi
}

# Main spawning loop
echo ""
echo "🔄 Starting device spawning..."
START_TIME=$(date +%s)

for i in $(seq 1 $NUM_DEVICES); do
    # Show progress every 50 devices
    if [ $((i % 50)) -eq 0 ] || [ $i -eq 1 ]; then
        echo "📊 Progress: $i/$NUM_DEVICES devices..."
    fi
    
    spawn_device $i
    
    # Small delay to prevent overwhelming the API
    sleep 0.1
done

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Summary report
echo ""
echo "📊 SPAWNING COMPLETE"
echo "================================="
echo "✅ Successful: $SUCCESS_COUNT/$NUM_DEVICES"
echo "❌ Failed: $FAILED_COUNT/$NUM_DEVICES" 
echo "⏱️  Duration: ${DURATION} seconds"
echo "📈 Rate: $(echo "scale=2; $SUCCESS_COUNT / $DURATION" | bc -l 2>/dev/null || echo "N/A") devices/second"

# Show first 10 and last 10 serial numbers if many devices
if [ ${#SPAWNED_SERIALS[@]} -gt 20 ]; then
    echo ""
    echo "📱 Sample Spawned Devices:"
    echo "   First 10: ${SPAWNED_SERIALS[@]:0:10}"
    echo "   Last 10: ${SPAWNED_SERIALS[@]: -10}"
elif [ ${#SPAWNED_SERIALS[@]} -gt 0 ]; then
    echo ""
    echo "📱 Spawned Devices: ${SPAWNED_SERIALS[@]}"
fi

echo ""
echo "🌐 Check status at: http://localhost:3000"
echo "🔍 View devices with: curl $BACKEND_URL/api/console/devices"