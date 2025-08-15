#!/usr/bin/env python3
"""
Simple connectivity test for the LLM server.
"""
import socket
import httpx
import time

def test_tcp_connection():
    """Test basic TCP connection to the server."""
    host = "100.98.151.66"
    port = 1234
    timeout = 5
    
    print(f"Testing TCP connection to {host}:{port}...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ TCP connection successful to {host}:{port}")
            return True
        else:
            print(f"❌ TCP connection failed to {host}:{port} (error code: {result})")
            return False
            
    except Exception as e:
        print(f"❌ TCP connection error: {e}")
        return False

def test_http_connection():
    """Test HTTP connection to the server."""
    url = "http://100.98.151.66:1234/v1"
    
    print(f"Testing HTTP connection to {url}...")
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            print(f"✅ HTTP connection successful - Status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            return True
            
    except httpx.TimeoutException:
        print(f"❌ HTTP request timed out after 10 seconds")
        return False
    except httpx.ConnectError as e:
        print(f"❌ HTTP connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ HTTP error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 LLM Server Connectivity Test")
    print("=" * 40)
    
    tcp_ok = test_tcp_connection()
    print()
    
    if tcp_ok:
        http_ok = test_http_connection()
        print()
        
        if http_ok:
            print("🎉 Server is reachable and responding!")
        else:
            print("⚠️  Server is reachable but HTTP requests are failing")
    else:
        print("❌ Server is not reachable - check network or server status")
    
    print("\nDone.")
