#!/usr/bin/env python3
"""
Bulk Thermostat Temperature Control CLI

Usage: 
  python adjust_bulk_temperature.py setpoint [temperature] [username] 
  python adjust_bulk_temperature.py weather [temperature] [duration_hours]
  python adjust_bulk_temperature.py mode [mode] [username]

Examples:
  # Set all thermostats to 72°F setpoint for user 'admin'
  python adjust_bulk_temperature.py setpoint 72 admin
  
  # Override outside temperature to 95°F for 2 hours (affects all devices)
  python adjust_bulk_temperature.py weather 95 2
  
  # Set all thermostats to cooling mode for user 'admin'
  python adjust_bulk_temperature.py mode cool admin
"""

import requests
import json
import sys
import time
import concurrent.futures
from threading import Lock

# Default configuration
DEFAULT_BACKEND_URL = "http://localhost:8088"
DEFAULT_USERNAME = "admin"

# Global counters (thread-safe)
success_count = 0
failed_count = 0
processed_devices = []
counter_lock = Lock()

def get_all_devices(backend_url, username=None):
    """Get all active devices, optionally filtered by username"""
    try:
        response = requests.get(f"{backend_url}/api/console/devices", timeout=30)
        if response.status_code == 200:
            devices = response.json()
            
            # Filter by username if specified
            if username and username != "all":
                devices = [d for d in devices if d.get("username") == username]
                
            return devices
        else:
            print(f"❌ Failed to get devices: HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error getting devices: {e}")
        return []

def adjust_device_setpoint(serial, target_temp, backend_url):
    """Adjust setpoint temperature for a single device"""
    global success_count, failed_count, processed_devices
    
    try:
        payload = {"target_temp": target_temp}
        response = requests.post(
            f"{backend_url}/api/console/device/{serial}/setpoint",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            with counter_lock:
                success_count += 1
                processed_devices.append(f"{serial}: {target_temp}°F")
            print(f"✅ {serial}: Setpoint → {target_temp}°F")
            return True
        else:
            with counter_lock:
                failed_count += 1
            print(f"❌ {serial}: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        with counter_lock:
            failed_count += 1
        print(f"❌ {serial}: {str(e)}")
        return False

def adjust_device_mode(serial, mode, backend_url):
    """Adjust operating mode for a single device"""
    global success_count, failed_count, processed_devices
    
    try:
        payload = {"mode": mode}
        response = requests.post(
            f"{backend_url}/api/console/device/{serial}/mode",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            with counter_lock:
                success_count += 1
                processed_devices.append(f"{serial}: {mode}")
            print(f"✅ {serial}: Mode → {mode}")
            return True
        else:
            with counter_lock:
                failed_count += 1
            print(f"❌ {serial}: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        with counter_lock:
            failed_count += 1
        print(f"❌ {serial}: {str(e)}")
        return False

def override_weather_all(temperature, duration_hours, backend_url):
    """Override outside temperature for ALL environments"""
    try:
        payload = {
            "temperature": temperature,
            "duration_hours": duration_hours
        }
        response = requests.post(
            f"{backend_url}/api/console/weather-override",
            json=payload,
            timeout=60  # Weather override can take longer
        )
        
        if response.status_code == 200:
            result = response.json()
            devices_updated = result.get("devices_updated", 0)
            print(f"✅ Weather Override: {temperature}°F for {duration_hours}h → {devices_updated} environments")
            return True, devices_updated
        else:
            print(f"❌ Weather Override Failed: HTTP {response.status_code}")
            return False, 0
            
    except Exception as e:
        print(f"❌ Weather Override Error: {e}")
        return False, 0

def check_backend_availability(backend_url):
    """Check if backend console is available"""
    try:
        response = requests.get(f"{backend_url}/health", timeout=10)
        return response.status_code == 200
    except:
        return False

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    backend_url = DEFAULT_BACKEND_URL
    
    print("🌡️ Bulk Thermostat Temperature Control")
    print("=" * 45)
    
    # Check backend availability
    print("🔍 Checking backend availability...")
    if not check_backend_availability(backend_url):
        print(f"❌ Backend console not available at {backend_url}")
        print("   Make sure docker-compose is running: docker-compose up -d")
        sys.exit(1)
    print("✅ Backend available")
    
    if command == "setpoint":
        # Individual device setpoint control
        if len(sys.argv) < 3:
            print("Usage: python adjust_bulk_temperature.py setpoint [temperature] [username]")
            sys.exit(1)
            
        target_temp = float(sys.argv[2])
        username = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_USERNAME
        
        print(f"🎯 Setting thermostat setpoints to {target_temp}°F")
        print(f"👤 Username filter: {username}")
        
        # Get all devices for the user
        devices = get_all_devices(backend_url, username)
        if not devices:
            print("❌ No devices found")
            sys.exit(1)
        
        print(f"📊 Found {len(devices)} devices to adjust")
        
        # Determine concurrency
        max_workers = min(10, len(devices))
        print(f"🔄 Processing with {max_workers} workers...")
        
        start_time = time.time()
        
        # Process devices concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for device in devices:
                serial = device["serial_number"]
                future = executor.submit(adjust_device_setpoint, serial, target_temp, backend_url)
                futures.append(future)
            
            # Wait for completion
            for future in concurrent.futures.as_completed(futures):
                pass
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n📊 SETPOINT ADJUSTMENT COMPLETE")
        print("=" * 40)
        print(f"✅ Successful: {success_count}/{len(devices)}")
        print(f"❌ Failed: {failed_count}/{len(devices)}")
        print(f"⏱️  Duration: {duration:.1f} seconds")
        
    elif command == "weather":
        # Global weather override
        if len(sys.argv) < 4:
            print("Usage: python adjust_bulk_temperature.py weather [temperature] [duration_hours]")
            sys.exit(1)
            
        temperature = float(sys.argv[2])
        duration_hours = int(sys.argv[3])
        
        print(f"🌡️ Setting outside temperature to {temperature}°F for {duration_hours} hours")
        print("   This affects ALL environment simulators")
        
        start_time = time.time()
        success, devices_updated = override_weather_all(temperature, duration_hours, backend_url)
        end_time = time.time()
        
        print(f"\n📊 WEATHER OVERRIDE {'COMPLETE' if success else 'FAILED'}")
        print("=" * 40)
        if success:
            print(f"✅ Updated {devices_updated} environment simulators")
            print(f"🌡️ Outside temperature: {temperature}°F")
            print(f"⏱️  Duration: {duration_hours} hours")
        print(f"⏱️  Execution time: {end_time - start_time:.1f} seconds")
        
    elif command == "mode":
        # Operating mode control
        if len(sys.argv) < 3:
            print("Usage: python adjust_bulk_temperature.py mode [heat|cool|auto|off] [username]")
            sys.exit(1)
            
        mode = sys.argv[2].lower()
        if mode not in ["heat", "cool", "auto", "off"]:
            print("❌ Invalid mode. Use: heat, cool, auto, or off")
            sys.exit(1)
            
        username = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_USERNAME
        
        print(f"🔧 Setting thermostat mode to '{mode}'")
        print(f"👤 Username filter: {username}")
        
        # Get all devices for the user
        devices = get_all_devices(backend_url, username)
        if not devices:
            print("❌ No devices found")
            sys.exit(1)
        
        print(f"📊 Found {len(devices)} devices to adjust")
        
        # Determine concurrency
        max_workers = min(10, len(devices))
        print(f"🔄 Processing with {max_workers} workers...")
        
        start_time = time.time()
        
        # Process devices concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for device in devices:
                serial = device["serial_number"]
                future = executor.submit(adjust_device_mode, serial, mode, backend_url)
                futures.append(future)
            
            # Wait for completion
            for future in concurrent.futures.as_completed(futures):
                pass
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n📊 MODE ADJUSTMENT COMPLETE")
        print("=" * 40)
        print(f"✅ Successful: {success_count}/{len(devices)}")
        print(f"❌ Failed: {failed_count}/{len(devices)}")
        print(f"⏱️  Duration: {duration:.1f} seconds")
        
    else:
        print("❌ Invalid command. Use 'setpoint', 'weather', or 'mode'")
        print(__doc__)
        sys.exit(1)
    
    # Show sample of processed devices if many
    if len(processed_devices) > 20:
        print(f"\n📱 Sample Results:")
        print(f"   First 10: {processed_devices[:10]}")
        print(f"   Last 10: {processed_devices[-10:]}")
    elif processed_devices:
        print(f"\n📱 All Results: {processed_devices}")
    
    print(f"\n🌐 Check status at: http://localhost:3000")

if __name__ == "__main__":
    main()