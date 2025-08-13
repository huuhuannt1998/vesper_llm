"""
Enhanced Bird's-Eye View Screenshot System for VESPER LLM

This module provides optimized screenshot capture with automatic ceiling management,
proper camera positioning, and clear actor visibility for LLM analysis.
"""

import bpy
import base64
import tempfile
import os

class BirdEyeViewCapture:
    """Enhanced bird's-eye view capture system for LLM analysis."""
    
    def __init__(self):
        self.camera_name = "BirdEyeCamera"
        self.ceilings_collection_name = "Ceilings"
        self.capture_height = 12.0
        self.lens_size = 35.0
        
    def setup_camera(self, actor_position=None):
        """Setup or update bird's-eye camera position."""
        
        camera = bpy.data.objects.get(self.camera_name)
        
        if not camera:
            # Create camera if it doesn't exist
            bpy.ops.object.camera_add()
            camera = bpy.context.active_object
            camera.name = self.camera_name
        
        # Position camera above actor or scene center
        if actor_position:
            camera.location = (actor_position[0], actor_position[1], self.capture_height)
        else:
            # Find actor automatically
            actor = bpy.data.objects.get('Actor')
            if actor:
                camera.location = (actor.location.x, actor.location.y, self.capture_height)
            else:
                camera.location = (0, 0, self.capture_height)
        
        # Point straight down
        camera.rotation_euler = (0, 0, 0)
        
        # Set camera properties
        camera_data = camera.data
        camera_data.lens = self.lens_size
        camera_data.sensor_width = 36
        
        # Set as active camera
        bpy.context.scene.camera = camera
        
        return camera
        
    def hide_ceilings(self):
        """Hide ceiling objects for clear bird's-eye view."""
        ceilings_collection = bpy.data.collections.get(self.ceilings_collection_name)
        
        if ceilings_collection:
            ceilings_collection.hide_viewport = True
            ceilings_collection.hide_render = True
            return True
        
        # Fallback: hide individual ceiling objects
        hidden_count = 0
        for obj in bpy.context.scene.objects:
            if 'ceiling' in obj.name.lower() and obj.type == 'MESH':
                obj.hide_viewport = True
                obj.hide_render = True
                hidden_count += 1
        
        return hidden_count > 0
    
    def show_ceilings(self):
        """Restore ceiling visibility after screenshot."""
        ceilings_collection = bpy.data.collections.get(self.ceilings_collection_name)
        
        if ceilings_collection:
            ceilings_collection.hide_viewport = False
            ceilings_collection.hide_render = False
            return True
        
        # Fallback: show individual ceiling objects
        shown_count = 0
        for obj in bpy.context.scene.objects:
            if 'ceiling' in obj.name.lower() and obj.type == 'MESH':
                obj.hide_viewport = False
                obj.hide_render = False
                shown_count += 1
        
        return shown_count > 0
    
    def capture_screenshot_b64(self, width=800, height=600):
        """Capture optimized bird's-eye view screenshot as base64."""
        
        try:
            # Setup camera
            actor = bpy.data.objects.get('Actor')
            actor_pos = [actor.location.x, actor.location.y] if actor else None
            camera = self.setup_camera(actor_pos)
            
            # Hide ceilings for clear view
            ceilings_hidden = self.hide_ceilings()
            
            # Update scene
            bpy.context.view_layer.update()
            
            # Set render settings for screenshot
            scene = bpy.context.scene
            original_width = scene.render.resolution_x
            original_height = scene.render.resolution_y
            original_camera = scene.camera
            
            scene.render.resolution_x = width
            scene.render.resolution_y = height  
            scene.camera = camera
            
            # Create temporary file for screenshot
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                temp_path = tmp_file.name
            
            # Render the screenshot
            scene.render.filepath = temp_path
            bpy.ops.render.render(write_still=True)
            
            # Read and encode the image
            with open(temp_path, 'rb') as f:
                image_data = f.read()
            
            b64_encoded = base64.b64encode(image_data).decode('ascii')
            
            # Clean up
            try:
                os.unlink(temp_path)
            except:
                pass
            
            # Restore original render settings
            scene.render.resolution_x = original_width
            scene.render.resolution_y = original_height
            scene.camera = original_camera
            
            # Restore ceiling visibility
            if ceilings_hidden:
                self.show_ceilings()
            
            return b64_encoded
            
        except Exception as e:
            print(f"Screenshot capture failed: {e}")
            
            # Ensure ceilings are restored on error
            try:
                self.show_ceilings()
            except:
                pass
            
            return None
    
    def get_view_info(self):
        """Get information about the current bird's-eye view setup."""
        
        camera = bpy.data.objects.get(self.camera_name)
        actor = bpy.data.objects.get('Actor')
        ceilings_collection = bpy.data.collections.get(self.ceilings_collection_name)
        
        info = {
            "camera_exists": camera is not None,
            "camera_position": list(camera.location) if camera else None,
            "actor_position": [actor.location.x, actor.location.y, actor.location.z] if actor else None,
            "ceilings_managed": ceilings_collection is not None,
            "ceiling_count": len(ceilings_collection.objects) if ceilings_collection else 0,
            "camera_height": self.capture_height,
            "lens_size": self.lens_size
        }
        
        return info

# Global instance for easy access
bird_eye_capture = BirdEyeViewCapture()

def capture_optimized_screenshot():
    """Convenience function to capture optimized screenshot."""
    return bird_eye_capture.capture_screenshot_b64()

def get_bird_eye_status():
    """Get current bird's-eye view system status."""
    return bird_eye_capture.get_view_info()
