#!/usr/bin/env python3
"""
Network connectivity diagnostic for LLM server
"""
import socket
import time

def diagnose_connectivity():
    host = "100.98.151.66"
    port = 1234
    
    print(f"🔍 Diagnosing connectivity to {host}:{port}")
    
    # Test basic socket connectivity
    try:
        print("📡 Testing socket connection...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        start_time = time.time()
        result = sock.connect_ex((host, port))
        end_time = time.time()
        
        if result == 0:
            print(f"✅ Socket connection successful ({end_time - start_time:.2f}s)")
            sock.close()
        else:
            print(f"❌ Socket connection failed: {result}")
        
    except Exception as e:
        print(f"❌ Socket error: {e}")
    
    # Test HTTP connectivity with low-level socket
    try:
        print("🌐 Testing HTTP request via socket...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        
        http_request = f"GET /v1/models HTTP/1.1\r\nHost: {host}:{port}\r\nConnection: close\r\n\r\n"
        sock.send(http_request.encode())
        
        response = sock.recv(4096).decode()
        
        if "HTTP/1.1" in response:
            status_line = response.split('\r\n')[0]
            print(f"✅ HTTP response received: {status_line}")
        else:
            print(f"❌ Unexpected response: {response[:100]}...")
        
        sock.close()
        
    except Exception as e:
        print(f"❌ HTTP socket error: {e}")

if __name__ == "__main__":
    diagnose_connectivity()
