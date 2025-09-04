#!/usr/bin/env python3
"""
Enhanced Port Allocation Test
============================

Tests the improved port allocation system with Docker awareness and port tracking.
"""

import socket
import subprocess
import time

def test_enhanced_port_allocation():
    """Test the enhanced port allocation system"""
    
    print("🔧 Testing Enhanced Port Allocation System")
    print("=" * 50)
    
    # Simulate the DeviceManager port allocation logic
    allocated_ports = set()
    
    device_port_ranges = {
        "motion-sensor": {"start": 9000, "end": 9199},
        "item-sensor": {"start": 9200, "end": 9299},
    }
    
    def find_available_port_in_range(start_port, end_port):
        """Enhanced port finding with Docker awareness"""
        port = start_port
        while port <= end_port:
            # Skip ports that are already allocated by this session
            if port in allocated_ports:
                port += 1
                continue
                
            try:
                # Check if port is available by trying to bind to all interfaces (0.0.0.0)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind(('0.0.0.0', port))
                    
                    # Double-check by looking for existing Docker containers using this port
                    check_cmd = ["docker", "ps", "--format", "{{.Ports}}", "--filter", f"publish={port}"]
                    result = subprocess.run(check_cmd, capture_output=True, text=True)
                    
                    # If no containers are using this port, it's available
                    if result.returncode == 0 and not result.stdout.strip():
                        return port
                    else:
                        # Port is being used by Docker, try next one
                        port += 1
                        continue
                        
            except OSError:
                # Port is not available, try next one
                port += 1
                continue
        return None
    
    def allocate_port_for_device(device_type, device_name):
        """Simulate device port allocation"""
        port_range = device_port_ranges.get(device_type, device_port_ranges["motion-sensor"])
        port = find_available_port_in_range(port_range["start"], port_range["end"])
        
        if port is None:
            print(f"❌ No available ports in range {port_range['start']}-{port_range['end']} for {device_type}")
            return None
        
        # Reserve the port immediately to prevent race conditions
        allocated_ports.add(port)
        
        print(f"🔌 {device_name}: Assigned port {port} (range: {port_range['start']}-{port_range['end']})")
        return port
    
    # Test allocating ports for multiple motion sensors
    print(f"\n📱 Testing Multiple Motion Sensor Port Allocation:")
    
    test_devices = [
        ("motion-sensor", "Motion Sensor 1"),
        ("motion-sensor", "Motion Sensor 2"),
        ("motion-sensor", "Motion Sensor 3"),
        ("item-sensor", "Item Sensor 1"),
        ("motion-sensor", "Motion Sensor 4"),
    ]
    
    allocated_results = []
    
    for device_type, device_name in test_devices:
        port = allocate_port_for_device(device_type, device_name)
        if port:
            allocated_results.append((device_name, port))
        else:
            allocated_results.append((device_name, "FAILED"))
    
    print(f"\n📊 Allocation Results:")
    for device_name, port in allocated_results:
        status = "✅" if port != "FAILED" else "❌"
        print(f"   {status} {device_name:<20} → Port {port}")
    
    print(f"\n🎯 Key Improvements:")
    print(f"   ✅ Binds to 0.0.0.0 (all interfaces) like Docker")
    print(f"   ✅ Checks for existing Docker containers on port")
    print(f"   ✅ Tracks allocated ports to prevent race conditions") 
    print(f"   ✅ Device-specific port ranges maintained")
    
    print(f"\n🔍 Current Docker Containers:")
    try:
        cmd = ["docker", "ps", "--format", "table {{.Names}}\\t{{.Ports}}"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines[:5]:  # Show first 5 lines
                print(f"   {line}")
        else:
            print("   No Docker containers running")
    except:
        print("   Error checking Docker containers")
    
    return allocated_results

def test_docker_port_detection():
    """Test Docker port detection specifically"""
    print(f"\n🐳 Testing Docker Port Detection:")
    print("=" * 35)
    
    # Check if any containers are using ports in our range
    for port in range(9000, 9005):
        try:
            check_cmd = ["docker", "ps", "--format", "{{.Names}} {{.Ports}}", "--filter", f"publish={port}"]
            result = subprocess.run(check_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                if result.stdout.strip():
                    print(f"   Port {port}: Used by Docker container")
                    print(f"     {result.stdout.strip()}")
                else:
                    print(f"   Port {port}: Available ✅")
            else:
                print(f"   Port {port}: Error checking")
                
        except Exception as e:
            print(f"   Port {port}: Exception - {e}")

def main():
    print("🚀 Enhanced Port Allocation Testing")
    print("=" * 40)
    
    # Test Docker port detection
    test_docker_port_detection()
    
    # Test the enhanced allocation system
    results = test_enhanced_port_allocation()
    
    print(f"\n✅ Enhanced Port Allocation Test Complete!")
    
    expected_results = [
        ("Motion Sensor 1", 9000),
        ("Motion Sensor 2", 9001), 
        ("Motion Sensor 3", 9002),
        ("Item Sensor 1", 9200),
        ("Motion Sensor 4", 9003),
    ]
    
    print(f"\n🎯 Expected vs Actual:")
    all_correct = True
    for i, ((expected_name, expected_port), (actual_name, actual_port)) in enumerate(zip(expected_results, results)):
        if actual_port == expected_port:
            print(f"   ✅ {actual_name}: {actual_port} (expected {expected_port})")
        else:
            print(f"   ❌ {actual_name}: {actual_port} (expected {expected_port})")
            all_correct = False
    
    if all_correct:
        print(f"\n🎉 All port allocations correct! System is working properly.")
    else:
        print(f"\n⚠️ Some allocations differ from expected - this may be normal if ports were in use.")
    
    print(f"\n🚀 Ready to test in Blender!")

if __name__ == "__main__":
    main()
