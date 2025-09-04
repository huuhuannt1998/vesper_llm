#!/usr/bin/env python3
"""
Motion Sensor Port Conflict Fix
==============================

Fixes port allocation conflicts when spawning multiple motion sensors.
"""

import subprocess
import socket
import json
import re

def check_docker_containers():
    """Check existing motion sensor containers"""
    print("🔍 Checking existing motion sensor containers...")
    
    try:
        cmd = ["docker", "ps", "-a", "--filter", "name=motion-sensor", "--format", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            containers = []
            for line in lines:
                try:
                    container = json.loads(line)
                    containers.append(container)
                except json.JSONDecodeError:
                    pass
            
            if containers:
                print(f"📦 Found {len(containers)} motion sensor containers:")
                for container in containers:
                    name = container.get('Names', 'Unknown')
                    status = container.get('State', 'Unknown')
                    ports = container.get('Ports', 'No ports')
                    print(f"   - {name}: {status} ({ports})")
                return containers
            else:
                print("✅ No motion sensor containers found")
                return []
        else:
            print("✅ No motion sensor containers found")
            return []
            
    except Exception as e:
        print(f"❌ Error checking containers: {e}")
        return []

def find_used_ports():
    """Find ports currently used by Docker containers"""
    print("\n🔍 Checking used ports...")
    
    try:
        cmd = ["docker", "ps", "--format", "{{.Ports}}"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        used_ports = set()
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line:
                    # Extract port numbers from Docker port mappings
                    port_matches = re.findall(r'0\.0\.0\.0:(\d+)', line)
                    for port in port_matches:
                        used_ports.add(int(port))
        
        if used_ports:
            print(f"📊 Currently used ports: {sorted(used_ports)}")
        else:
            print("✅ No ports currently in use")
            
        return used_ports
        
    except Exception as e:
        print(f"❌ Error checking ports: {e}")
        return set()

def find_available_port(start_port=9000, used_ports=None):
    """Find an available port that's not used by Docker or system"""
    if used_ports is None:
        used_ports = set()
    
    port = start_port
    while port < 65535:
        # Skip if port is already used by Docker
        if port in used_ports:
            port += 1
            continue
            
        # Check if port is available on system
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                print(f"✅ Found available port: {port}")
                return port
        except OSError:
            port += 1
    
    print("❌ No available ports found")
    return None

def clean_motion_sensor_containers():
    """Clean up any existing motion sensor containers"""
    print("\n🧹 Cleaning up existing motion sensor containers...")
    
    containers = check_docker_containers()
    if not containers:
        return
    
    for container in containers:
        name = container.get('Names', '')
        if 'motion-sensor' in name:
            print(f"   🗑️ Removing container: {name}")
            try:
                # Stop container
                subprocess.run(["docker", "stop", name], capture_output=True, text=True)
                # Remove container
                subprocess.run(["docker", "rm", name], capture_output=True, text=True)
                print(f"   ✅ Removed: {name}")
            except Exception as e:
                print(f"   ❌ Error removing {name}: {e}")

def get_next_available_ports(count=5):
    """Get the next available ports for motion sensors"""
    print(f"\n🔍 Finding {count} available ports for motion sensors...")
    
    used_ports = find_used_ports()
    available_ports = []
    
    start_port = 9000
    for i in range(count):
        port = find_available_port(start_port, used_ports)
        if port:
            available_ports.append(port)
            used_ports.add(port)  # Mark as used for next search
            start_port = port + 1
        else:
            break
    
    return available_ports

def fix_motion_sensor_deployment():
    """Main function to fix motion sensor deployment issues"""
    print("🔧 VESPER Motion Sensor Port Conflict Fix")
    print("=" * 45)
    
    # Check current state
    containers = check_docker_containers()
    used_ports = find_used_ports()
    
    # Clean up if needed
    if containers:
        response = input("\n❓ Clean up existing motion sensor containers? (y/n): ")
        if response.lower() in ['y', 'yes']:
            clean_motion_sensor_containers()
            print("\n✅ Cleanup complete")
    
    # Get available ports
    available_ports = get_next_available_ports(8)  # 8 rooms need sensors
    
    print(f"\n📊 Port Allocation Plan:")
    room_names = ['living_room', 'kitchen', 'dining_room', 'bedroom', 'bathroom', 'hallway', 'office', 'garage']
    
    for i, (room, port) in enumerate(zip(room_names, available_ports)):
        print(f"   {i+1}. {room}: Port {port}")
    
    print(f"\n💡 Recommended Fix:")
    print(f"1. Update vesper_motion_validation.py to use sequential port allocation")
    print(f"2. Modify _deploy_motion_sensor() to track used ports")
    print(f"3. Ensure proper container cleanup between deployments")
    
    return available_ports

def create_port_fix_patch():
    """Create a patch for the motion validation system"""
    print(f"\n🔧 Creating port allocation fix...")
    
    patch_content = '''
# Add this to vesper_motion_validation.py in the __init__ method:
self.used_ports = set()
self.next_port = 9000

# Replace the _deploy_motion_sensor method port allocation with:
def get_next_available_port(self):
    """Get next available port for motion sensor"""
    import socket
    
    port = self.next_port
    while port < 65535:
        if port in self.used_ports:
            port += 1
            continue
            
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                self.used_ports.add(port)
                self.next_port = port + 1
                return port
        except OSError:
            port += 1
    
    return None

# Update the Docker command in _deploy_motion_sensor to use:
available_port = self.get_next_available_port()
if available_port is None:
    print("❌ No available ports for motion sensor")
    return None

# Use available_port instead of hardcoded port
'''
    
    with open("motion_sensor_port_fix.patch", "w") as f:
        f.write(patch_content)
    
    print("📄 Port fix patch created: motion_sensor_port_fix.patch")

if __name__ == "__main__":
    available_ports = fix_motion_sensor_deployment()
    create_port_fix_patch()
    
    print(f"\n🎯 Summary:")
    print(f"   Available ports: {available_ports}")
    print(f"   Containers checked and cleaned")
    print(f"   Port allocation patch created")
    print(f"\n💡 To fix the issue:")
    print(f"   1. Apply the port allocation patch to vesper_motion_validation.py")
    print(f"   2. Clean up existing containers before spawning new ones")
    print(f"   3. Use sequential port allocation starting from {available_ports[0] if available_ports else 9000}")
