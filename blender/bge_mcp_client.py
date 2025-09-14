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
        """Initialize aiohttp session"""
        
        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # Create new event loop if none exists
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        timeout = aiohttp.ClientTimeout(total=self.request_timeout)
        self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def _ensure_session(self):
        """Ensure session is available"""
        
        if self.session is None or self.session.closed:
            self._initialize_session()
    
    async def _make_request(self, method: str, url: str, data: Dict = None) -> Optional[Dict]:
        """Make HTTP request to MCP service"""
        
        await self._ensure_session()
        
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
            return None
            
        except Exception as e:
            print(f"❌ Request error: {method} {url} -> {str(e)}")
            return None
    
    def _run_async(self, coro):
        """Run async function in sync context"""
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a task
                future = asyncio.ensure_future(coro)
                # Wait for completion (this is a simplified approach)
                while not future.done():
                    time.sleep(0.01)
                return future.result()
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            # No event loop, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()
    
    def check_services_health(self) -> Dict[str, bool]:
        """Check health of all MCP services"""
        
        async def _check_health():
            health_status = {}
            
            # Check orchestration service
            orch_url = f"{self.config['orchestration_url']}/health"
            result = await self._make_request("GET", orch_url)
            health_status["orchestration"] = result is not None
            
            # Check individual services
            for service_name, service_config in self.config["services"].items():
                service_url = f"{service_config['url']}/health"
                result = await self._make_request("GET", service_url)
                health_status[service_name] = result is not None
            
            return health_status
        
        return self._run_async(_check_health())
    
    def get_comprehensive_context(self, current_task: str = None, additional_context: Dict = None) -> Optional[Dict]:
        """Get comprehensive context from orchestration service"""
        
        async def _get_context():
            url = f"{self.config['orchestration_url']}/get_comprehensive_context"
            data = {
                "current_task": current_task,
                "additional_context": additional_context or {}
            }
            return await self._make_request("POST", url, data)
        
        return self._run_async(_get_context())
    
    def create_vlm_decision_prompt(self, current_task: str, context: Dict = None) -> Optional[Dict]:
        """Create VLM decision prompt via orchestration service"""
        
        async def _create_prompt():
            url = f"{self.config['orchestration_url']}/create_vlm_decision_prompt"
            data = {
                "current_task": current_task,
                "context": context or {}
            }
            return await self._make_request("POST", url, data)
        
        return self._run_async(_create_prompt())
    
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
