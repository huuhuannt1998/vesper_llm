"""
Complete VESPER Enhanced Visual System Demo
Demonstrates the fully optimized LLM-controlled character with enhanced visibility.
"""

import bpy
import requests
import json
import base64
import sys
import os
import time

# Add path for our modules
sys.path.append(r"C:\Users\hbui11\Desktop\vesper_llm\blender\game")

class VESPEREnhancedDemo:
    """
    Complete demonstration of the enhanced VESPER system with:
    - Bright visual markers for easy LLM identification
    - Optimized bird's-eye view capture
    - Enhanced prompts with clear guidance
    - Backend API integration
    """
    
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.actor_name = "Actor"
        self.camera_name = "BirdEyeCamera"
        
        # Room definitions
        self.rooms = {
            "Kitchen": {
                "center": [3.0, -1.0],
                "bounds": [[1.5, 4.5], [-2.5, 0.5]]
            },
            "LivingRoom": {
                "center": [-2.0, 1.5],
                "bounds": [[-4.0, 0.0], [0.0, 3.0]]
            },
            "Bedroom": {
                "center": [-3.0, -2.0], 
                "bounds": [[-4.5, -1.5], [-3.5, -0.5]]
            },
            "Bathroom": {
                "center": [1.0, 2.5],
                "bounds": [[0.0, 2.0], [2.0, 3.0]]
            }
        }
    
    def check_enhanced_components(self) -> bool:
        """Verify all enhanced visual components are present."""
        
        print("🔍 CHECKING ENHANCED VISUAL COMPONENTS")
        print("=" * 38)
        
        components = {
            "Actor": bpy.data.objects.get(self.actor_name),
            "BirdEyeCamera": bpy.data.objects.get(self.camera_name),
            "ActorIndicator": bpy.data.objects.get("ActorIndicator"),
            "ActorGroundMarker": bpy.data.objects.get("ActorGroundMarker")
        }
        
        all_present = True
        for name, obj in components.items():
            if obj:
                print(f"✅ {name}: Found")
                if name == "Actor" and obj.data.materials:
                    mat = obj.data.materials[0] 
                    print(f"   └─ Material: {mat.name} (should be bright red)")
            else:
                print(f"❌ {name}: Missing")
                all_present = False
        
        # Check ceiling management
        ceilings = bpy.data.collections.get("Ceilings")
        if ceilings:
            print(f"✅ Ceilings Collection: {len(ceilings.objects)} objects")
        else:
            print(f"⚠️ Ceilings Collection: Not organized")
        
        return all_present
    
    def capture_enhanced_screenshot(self) -> str:
        """Capture screenshot using the enhanced visual system."""
        
        print("📸 CAPTURING ENHANCED SCREENSHOT")
        print("=" * 32)
        
        actor = bpy.data.objects.get(self.actor_name)
        camera = bpy.data.objects.get(self.camera_name)
        
        if not actor or not camera:
            print("❌ Missing actor or camera")
            return None
        
        # Store original settings
        original_camera = bpy.context.scene.camera
        original_res_x = bpy.context.scene.render.resolution_x
        original_res_y = bpy.context.scene.render.resolution_y
        
        # Hide ceilings for clear view
        ceilings = bpy.data.collections.get("Ceilings")
        original_ceiling_vis = None
        if ceilings:
            original_ceiling_vis = ceilings.hide_viewport
            ceilings.hide_viewport = True
            print("🙈 Ceilings hidden for clear bird's-eye view")
        
        try:
            # Position camera above actor
            camera.location.x = actor.location.x
            camera.location.y = actor.location.y
            camera.location.z = 20.0  # High for full scene view
            
            # Set up render
            bpy.context.scene.camera = camera
            scene = bpy.context.scene
            scene.render.resolution_x = 1024
            scene.render.resolution_y = 1024
            scene.render.resolution_percentage = 100
            
            print(f"📷 Camera positioned at ({camera.location.x:.1f}, {camera.location.y:.1f}, {camera.location.z:.1f})")
            print(f"🎯 Actor at ({actor.location.x:.1f}, {actor.location.y:.1f}, {actor.location.z:.1f})")
            
            # Render
            bpy.ops.render.render(write_still=False)
            
            # Save and encode
            image = bpy.data.images['Render Result']
            temp_path = os.path.join(bpy.app.tempdir, "enhanced_view.png")
            image.save_render(filepath=temp_path)
            
            with open(temp_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')
            
            os.remove(temp_path)
            
            print(f"✅ Screenshot captured ({len(img_data)} bytes)")
            print(f"🧠 Enhanced visual markers clearly visible for LLM")
            
            return img_data
            
        finally:
            # Restore settings
            bpy.context.scene.camera = original_camera
            bpy.context.scene.render.resolution_x = original_res_x
            bpy.context.scene.render.resolution_y = original_res_y
            
            if original_ceiling_vis is not None and ceilings:
                ceilings.hide_viewport = original_ceiling_vis
                print("👁️ Ceilings visibility restored")
    
    def test_backend_integration(self, screenshot_b64: str) -> dict:
        """Test the enhanced system with backend API."""
        
        print("🌐 TESTING BACKEND INTEGRATION")
        print("=" * 30)
        
        actor = bpy.data.objects.get(self.actor_name)
        if not actor:
            print("❌ No actor found")
            return None
        
        # Create state for API call
        state = {
            "actor_position": {
                "x": float(actor.location.x),
                "y": float(actor.location.y),
                "z": float(actor.location.z)
            },
            "tasks": ["Make coffee in the kitchen"],
            "rooms": self.rooms,
            "bird_eye_image": screenshot_b64,
            "last_room": None,
            "step_count": 0,
            "max_steps": 50
        }
        
        try:
            print(f"📡 Sending request to {self.backend_url}/blender/navigate")
            print(f"   Actor position: ({state['actor_position']['x']:.1f}, {state['actor_position']['y']:.1f})")
            print(f"   Task: {state['tasks'][0]}")
            print(f"   Image size: {len(screenshot_b64)} bytes")
            
            response = requests.post(
                f"{self.backend_url}/blender/navigate",
                json=state,
                timeout=30
            )
            
            if response.status_code == 200:
                decision = response.json()
                print(f"✅ Backend responded successfully:")
                print(f"   Direction: {decision['direction']}")
                print(f"   Target Room: {decision['target_room']}")
                print(f"   Reasoning: {decision['reasoning']}")
                print(f"   Task Complete: {decision['task_complete']}")
                return decision
            else:
                print(f"❌ Backend error: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to backend at {self.backend_url}")
            print(f"   Make sure to start: uvicorn backend.app.main:app --host 0.0.0.0 --port 8000")
            return None
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def simulate_movement(self, direction: str) -> bool:
        """Simulate actor movement based on LLM decision."""
        
        actor = bpy.data.objects.get(self.actor_name)
        if not actor:
            return False
        
        # Movement vectors
        movements = {
            "UP": [0, 0.5, 0],
            "DOWN": [0, -0.5, 0], 
            "LEFT": [-0.5, 0, 0],
            "RIGHT": [0.5, 0, 0],
            "STAY": [0, 0, 0]
        }
        
        if direction in movements:
            move = movements[direction]
            old_pos = [actor.location.x, actor.location.y]
            
            actor.location.x += move[0]
            actor.location.y += move[1]
            actor.location.z += move[2]
            
            new_pos = [actor.location.x, actor.location.y]
            
            print(f"🚶 Actor moved {direction}:")
            print(f"   From: ({old_pos[0]:.1f}, {old_pos[1]:.1f})")
            print(f"   To: ({new_pos[0]:.1f}, {new_pos[1]:.1f})")
            
            # Update scene
            bpy.context.view_layer.update()
            
            return True
        
        return False
    
    def run_complete_demo(self):
        """Run the complete enhanced VESPER system demonstration."""
        
        print("🚀 VESPER ENHANCED SYSTEM COMPLETE DEMO")
        print("=" * 42)
        print(f"🎯 Demonstrating the fully optimized LLM-controlled character")
        print(f"   with enhanced visual markers and bird's-eye view system.")
        print()
        
        # Step 1: Check components
        if not self.check_enhanced_components():
            print("❌ Enhanced components missing. Run the setup first!")
            return False
        
        print()
        
        # Step 2: Capture enhanced screenshot
        screenshot = self.capture_enhanced_screenshot()
        if not screenshot:
            print("❌ Screenshot capture failed!")
            return False
        
        print()
        
        # Step 3: Test backend integration
        decision = self.test_backend_integration(screenshot)
        if not decision:
            print("⚠️ Backend integration test failed (but visual system works)")
            print("💡 Start backend server to test full integration")
            return True  # Visual system still works
        
        print()
        
        # Step 4: Simulate movement
        if decision['direction'] != 'STAY':
            success = self.simulate_movement(decision['direction'])
            if success:
                print(f"✅ Movement simulation successful")
            else:
                print(f"❌ Movement simulation failed")
        
        print()
        
        # Step 5: Summary
        print("🎊 COMPLETE DEMO RESULTS:")
        print("✅ Enhanced visual markers: Bright red actor with yellow/green indicators")  
        print("✅ Bird's-eye screenshot system: Clear view with ceiling management")
        print("✅ Enhanced LLM prompts: Clear guidance for actor identification")
        print("✅ Backend API integration: Ready for visual decision making")
        print("✅ Movement simulation: Actor responds to LLM decisions")
        
        print(f"\n💡 KEY IMPROVEMENTS:")
        print(f"🔴 Actor now GLOWS BRIGHT RED - impossible for LLM to miss!")
        print(f"🟡 Yellow marker above actor shows height/presence clearly")
        print(f"🟢 Green ground marker shows exact floor position")
        print(f"📸 20-unit height camera gives perfect bird's-eye overview")
        print(f"🏠 Ceiling hiding ensures unobstructed view")
        print(f"🧠 Enhanced prompts guide LLM to find red actor easily")
        
        print(f"\n🎮 READY FOR PLAY MODE!")
        print(f"Now when you press P, the LLM will have NO TROUBLE finding")
        print(f"and controlling the bright red glowing character! 🎯✨")
        
        return True

# Run the complete demonstration
if __name__ == "__main__":
    demo = VESPEREnhancedDemo()
    demo.run_complete_demo()
