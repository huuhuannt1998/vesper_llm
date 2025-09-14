"""
MCP Services Launcher for Blender Game Engine Integration
========================================================

This script launches all required MCP microservices as background processes
for integration with the Blender Game Engine.
"""

import asyncio
import subprocess
import sys
import os
import time
import json
import signal
import threading
from pathlib import Path
from typing import Dict, List, Optional
import aiohttp

class MCPServiceLauncher:
    """Manages launching and monitoring MCP microservices for BGE integration"""
    
    def __init__(self, vesper_root: str = None):
        self.vesper_root = vesper_root or r"C:\Users\hbui11\Desktop\vesper_llm"
        self.services_dir = os.path.join(self.vesper_root, "vesper_mcp", "services")
        self.processes: Dict[str, subprocess.Popen] = {}
        self.service_configs = {
            "orchestration": {
                "script": "orchestration_service.py",
                "port": 8000,
                "timeout": 30
            },
            "camera": {
                "script": "camera_service.py", 
                "port": 8001,
                "timeout": 15
            },
            "spatial": {
                "script": "spatial_service.py",
                "port": 8002,
                "timeout": 20
            },
            "movement": {
                "script": "movement_service.py",
                "port": 8003,
                "timeout": 10
            },
            "task_planning": {
                "script": "task_planning_service.py",
                "port": 8004,
                "timeout": 25
            }
        }
        self.running = False
        self.health_check_interval = 10  # seconds
    
    def start_service(self, service_name: str) -> bool:
        """Start a single MCP service"""
        
        if service_name not in self.service_configs:
            print(f"❌ Unknown service: {service_name}")
            return False
        
        config = self.service_configs[service_name]
        script_path = os.path.join(self.services_dir, config["script"])
        
        if not os.path.exists(script_path):
            print(f"❌ Service script not found: {script_path}")
            return False
        
        try:
            # Start the service process
            env = os.environ.copy()
            env["VESPER_SERVICE_PORT"] = str(config["port"])
            env["VESPER_SERVICE_NAME"] = service_name
            
            process = subprocess.Popen([
                sys.executable, script_path
            ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0)
            
            self.processes[service_name] = process
            print(f"✅ Started {service_name} service (PID: {process.pid}, Port: {config['port']})")
            
            # Give service time to start
            time.sleep(2)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start {service_name}: {str(e)}")
            return False
    
    async def check_service_health(self, service_name: str) -> bool:
        """Check if a service is healthy"""
        
        config = self.service_configs[service_name]
        url = f"http://localhost:{config['port']}/health"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        return True
        except Exception:
            pass
        
        return False
    
    async def wait_for_services(self, timeout: int = 60) -> bool:
        """Wait for all services to be healthy"""
        
        print("⏳ Waiting for services to be ready...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            all_healthy = True
            
            for service_name in self.service_configs:
                if not await self.check_service_health(service_name):
                    all_healthy = False
                    break
            
            if all_healthy:
                print("✅ All services are healthy and ready")
                return True
            
            await asyncio.sleep(2)
        
        print("❌ Timeout waiting for services to be ready")
        return False
    
    def start_all_services(self) -> bool:
        """Start all MCP services"""
        
        print("🚀 Starting MCP services for BGE integration...")
        
        success_count = 0
        for service_name in self.service_configs:
            if self.start_service(service_name):
                success_count += 1
        
        self.running = True
        
        if success_count == len(self.service_configs):
            print(f"✅ All {success_count} services started successfully")
            return True
        else:
            print(f"⚠️ Only {success_count}/{len(self.service_configs)} services started")
            return False
    
    def stop_service(self, service_name: str):
        """Stop a single service"""
        
        if service_name in self.processes:
            process = self.processes[service_name]
            
            try:
                if sys.platform == "win32":
                    os.kill(process.pid, signal.CTRL_BREAK_EVENT)
                else:
                    process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                
                print(f"✅ Stopped {service_name} service")
            except Exception as e:
                print(f"⚠️ Error stopping {service_name}: {str(e)}")
            
            del self.processes[service_name]
    
    def stop_all_services(self):
        """Stop all running services"""
        
        print("🛑 Stopping MCP services...")
        self.running = False
        
        for service_name in list(self.processes.keys()):
            self.stop_service(service_name)
        
        print("✅ All services stopped")
    
    async def health_monitor(self):
        """Monitor service health and restart if needed"""
        
        while self.running:
            for service_name in self.service_configs:
                if service_name in self.processes:
                    # Check if process is still running
                    process = self.processes[service_name]
                    if process.poll() is not None:
                        print(f"⚠️ Service {service_name} crashed, restarting...")
                        del self.processes[service_name]
                        self.start_service(service_name)
                    
                    # Check service health
                    elif not await self.check_service_health(service_name):
                        print(f"⚠️ Service {service_name} unhealthy")
            
            await asyncio.sleep(self.health_check_interval)
    
    def get_service_status(self) -> Dict[str, Dict]:
        """Get status of all services"""
        
        status = {}
        for service_name, config in self.service_configs.items():
            status[service_name] = {
                "running": service_name in self.processes,
                "port": config["port"],
                "pid": self.processes[service_name].pid if service_name in self.processes else None
            }
        
        return status
    
    def create_bge_client_config(self) -> str:
        """Create configuration file for BGE client"""
        
        config = {
            "services": {},
            "orchestration_url": f"http://localhost:{self.service_configs['orchestration']['port']}",
            "health_check_interval": 30,
            "request_timeout": 10
        }
        
        for service_name, service_config in self.service_configs.items():
            config["services"][service_name] = {
                "url": f"http://localhost:{service_config['port']}",
                "timeout": service_config["timeout"]
            }
        
        config_path = os.path.join(self.vesper_root, "blender", "mcp_services_config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ BGE client config saved to: {config_path}")
        return config_path

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    global launcher
    if 'launcher' in globals() and launcher:
        print("\n🛑 Received shutdown signal")
        launcher.stop_all_services()
    sys.exit(0)

async def main():
    """Main function to launch and monitor services"""
    
    global launcher
    launcher = MCPServiceLauncher()
    
    # Set up signal handlers
    if sys.platform != "win32":
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start all services
        if not launcher.start_all_services():
            print("❌ Failed to start all services")
            return 1
        
        # Wait for services to be ready
        if not await launcher.wait_for_services():
            print("❌ Services failed to become ready")
            launcher.stop_all_services()
            return 1
        
        # Create BGE client configuration
        launcher.create_bge_client_config()
        
        print("✅ MCP services ready for BGE integration")
        print("\nService Status:")
        for service_name, status in launcher.get_service_status().items():
            print(f"  {service_name}: {'✅ Running' if status['running'] else '❌ Stopped'} (Port: {status['port']})")
        
        print("\n🎮 You can now start Blender/UPBGE with llm_bge_navigation.py")
        print("📋 Press Ctrl+C to stop all services")
        
        # Start health monitoring
        await launcher.health_monitor()
        
    except KeyboardInterrupt:
        print("\n🛑 Keyboard interrupt received")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        launcher.stop_all_services()
        return 0

if __name__ == "__main__":
    launcher = None
    
    if sys.platform == "win32":
        # Handle Windows console interrupt
        def windows_handler(dwCtrlType):
            global launcher
            if launcher:
                launcher.stop_all_services()
            return True
        
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleCtrlHandler(windows_handler, True)
    
    # Run the launcher
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
