"""
Enhanced Visual System for LLM-Controlled Actor
Provides clear visual markers and context for optimal LLM decision making.
"""

import bpy
import base64
import os
from typing import Dict, List, Tuple, Optional
import json

class EnhancedVisualSystem:
    """
    Enhanced visual system that makes the actor highly visible to LLM
    and provides clear contextual information for decision making.
    """
    
    def __init__(self):
        self.camera_name = "BirdEyeCamera"
        self.actor_name = "Actor" 
        self.indicator_name = "ActorIndicator"
        self.ground_marker_name = "ActorGroundMarker"
        
        # Room definitions for context
        self.rooms = {
            "Kitchen": {
                "center": [3.0, -1.0],
                "bounds": [[1.5, 4.5], [-2.5, 0.5]],
                "objects": ["stove", "refrigerator", "sink", "oven"]
            },
            "LivingRoom": {
                "center": [-2.0, 1.5],
                "bounds": [[-4.0, 0.0], [0.0, 3.0]],
                "objects": ["sofa", "tv", "table", "fireplace"]
            },
            "Bedroom": {
                "center": [-3.0, -2.0], 
                "bounds": [[-4.5, -1.5], [-3.5, -0.5]],
                "objects": ["bed", "dresser", "nightstand"]
            },
            "Bathroom": {
                "center": [1.0, 2.5],
                "bounds": [[0.0, 2.0], [2.0, 3.0]],
                "objects": ["toilet", "sink", "bathtub"]
            }
        }
    
    def capture_enhanced_screenshot(self, hide_ceilings: bool = True) -> Optional[str]:
        """
        Capture an enhanced bird's-eye screenshot optimized for LLM analysis.
        
        Args:
            hide_ceilings: Whether to hide ceiling objects for clearer view
            
        Returns:
            Base64 encoded screenshot or None if failed
        """
        try:
            print("📸 Capturing enhanced screenshot for LLM analysis...")
            
            # Get camera and actor
            camera = bpy.data.objects.get(self.camera_name)
            actor = bpy.data.objects.get(self.actor_name)
            
            if not camera or not actor:
                print(f"❌ Missing camera ({bool(camera)}) or actor ({bool(actor)})")
                return None
            
            # Store original settings
            original_camera = bpy.context.scene.camera
            original_resolution_x = bpy.context.scene.render.resolution_x
            original_resolution_y = bpy.context.scene.render.resolution_y
            
            # Hide ceilings if requested
            ceilings_collection = bpy.data.collections.get("Ceilings")
            original_ceiling_visibility = None
            if hide_ceilings and ceilings_collection:
                original_ceiling_visibility = ceilings_collection.hide_viewport
                ceilings_collection.hide_viewport = True
                print("🙈 Ceilings hidden for clear view")
            
            # Set up camera
            bpy.context.scene.camera = camera
            
            # Update camera position to follow actor
            camera.location.x = actor.location.x
            camera.location.y = actor.location.y
            # Keep camera high enough for full scene view
            camera.location.z = 20.0
            
            # Configure render settings for high quality
            scene = bpy.context.scene
            scene.render.resolution_x = 1024
            scene.render.resolution_y = 1024 
            scene.render.resolution_percentage = 100
            scene.render.image_settings.file_format = 'PNG'
            
            # Render the image
            bpy.ops.render.render(write_still=False)
            
            # Get the rendered image
            image = bpy.data.images['Render Result']
            
            # Save to temporary file
            temp_path = os.path.join(bpy.app.tempdir, "actor_view.png")
            image.save_render(filepath=temp_path)
            
            # Convert to base64
            with open(temp_path, "rb") as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            # Restore original settings
            bpy.context.scene.camera = original_camera
            scene.render.resolution_x = original_resolution_x
            scene.render.resolution_y = original_resolution_y
            
            # Restore ceiling visibility
            if original_ceiling_visibility is not None and ceilings_collection:
                ceilings_collection.hide_viewport = original_ceiling_visibility
                print("👁️ Ceilings visibility restored")
            
            print("✅ Enhanced screenshot captured successfully")
            return img_data
            
        except Exception as e:
            print(f"❌ Screenshot capture failed: {e}")
            return None
    
    def get_actor_context(self) -> Dict:
        """
        Get comprehensive context about the actor's current situation.
        
        Returns:
            Dictionary with actor position, current room, nearby objects, etc.
        """
        actor = bpy.data.objects.get(self.actor_name)
        if not actor:
            return {"error": "Actor not found"}
        
        # Get actor position
        pos = [round(actor.location.x, 2), round(actor.location.y, 2)]
        
        # Determine current room
        current_room = "Unknown"
        for room_name, room_data in self.rooms.items():
            bounds = room_data["bounds"]
            if (bounds[0][0] <= pos[0] <= bounds[0][1] and 
                bounds[1][0] <= pos[1] <= bounds[1][1]):
                current_room = room_name
                break
        
        # Find nearby objects
        nearby_objects = []
        scene_objects = bpy.context.scene.objects
        
        for obj in scene_objects:
            if obj.type == 'MESH' and obj != actor and not obj.name.startswith('Actor'):
                distance = ((obj.location.x - actor.location.x)**2 + 
                           (obj.location.y - actor.location.y)**2)**0.5
                
                if distance <= 3.0:  # Within 3 units
                    nearby_objects.append({
                        "name": obj.name,
                        "distance": round(distance, 1),
                        "position": [round(obj.location.x, 1), round(obj.location.y, 1)]
                    })
        
        # Sort by distance
        nearby_objects.sort(key=lambda x: x["distance"])
        
        # Calculate distances to room centers
        room_distances = {}
        for room_name, room_data in self.rooms.items():
            center = room_data["center"]
            distance = abs(center[0] - pos[0]) + abs(center[1] - pos[1])  # Manhattan distance
            room_distances[room_name] = round(distance, 1)
        
        return {
            "actor_position": pos,
            "current_room": current_room,
            "nearby_objects": nearby_objects[:5],  # Top 5 closest
            "room_distances": room_distances,
            "visual_markers": {
                "red_figure": "This is the ACTOR (your character to control)",
                "yellow_marker": "Floating indicator above actor",
                "green_circle": "Ground position marker below actor"
            },
            "rooms_available": list(self.rooms.keys())
        }
    
    def generate_llm_prompt(self, task: str, screenshot_b64: str) -> str:
        """
        Generate a comprehensive prompt for the LLM with visual context.
        
        Args:
            task: The task the actor should accomplish
            screenshot_b64: Base64 encoded screenshot
            
        Returns:
            Complete prompt string for LLM
        """
        context = self.get_actor_context()
        
        prompt = f"""
# VESPER Virtual Character Control

## TASK: {task}

## CURRENT SITUATION:
- **Actor Position**: {context['actor_position']} 
- **Current Room**: {context['current_room']}
- **Nearby Objects**: {', '.join([obj['name'] for obj in context['nearby_objects'][:3]])}

## VISUAL MARKERS (what you see in the image):
🔴 **BRIGHT RED FIGURE** = The ACTOR (your character to control)
🟡 **YELLOW MARKER** = Floating above actor (shows height/presence)  
🟢 **GREEN CIRCLE** = Ground position (shows exact floor location)

## AVAILABLE ROOMS & DISTANCES:
{chr(10).join([f"- **{room}**: {dist} units away" for room, dist in context['room_distances'].items()])}

## MOVEMENT OPTIONS:
- **UP**: Move north (+Y direction)
- **DOWN**: Move south (-Y direction)  
- **LEFT**: Move west (-X direction)
- **RIGHT**: Move east (+X direction)

## INSTRUCTIONS:
1. Look at the bird's-eye view image
2. Identify the bright RED figure (that's the actor you control)
3. See the GREEN circle showing exact ground position
4. Determine the best direction to move toward your goal
5. Choose ONE direction: UP, DOWN, LEFT, or RIGHT

## YOUR RESPONSE FORMAT:
```json
{{
    "reasoning": "I can see the red actor at position [X,Y]. To reach [goal], I need to move [direction] because...",
    "direction": "UP|DOWN|LEFT|RIGHT", 
    "confidence": 0.8,
    "next_action": "Brief description of what should happen next"
}}
```

Analyze the image and decide the best move!
"""
        
        return prompt.strip()
    
    def test_visual_system(self):
        """Test the complete visual system."""
        print("🧪 TESTING ENHANCED VISUAL SYSTEM")
        print("=" * 35)
        
        # Check all components
        actor = bpy.data.objects.get(self.actor_name)
        camera = bpy.data.objects.get(self.camera_name)
        indicator = bpy.data.objects.get(self.indicator_name)
        ground_marker = bpy.data.objects.get(self.ground_marker_name)
        
        components = {
            "Actor": actor,
            "Camera": camera,
            "Yellow Indicator": indicator,
            "Green Ground Marker": ground_marker
        }
        
        print("📋 Component Status:")
        all_good = True
        for name, obj in components.items():
            if obj:
                print(f"   ✅ {name}: Found")
            else:
                print(f"   ❌ {name}: Missing") 
                all_good = False
        
        if all_good:
            # Test context generation
            context = self.get_actor_context()
            print(f"\n📍 Actor Context:")
            print(f"   Position: {context['actor_position']}")
            print(f"   Room: {context['current_room']}")
            print(f"   Nearby: {len(context['nearby_objects'])} objects")
            
            # Test screenshot capture
            print(f"\n📸 Testing Screenshot Capture...")
            screenshot = self.capture_enhanced_screenshot()
            
            if screenshot:
                print(f"   ✅ Screenshot captured ({len(screenshot)} bytes)")
                print(f"   🧠 Ready for LLM analysis")
                
                # Generate sample prompt
                sample_task = "Go to the kitchen to make coffee"
                prompt = self.generate_llm_prompt(sample_task, screenshot)
                print(f"\n📝 Sample LLM Prompt Generated:")
                print(f"   Length: {len(prompt)} characters")
                print(f"   Includes: Visual markers, context, clear instructions")
                
                return True
            else:
                print(f"   ❌ Screenshot capture failed")
                return False
        else:
            print(f"\n❌ Missing components - please run setup first")
            return False

# Create global instance
visual_system = EnhancedVisualSystem()

if __name__ == "__main__":
    # Test the system
    visual_system.test_visual_system()
