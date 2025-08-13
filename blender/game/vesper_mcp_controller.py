"""
VESPER MCP Integration Script

This creates a complete automated virtual character system that you can control
through the chat interface using Blender MCP.

Usage in chat:
- "Start coffee automation"  
- "Move character to kitchen"
- "Run 5 automation steps"
- "Take screenshot and decide next move"
"""

import json
import base64
import requests
from typing import Dict, List, Optional, Any

class VESPERChatController:
    """VESPER controller that integrates with chat interface via MCP."""
    
    def __init__(self):
        self.backend_url = "http://127.0.0.1:8000"
        self.current_tasks = ["Make coffee"]
        self.step_count = 0
        self.last_room = None
        self.step_size = 0.25
        self.max_steps = 50
        
        self.rooms = {
            "Kitchen": {"center": [3.0, -1.0]},
            "LivingRoom": {"center": [-2.0, 1.5]}, 
            "Bedroom": {"center": [-3.0, -2.0]},
            "Bathroom": {"center": [1.0, 3.0]}
        }
    
    def get_actor_position_via_mcp(self) -> Dict[str, float]:
        """Get actor position using MCP commands (will be called via chat)."""
        # This will be executed via MCP in the chat interface
        return {"x": 0.0, "y": 0.0, "z": 0.0}  # Placeholder
    
    def move_actor_via_mcp(self, direction: str) -> bool:
        """Move actor using MCP commands (will be called via chat)."""
        # This will be executed via MCP in the chat interface  
        return True  # Placeholder
    
    def capture_screenshot_via_mcp(self) -> Optional[str]:
        """Capture screenshot using MCP (will be called via chat)."""
        # This will be executed via MCP in the chat interface
        return None  # Placeholder
    
    def call_backend_navigation(self, actor_pos: Dict[str, float], 
                              bird_eye_b64: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Call the VESPER backend for navigation decision."""
        
        payload = {
            "actor_position": actor_pos,
            "tasks": self.current_tasks,
            "rooms": self.rooms,
            "bird_eye_image": bird_eye_b64,
            "last_room": self.last_room,
            "step_count": self.step_count,
            "max_steps": self.max_steps
        }
        
        try:
            response = requests.post(
                f"{self.backend_url}/blender/navigate",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Backend call failed: {e}")
            return None
    
    def execute_single_step(self, actor_pos: Dict[str, float], 
                           bird_eye_b64: Optional[str] = None) -> Dict[str, Any]:
        """Execute one automation step."""
        
        # Get LLM decision
        decision = self.call_backend_navigation(actor_pos, bird_eye_b64)
        
        if not decision:
            return {
                "success": False,
                "error": "Backend decision failed",
                "step_count": self.step_count
            }
        
        direction = decision.get("direction", "STAY")
        target_room = decision.get("target_room", self.last_room)
        reasoning = decision.get("reasoning", "No reasoning")
        task_complete = decision.get("task_complete", False)
        
        # Update state
        self.step_count += 1
        self.last_room = target_room
        
        return {
            "success": True,
            "direction": direction,
            "target_room": target_room,
            "reasoning": reasoning,
            "task_complete": task_complete,
            "step_count": self.step_count,
            "actor_position": actor_pos
        }

# Global instance for chat interface
vesper_controller = VESPERChatController()

def get_automation_status() -> Dict[str, Any]:
    """Get current automation status."""
    return {
        "tasks": vesper_controller.current_tasks,
        "step_count": vesper_controller.step_count,
        "last_room": vesper_controller.last_room,
        "rooms": vesper_controller.rooms
    }

def set_automation_tasks(tasks: List[str]) -> Dict[str, Any]:
    """Set new tasks for automation."""
    vesper_controller.current_tasks = tasks
    vesper_controller.step_count = 0  # Reset steps
    return {
        "message": f"Tasks updated: {', '.join(tasks)}",
        "tasks": tasks
    }

def reset_automation() -> Dict[str, Any]:
    """Reset automation state."""
    vesper_controller.step_count = 0
    vesper_controller.last_room = None
    return {
        "message": "Automation reset",
        "step_count": 0
    }
