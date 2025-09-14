"""
VESPER Microservices Deployment Manager
======================================

Deployment and management utilities for VESPER VLM microservices architecture.
"""

import asyncio
import subprocess
import time
import logging
import json
import os
from typing import Dict, Any, List
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import service registry
from . import SERVICES

class ServiceDeploymentManager:
    """Manages deployment and lifecycle of all VESPER microservices"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent
        self.processes = {}
        self.service_status = {}
    
    async def deploy_all_services(self) -> Dict[str, Any]:
        """Deploy all microservices"""
        logger.info("Starting deployment of all VESPER microservices")
        
        deployment_results = {}
        
        # Deploy services in dependency order (orchestration last)
        service_order = [
            "camera", "image_analysis", "spatial", "movement", 
            "interaction", "task_analysis", "history", 
            "sensor_simulation", "device", "task_manager",
            "orchestration"  # Last - coordinates others
        ]
        
        for service_name in service_order:
            if service_name in SERVICES:
                result = await self.deploy_service(service_name)
                deployment_results[service_name] = result
                
                # Brief pause between deployments
                await asyncio.sleep(1)
        
        return {
            "success": True,
            "deployed_services": len(deployment_results),
            "results": deployment_results
        }
    
    async def deploy_service(self, service_name: str) -> Dict[str, Any]:
        """Deploy a specific microservice"""
        try:
            if service_name not in SERVICES:
                return {
                    "success": False,
                    "error": f"Unknown service: {service_name}"
                }
            
            service_info = SERVICES[service_name]
            module_name = service_info["module"]
            port = service_info["port"]
            
            # Service file path
            service_file = self.base_path / f"{module_name}.py"
            
            if not service_file.exists():
                return {
                    "success": False,
                    "error": f"Service file not found: {service_file}"
                }
            
            # Start the service process
            logger.info(f"Starting {service_name} on port {port}")
            
            # Use Python to run the service
            cmd = [
                "python", str(service_file)
            ]
            
            process = subprocess.Popen(
                cmd,
                cwd=str(self.base_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Store process reference
            self.processes[service_name] = process
            
            # Wait a moment for startup
            await asyncio.sleep(2)
            
            # Check if process is still running
            if process.poll() is None:
                self.service_status[service_name] = {
                    "status": "running",
                    "port": port,
                    "pid": process.pid,
                    "started_at": time.time()
                }
                
                logger.info(f"✅ {service_name} started successfully on port {port} (PID: {process.pid})")
                
                return {
                    "success": True,
                    "service": service_name,
                    "port": port,
                    "pid": process.pid,
                    "status": "running"
                }
            else:
                # Process failed to start
                stdout, stderr = process.communicate()
                return {
                    "success": False,
                    "service": service_name,
                    "error": f"Failed to start: {stderr}",
                    "stdout": stdout
                }
        
        except Exception as e:
            logger.error(f"Error deploying {service_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def stop_service(self, service_name: str) -> Dict[str, Any]:
        """Stop a specific service"""
        try:
            if service_name not in self.processes:
                return {
                    "success": False,
                    "error": f"Service {service_name} not found in processes"
                }
            
            process = self.processes[service_name]
            
            # Terminate the process
            process.terminate()
            
            # Wait for termination
            try:
                process.wait(timeout=10)
                logger.info(f"✅ {service_name} stopped successfully")
            except subprocess.TimeoutExpired:
                # Force kill if not terminated
                process.kill()
                process.wait()
                logger.warning(f"⚠️ {service_name} force killed")
            
            # Remove from tracking
            del self.processes[service_name]
            if service_name in self.service_status:
                del self.service_status[service_name]
            
            return {
                "success": True,
                "service": service_name,
                "status": "stopped"
            }
        
        except Exception as e:
            logger.error(f"Error stopping {service_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def stop_all_services(self) -> Dict[str, Any]:
        """Stop all running services"""
        logger.info("Stopping all VESPER microservices")
        
        stop_results = {}
        
        # Stop in reverse order (orchestration first)
        service_names = list(self.processes.keys())
        service_names.reverse()
        
        for service_name in service_names:
            result = await self.stop_service(service_name)
            stop_results[service_name] = result
        
        return {
            "success": True,
            "stopped_services": len(stop_results),
            "results": stop_results
        }
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get status of all services"""
        status = {}
        
        for service_name, process in self.processes.items():
            if process.poll() is None:
                # Process is running
                status[service_name] = {
                    "status": "running",
                    "pid": process.pid,
                    **self.service_status.get(service_name, {})
                }
            else:
                # Process has stopped
                status[service_name] = {
                    "status": "stopped",
                    "exit_code": process.poll()
                }
        
        return {
            "success": True,
            "services": status,
            "total_services": len(SERVICES),
            "running_services": len([s for s in status.values() if s["status"] == "running"])
        }
    
    async def health_check_all_services(self) -> Dict[str, Any]:
        """Perform health check on all services"""
        import aiohttp
        
        health_results = {}
        
        async with aiohttp.ClientSession() as session:
            for service_name, service_info in SERVICES.items():
                if service_name == "orchestration":
                    continue  # Skip orchestration for now
                
                port = service_info["port"]
                health_url = f"http://localhost:{port}/health"
                
                try:
                    async with session.get(health_url, timeout=5) as response:
                        if response.status == 200:
                            data = await response.json()
                            health_results[service_name] = {
                                "healthy": True,
                                "response": data
                            }
                        else:
                            health_results[service_name] = {
                                "healthy": False,
                                "error": f"HTTP {response.status}"
                            }
                
                except asyncio.TimeoutError:
                    health_results[service_name] = {
                        "healthy": False,
                        "error": "Timeout"
                    }
                except Exception as e:
                    health_results[service_name] = {
                        "healthy": False,
                        "error": str(e)
                    }
        
        healthy_count = sum(1 for r in health_results.values() if r.get("healthy"))
        
        return {
            "success": True,
            "health_results": health_results,
            "healthy_services": healthy_count,
            "total_checked": len(health_results),
            "overall_health": "healthy" if healthy_count == len(health_results) else "degraded"
        }

# Global deployment manager instance
deployment_manager = ServiceDeploymentManager()

async def main():
    """Main deployment script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="VESPER Microservices Deployment Manager")
    parser.add_argument("action", choices=["deploy", "stop", "status", "health"], 
                       help="Action to perform")
    parser.add_argument("--service", help="Specific service name (optional)")
    
    args = parser.parse_args()
    
    if args.action == "deploy":
        if args.service:
            result = await deployment_manager.deploy_service(args.service)
        else:
            result = await deployment_manager.deploy_all_services()
        print(json.dumps(result, indent=2))
    
    elif args.action == "stop":
        if args.service:
            result = await deployment_manager.stop_service(args.service)
        else:
            result = await deployment_manager.stop_all_services()
        print(json.dumps(result, indent=2))
    
    elif args.action == "status":
        result = await deployment_manager.get_service_status()
        print(json.dumps(result, indent=2))
    
    elif args.action == "health":
        result = await deployment_manager.health_check_all_services()
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
