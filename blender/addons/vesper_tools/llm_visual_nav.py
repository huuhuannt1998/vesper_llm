"""
LLM Visual Navigation System for Blender
NO HARDCODED COORDINATES - Pure LLM visual analysis and control
"""
import bpy
import bmesh
import mathutils
import os
import sys
import base64
import tempfile
import json
from io import BytesIO

# Dynamically find VESPER path for LLM client
def find_vesper_root():
    """Find the VESPER project root directory dynamically"""
    current_file = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file)
    
    # Look for vesper_llm directory by walking up the directory tree
    while current_dir and current_dir != os.path.dirname(current_dir):
        if os.path.basename(current_dir) == 'vesper_llm':
            return current_dir
        if os.path.exists(os.path.join(current_dir, 'backend', 'app', 'llm', 'client.py')):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    
    # Fallback to hardcoded path if not found
    return r"c:\Users\hbui11\Desktop\vesper_llm"

vesper_path = find_vesper_root()
if vesper_path not in sys.path:
    sys.path.insert(0, vesper_path)

try:
    from backend.app.llm.client import chat_completion
    from scripts.visual_navigation import analyze_visual_scene_for_navigation, convert_llm_direction_to_movement
    LLM_AVAILABLE = True
    print("✅ LLM Visual Navigation: Connected to LLM client")
except ImportError as e:
    print(f"⚠️ LLM Visual Navigation: LLM client not available - {e}")
    LLM_AVAILABLE = False

class LLMVisualNavigator:
    """
    LLM-driven visual navigation system - NO hardcoded coordinates
    """
    
    def __init__(self):
        self.llm_available = LLM_AVAILABLE
        self.navigation_active = False
        self.current_target_room = None
        self.movement_history = []
        self.screenshot_count = 0
        
    def capture_birds_eye_screenshot(self) -> str:
        """
        Capture bird's-eye view screenshot for LLM visual analysis
        """
        try:
            # Set up bird's-eye camera view
            scene = bpy.context.scene
            
            # Store original camera settings
            original_camera = scene.camera
            
            # Create temporary bird's-eye camera
            bpy.ops.object.camera_add(location=(0, 0, 10))
            birds_eye_cam = bpy.context.object
            birds_eye_cam.name = "BirdsEyeTemp"
            
            # Configure camera for top-down view
            birds_eye_cam.rotation_euler = (0, 0, 0)  # Point straight down
            birds_eye_cam.data.type = 'ORTHO'
            birds_eye_cam.data.ortho_scale = 12
            
            # Set as active camera
            scene.camera = birds_eye_cam
            
            # Configure render settings for screenshot
            scene.render.resolution_x = 800
            scene.render.resolution_y = 800
            scene.render.filepath = os.path.join(tempfile.gettempdir(), f"vesper_nav_{self.screenshot_count}.png")
            
            # Render the screenshot
            bpy.ops.render.render(write_still=True)
            
            # Read screenshot and encode to base64
            screenshot_path = scene.render.filepath
            if os.path.exists(screenshot_path):
                with open(screenshot_path, "rb") as img_file:
                    img_data = img_file.read()
                    img_base64 = base64.b64encode(img_data).decode('utf-8')
                
                # Clean up
                os.remove(screenshot_path)
                bpy.data.objects.remove(birds_eye_cam, do_unlink=True)
                scene.camera = original_camera
                
                self.screenshot_count += 1
                print(f"📸 LLM Visual Nav: Screenshot {self.screenshot_count} captured for analysis")
                return img_base64
            
            # Cleanup on failure
            bpy.data.objects.remove(birds_eye_cam, do_unlink=True)
            scene.camera = original_camera
            return None
            
        except Exception as e:
            print(f"❌ LLM Visual Nav: Screenshot capture failed - {e}")
            return None
    
    def get_llm_navigation_command(self, target_room: str) -> dict:
        """
        Get navigation command from LLM based on visual analysis
        """
        if not self.llm_available:
            return self.fallback_navigation_command()
        
        print(f"🧠 LLM Visual Nav: Analyzing scene for navigation to {target_room}")
        
        # Capture current scene screenshot
        screenshot_base64 = self.capture_birds_eye_screenshot()
        
        if not screenshot_base64:
            print("❌ LLM Visual Nav: No screenshot available, using fallback")
            return self.fallback_navigation_command()
        
        # Get LLM visual analysis
        try:
            nav_analysis = analyze_visual_scene_for_navigation(screenshot_base64, target_room)
            
            # Validate LLM response
            if nav_analysis and "next_direction" in nav_analysis:
                direction = nav_analysis["next_direction"]
                distance = nav_analysis.get("movement_distance", "SHORT")
                
                # Convert to Blender movement
                movement_offset = convert_llm_direction_to_movement(direction, distance)
                
                command = {
                    "direction": direction,
                    "movement_offset": movement_offset,
                    "llm_analysis": nav_analysis,
                    "source": "LLM_VISUAL_ANALYSIS"
                }
                
                print(f"🎯 LLM Visual Nav: Command - {direction} ({distance}) → {movement_offset}")
                return command
            
            else:
                print("⚠️ LLM Visual Nav: Invalid LLM response, using fallback")
                return self.fallback_navigation_command()
                
        except Exception as e:
            print(f"❌ LLM Visual Nav: Analysis failed - {e}")
            return self.fallback_navigation_command()
    
    def fallback_navigation_command(self) -> dict:
        """
        Fallback navigation when LLM is unavailable
        """
        return {
            "direction": "STAY",
            "movement_offset": (0, 0, 0),
            "llm_analysis": {"reasoning": "LLM unavailable - staying in place"},
            "source": "FALLBACK"
        }
    
    def execute_navigation_step(self, actor, target_room: str) -> bool:
        """
        Execute one navigation step using LLM visual guidance
        Returns True if navigation complete, False if continuing
        """
        if not actor:
            print("❌ LLM Visual Nav: No actor available")
            return True
        
        # Get LLM navigation command based on current visual scene
        nav_command = self.get_llm_navigation_command(target_room)
        
        direction = nav_command["direction"]
        movement_offset = nav_command["movement_offset"]
        llm_analysis = nav_command["llm_analysis"]
        
        print(f"📍 LLM Visual Nav: Current actor position: {[round(x, 2) for x in actor.location]}")
        
        # Check if we should stay (arrived or blocked)
        if direction == "STAY":
            reasoning = llm_analysis.get("reasoning", "No movement needed")
            print(f"✅ LLM Visual Nav: Navigation complete - {reasoning}")
            return True
        
        # Apply movement based on LLM guidance
        try:
            new_location = [
                actor.location[0] + movement_offset[0],
                actor.location[1] + movement_offset[1], 
                actor.location[2] + movement_offset[2]
            ]
            
            actor.location = new_location
            
            # Record movement in history
            self.movement_history.append({
                "step": len(self.movement_history) + 1,
                "from": [round(x, 2) for x in actor.location],
                "to": [round(x, 2) for x in new_location],
                "direction": direction,
                "llm_reasoning": llm_analysis.get("reasoning", "No reasoning provided")
            })
            
            print(f"🎮 LLM Visual Nav: Moved {direction} → {[round(x, 2) for x in new_location]}")
            print(f"💭 LLM Reasoning: {llm_analysis.get('reasoning', 'No reasoning provided')}")
            
            return False  # Continue navigation
            
        except Exception as e:
            print(f"❌ LLM Visual Nav: Movement execution failed - {e}")
            return True  # Stop navigation on error
    
    def start_llm_navigation_to_room(self, actor, target_room: str, max_steps: int = 20):
        """
        Start LLM-driven navigation to target room
        """
        if not actor:
            print("❌ LLM Visual Nav: No actor provided")
            return False
        
        print(f"🚀 LLM Visual Navigation: Starting journey to {target_room}")
        print(f"🧠 Navigation Method: LLM visual analysis - NO hardcoded coordinates")
        print(f"📸 Bird's-eye view screenshots will guide each movement step")
        print()
        
        self.navigation_active = True
        self.current_target_room = target_room
        self.movement_history = []
        
        step_count = 0
        
        while step_count < max_steps and self.navigation_active:
            step_count += 1
            print(f"\n📍 LLM Navigation Step {step_count}/{max_steps}")
            
            # Execute one navigation step with LLM guidance
            navigation_complete = self.execute_navigation_step(actor, target_room)
            
            if navigation_complete:
                print(f"\n✅ LLM Visual Navigation Complete!")
                print(f"🎯 Target: {target_room}")
                print(f"📊 Total Steps: {step_count}")
                print(f"📍 Final Position: {[round(x, 2) for x in actor.location]}")
                break
            
            # Add small delay for visual feedback
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        
        if step_count >= max_steps:
            print(f"⚠️ LLM Navigation: Reached maximum steps ({max_steps})")
            
        self.navigation_active = False
        return step_count < max_steps
    
    def get_navigation_summary(self) -> dict:
        """
        Get summary of the navigation session
        """
        return {
            "llm_available": self.llm_available,
            "target_room": self.current_target_room,
            "total_steps": len(self.movement_history),
            "screenshot_count": self.screenshot_count,
            "movement_history": self.movement_history
        }

# Global navigator instance
llm_navigator = LLMVisualNavigator()

def start_llm_visual_navigation(actor_name: str, target_room: str):
    """
    Start LLM visual navigation for specified actor
    """
    # Find actor in scene
    actor = bpy.data.objects.get(actor_name)
    if not actor:
        print(f"❌ LLM Visual Nav: Actor '{actor_name}' not found in scene")
        return False
    
    # Start LLM-driven navigation
    success = llm_navigator.start_llm_navigation_to_room(actor, target_room)
    
    # Show navigation summary
    summary = llm_navigator.get_navigation_summary()
    print("\n📊 LLM VISUAL NAVIGATION SUMMARY:")
    print(f"   🎯 Target Room: {summary['target_room']}")
    print(f"   📈 Total Steps: {summary['total_steps']}")  
    print(f"   📸 Screenshots Analyzed: {summary['screenshot_count']}")
    print(f"   🧠 LLM Available: {summary['llm_available']}")
    
    return success

if __name__ == "__main__":
    print("🧠 LLM Visual Navigation System Loaded")
    print("📸 Ready for bird's-eye view analysis")
    print("🎯 NO hardcoded coordinates - Pure LLM guidance")
