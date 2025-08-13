"""
Blender MCP Integration for VESPER LLM Character Control

This module provides the Blender side of the automation system.
It captures bird-eye views, sends them to the LLM backend, and executes movement decisions.
"""

import time
import base64
import json
import urllib.request
import urllib.error
from typing import Dict, List, Optional, Any

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
STEP_SIZE = 0.25  # meters per movement step
MAX_STEPS_PER_TASK = 50
SCREENSHOT_INTERVAL = 0.5  # seconds between screenshots

class VESPERAutomationController:
    """Main controller for automated LLM character navigation in Blender."""
    
    def __init__(self):
        self.is_running = False
        self.current_tasks = ["Make coffee"]  # Default task
        self.step_count = 0
        self.last_room = None
        self.actor_name = "Actor"
        self.rooms = {
            "Kitchen": {"center": [3.0, -1.0]},
            "LivingRoom": {"center": [-2.0, 1.5]},
            "Bedroom": {"center": [-3.0, -2.0]},
            "Bathroom": {"center": [1.0, 3.0]}
        }
        
    def capture_bird_eye_view(self) -> Optional[str]:
        """Capture bird's-eye screenshot and return as base64."""
        try:
            import bpy
            
            # Save current view settings
            scene = bpy.context.scene
            
            # Create temporary camera for bird's-eye view if needed
            # For now, we'll use current viewport
            
            # Capture screenshot
            temp_path = "/tmp/bird_eye_view.png"
            bpy.ops.render.opengl(write_still=True, view_context=True)
            
            # Alternative: use direct viewport screenshot
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                temp_path = tmp_file.name
                
            bpy.ops.screen.screenshot(filepath=temp_path, check_existing=False)
            
            # Read and encode
            with open(temp_path, 'rb') as f:
                image_data = f.read()
                
            # Clean up
            try:
                os.unlink(temp_path)
            except:
                pass
                
            return base64.b64encode(image_data).decode('ascii')
            
        except Exception as e:
            print(f"Screenshot capture failed: {e}")
            return None
    
    def get_actor_position(self) -> Dict[str, float]:
        """Get current actor position."""
        try:
            import bpy
            actor = bpy.data.objects.get(self.actor_name)
            if actor:
                return {
                    "x": float(actor.location.x),
                    "y": float(actor.location.y), 
                    "z": float(actor.location.z)
                }
        except Exception as e:
            print(f"Failed to get actor position: {e}")
            
        return {"x": 0.0, "y": 0.0, "z": 0.0}
    
    def move_actor(self, direction: str) -> bool:
        """Move actor one step in the specified direction."""
        try:
            import bpy
            actor = bpy.data.objects.get(self.actor_name)
            if not actor:
                print(f"Actor '{self.actor_name}' not found")
                return False
                
            direction = direction.upper()
            
            if direction == "RIGHT":
                actor.location.x += STEP_SIZE
            elif direction == "LEFT":
                actor.location.x -= STEP_SIZE
            elif direction == "UP":
                actor.location.y += STEP_SIZE
            elif direction == "DOWN":
                actor.location.y -= STEP_SIZE
            elif direction == "STAY":
                pass  # No movement
            else:
                print(f"Unknown direction: {direction}")
                return False
                
            # Update viewport
            bpy.context.view_layer.update()
            return True
            
        except Exception as e:
            print(f"Failed to move actor: {e}")
            return False
    
    def call_llm_backend(self, bird_eye_b64: Optional[str]) -> Optional[Dict[str, Any]]:
        """Send current state to LLM backend and get navigation decision."""
        
        actor_pos = self.get_actor_position()
        
        payload = {
            "actor_position": actor_pos,
            "tasks": self.current_tasks,
            "rooms": self.rooms,
            "bird_eye_image": bird_eye_b64,
            "last_room": self.last_room,
            "step_count": self.step_count,
            "max_steps": MAX_STEPS_PER_TASK
        }
        
        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                f"{BACKEND_URL}/blender/navigate",
                data=data,
                headers={"Content-Type": "application/json"}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result
                
        except urllib.error.URLError as e:
            print(f"Backend connection failed: {e}")
        except Exception as e:
            print(f"LLM backend error: {e}")
            
        return None
    
    def execute_navigation_step(self) -> bool:
        """Execute one step of the automation loop."""
        
        print(f"\n=== Step {self.step_count + 1} ===")
        
        # 1. Capture bird's-eye view
        print("📸 Capturing bird's-eye view...")
        bird_eye_b64 = self.capture_bird_eye_view()
        
        if bird_eye_b64:
            img_size = len(bird_eye_b64)
            print(f"✅ Screenshot captured ({img_size} chars)")
        else:
            print("❌ Screenshot failed, proceeding without image")
        
        # 2. Get LLM decision
        print("🧠 Consulting LLM for navigation decision...")
        decision = self.call_llm_backend(bird_eye_b64)
        
        if not decision:
            print("❌ LLM decision failed, stopping automation")
            return False
        
        # 3. Execute movement
        direction = decision.get("direction", "STAY")
        target_room = decision.get("target_room", self.last_room)
        reasoning = decision.get("reasoning", "No reasoning provided")
        task_complete = decision.get("task_complete", False)
        
        actor_pos = self.get_actor_position()
        
        print(f"🎯 Decision: {direction} toward {target_room}")
        print(f"💭 Reasoning: {reasoning}")
        print(f"📍 Current position: ({actor_pos['x']:.2f}, {actor_pos['y']:.2f})")
        
        # Move the actor
        if self.move_actor(direction):
            new_pos = self.get_actor_position()
            print(f"✅ Moved to: ({new_pos['x']:.2f}, {new_pos['y']:.2f})")
        else:
            print("❌ Movement failed")
            
        # Update state
        self.step_count += 1
        self.last_room = target_room
        
        # Check completion
        if task_complete:
            print("🎉 Task completed!")
            return False  # Stop automation
            
        if self.step_count >= MAX_STEPS_PER_TASK:
            print("⚠️ Max steps reached")
            return False  # Stop automation
            
        return True  # Continue automation
    
    def start_automation(self, tasks: Optional[List[str]] = None):
        """Start the automated navigation loop."""
        
        if tasks:
            self.current_tasks = tasks
            
        print("🚀 Starting VESPER LLM automation...")
        print(f"📋 Tasks: {', '.join(self.current_tasks)}")
        print(f"🏠 Rooms: {list(self.rooms.keys())}")
        
        self.is_running = True
        self.step_count = 0
        
        try:
            while self.is_running:
                if not self.execute_navigation_step():
                    break
                    
                # Wait before next step
                time.sleep(SCREENSHOT_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n⏹️ Automation stopped by user")
        except Exception as e:
            print(f"💥 Automation error: {e}")
        finally:
            self.is_running = False
            print("🏁 Automation finished")
    
    def stop_automation(self):
        """Stop the automation loop."""
        self.is_running = False
    
    def set_tasks(self, tasks: List[str]):
        """Update current tasks."""
        self.current_tasks = tasks
        print(f"📋 Tasks updated: {', '.join(tasks)}")
    
    def set_actor(self, actor_name: str):
        """Set the name of the actor object."""
        self.actor_name = actor_name
        print(f"🎭 Actor set to: {actor_name}")

# Global controller instance
automation_controller = VESPERAutomationController()

def start_vesper_automation(tasks: Optional[List[str]] = None):
    """Convenience function to start automation."""
    automation_controller.start_automation(tasks)

def stop_vesper_automation():
    """Convenience function to stop automation."""
    automation_controller.stop_automation()

def set_vesper_tasks(tasks: List[str]):
    """Convenience function to set tasks."""
    automation_controller.set_tasks(tasks)

# Example usage functions for Blender console:
def demo_coffee_task():
    """Demo: Make coffee task."""
    set_vesper_tasks(["Make coffee"])
    start_vesper_automation()

def demo_living_room_task():
    """Demo: Go to living room.""" 
    set_vesper_tasks(["Turn off living room lights"])
    start_vesper_automation()

def demo_multi_task():
    """Demo: Multiple tasks."""
    set_vesper_tasks(["Make coffee", "Turn off living room lights", "Go to bedroom"])
    start_vesper_automation()
