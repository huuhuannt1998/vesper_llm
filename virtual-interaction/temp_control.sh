#!/bin/bash
#
# Quick Thermostat Temperature Control CLI
#
# Usage: ./temp_control.sh [setpoint|weather|mode] [value] [username/duration]
#

BACKEND_URL="http://localhost:8088"

# Check if backend is available
check_backend() {
    echo "🔍 Checking backend availability..."
    if ! curl -s -f "$BACKEND_URL/health" > /dev/null; then
        echo "❌ Backend console not available at $BACKEND_URL"
        echo "   Make sure docker-compose is running: docker-compose up -d"
        exit 1
    fi
    echo "✅ Backend available"
}

# Get all device serials for a user
get_device_serials() {
    local username=$1
    curl -s "$BACKEND_URL/api/console/devices" | \
    jq -r --arg user "$username" '.[] | select(.username == $user) | .serial_number' 2>/dev/null
}

# Set temperature for all devices
set_bulk_setpoint() {
    local temperature=$1
    local username=${2:-"admin"}
    
    echo "🌡️ Setting all thermostats to ${temperature}°F for user: $username"
    
    # Get device list
    devices=$(get_device_serials "$username")
    device_count=$(echo "$devices" | wc -l)
    
    if [ -z "$devices" ] || [ "$device_count" -eq 0 ]; then
        echo "❌ No devices found for user: $username"
        exit 1
    fi
    
    echo "📊 Found $device_count devices"
    
    success_count=0
    failed_count=0
    
    # Process each device
    while IFS= read -r serial; do
        if [ -n "$serial" ]; then
            response=$(curl -s -X POST "$BACKEND_URL/api/console/device/$serial/setpoint" \
                -H "Content-Type: application/json" \
                -d "{\"target_temp\": $temperature}" \
                -w "%{http_code}")
            
            http_code="${response: -3}"
            if [ "$http_code" = "200" ]; then
                echo "✅ $serial: Setpoint → ${temperature}°F"
                ((success_count++))
            else
                echo "❌ $serial: Failed (HTTP $http_code)"
                ((failed_count++))
            fi
        fi
    done <<< "$devices"
    
    echo ""
    echo "📊 SETPOINT ADJUSTMENT COMPLETE"
    echo "✅ Successful: $success_count/$device_count"
    echo "❌ Failed: $failed_count/$device_count"
}

# Override weather for all environments
set_bulk_weather() {
    local temperature=$1
    local duration=${2:-2}
    
    echo "🌡️ Setting outside temperature to ${temperature}°F for ${duration} hours"
    echo "   This affects ALL environment simulators"
    
    response=$(curl -s -X POST "$BACKEND_URL/api/console/weather-override" \
        -H "Content-Type: application/json" \
        -d "{\"temperature\": $temperature, \"duration_hours\": $duration}")
    
    if echo "$response" | grep -q "success"; then
        devices_updated=$(echo "$response" | jq -r '.devices_updated' 2>/dev/null)
        echo "✅ Weather Override Complete"
        echo "   Updated $devices_updated environment simulators"
        echo "   Outside temperature: ${temperature}°F for ${duration}h"
    else
        echo "❌ Weather override failed"
        echo "   Response: $response"
    fi
}

# Set mode for all devices
set_bulk_mode() {
    local mode=$1
    local username=${2:-"admin"}
    
    # Validate mode
    if [[ ! "$mode" =~ ^(heat|cool|auto|off)$ ]]; then
        echo "❌ Invalid mode: $mode"
        echo "   Valid modes: heat, cool, auto, off"
        exit 1
    fi
    
    echo "🔧 Setting all thermostats to '$mode' mode for user: $username"
    
    # Get device list
    devices=$(get_device_serials "$username")
    device_count=$(echo "$devices" | wc -l)
    
    if [ -z "$devices" ] || [ "$device_count" -eq 0 ]; then
        echo "❌ No devices found for user: $username"
        exit 1
    fi
    
    echo "📊 Found $device_count devices"
    
    success_count=0
    failed_count=0
    
    # Process each device
    while IFS= read -r serial; do
        if [ -n "$serial" ]; then
            response=$(curl -s -X POST "$BACKEND_URL/api/console/device/$serial/mode" \
                -H "Content-Type: application/json" \
                -d "{\"mode\": \"$mode\"}" \
                -w "%{http_code}")
            
            http_code="${response: -3}"
            if [ "$http_code" = "200" ]; then
                echo "✅ $serial: Mode → $mode"
                ((success_count++))
            else
                echo "❌ $serial: Failed (HTTP $http_code)"
                ((failed_count++))
            fi
        fi
    done <<< "$devices"
    
    echo ""
    echo "📊 MODE ADJUSTMENT COMPLETE"
    echo "✅ Successful: $success_count/$device_count"
    echo "❌ Failed: $failed_count/$device_count"
}

# Show usage
show_usage() {
    echo "🌡️ Quick Thermostat Temperature Control"
    echo "========================================="
    echo "Usage: $0 [command] [value] [username/duration]"
    echo ""
    echo "Commands:"
    echo "  setpoint [temp] [username]    - Set thermostat target temperature"
    echo "  weather [temp] [hours]        - Override outside temperature"
    echo "  mode [heat|cool|auto|off] [username] - Set thermostat operating mode"
    echo ""
    echo "Examples:"
    echo "  $0 setpoint 72 admin         - Set all admin's thermostats to 72°F"
    echo "  $0 weather 95 4              - Set outside temp to 95°F for 4 hours"
    echo "  $0 mode cool admin           - Set all admin's thermostats to cool mode"
}

# Main script
main() {
    if [ $# -lt 2 ]; then
        show_usage
        exit 1
    fi
    
    check_backend
    
    command=$1
    value=$2
    param3=${3:-"admin"}
    
    case "$command" in
        "setpoint")
            set_bulk_setpoint "$value" "$param3"
            ;;
        "weather")
            set_bulk_weather "$value" "$param3"
            ;;
        "mode")
            set_bulk_mode "$value" "$param3"
            ;;
        *)
            echo "❌ Invalid command: $command"
            show_usage
            exit 1
            ;;
    esac
    
    echo ""
    echo "🌐 Check status at: http://localhost:3000"
}

main "$@"