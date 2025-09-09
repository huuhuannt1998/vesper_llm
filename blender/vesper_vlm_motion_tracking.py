"""
VESPER VLM Motion Tracking - Simplified Blender Addon
Focused on tracking VLM-controlled actor movement using virtual motion sensors
For CASAS dataset validation
"""

bl_info = {
    "name": "VESPER VLM Motion Tracking",
    "author": "VESPER Team", 
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > VLM Tracking",
    "description": "Track VLM-controlled actor movement with virtual motion sensors",
    "category": "System",
    "support": "COMMUNITY"
}

import bpy
import bpy.props
import bmesh
import time
import math
import json
import os
from mathutils import Vector
from datetime import datetime

# Try to import requests for motion sensor communication
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️ requests module not available. Install with: pip install requests")

# =============================================================================
# MOTION SENSOR MANAGER
# =============================================================================

class VLMMotionSensorManager:
    """Manages virtual motion sensors for VLM actor tracking"""
    
    def __init__(self):
        self.motion_sensors = {}
        self.tracking_data = []
        self.start_time = None
        self.backend_url = "http://localhost:8088"  # Backend console API
        
    def create_motion_sensor(self, room_name, location):
        """Create a virtual motion sensor in the specified room"""
        sensor_id = f"VSM-{room_name}-{int(time.time())}"
        
        # Create sensor cube object
        bpy.ops.mesh.primitive_cube_add(location=location)
        sensor_obj = bpy.context.active_object
        sensor_obj.name = f"MotionSensor_{sensor_id}"
        sensor_obj.scale = (0.2, 0.2, 0.2)
        
        # Set material to green
        mat = bpy.data.materials.new(name=f"MotionSensor_Mat_{sensor_id}")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.0, 0.8, 0.0, 1.0)
        sensor_obj.data.materials.append(mat)
        
        # Store sensor properties
        sensor_obj["vesper_device_type"] = "motion_sensor"
        sensor_obj["vesper_sensor_id"] = sensor_id
        sensor_obj["vesper_room"] = room_name
        sensor_obj["vesper_last_triggered"] = 0
        
        # Create detection area
        self._create_detection_area(sensor_obj, room_name)
        
        # Register with backend if available
        if REQUESTS_AVAILABLE:
            self._register_with_backend(sensor_id, room_name, location)
        
        self.motion_sensors[sensor_id] = {
            'object': sensor_obj,
            'room': room_name,
            'location': location,
            'active': False,
            'last_detection': None
        }
        
        print(f"✅ Created motion sensor {sensor_id} in {room_name}")
        return sensor_id
    
    def _create_detection_area(self, sensor_obj, room_name):
        """Create an invisible detection area around the motion sensor"""
        # Create detection area cube
        bpy.ops.mesh.primitive_cube_add(location=sensor_obj.location)
        detection_obj = bpy.context.active_object
        detection_obj.name = f"DetectionArea_{sensor_obj['vesper_sensor_id']}"
        detection_obj.scale = (2.0, 2.0, 0.5)  # Room-sized detection area
        
        # Make it wireframe and semi-transparent in editor
        detection_obj.display_type = 'WIRE'
        detection_obj.color = (0.0, 1.0, 0.0, 0.3)  # Green wireframe
        
        # BGE properties: Invisible in game engine but detectable
        detection_obj.game.use_collision_bounds = True
        detection_obj.game.collision_bounds_type = 'BOX'
        detection_obj.visible = False  # Invisible in BGE
        
        # Store relationship
        detection_obj["vesper_device_type"] = "detection_area"
        detection_obj["vesper_parent_sensor"] = sensor_obj["vesper_sensor_id"]
        sensor_obj["vesper_detection_area"] = detection_obj.name
        
        # Parent to sensor for easy movement
        detection_obj.parent = sensor_obj
        
        print(f"🔍 Created detection area for sensor {sensor_obj['vesper_sensor_id']}")
    
    def _register_with_backend(self, sensor_id, room_name, location):
        """Register motion sensor with backend console"""
        try:
            payload = {
                "device_type": "motion_sensor",
                "device_name": sensor_id,
                "room": room_name,
                "properties": {
                    "location": list(location),
                    "detection_range": 2.0,
                    "created_time": datetime.now().isoformat()
                }
            }
            
            response = requests.post(f"{self.backend_url}/devices", json=payload, timeout=5)
            if response.status_code == 200:
                print(f"✅ Registered {sensor_id} with backend")
            else:
                print(f"⚠️ Failed to register {sensor_id} with backend: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Backend registration failed for {sensor_id}: {e}")
    
    def start_tracking_session(self):
        """Start a new VLM tracking session"""
        self.start_time = time.time()
        self.tracking_data = []
        print(f"🎯 Started VLM motion tracking session at {datetime.now()}")
    
    def log_motion_event(self, sensor_id, actor_name, detected=True):
        """Log a motion detection event for dataset creation"""
        if self.start_time is None:
            self.start_tracking_session()
        
        timestamp = time.time() - self.start_time
        event = {
            'timestamp': timestamp,
            'sensor_id': sensor_id,
            'room': self.motion_sensors[sensor_id]['room'],
            'actor': actor_name,
            'detected': detected,
            'datetime': datetime.now().isoformat()
        }
        
        self.tracking_data.append(event)
        
        # Update sensor status
        self.motion_sensors[sensor_id]['active'] = detected
        self.motion_sensors[sensor_id]['last_detection'] = timestamp if detected else None
        
        # Update sensor color
        self._update_sensor_visual(sensor_id, detected)
        
        # Notify backend if available
        if REQUESTS_AVAILABLE:
            self._notify_backend(sensor_id, detected)
        
        print(f"📊 Motion {('detected' if detected else 'cleared')} - {sensor_id} in {self.motion_sensors[sensor_id]['room']}")
    
    def _update_sensor_visual(self, sensor_id, detected):
        """Update sensor visual state (green=inactive, red=detecting)"""
        sensor = self.motion_sensors[sensor_id]['object']
        if sensor and sensor.data.materials:
            material = sensor.data.materials[0]
            if detected:
                # Red when detecting
                material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (1.0, 0.0, 0.0, 1.0)
            else:
                # Green when inactive
                material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.0, 0.8, 0.0, 1.0)
    
    def _notify_backend(self, sensor_id, detected):
        """Send motion detection to backend console"""
        try:
            payload = {
                "sensor_id": sensor_id,
                "state": "motion_detected" if detected else "no_motion",
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(f"{self.backend_url}/motion/{sensor_id}", json=payload, timeout=2)
            if response.status_code != 200:
                print(f"⚠️ Backend notification failed for {sensor_id}")
                
        except Exception as e:
            print(f"⚠️ Backend notification error: {e}")
    
    def save_tracking_data(self, filename=None):
        """Save motion tracking data for CASAS comparison"""
        if not filename:
            filename = f"vlm_motion_tracking_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = os.path.join(bpy.path.abspath("//"), filename)
        
        session_data = {
            'session_start': datetime.fromtimestamp(self.start_time).isoformat() if self.start_time else None,
            'duration': time.time() - self.start_time if self.start_time else 0,
            'sensors': {sid: {'room': data['room'], 'location': list(data['location'])} 
                       for sid, data in self.motion_sensors.items()},
            'motion_events': self.tracking_data,
            'summary': {
                'total_events': len(self.tracking_data),
                'sensors_triggered': len(set(event['sensor_id'] for event in self.tracking_data)),
                'rooms_visited': len(set(event['room'] for event in self.tracking_data))
            }
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(session_data, f, indent=2)
            print(f"💾 Saved tracking data to {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ Failed to save tracking data: {e}")
            return None

# Global motion sensor manager
motion_manager = VLMMotionSensorManager()

# =============================================================================
# BGE MOTION DETECTION SYSTEM  
# =============================================================================

class BGEVLMMotionController:
    """BGE motion detection controller for VLM actor tracking"""
    
    def __init__(self):
        self.last_update = 0
        self.update_interval = 0.1  # Update every 0.1 seconds
        
    def update_motion_detection(self):
        """Called every frame from BGE to check actor-sensor collision"""
        current_time = time.time()
        if current_time - self.last_update < self.update_interval:
            return
        
        self.last_update = current_time
        
        try:
            # Import BGE modules (only available in game engine)
            import bge
            scene = bge.logic.getCurrentScene()
            
            # Find actor object (assuming it's named "Actor" or contains "actor")
            actor = None
            for obj in scene.objects:
                if "actor" in obj.name.lower() or obj.name == "Actor":
                    actor = obj
                    break
            
            if not actor:
                return
            
            # Check collision with detection areas
            for obj in scene.objects:
                if hasattr(obj, 'name') and 'DetectionArea_' in obj.name:
                    # Calculate distance between actor and detection area
                    distance = actor.worldPosition.distance(obj.worldPosition)
                    detection_radius = max(obj.localScale) * 1.5  # Rough collision detection
                    
                    # Extract sensor ID from detection area name
                    sensor_id = obj.name.replace('DetectionArea_', '')
                    
                    if distance < detection_radius:
                        # Motion detected
                        if sensor_id in motion_manager.motion_sensors:
                            if not motion_manager.motion_sensors[sensor_id]['active']:
                                motion_manager.log_motion_event(sensor_id, actor.name, detected=True)
                    else:
                        # No motion 
                        if sensor_id in motion_manager.motion_sensors:
                            if motion_manager.motion_sensors[sensor_id]['active']:
                                motion_manager.log_motion_event(sensor_id, actor.name, detected=False)
                                
        except ImportError:
            # BGE not available (running in Blender editor)
            pass
        except Exception as e:
            print(f"⚠️ BGE motion detection error: {e}")

# Global BGE controller
bge_controller = BGEVLMMotionController()

def bge_vlm_motion_update():
    """Main function to call from BGE Always sensor"""
    bge_controller.update_motion_detection()

# =============================================================================
# BLENDER OPERATORS
# =============================================================================

class VLM_OT_CreateMotionSensor(bpy.types.Operator):
    """Create a motion sensor for VLM tracking"""
    bl_idname = "vlm.create_motion_sensor"
    bl_label = "Create Motion Sensor"
    bl_description = "Create a virtual motion sensor with detection area"
    
    room_name: bpy.props.StringProperty(
        name="Room Name",
        description="Name of the room where the sensor is placed",
        default="living_room"
    )
    
    def execute(self, context):
        if not self.room_name:
            self.report({'ERROR'}, "Room name is required")
            return {'CANCELLED'}
        
        # Use cursor location or selected object location
        location = context.scene.cursor.location.copy()
        
        sensor_id = motion_manager.create_motion_sensor(self.room_name, location)
        self.report({'INFO'}, f"Created motion sensor {sensor_id} in {self.room_name}")
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class VLM_OT_StartTracking(bpy.types.Operator):
    """Start VLM motion tracking session"""
    bl_idname = "vlm.start_tracking"
    bl_label = "Start VLM Tracking"
    bl_description = "Begin tracking VLM-controlled actor movement"
    
    def execute(self, context):
        motion_manager.start_tracking_session()
        self.report({'INFO'}, "VLM tracking session started")
        return {'FINISHED'}

class VLM_OT_SaveTrackingData(bpy.types.Operator):
    """Save motion tracking data"""
    bl_idname = "vlm.save_tracking_data"
    bl_label = "Save Tracking Data"
    bl_description = "Save motion tracking data for CASAS comparison"
    
    def execute(self, context):
        filepath = motion_manager.save_tracking_data()
        if filepath:
            self.report({'INFO'}, f"Tracking data saved to {filepath}")
        else:
            self.report({'ERROR'}, "Failed to save tracking data")
        return {'FINISHED'}

class VLM_OT_SetupBGEController(bpy.types.Operator):
    """Setup BGE motion detection controller"""
    bl_idname = "vlm.setup_bge_controller"
    bl_label = "Setup BGE Controller"
    bl_description = "Create BGE controller for motion detection"
    
    def execute(self, context):
        # Create empty object as controller
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 5))
        controller = context.active_object
        controller.name = "VLM_MotionController"
        
        # Add BGE logic
        bpy.ops.logic.sensor_add(type='ALWAYS', name="AlwaysSensor")
        bpy.ops.logic.controller_add(type='PYTHON', name="MotionController")
        bpy.ops.logic.actuator_add(type='NULL', name="NullActuator")
        
        # Set up Python script
        if controller.game.sensors:
            sensor = controller.game.sensors["AlwaysSensor"]
            sensor.use_pulse_true_level = True
            sensor.frequency = 0  # Run every frame
            
        if controller.game.controllers:
            python_controller = controller.game.controllers["MotionController"]
            python_controller.mode = 'MODULE'
            python_controller.module = f"{__name__}.bge_vlm_motion_update"
            
        self.report({'INFO'}, "BGE motion controller created. Press P to test!")
        return {'FINISHED'}

class VLM_OT_CreateDemoScene(bpy.types.Operator):
    """Create a demo scene with actor and motion sensors"""
    bl_idname = "vlm.create_demo_scene"
    bl_label = "Create Demo Scene"
    bl_description = "Create a simple demo scene for VLM testing"
    
    def execute(self, context):
        # Clear existing scene
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        
        # Create floor
        bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
        floor = context.active_object
        floor.name = "Floor"
        
        # Create walls
        rooms = [
            ("living_room", (0, 0, 0)),
            ("kitchen", (8, 0, 0)),
            ("bedroom", (0, 8, 0)),
            ("bathroom", (8, 8, 0))
        ]
        
        # Create actor
        bpy.ops.mesh.primitive_cube_add(size=1.5, location=(0, 0, 1))
        actor = context.active_object
        actor.name = "Actor"
        actor.color = (0.0, 0.0, 1.0, 1.0)  # Blue
        
        # Create motion sensors in each room
        for room_name, location in rooms:
            sensor_location = Vector(location) + Vector((0, 0, 2))
            motion_manager.create_motion_sensor(room_name, sensor_location)
        
        # Setup BGE controller
        bpy.ops.vlm.setup_bge_controller()
        
        self.report({'INFO'}, "Demo scene created with 4 motion sensors")
        return {'FINISHED'}

# =============================================================================
# UI PANEL
# =============================================================================

class VLM_PT_MotionTrackingPanel(bpy.types.Panel):
    """VLM Motion Tracking Panel"""
    bl_label = "VLM Motion Tracking"
    bl_idname = "VLM_PT_motion_tracking"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'VLM Tracking'
    
    def draw(self, context):
        layout = self.layout
        
        # Header
        row = layout.row()
        row.label(text="🎯 VLM Motion Tracking", icon='TRACKER')
        
        # Status
        if not REQUESTS_AVAILABLE:
            box = layout.box()
            box.alert = True
            box.label(text="⚠️ Limited Mode", icon='ERROR')
            box.label(text="Install: pip install requests")
        
        # Sensor Creation
        box = layout.box()
        box.label(text="Motion Sensors", icon='RADIOBUT_ON')
        row = box.row()
        row.operator("vlm.create_motion_sensor", icon='ADD')
        
        # Show sensor count
        sensor_count = len(motion_manager.motion_sensors)
        box.label(text=f"Active Sensors: {sensor_count}")
        
        # Tracking Controls
        box = layout.box()
        box.label(text="VLM Tracking Session", icon='PLAY')
        
        row = box.row(align=True)
        row.operator("vlm.start_tracking", icon='PLAY')
        row.operator("vlm.save_tracking_data", icon='FILE_TICK')
        
        # Show session info
        if motion_manager.start_time:
            duration = time.time() - motion_manager.start_time
            box.label(text=f"Session: {duration:.1f}s")
            box.label(text=f"Events: {len(motion_manager.tracking_data)}")
        
        # BGE Setup
        box = layout.box()
        box.label(text="Game Engine Setup", icon='GAME')
        
        row = box.row(align=True)
        row.operator("vlm.setup_bge_controller", icon='SCRIPT')
        row.operator("vlm.create_demo_scene", icon='SCENE_DATA')
        
        # Instructions
        col = box.column()
        col.scale_y = 0.8
        col.label(text="💡 1. Create demo scene or add sensors", icon='INFO')
        col.label(text="💡 2. Setup BGE controller", icon='INFO')
        col.label(text="💡 3. Press P to start game engine", icon='INFO')
        col.label(text="💡 4. Move actor to test detection", icon='INFO')
        
        # Active Sensors Status
        if motion_manager.motion_sensors:
            layout.separator()
            box = layout.box()
            box.label(text="Sensor Status", icon='INFO')
            
            for sensor_id, data in motion_manager.motion_sensors.items():
                row = box.row()
                status_icon = 'RECORD_ON' if data['active'] else 'RECORD_OFF'
                status_text = "DETECTING" if data['active'] else "IDLE"
                row.label(text=f"{data['room']}: {status_text}", icon=status_icon)

# =============================================================================
# REGISTRATION
# =============================================================================

classes = [
    VLM_OT_CreateMotionSensor,
    VLM_OT_StartTracking, 
    VLM_OT_SaveTrackingData,
    VLM_OT_SetupBGEController,
    VLM_OT_CreateDemoScene,
    VLM_PT_MotionTrackingPanel
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    print("✅ VESPER VLM Motion Tracking v1.0 registered")
    print("   🎯 Focus: VLM actor movement validation")
    print("   📊 Purpose: CASAS dataset comparison")
    print("   🎮 Method: BGE motion sensor detection")

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    print("❌ VLM Motion Tracking unregistered")

if __name__ == "__main__":
    register()
