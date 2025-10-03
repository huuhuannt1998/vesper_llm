#!/usr/bin/env python3
"""
Virtual Device Bulk Spawner CLI (Python version)

Usage: python spawn_bulk_devices.py [number_of_devices] [username] [config_type]

Example: python spawn_bulk_devices.py 1000 admin medium_house_efficient
"""

import requests
import json
import sys
import time
import concurrent.futures
from threading import Lock

# Default configuration
DEFAULT_NUM_DEVICES = 1
DEFAULT_USERNAME = "admin"
DEFAULT_CONFIG_TYPE = "medium_house_efficient"
DEFAULT_BACKEND_URL = "http://localhost:8088"

# Global counters (thread-safe)
success_count = 0
failed_count = 0
spawned_serials = []
counter_lock = Lock()

def spawn_device(device_number, username, config_type, backend_url):
    """Spawn a single virtual device"""
    global success_count, failed_count, spawned_serials
    
    payload = {
        "device_type": "thermostat",
        "username": username,
        "environment_config": config_type
    }
    
    try:
        response = requests.post(
            f"{backend_url}/api/console/spawn",
            json=payload,
            timeout=60  # 60 second timeout for each device
        )
        
        if response.status_code == 200:
            result = response.json()
            serial = result.get("serial_number", "unknown")
            
            with counter_lock:
                spawned_serials.append(serial)
                success_count += 1
                
            print(f"✅ Device {device_number}: {serial}")
            return True
        else:
            with counter_lock:
                failed_count += 1
            print(f"❌ Device {device_number}: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        with counter_lock:
            failed_count += 1
        print(f"❌ Device {device_number}: {str(e)}")
        return False

def check_backend_availability(backend_url):
    """Check if backend console is available"""
    try:
        response = requests.get(f"{backend_url}/health", timeout=10)
        return response.status_code == 200
    except:
        return False

def main():
    # Parse command line arguments
    num_devices = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_NUM_DEVICES
    username = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_USERNAME
    config_type = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_CONFIG_TYPE
    backend_url = DEFAULT_BACKEND_URL
    
    print("🚀 Virtual Device Bulk Spawner (Python)")
    print("=" * 45)
    print(f"📊 Spawning {num_devices} devices")
    print(f"👤 Username: {username}")
    print(f"⚙️  Config: {config_type}")
    print(f"🌐 Backend: {backend_url}")
    print("=" * 45)
    
    # Check backend availability
    print("🔍 Checking backend availability...")
    if not check_backend_availability(backend_url):
        print(f"❌ Backend console not available at {backend_url}")
        print("   Make sure docker-compose is running: docker-compose up -d")
        sys.exit(1)
    print("✅ Backend available")
    
    # Determine concurrency based on number of devices
    if num_devices <= 10:
        max_workers = 2  # Low concurrency for small batches
    elif num_devices <= 100:
        max_workers = 5  # Medium concurrency
    else:
        max_workers = 10  # Higher concurrency for large batches
        
    print(f"🔄 Starting device spawning with {max_workers} concurrent workers...")
    start_time = time.time()
    
    # Use ThreadPoolExecutor for concurrent spawning
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        futures = []
        for i in range(1, num_devices + 1):
            future = executor.submit(spawn_device, i, username, config_type, backend_url)
            futures.append(future)
        
        # Process results as they complete
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            completed += 1
            
            # Show progress every 50 completions or for small batches
            if completed % 50 == 0 or num_devices <= 50:
                print(f"📊 Progress: {completed}/{num_devices} devices completed...")
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Final report
    print()
    print("📊 SPAWNING COMPLETE")
    print("=" * 35)
    print(f"✅ Successful: {success_count}/{num_devices}")
    print(f"❌ Failed: {failed_count}/{num_devices}")
    print(f"⏱️  Duration: {duration:.1f} seconds")
    if duration > 0:
        print(f"📈 Rate: {success_count/duration:.2f} devices/second")
    
    # Show sample of spawned devices
    if len(spawned_serials) > 20:
        print()
        print("📱 Sample Spawned Devices:")
        print(f"   First 10: {spawned_serials[:10]}")
        print(f"   Last 10: {spawned_serials[-10:]}")
    elif spawned_serials:
        print()
        print(f"📱 Spawned Devices: {spawned_serials}")
    
    print()
    print("🌐 Check status at: http://localhost:3000")
    print(f"🔍 View devices with: curl {backend_url}/api/console/devices")

if __name__ == "__main__":
    main()