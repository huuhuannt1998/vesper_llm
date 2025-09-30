#!/usr/bin/env python3
"""
Clean Motion Detection Integration for BGE Navigation
Fixes the import issues and removes fallback code for cleaner testing.
"""

def update_motion_detection_clean(final_pos):
    """
    Clean motion detection update without fallbacks
    """
    try:
        import bge
        scene = bge.logic.getCurrentScene()
        current_room = "UNKNOWN"
        
        # Try to import the VESPER smart home addon properly
        try:
            import sys
            import os
            
            # Add the correct addon path
            addon_path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "UPBGE", "Blender", "4.4", "scripts", "addons", "vesper_smart_home")
            if addon_path not in sys.path:
                sys.path.append(addon_path)
            
            # Import motion detection functions from the vesper_smart_home addon module
            import vesper_smart_home
            from vesper_smart_home import update_motion_detection, get_motion_detection_status, initialize_motion_detection
            
            print(f"✅ Motion detection addon imported successfully")
            
            # Initialize if needed (this is safe to call multiple times)
            if not hasattr(bge.logic, 'motion_detection_initialized'):
                initialize_motion_detection()
                bge.logic.motion_detection_initialized = True
                print("🔍 Motion detection system initialized")
            
            # Update motion detection - this checks if actor entered/left detection areas  
            update_motion_detection()
            
            # Get current motion detection status
            motion_status = get_motion_detection_status()
            if motion_status:
                sensors_detecting = motion_status.get('sensors_detecting', 0)
                if sensors_detecting > 0:
                    current_room = motion_status.get('current_room', 'unknown').upper()
                    print(f"🏠 Motion detection room: {current_room}")
                    
                    # Log each active sensor and sync with Docker
                    for sensor_id, sensor_data in motion_status.get('sensors', {}).items():
                        if sensor_data.get('detecting', False):
                            casas_id = "M01" if sensor_id == "motion1" else "M02" if sensor_id == "motion2" else sensor_id.upper()
                            room_name = sensor_data.get('room_name', 'unknown').upper()
                            print(f"  📍 {casas_id} ({sensor_id}) ACTIVE in {room_name}")
                            
                            # Sync with appropriate Docker container
                            try:
                                import requests
                                from datetime import datetime, timezone
                                
                                position_data = {
                                    "x": float(final_pos.x),
                                    "y": float(final_pos.y), 
                                    "timestamp": datetime.now(timezone.utc).isoformat(),
                                    "room": room_name,
                                    "casas_sensor_id": casas_id
                                }
                                
                                docker_port = 9000 if casas_id == 'M01' else 9001
                                docker_url = f"http://localhost:{docker_port}/actor_position"
                                response = requests.post(docker_url, json=position_data, timeout=1)
                                if response.status_code == 200:
                                    print(f"🔄 Docker {casas_id} synced: [{final_pos.x:.2f}, {final_pos.y:.2f}] in {room_name}")
                                else:
                                    print(f"⚠️ Docker {casas_id} sync failed: HTTP {response.status_code}")
                            except Exception as sync_error:
                                print(f"⚠️ Docker {casas_id} sync failed: {sync_error}")
                            
                            # Override current_room with detected room
                            current_room = room_name
                else:
                    print(f"🔍 Motion detection: No sensors detecting at position [{final_pos.x:.2f}, {final_pos.y:.2f}]")
                            
        except ImportError as import_error:
            print(f"❌ Motion detection addon import failed: {import_error}")
            print(f"   Expected addon at: {addon_path}")
            print(f"   Please ensure the vesper_smart_home addon is properly installed")
            raise  # Re-raise to make the issue clear for testing
                    
        return current_room
        
    except Exception as e:
        print(f"❌ Motion detection update error: {e}")
        import traceback
        traceback.print_exc()
        raise  # Re-raise to make issues clear for testing

if __name__ == "__main__":
    print("Motion detection integration module loaded")