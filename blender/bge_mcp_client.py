"""
BGE MCP Client - Integration layer for Blender Game Engine with MCP services
============================================================================

This module provides a clean interface for llm_bge_navigation.py to communicate
with the MCP microservices architecture.
"""

import json
import time
import os
import sys
import asyncio
from typing import Dict, Any, List, Optional, Tuple
import aiohttp
from pathlib import Path

class BGEMCPClient:
    """Client for communicating with MCP services from within BGE"""
    
    def __init__(self, config_path: str = None):
        """Initialize BGE MCP client"""
        
        # Default config path
        if config_path is None:
            vesper_root = r"C:\Users\hbui11\Desktop\vesper_llm"
            config_path = os.path.join(vesper_root, "blender", "mcp_services_config.json")
        
        self.config_path = config_path
        self.config = self._load_config()
        self.session = None
        self._event_loop = None
        self._loop_thread = None
        self.last_health_check = 0
        self.health_check_interval = self.config.get("health_check_interval", 30)
        self.request_timeout = self.config.get("request_timeout", 10)
        
        # Initialize async session
        self._initialize_session()
        
        print(f"🔗 BGE MCP Client initialized")
        print(f"📋 Orchestration URL: {self.config.get('orchestration_url')}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load MCP services configuration"""
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            print(f"✅ Loaded MCP config from: {self.config_path}")
            return config
        except Exception as e:
            print(f"❌ Failed to load MCP config: {str(e)}")
            # Return default config
            return {
                "orchestration_url": "http://localhost:8000",
                "services": {
                    "camera": {"url": "http://localhost:8001", "timeout": 15},
                    "spatial": {"url": "http://localhost:8002", "timeout": 20},
                    "movement": {"url": "http://localhost:8003", "timeout": 10},
                    "task_planning": {"url": "http://localhost:8004", "timeout": 25}
                },
                "request_timeout": 10,
                "health_check_interval": 30
            }
    
    def _initialize_session(self):
        """Initialize aiohttp session with BGE-compatible event loop"""
        
        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError("Event loop is closed")
        except RuntimeError:
            # Create new event loop if none exists or is closed
            print("🔄 BGE: Creating new event loop for MCP services")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        # Ensure the loop is running in a separate thread for BGE compatibility
        import threading
        
        if not hasattr(self, '_loop_thread') or not self._loop_thread.is_alive():
            self._loop_thread = threading.Thread(target=self._run_event_loop, daemon=True)
            self._loop_thread.start()
            time.sleep(0.1)  # Give thread time to start
        
        timeout = aiohttp.ClientTimeout(total=self.request_timeout)
        # Create session in the event loop thread
        future = asyncio.run_coroutine_threadsafe(
            self._create_session_async(timeout), loop
        )
        self.session = future.result(timeout=5)
        
    def _run_event_loop(self):
        """Run event loop in separate thread for BGE compatibility"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._event_loop = loop
        try:
            loop.run_forever()
        except Exception as e:
            print(f"⚠️ Event loop error: {e}")
        finally:
            loop.close()
            
    async def _create_session_async(self, timeout):
        """Create aiohttp session asynchronously"""
        return aiohttp.ClientSession(timeout=timeout)
    
    async def _ensure_session(self):
        """Ensure session is available"""
        
        if self.session is None or self.session.closed:
            self._initialize_session()
    
    def make_request_sync(self, method: str, url: str, data: Dict = None) -> Optional[Dict]:
        """Make synchronous HTTP request (BGE-compatible wrapper)"""
        
        if not self._event_loop or not self._loop_thread.is_alive():
            print("⚠️ Event loop not available, reinitializing...")
            self._initialize_session()
            
        try:
            # Run async request in the event loop thread
            future = asyncio.run_coroutine_threadsafe(
                self._make_request_async(method, url, data), 
                self._event_loop
            )
            return future.result(timeout=self.request_timeout)
            
        except Exception as e:
            print(f"❌ MCP request failed: {e}")
            return None
    
    async def _make_request_async(self, method: str, url: str, data: Dict = None) -> Optional[Dict]:
        """Make HTTP request to MCP service (async implementation)"""
        
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.request_timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
            elif method.upper() == "POST":
                async with self.session.post(url, json=data) as response:
                    if response.status == 200:
                        return await response.json()
            
            print(f"⚠️ Request failed: {method} {url} -> {response.status}")
        except asyncio.TimeoutError:
            print(f"⏰ Request timeout: {method} {url}")
            return None
        except Exception as e:
            print(f"❌ Request error: {method} {url} -> {e}")
            return None
    
    def cleanup(self):
        """Cleanup resources"""
        if self.session and not self.session.closed:
            # Schedule session close in event loop
            if self._event_loop and self._loop_thread.is_alive():
                asyncio.run_coroutine_threadsafe(
                    self.session.close(), self._event_loop
                )
        
        if self._event_loop and self._loop_thread.is_alive():
            self._event_loop.call_soon_threadsafe(self._event_loop.stop)
            self._loop_thread.join(timeout=2)
    
    def check_services_health(self) -> Dict[str, bool]:
        """Check health of all MCP services"""
        
        health_status = {}
        
        # Check orchestration service
        orch_url = f"{self.config['orchestration_url']}/health"
        result = self.make_request_sync("GET", orch_url)
        health_status["orchestration"] = result is not None
        
        # Check individual services
        for service_name, service_config in self.config.get("services", {}).items():
            service_url = f"{service_config['url']}/health"
            result = self.make_request_sync("GET", service_url)
            health_status[service_name] = result is not None
        
        return health_status
    
    def get_comprehensive_context(self, current_task: str = None, additional_context: Dict = None) -> Optional[Dict]:
        """Get comprehensive context from orchestration service"""
        
        url = f"{self.config['orchestration_url']}/get_comprehensive_context"
        data = {
            "current_task": current_task,
            "additional_context": additional_context or {}
        }
        return self.make_request_sync("POST", url, data)
    
    def create_vlm_decision_prompt(self, current_task: str, context: Dict = None) -> Optional[Dict]:
        """Create VLM decision prompt via orchestration service"""
        
        url = f"{self.config['orchestration_url']}/create_vlm_decision_prompt"
        data = {
            "current_task": current_task,
            "context": context or {}
        }
        return self.make_request_sync("POST", url, data)
    
    def execute_tool_action(self, tool_name: str, parameters: Dict) -> Optional[Dict]:
        """Execute a tool action via orchestration service"""
        
        async def _execute_tool():
            url = f"{self.config['orchestration_url']}/execute_tool"
            data = {
                "tool_name": tool_name,
                "parameters": parameters
            }
            return await self._make_request("POST", url, data)
        
        return self._run_async(_execute_tool())
    
    # Direct service calls (bypass orchestration)
    
    def capture_dual_view_images(self, scene_name: str = None, analysis_focus: str = None) -> Optional[Dict]:
        """Capture images via camera service"""
        
        async def _capture_images():
            url = f"{self.config['services']['camera']['url']}/capture_dual_view"
            data = {
                "scene_name": scene_name,
                "analysis_focus": analysis_focus
            }
            return await self._make_request("POST", url, data)
        
        return self._run_async(_capture_images())
    
    def get_spatial_context(self, include_navigation: bool = True) -> Optional[Dict]:
        """Get spatial context via spatial service"""
        
        async def _get_spatial():
            url = f"{self.config['services']['spatial']['url']}/get_spatial_context"
            data = {"include_navigation": include_navigation}
            return await self._make_request("POST", url, data)
        
        return self._run_async(_get_spatial())
    
    def execute_movement_action(self, action: str, parameters: Dict) -> Optional[Dict]:
        """Execute movement via movement service"""
        
        async def _execute_movement():
            url = f"{self.config['services']['movement']['url']}/execute_movement"
            data = {
                "action": action,
                "parameters": parameters
            }
            return await self._make_request("POST", url, data)
        
        return self._run_async(_execute_movement())
    
    def plan_task_sequence(self, task_description: str, constraints: List[str] = None) -> Optional[Dict]:
        """Plan task sequence via task planning service"""
        
        async def _plan_task():
            url = f"{self.config['services']['task_planning']['url']}/plan_sequence"
            data = {
                "task_description": task_description,
                "constraints": constraints or []
            }
            return await self._make_request("POST", url, data)
        
        return self._run_async(_plan_task())
    
    def cleanup(self):
        """Clean up resources"""
        
        async def _cleanup():
            if self.session and not self.session.closed:
                await self.session.close()
        
        self._run_async(_cleanup())

# Global client instance for BGE
_bge_mcp_client = None

def get_bge_mcp_client(config_path: str = None) -> BGEMCPClient:
    """Get or create BGE MCP client instance"""
    
    global _bge_mcp_client
    
    if _bge_mcp_client is None:
        _bge_mcp_client = BGEMCPClient(config_path)
    
    return _bge_mcp_client

def initialize_bge_mcp_integration(config_path: str = None) -> bool:
    """Initialize BGE MCP integration"""
    
    try:
        client = get_bge_mcp_client(config_path)
        
        # Check if services are available
        health_status = client.check_services_health()
        
        healthy_services = sum(1 for status in health_status.values() if status)
        total_services = len(health_status)
        
        print(f"🔍 MCP Services Health: {healthy_services}/{total_services} healthy")
        
        for service_name, is_healthy in health_status.items():
            status_icon = "✅" if is_healthy else "❌"
            print(f"  {status_icon} {service_name}")
        
        if healthy_services == total_services:
            print("✅ BGE MCP integration ready")
            return True
        else:
            print("⚠️ Some services are unavailable - continuing with degraded functionality")
            return False
            
    except Exception as e:
        print(f"❌ Failed to initialize BGE MCP integration: {str(e)}")
        return False

# Compatibility functions for existing llm_bge_navigation.py code

def get_enhanced_context_for_llm(current_task: str = None) -> Dict[str, Any]:
    """Get enhanced context for LLM (compatibility function)"""
    
    client = get_bge_mcp_client()
    context = client.get_comprehensive_context(current_task)
    
    if context:
        return context
    else:
        # Fallback to basic context
        return {
            "timestamp": time.time(),
            "current_task": current_task,
            "status": "mcp_services_unavailable",
            "fallback_mode": True
        }

def create_vlm_prompt_with_context(task: str, additional_context: Dict = None) -> str:
    """Create VLM prompt with context (compatibility function)"""
    
    client = get_bge_mcp_client()
    prompt_data = client.create_vlm_decision_prompt(task, additional_context)
    
    if prompt_data and "prompt" in prompt_data:
        return prompt_data["prompt"]
    else:
        # Fallback prompt
        return f"Task: {task}\nContext: MCP services unavailable\nPlease provide basic navigation response."

def execute_llm_suggested_action(action_data: Dict) -> Dict[str, Any]:
    """Execute LLM suggested action (compatibility function)"""
    
    client = get_bge_mcp_client()
    
    if "tool_name" in action_data and "parameters" in action_data:
        result = client.execute_tool_action(action_data["tool_name"], action_data["parameters"])
        
        if result:
            return result
    
    # Fallback response
    return {
        "success": False,
        "error": "MCP services unavailable or invalid action",
        "fallback_mode": True
    }
