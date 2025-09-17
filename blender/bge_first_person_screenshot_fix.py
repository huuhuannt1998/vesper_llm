"""
BGE First-Person Screenshot Fix
==============================

This module provides alternative methods for capturing first-person screenshots
when the standard BGE screenshot method fails.
"""

import bge
import os
import time

def alternative_first_person_capture(camera_object, output_path, width=1024, height=768):
    """
    Alternative first-person capture method using BGE's offscreen rendering
    
    Args:
        camera_object: The first-person camera object
        output_path: Path where to save the screenshot
        width: Image width
        height: Image height
    
    Returns:
        bool: True if capture succeeded, False otherwise
    """
    
    print(f"🔧 BGE: Trying alternative first-person capture method...")
    
    try:
        scene = bge.logic.getCurrentScene()
        
        # Store original camera
        original_camera = scene.active_camera
        
        # Method 1: Try offscreen rendering if available
        try:
            if hasattr(bge.render, 'offScreenCreate'):
                print(f"📸 BGE: Attempting offscreen rendering...")
                
                # Create offscreen buffer
                offscreen = bge.render.offScreenCreate(width, height)
                
                # Set camera and render
                scene.active_camera = camera_object
                bge.render.offScreenDraw(offscreen, scene, camera_object)
                
                # Save to file
                bge.render.offScreenSave(offscreen, output_path)
                bge.render.offScreenDestroy(offscreen)
                
                # Restore original camera
                scene.active_camera = original_camera
                
                # Check if file was created
                if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                    print(f"✅ BGE: Offscreen capture successful: {output_path}")
                    return True
                else:
                    print(f"⚠️ BGE: Offscreen capture created empty file")
                    
        except Exception as e:
            print(f"⚠️ BGE: Offscreen rendering failed: {e}")
        
        # Method 2: Force viewport update and retry standard method
        try:
            print(f"🔄 BGE: Trying viewport refresh method...")
            
            scene.active_camera = camera_object
            
            # Force multiple viewport updates
            for i in range(3):
                bge.logic.getCurrentController().owner.worldPosition = bge.logic.getCurrentController().owner.worldPosition
                time.sleep(0.01)  # Small delay
            
            # Try screenshot with explicit flush
            bge.render.makeScreenshot(output_path)
            
            # Wait a moment for file system
            time.sleep(0.1)
            
            # Restore camera
            scene.active_camera = original_camera
            
            # Check result
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                print(f"✅ BGE: Viewport refresh capture successful: {output_path}")
                return True
            else:
                print(f"⚠️ BGE: Viewport refresh capture failed")
                
        except Exception as e:
            print(f"⚠️ BGE: Viewport refresh method failed: {e}")
        
        # Method 3: Copy from frame buffer if available
        try:
            print(f"📋 BGE: Trying frame buffer copy method...")
            
            scene.active_camera = camera_object
            
            # Force scene update
            scene.replace(scene)
            
            # Try to get pixel data directly (if bgl is available)
            try:
                import bgl
                
                # Get viewport size
                viewport = bgl.glGetIntegerv(bgl.GL_VIEWPORT)
                width, height = viewport[2], viewport[3]
                
                # Read pixels
                pixels = bgl.glReadPixels(0, 0, width, height, bgl.GL_RGB, bgl.GL_UNSIGNED_BYTE)
                
                # Convert to image (this would need PIL or similar)
                print(f"📸 BGE: Got pixel data: {len(pixels)} bytes")
                
                # For now, just indicate we got data
                scene.active_camera = original_camera
                return False  # Can't save without image library
                
            except ImportError:
                print(f"⚠️ BGE: bgl not available for pixel reading")
            except Exception as e:
                print(f"⚠️ BGE: Frame buffer copy failed: {e}")
        
        except Exception as e:
            print(f"⚠️ BGE: Frame buffer method failed: {e}")
        
        # Restore original camera
        scene.active_camera = original_camera
        
        print(f"❌ BGE: All alternative capture methods failed")
        return False
        
    except Exception as e:
        print(f"❌ BGE: Alternative capture error: {e}")
        return False

def diagnose_camera_capture_issue(camera_object):
    """
    Diagnose why camera capture might be failing
    
    Args:
        camera_object: The camera object to diagnose
    
    Returns:
        dict: Diagnostic information
    """
    
    print(f"🔍 BGE: Diagnosing camera capture issue for {camera_object.name}")
    
    diagnosis = {
        "camera_name": camera_object.name,
        "has_camera_data": False,
        "is_active": False,
        "position": None,
        "orientation": None,
        "issues": []
    }
    
    try:
        # Check camera data
        if hasattr(camera_object, 'camera'):
            diagnosis["has_camera_data"] = True
            print(f"✅ BGE: Camera has camera data")
        else:
            diagnosis["has_camera_data"] = False
            diagnosis["issues"].append("No camera data - object might not be a real camera")
            print(f"❌ BGE: Camera has NO camera data")
        
        # Check if it can be set as active
        scene = bge.logic.getCurrentScene()
        original_camera = scene.active_camera
        
        try:
            scene.active_camera = camera_object
            diagnosis["is_active"] = (scene.active_camera == camera_object)
            
            if diagnosis["is_active"]:
                print(f"✅ BGE: Camera can be set as active")
            else:
                diagnosis["issues"].append("Cannot be set as active camera")
                print(f"❌ BGE: Camera CANNOT be set as active")
            
            # Restore original
            scene.active_camera = original_camera
            
        except Exception as e:
            diagnosis["issues"].append(f"Error setting as active: {e}")
            print(f"❌ BGE: Error setting camera active: {e}")
        
        # Get position and orientation
        try:
            pos = camera_object.worldPosition
            orient = camera_object.worldOrientation
            diagnosis["position"] = [pos.x, pos.y, pos.z]
            diagnosis["orientation"] = orient.to_euler()
            print(f"📍 BGE: Camera position: [{pos.x:.2f}, {pos.y:.2f}, {pos.z:.2f}]")
        except Exception as e:
            diagnosis["issues"].append(f"Cannot get position/orientation: {e}")
            print(f"❌ BGE: Cannot get camera position: {e}")
        
        # Check camera properties
        if hasattr(camera_object, 'camera'):
            try:
                cam_data = camera_object.camera
                print(f"🎯 BGE: Camera type: {cam_data.type}")
                if hasattr(cam_data, 'lens'):
                    print(f"🔍 BGE: Camera lens: {cam_data.lens}")
                if hasattr(cam_data, 'clip_start'):
                    print(f"📏 BGE: Clip start: {cam_data.clip_start}")
                if hasattr(cam_data, 'clip_end'):
                    print(f"📏 BGE: Clip end: {cam_data.clip_end}")
            except Exception as e:
                diagnosis["issues"].append(f"Cannot read camera properties: {e}")
                print(f"⚠️ BGE: Cannot read camera properties: {e}")
        
        return diagnosis
        
    except Exception as e:
        diagnosis["issues"].append(f"Diagnosis failed: {e}")
        print(f"❌ BGE: Camera diagnosis failed: {e}")
        return diagnosis

def fix_first_person_camera_capture():
    """
    Main function to fix first-person camera capture issues
    """
    
    print(f"🔧 BGE: FIRST-PERSON CAMERA CAPTURE FIX")
    print("=" * 45)
    
    try:
        scene = bge.logic.getCurrentScene()
        
        # Find Actor and its first-person camera
        actor = scene.objects.get("Actor")
        if not actor:
            print(f"❌ BGE: Actor not found")
            return False
        
        # Find the first-person camera
        fp_camera = None
        if hasattr(actor, 'children'):
            for child in actor.children:
                if child.name == "Actor_FPCamera" or "FPCamera" in child.name:
                    fp_camera = child
                    break
        
        if not fp_camera:
            fp_camera = scene.objects.get("Actor_FPCamera")
        
        if not fp_camera:
            print(f"❌ BGE: No first-person camera found")
            return False
        
        print(f"✅ BGE: Found first-person camera: {fp_camera.name}")
        
        # Diagnose the camera
        diagnosis = diagnose_camera_capture_issue(fp_camera)
        
        if diagnosis["issues"]:
            print(f"🚨 BGE: Camera issues found:")
            for issue in diagnosis["issues"]:
                print(f"   - {issue}")
        
        # Try to fix common issues
        fixes_applied = []
        
        # Fix 1: Ensure camera has proper lens settings
        if hasattr(fp_camera, 'camera') and hasattr(fp_camera.camera, 'lens'):
            if fp_camera.camera.lens < 10 or fp_camera.camera.lens > 200:
                fp_camera.camera.lens = 50.0
                fixes_applied.append("Reset lens to 50mm")
        
        # Fix 2: Ensure camera is positioned correctly relative to Actor
        actor_pos = actor.worldPosition
        camera_pos = fp_camera.worldPosition
        distance = ((camera_pos.x - actor_pos.x)**2 + 
                   (camera_pos.y - actor_pos.y)**2 + 
                   (camera_pos.z - actor_pos.z)**2)**0.5
        
        if distance > 3.0:
            # Move camera to Actor position with eye-level offset
            fp_camera.worldPosition = [actor_pos.x, actor_pos.y, actor_pos.z + 1.7]
            fixes_applied.append(f"Repositioned camera from distance {distance:.2f} to Actor eye level")
        
        # Fix 3: Test capture
        test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "captures", "test")
        os.makedirs(test_dir, exist_ok=True)
        test_path = os.path.join(test_dir, "fp_camera_test.png")
        
        print(f"🧪 BGE: Testing capture to: {test_path}")
        
        # Try alternative capture method
        capture_success = alternative_first_person_capture(fp_camera, test_path)
        
        if capture_success:
            print(f"✅ BGE: First-person camera capture FIXED!")
            if fixes_applied:
                print(f"🔧 BGE: Applied fixes:")
                for fix in fixes_applied:
                    print(f"   - {fix}")
            return True
        else:
            print(f"❌ BGE: First-person camera capture still failing")
            print(f"💡 BGE: Consider:")
            print(f"   - Check if Actor_FPCamera is a real camera in Blender")
            print(f"   - Verify camera data block is assigned")
            print(f"   - Try recreating the camera")
            return False
        
    except Exception as e:
        print(f"❌ BGE: Fix attempt failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# Auto-run fix when imported
if __name__ == "__main__":
    fix_first_person_camera_capture()

print("✅ BGE First-Person Screenshot Fix loaded - call fix_first_person_camera_capture() to run")
