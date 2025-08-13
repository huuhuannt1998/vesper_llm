"""
Enhanced Visual System - Recovered Version
Complete recreation of the enhanced visual system for LLM control.
"""

import bpy
import base64
import os
from typing import Dict, List, Optional
import json

class EnhancedVisualSystemRecovered:
    """
    Recovered enhanced visual system with open-top design.
    Optimized for perfect LLM visibility and control.
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
    
    def capture_optimized_screenshot(self) -> Optional[str]:
        """
        Capture optimized screenshot with open-top design.
        No ceiling management needed - permanently clear view!
        """
        try:
            print("📸 Capturing optimized screenshot (open-top design)...")
            
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
            
            # Position camera above actor for optimal view
            camera.location.x = actor.location.x
            camera.location.y = actor.location.y
            camera.location.z = 20.0  # High for complete scene overview
            
            # Set up render settings
            bpy.context.scene.camera = camera
            scene = bpy.context.scene
            scene.render.resolution_x = 1024
            scene.render.resolution_y = 1024
            scene.render.resolution_percentage = 100
            scene.render.image_settings.file_format = 'PNG'
            
            print(f"📷 Camera positioned at ({camera.location.x:.1f}, {camera.location.y:.1f}, {camera.location.z:.1f})")
            print(f"🎯 Actor at ({actor.location.x:.1f}, {actor.location.y:.1f}, {actor.location.z:.1f})")
            
            # Render the image
            bpy.ops.render.render(write_still=False)
            
            # Get rendered image and save
            image = bpy.data.images['Render Result']
            temp_path = os.path.join(bpy.app.tempdir, "vesper_view.png")
            image.save_render(filepath=temp_path)
            
            # Convert to base64
            with open(temp_path, "rb") as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
            
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            # Restore original settings
            bpy.context.scene.camera = original_camera
            scene.render.resolution_x = original_resolution_x
            scene.render.resolution_y = original_resolution_y
            
            print(f"✅ Screenshot captured successfully ({len(img_data)} bytes)")
            print(f"🏠 Open-top design provides perfect unobstructed view!")
            
            return img_data
            
        except Exception as e:
            print(f"❌ Screenshot capture failed: {e}")
            return None
    
    def get_actor_context(self) -> Dict:
        """Get comprehensive context about actor's current situation."""
        
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
        for obj in bpy.context.scene.objects:
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
        
        # Calculate room distances
        room_distances = {}
        for room_name, room_data in self.rooms.items():
            center = room_data["center"]
            distance = abs(center[0] - pos[0]) + abs(center[1] - pos[1])
            room_distances[room_name] = round(distance, 1)
        
        return {
            "actor_position": pos,
            "current_room": current_room,
            "nearby_objects": nearby_objects[:5],
            "room_distances": room_distances,
            "visual_markers": {
                "red_figure": "BRIGHT RED GLOWING ACTOR (your character)",
                "yellow_marker": "Floating indicator above actor",  
                "green_circle": "Ground position marker below actor"
            },
            "rooms_available": list(self.rooms.keys()),
            "design_note": "Open-top house design - no ceiling obstruction!"
        }
    
    def generate_enhanced_llm_prompt(self, task: str, screenshot_b64: str) -> str:
        """Generate enhanced prompt for LLM with open-top design context."""
        
        context = self.get_actor_context()
        
        prompt = f"""
# VESPER Enhanced Virtual Character Control - OPEN-TOP DESIGN

## CURRENT TASK: {task}

## ACTOR STATUS:
- **Position**: {context['actor_position']}
- **Current Room**: {context['current_room']}
- **Nearby Objects**: {', '.join([obj['name'] for obj in context['nearby_objects'][:3]])}

## 🎯 ENHANCED VISUAL MARKERS (Crystal Clear in Open-Top Design):

🔴 **BRIGHT RED GLOWING FIGURE** = The ACTOR you must control
   - Emits intense red light, impossible to miss
   - This is your character that needs to move

🟡 **YELLOW FLOATING MARKER** = Height indicator above red actor
   - Floats 2.5 units above the actor
   - Confirms actor location from bird's-eye view

🟢 **GREEN GLOWING CIRCLE** = Ground position marker
   - Shows exact floor position beneath actor
   - Marks where actor is standing

## 🏠 OPEN-TOP HOUSE ADVANTAGE:
✨ **PERFECT VISIBILITY**: No ceilings to obstruct the view!
📸 **CRYSTAL CLEAR**: Unobstructed bird's-eye perspective
🎯 **ZERO CONFUSION**: Red actor stands out against open rooms

## AVAILABLE ROOMS & DISTANCES:
{chr(10).join([f"- **{room}**: {dist} units away" for room, dist in context['room_distances'].items()])}

## MOVEMENT DIRECTIONS:
- **UP**: Move north (+Y direction)
- **DOWN**: Move south (-Y direction)
- **LEFT**: Move west (-X direction)  
- **RIGHT**: Move east (+X direction)
- **STAY**: Don't move (if at target or blocked)

## DECISION PROCESS:
1. 🔍 **LOCATE RED ACTOR**: Find the bright red glowing figure
2. 🎯 **IDENTIFY GOAL**: Which room is needed for the task?
3. 🧭 **CHOOSE PATH**: What direction moves red actor closer?
4. ✅ **EXECUTE**: Move toward completing the task

## RESPONSE FORMAT:
```json
{{
    "reasoning": "I can see the bright red actor at [position]. The open-top design gives perfect visibility. To reach [goal] for [task], I need to move [direction] because...",
    "direction": "UP|DOWN|LEFT|RIGHT|STAY",
    "confidence": 0.9,
    "next_action": "Brief description of what should happen next"
}}
```

The open-top design eliminates ALL visual obstruction - analyze and guide the red actor!
"""
        
        return prompt.strip()
    
    def test_recovered_system(self):
        """Test the complete recovered system."""
        
        print("🧪 TESTING RECOVERED ENHANCED SYSTEM")
        print("=" * 36)
        
        # Check all components
        components = {
            "Actor": bpy.data.objects.get(self.actor_name),
            "BirdEyeCamera": bpy.data.objects.get(self.camera_name),
            "Yellow Indicator": bpy.data.objects.get(self.indicator_name),
            "Green Ground Marker": bpy.data.objects.get(self.ground_marker_name)
        }
        
        print("📋 Component Status:")
        all_good = True
        for name, obj in components.items():
            if obj:
                print(f"   ✅ {name}: Found and functional")
            else:
                print(f"   ❌ {name}: Missing")
                all_good = False
        
        if all_good:
            # Test screenshot system
            print(f"\n📸 Testing Screenshot System...")
            screenshot = self.capture_optimized_screenshot()
            
            if screenshot:
                print(f"   ✅ Screenshot captured: {len(screenshot)} bytes")
                print(f"   🏠 Open-top design: Perfect unobstructed view")
                
                # Test context generation
                context = self.get_actor_context()
                print(f"\n📍 Actor Context:")
                print(f"   Position: {context['actor_position']}")
                print(f"   Room: {context['current_room']}")
                print(f"   Design: {context['design_note']}")
                
                # Generate sample prompt
                sample_task = "Go to the kitchen and make coffee"
                prompt = self.generate_enhanced_llm_prompt(sample_task, screenshot)
                print(f"\n📝 Enhanced Prompt Generated:")
                print(f"   Length: {len(prompt)} characters")
                print(f"   Features: Open-top design context, enhanced markers")
                
                return True
            else:
                print(f"   ❌ Screenshot capture failed")
        
        return False

# Create global instance for easy use
enhanced_visual = EnhancedVisualSystemRecovered()

# Test on import
if __name__ == "__main__":
    enhanced_visual.test_recovered_system()
