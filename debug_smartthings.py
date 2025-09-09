#!/usr/bin/env python3
"""
Debug SmartThings Virtual Motion Sensor Containers
This script helps diagnose connectivity issues with virtual motion sensor containers.
"""

import requests
import subprocess
import json
import time
import sys

def check_docker_containers():
    """Check all virtual motion sensor containers"""
    print("🐳 Checking Docker containers...")
    
    try:
        # List all containers with virtual_motion prefix
        result = subprocess.run(
            ["docker", "ps", "-a", "--filter", "name=virtual_motion", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"],
            capture_output=True,
            text=True,
            check=True
        )
        
        print("📋 Virtual Motion Sensor Containers:")
        print(result.stdout)
        
        # Get container details
        containers_result = subprocess.run(
            ["docker", "ps", "--filter", "name=virtual_motion", "--format", "{{.Names}}:{{.Ports}}"],
            capture_output=True,
            text=True,
            check=True
        )
        
        containers = []
        if containers_result.stdout.strip():
            for line in containers_result.stdout.strip().split('\n'):
                if ':' in line:
                    name, ports = line.split(':', 1)
                    containers.append((name, ports))
        
        return containers
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker command failed: {e}")
        print("💡 Make sure Docker is running and accessible")
        return []
    except FileNotFoundError:
        print("❌ Docker not found in PATH")
        print("💡 Make sure Docker is installed and in your PATH")
        return []

def test_container_health(container_name, port):
    """Test container health endpoint"""
    print(f"\n🏥 Testing health for {container_name} on port {port}...")
    
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=5)
        
        if response.status_code == 200:
            print(f"✅ Health check passed")
            try:
                health_data = response.json()
                print(f"   📊 Status: {health_data.get('status', 'unknown')}")
                print(f"   🕐 Uptime: {health_data.get('uptime', 'unknown')}")
                print(f"   📱 SmartThings: {health_data.get('smartthings_connected', 'unknown')}")
            except:
                print(f"   📄 Response: {response.text}")
            return True
        else:
            print(f"❌ Health check failed: HTTP {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection failed - container not reachable on port {port}")
        return False
    except requests.exceptions.Timeout:
        print(f"⏱️ Health check timeout")
        return False
    except Exception as e:
        print(f"⚠️ Health check error: {e}")
        return False

def test_motion_trigger(container_name, port):
    """Test motion trigger endpoint"""
    print(f"\n🚨 Testing motion trigger for {container_name} on port {port}...")
    
    try:
        # Test motion detected
        payload = {
            "motion": True,
            "actor_position": {"x": 1.0, "y": 2.0, "z": 0.0},
            "room": "debug_test",
            "timestamp": time.time(),
            "trigger_source": "debug_script"
        }
        
        response = requests.post(
            f"http://localhost:{port}/motion/trigger",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ Motion trigger successful")
            try:
                result_data = response.json()
                print(f"   📱 SmartThings status: {result_data.get('smartthings_status', 'unknown')}")
                print(f"   🔗 Device ID: {result_data.get('device_id', 'unknown')}")
                if 'error' in result_data:
                    print(f"   ⚠️ Error reported: {result_data['error']}")
                if 'smartthings_error' in result_data:
                    print(f"   🚫 SmartThings error: {result_data['smartthings_error']}")
            except:
                print(f"   📄 Response: {response.text}")
            
            # Test motion cleared after 2 seconds
            time.sleep(2)
            payload["motion"] = False
            payload["timestamp"] = time.time()
            
            print(f"   🟢 Testing motion cleared...")
            response2 = requests.post(
                f"http://localhost:{port}/motion/trigger",
                json=payload,
                timeout=10
            )
            
            if response2.status_code == 200:
                print(f"   ✅ Motion clear successful")
            else:
                print(f"   ⚠️ Motion clear failed: HTTP {response2.status_code}")
            
            return True
        else:
            print(f"❌ Motion trigger failed: HTTP {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"⚠️ Motion trigger error: {e}")
        return False

def get_container_logs(container_name):
    """Get recent container logs"""
    print(f"\n📜 Getting logs for {container_name}...")
    
    try:
        result = subprocess.run(
            ["docker", "logs", "--tail", "20", container_name],
            capture_output=True,
            text=True,
            check=True
        )
        
        print("📋 Recent logs:")
        for line in result.stdout.split('\n'):
            if line.strip():
                print(f"   {line}")
        
        if result.stderr:
            print("⚠️ Error logs:")
            for line in result.stderr.split('\n'):
                if line.strip():
                    print(f"   {line}")
                    
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to get logs: {e}")
    except Exception as e:
        print(f"⚠️ Log retrieval error: {e}")

def extract_port_from_ports(ports_str):
    """Extract port number from Docker ports string"""
    # Example: "0.0.0.0:8001->8000/tcp"
    if '->' in ports_str:
        external_part = ports_str.split('->')[0]
        if ':' in external_part:
            return external_part.split(':')[-1]
    return None

def main():
    """Main debugging function"""
    print("🔍 SmartThings Virtual Motion Sensor Debug Tool")
    print("=" * 50)
    
    # Check Docker containers
    containers = check_docker_containers()
    
    if not containers:
        print("\n❌ No virtual motion sensor containers found")
        print("💡 Make sure containers are created with the VESPER addon")
        return
    
    print(f"\n✅ Found {len(containers)} virtual motion sensor container(s)")
    
    # Test each container
    for container_name, ports_str in containers:
        print(f"\n{'='*60}")
        print(f"🧪 Testing container: {container_name}")
        print(f"   🔌 Ports: {ports_str}")
        
        # Extract port number
        port = extract_port_from_ports(ports_str)
        if not port:
            print("⚠️ Could not extract port number from Docker ports")
            get_container_logs(container_name)
            continue
        
        print(f"   📡 Testing on port: {port}")
        
        # Test health
        health_ok = test_container_health(container_name, port)
        
        if health_ok:
            # Test motion trigger
            motion_ok = test_motion_trigger(container_name, port)
            
            if not motion_ok:
                print(f"⚠️ Motion trigger issues detected")
        else:
            print(f"⚠️ Health check failed - skipping motion test")
        
        # Show recent logs
        get_container_logs(container_name)
    
    print(f"\n{'='*60}")
    print("🏁 Debug session complete")
    print("\n💡 Troubleshooting tips:")
    print("   • If containers are not responding, try: docker restart <container_name>")
    print("   • Check SmartThings app for device connectivity")
    print("   • Verify Docker containers have network access")
    print("   • Check firewall settings for localhost connections")

if __name__ == "__main__":
    main()
