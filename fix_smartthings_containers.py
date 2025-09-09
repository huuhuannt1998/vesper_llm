#!/usr/bin/env python3
"""
Fix SmartThings Virtual Motion Sensor Containers
This script recreates the virtual motion sensor containers with proper port bindings for VESPER addon access.
"""

import subprocess
import json
import time
import sys
import random

def run_command(cmd, capture_output=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True, check=True)
        return result.stdout.strip() if capture_output else None
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        print(f"   Error: {e}")
        return None

def stop_and_remove_testbed_containers():
    """Stop and remove existing testbed motion sensor containers"""
    print("🛑 Stopping existing testbed motion sensor containers...")
    
    # Find all motion sensor containers from testbed
    containers = [
        "motion-sensor-VSM-15E8-AE80-15D9",
        "motion-sensor-VSM-B6A5-AA54-E568", 
        "motion-sensor-VSM-249A-1D39-4677",
        "motion-sensor-VSM-6BBE-2A49-14AF"
    ]
    
    for container in containers:
        print(f"   🔄 Stopping {container}...")
        run_command(f"docker stop {container}", capture_output=False)
        print(f"   🗑️ Removing {container}...")
        run_command(f"docker rm {container}", capture_output=False)
    
    print("✅ Testbed containers stopped and removed")

def create_vesper_motion_sensor(serial_number, port, room="living_room"):
    """Create a new VESPER-compatible virtual motion sensor container"""
    
    container_name = f"vesper_motion_{serial_number}"
    
    print(f"🏗️ Creating VESPER motion sensor: {container_name}")
    print(f"   🔢 Serial: {serial_number}")
    print(f"   🌐 Port: {port}")
    print(f"   🏠 Room: {room}")
    
    # Create container on the existing testbed network with port binding
    docker_cmd = f"""docker run -d --name {container_name} --restart unless-stopped --network virtual-interaction_testbed-network -p {port}:8000 -e SERIAL_NUMBER={serial_number} -e REDIS_HOST=redis -e CLOUD_SERVER_URL=http://cloud-server:8080 -e SENSOR_ZONES=M01,M02,M03,M04,M05,M06,M07,M08,M09,M10 -e ROOM={room} virtual-interaction-motion-sensor:latest"""
    
    result = run_command(docker_cmd)
    
    if result is not None:
        print(f"✅ Container {container_name} created successfully")
        
        # Wait a moment for startup
        time.sleep(5)
        
        # Test the container
        test_result = run_command(f"curl -s http://localhost:{port}/health")
        if test_result:
            print(f"   🏥 Health check: OK")
            try:
                health_data = json.loads(test_result)
                print(f"   📊 Status: {health_data.get('status', 'unknown')}")
            except:
                print(f"   📄 Health response: {test_result}")
        else:
            print(f"   ⚠️ Health check failed - checking logs...")
            log_result = run_command(f"docker logs {container_name} --tail 5")
            if log_result:
                print(f"   📜 Logs: {log_result}")
        
        return True
    else:
        print(f"❌ Failed to create {container_name}")
        return False

def main():
    """Main function to fix SmartThings containers"""
    print("🔧 VESPER SmartThings Virtual Motion Sensor Container Fix")
    print("=" * 60)
    
    # Check if Docker is available
    if not run_command("docker --version"):
        print("❌ Docker is not available")
        sys.exit(1)
    
    # Check if the motion sensor image exists
    if not run_command("docker images virtual-interaction-motion-sensor:latest -q"):
        print("❌ virtual-interaction-motion-sensor:latest image not found")
        print("💡 Make sure the testbed environment has been set up")
        sys.exit(1)
    
    # Stop existing testbed containers
    stop_and_remove_testbed_containers()
    
    print(f"\n🏗️ Creating new VESPER-compatible containers...")
    
    # Create new containers with proper port bindings
    motion_sensors = [
        {"serial": "VSM-15E8-AE80-15D9", "port": 8001, "room": "living_room"},
        {"serial": "VSM-B6A5-AA54-E568", "port": 8002, "room": "kitchen"}, 
        {"serial": "VSM-249A-1D39-4677", "port": 8003, "room": "bedroom"},
        {"serial": "VSM-6BBE-2A49-14AF", "port": 8004, "room": "bathroom"}
    ]
    
    created_count = 0
    for sensor in motion_sensors:
        if create_vesper_motion_sensor(sensor["serial"], sensor["port"], sensor["room"]):
            created_count += 1
        print()  # Blank line for readability
    
    print(f"🏁 Container recreation complete!")
    print(f"   ✅ Created: {created_count}/{len(motion_sensors)} containers")
    
    if created_count > 0:
        print(f"\n📱 Next steps:")
        print(f"   1. Test the containers with debug_smartthings.py")
        print(f"   2. Re-register virtual sensors in SmartThings app")
        print(f"   3. Update VESPER addon device configurations")
        print(f"   4. Test motion detection in Blender")
    
    print(f"\n💡 Container access URLs:")
    for sensor in motion_sensors:
        print(f"   • {sensor['serial']}: http://localhost:{sensor['port']}")

if __name__ == "__main__":
    main()
