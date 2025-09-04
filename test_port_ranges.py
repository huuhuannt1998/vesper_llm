#!/usr/bin/env python3
"""
Port Range Test for VESPER Device Manager
========================================

Tests the new device-specific port allocation system.
"""

import socket

def test_port_ranges():
    """Test the device-specific port ranges"""
    
    device_port_ranges = {
        "motion-sensor": {"start": 9000, "end": 9199},      # 200 ports for motion sensors
        "item-sensor": {"start": 9200, "end": 9299},        # 100 ports for item sensors
        "appliance": {"start": 9300, "end": 9399},          # 100 ports for appliances
        "light": {"start": 9400, "end": 9499},              # 100 ports for lights
        "smart-plug": {"start": 9500, "end": 9599},         # 100 ports for smart plugs
        "camera": {"start": 9600, "end": 9699},             # 100 ports for cameras
        "thermostat": {"start": 9700, "end": 9799},         # 100 ports for thermostats
        "smart-lock": {"start": 9800, "end": 9899},         # 100 ports for smart locks
        "default": {"start": 9900, "end": 9999}             # 100 ports for other devices
    }
    
    def find_available_port_in_range(start_port, end_port):
        """Find an available port within a specific range"""
        port = start_port
        while port <= end_port:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                port += 1
        return None
    
    print("🔌 Testing Device-Specific Port Allocation")
    print("=" * 50)
    
    # Test each device type
    for device_type, port_range in device_port_ranges.items():
        print(f"\n📱 Testing {device_type}:")
        print(f"   Range: {port_range['start']}-{port_range['end']} ({port_range['end'] - port_range['start'] + 1} ports)")
        
        # Find first 3 available ports in range
        used_ports = []
        for i in range(3):
            port = find_available_port_in_range(port_range['start'], port_range['end'])
            if port:
                used_ports.append(port)
                print(f"   ✅ Port {port} available")
                # Simulate port being used by binding to it briefly
                try:
                    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    test_socket.bind(('localhost', port))
                except:
                    pass
            else:
                print(f"   ❌ No available port found")
                break
        
        # Close test sockets
        try:
            test_socket.close()
        except:
            pass
    
    print(f"\n🎯 Port Range Summary:")
    print(f"   Motion Sensors: 9000-9199 (200 ports)")
    print(f"   Item Sensors:   9200-9299 (100 ports)")
    print(f"   Appliances:     9300-9399 (100 ports)")
    print(f"   Lights:         9400-9499 (100 ports)")
    print(f"   Smart Plugs:    9500-9599 (100 ports)")
    print(f"   Cameras:        9600-9699 (100 ports)")
    print(f"   Thermostats:    9700-9799 (100 ports)")
    print(f"   Smart Locks:    9800-9899 (100 ports)")
    print(f"   Other Devices:  9900-9999 (100 ports)")

def show_current_docker_containers():
    """Show currently running Docker containers and their ports"""
    import subprocess
    
    print(f"\n🐳 Current Docker Containers:")
    print("=" * 30)
    
    try:
        # List running containers with port info
        cmd = ["docker", "ps", "--format", "table {{.Names}}\\t{{.Ports}}\\t{{.Status}}"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                print(f"   {line}")
        else:
            print("   No running containers or Docker not available")
            
    except Exception as e:
        print(f"   Error checking containers: {e}")

def cleanup_vesper_containers():
    """Clean up any existing VESPER containers"""
    import subprocess
    
    print(f"\n🧹 Cleaning Up VESPER Containers:")
    print("=" * 35)
    
    try:
        # Find containers with motion-sensor in name
        cmd = ["docker", "ps", "-a", "--filter", "name=motion-sensor", "--format", "{{.Names}}"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            containers = result.stdout.strip().split('\n')
            for container in containers:
                if container:
                    print(f"   🗑️ Removing: {container}")
                    # Stop and remove container
                    subprocess.run(["docker", "stop", container], capture_output=True)
                    subprocess.run(["docker", "rm", container], capture_output=True)
            print(f"   ✅ Cleaned up {len(containers)} containers")
        else:
            print("   ✅ No VESPER containers to clean up")
            
    except Exception as e:
        print(f"   ❌ Error during cleanup: {e}")

def main():
    print("🔧 VESPER Port Range Testing Tool")
    print("=" * 40)
    
    # Show current containers
    show_current_docker_containers()
    
    # Clean up existing containers
    cleanup_vesper_containers()
    
    # Test port ranges
    test_port_ranges()
    
    print(f"\n💡 Benefits of Port Ranges:")
    print(f"   ✅ No more port conflicts between device types")
    print(f"   ✅ Easy to identify device type by port number")
    print(f"   ✅ Organized port allocation (200 ports for motion sensors)")
    print(f"   ✅ Room for expansion within each device category")
    
    print(f"\n🚀 Ready to spawn multiple motion sensors!")
    print(f"   First motion sensor will use port 9000")
    print(f"   Second motion sensor will use port 9001")
    print(f"   And so on up to port 9199...")

if __name__ == "__main__":
    main()
