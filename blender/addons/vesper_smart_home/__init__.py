"""
VESPER Smart Home Integration - Blender Addon
Integrates Blender 3D environment with Docker-hosted virtual smart devices
"""

bl_info = {
    "name": "VESPER Smart Home Integration",
    "author": "VESPER Team",
    "version": (2, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > VESPER Smart Home",
    "description": "Control Docker-hosted virtual smart devices from Blender",
    "category": "System",
    "support": "COMMUNITY"
}

import bpy
import bpy.props
from mathutils import Vector

# Try to import requests, handle gracefully if not available
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print(" requests module not available. Install with: pip install requests")

# =============================================================================
# DEVICE MANAGEMENT CLASSES
# =============================================================================

class DeviceManager:
    """Manages communication with Docker-hosted virtual devices"""
    
    def __init__(self):
        self.base_urls = {
            "motion": "http://localhost:8001",
            "item": "http://localhost:8002", 
            "appliance": "http://localhost:8003",
            "dataset": "http://localhost:8004"
        }
        self.device_registry = {}
    
    def check_services_health(self):
        """Check if all Docker services are running"""
        if not REQUESTS_AVAILABLE:
            return {"error": "requests module not available"}
            
        health_status = {}
        for service, url in self.base_urls.items():
            try:
                response = requests.get(f"{url}/health", timeout=5)
                health_status[service] = response.status_code == 200
            except Exception as e:
                health_status[service] = False
                print(f"Service {service} check failed: {e}")
        return health_status
    
    def add_motion_sensor(self, sensor_id: str, room: str, position: Vector) -> bool:
        """Add a motion sensor to the virtual environment"""
        if not REQUESTS_AVAILABLE:
            print(" requests module required for Docker communication")
            return False
            
        try:
            data = {
                "detection_zone": {
                    "x": position.x,
                    "y": position.y,
                    "radius": 2.0
                },
                "room_location": room,
                "sensitivity": 1.0,
                "cooldown_period": 2.0
            }
            response = requests.post(f"{self.base_urls['motion']}/configure", json=data, timeout=10)
            if response.status_code == 200:
                self.device_registry[sensor_id] = {
                    "type": "motion",
                    "room": room,
                    "position": position,
                    "state": "inactive"
                }
                print(f" Added motion sensor {sensor_id} in {room}")
                return True
        except Exception as e:
            print(f" Failed to add motion sensor: {e}")
        return False
    
    def add_item_sensor(self, sensor_id: str, item_name: str, position: Vector) -> bool:
        """Add an item sensor to track objects"""
        if not REQUESTS_AVAILABLE:
            print(" requests module required for Docker communication")
            return False
            
        try:
            data = {
                "sensor_id": sensor_id,
                "item_name": item_name,
                "position": [position.x, position.y, position.z],
                "state": "present"
            }
            response = requests.post(f"{self.base_urls['item']}/items", json=data, timeout=10)
            if response.status_code == 200:
                self.device_registry[sensor_id] = {
                    "type": "item",
                    "item_name": item_name,
                    "position": position,
                    "state": "present"
                }
                print(f" Added item sensor {sensor_id} for {item_name}")
                return True
        except Exception as e:
            print(f" Failed to add item sensor: {e}")
        return False
    
    def trigger_motion_sensor(self, sensor_id: str, state: str = "active") -> bool:
        """Trigger a motion sensor"""
        if not REQUESTS_AVAILABLE:
            return False
            
        try:
            data = {"motion": state}
            response = requests.post(f"{self.base_urls['motion']}/manual_trigger", json=data, timeout=10)
            if response.status_code == 200:
                if sensor_id in self.device_registry:
                    self.device_registry[sensor_id]["state"] = state
                return True
        except Exception as e:
            print(f" Failed to trigger motion sensor: {e}")
        return False
    
    def interact_with_item(self, sensor_id: str, state: str = "absent") -> bool:
        """Interact with an item (take/use)"""
        if not REQUESTS_AVAILABLE:
            return False
            
        try:
            data = {"sensor_id": sensor_id, "state": state}
            response = requests.post(f"{self.base_urls['item']}/interact", json=data, timeout=10)
            if response.status_code == 200:
                if sensor_id in self.device_registry:
                    self.device_registry[sensor_id]["state"] = state
                return True
        except Exception as e:
            print(f" Failed to interact with item: {e}")
        return False

# Global device manager instance
device_manager = DeviceManager()

# =============================================================================
# BLENDER INTEGRATION FUNCTIONS  
# =============================================================================

def create_device_visual(device_id: str, device_type: str, position: Vector, room: str = "") -> bpy.types.Object:
    """Create visual representation of device in Blender scene"""
    
    # Create different shapes for different device types
    if device_type == "motion":
        bpy.ops.mesh.primitive_ico_sphere_add(radius=0.1, location=position)
        obj = bpy.context.active_object
        obj.name = f"Motion_{device_id}"
        
        # Create red material for motion sensors
        mat = bpy.data.materials.new(name=f"Motion_Material_{device_id}")
        if mat.use_nodes:
            mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (1, 0, 0, 1)  # Red
        obj.data.materials.append(mat)
        
    elif device_type == "item":
        bpy.ops.mesh.primitive_cube_add(size=0.2, location=position)
        obj = bpy.context.active_object
        obj.name = f"Item_{device_id}"
        
        # Create blue material for item sensors
        mat = bpy.data.materials.new(name=f"Item_Material_{device_id}")
        if mat.use_nodes:
            mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0, 0, 1, 1)  # Blue
        obj.data.materials.append(mat)
        
    elif device_type == "appliance":
        bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.3, location=position)
        obj = bpy.context.active_object
        obj.name = f"Appliance_{device_id}"
        
        # Create green material for appliances
        mat = bpy.data.materials.new(name=f"Appliance_Material_{device_id}")
        if mat.use_nodes:
            mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0, 1, 0, 1)  # Green
        obj.data.materials.append(mat)
    
    # Add custom properties to track device info
    obj["vesper_device_id"] = device_id
    obj["vesper_device_type"] = device_type
    obj["vesper_room"] = room
    
    return obj

def update_device_visual_state(device_id: str, state: str):
    """Update visual representation based on device state"""
    for obj in bpy.data.objects:
        if obj.get("vesper_device_id") == device_id:
            # Change material emission based on state
            if obj.data.materials:
                mat = obj.data.materials[0]
                if mat.use_nodes:
                    principled = mat.node_tree.nodes.get("Principled BSDF")
                    if principled:
                        if state in ["active", "ON", "absent"]:
                            principled.inputs["Emission"].default_value = (1, 1, 1, 1)  # Bright when active
                            principled.inputs["Emission Strength"].default_value = 2.0
                        else:
                            principled.inputs["Emission"].default_value = (0, 0, 0, 1)  # Dark when inactive
                            principled.inputs["Emission Strength"].default_value = 0.0
            break

def auto_detect_room(position: Vector) -> str:
    """Auto-detect room based on position"""
    if position.x < 0 and position.y > 0:
        return "kitchen"
    elif position.x > 0 and position.y > 0:
        return "living_room"
    elif position.x < 0 and position.y < 0:
        return "bathroom"
    elif position.x > 0 and position.y < 0:
        return "bedroom"
    else:
        return "hallway"

# =============================================================================
# BLENDER OPERATORS
# =============================================================================

class VESPER_OT_CheckServices(bpy.types.Operator):
    """Check Docker services health"""
    bl_idname = "vesper_smart.check_services"
    bl_label = "Check Services"
    bl_description = "Check Docker services status"
    
    def execute(self, context):
        if not REQUESTS_AVAILABLE:
            self.report({'ERROR'}, "requests module not available")
            return {'CANCELLED'}
        
        health = device_manager.check_services_health()
        all_healthy = all(health.values())
        
        if all_healthy:
            self.report({'INFO'}, "All Docker services running!")
        else:
            failed = [k for k, v in health.items() if not v]
            self.report({'WARNING'}, f"Services down: {', '.join(failed)}")
        
        # Print detailed status
        print(" Docker Services Status:")
        for service, status in health.items():
            icon = "" if status else ""
            print(f"  {icon} {service}: {'Running' if status else 'Down'}")
        
        return {'FINISHED'}

class VESPER_OT_AddMotionSensor(bpy.types.Operator):
    """Add motion sensor at cursor location"""
    bl_idname = "vesper_smart.add_motion_sensor"
    bl_label = "Add Motion Sensor"
    bl_description = "Add motion sensor at 3D cursor"
    
    sensor_id: bpy.props.StringProperty(name="Sensor ID", default="M")
    room: bpy.props.StringProperty(name="Room", default="")
    
    def execute(self, context):
        cursor_location = context.scene.cursor.location.copy()
        room = self.room if self.room else auto_detect_room(cursor_location)
        
        # Generate ID
        existing = [obj for obj in bpy.data.objects if obj.name.startswith("Motion_")]
        sensor_id = f"M{len(existing) + 1:02d}" if self.sensor_id == "M" else self.sensor_id
        
        # Create visual device
        create_device_visual(sensor_id, "motion", cursor_location, room)
        
        # Add to Docker if available
        if REQUESTS_AVAILABLE:
            if device_manager.add_motion_sensor(sensor_id, room, cursor_location):
                self.report({'INFO'}, f"Added motion sensor {sensor_id} in {room}")
            else:
                self.report({'WARNING'}, f"Added visual sensor {sensor_id} (Docker failed)")
        else:
            self.report({'INFO'}, f"Added visual sensor {sensor_id} (Docker not available)")
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class VESPER_OT_AddItemSensor(bpy.types.Operator):
    """Add item sensor at cursor location"""
    bl_idname = "vesper_smart.add_item_sensor"
    bl_label = "Add Item Sensor"
    bl_description = "Add item sensor at 3D cursor"
    
    sensor_id: bpy.props.StringProperty(name="Sensor ID", default="I")
    item_name: bpy.props.StringProperty(name="Item Name", default="item")
    
    def execute(self, context):
        cursor_location = context.scene.cursor.location.copy()
        
        # Generate ID
        existing = [obj for obj in bpy.data.objects if obj.name.startswith("Item_")]
        sensor_id = f"I{len(existing) + 1:02d}" if self.sensor_id == "I" else self.sensor_id
        
        # Create visual device
        create_device_visual(sensor_id, "item", cursor_location, self.item_name)
        
        # Add to Docker if available
        if REQUESTS_AVAILABLE:
            if device_manager.add_item_sensor(sensor_id, self.item_name, cursor_location):
                self.report({'INFO'}, f"Added item sensor {sensor_id} for {self.item_name}")
            else:
                self.report({'WARNING'}, f"Added visual item {sensor_id} (Docker failed)")
        else:
            self.report({'INFO'}, f"Added visual item {sensor_id} (Docker not available)")
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class VESPER_OT_TriggerDevice(bpy.types.Operator):
    """Trigger selected device"""
    bl_idname = "vesper_smart.trigger_device"
    bl_label = "Trigger Device"
    bl_description = "Trigger selected device"
    
    def execute(self, context):
        obj = context.active_object
        
        if not obj or "vesper_device_id" not in obj:
            self.report({'ERROR'}, "No VESPER device selected")
            return {'CANCELLED'}
        
        device_id = obj["vesper_device_id"]
        device_type = obj["vesper_device_type"]
        
        success = False
        
        # Trigger based on device type
        if device_type == "motion" and REQUESTS_AVAILABLE:
            success = device_manager.trigger_motion_sensor(device_id, "active")
        elif device_type == "item" and REQUESTS_AVAILABLE:
            success = device_manager.interact_with_item(device_id, "absent")
        
        # Visual feedback
        if device_type == "motion":
            update_device_visual_state(device_id, "active")
        elif device_type == "item":
            update_device_visual_state(device_id, "absent")
        
        if success:
            self.report({'INFO'}, f"Triggered device {device_id}")
        else:
            self.report({'INFO'}, f"Visual trigger {device_id} (Docker not available)")
        
        return {'FINISHED'}

class VESPER_OT_RemoveDevice(bpy.types.Operator):
    """Remove selected device"""
    bl_idname = "vesper_smart.remove_device"
    bl_label = "Remove Device"
    bl_description = "Remove selected device"
    
    def execute(self, context):
        obj = context.active_object
        
        if not obj or "vesper_device_id" not in obj:
            self.report({'ERROR'}, "No VESPER device selected")
            return {'CANCELLED'}
        
        device_id = obj["vesper_device_id"]
        bpy.data.objects.remove(obj, do_unlink=True)
        
        self.report({'INFO'}, f"Removed device {device_id}")
        return {'FINISHED'}

class VESPER_OT_StartDockerServices(bpy.types.Operator):
    """Start Docker services helper"""
    bl_idname = "vesper_smart.start_docker"
    bl_label = "Docker Help"
    bl_description = "Instructions to start Docker services"
    
    def execute(self, context):
        message = """To start Docker services:
1. Open PowerShell/Terminal
2. Navigate to: C:\\Users\\hbui11\\Desktop\\vesper_llm\\virtual-interaction
3. Run: docker-compose -f docker-compose.casas.yml up -d
4. Wait 30-60 seconds
5. Click 'Check Services' to verify"""
        
        self.report({'INFO'}, "Check console for Docker instructions")
        print(" DOCKER SETUP INSTRUCTIONS:")
        print(message)
        return {'FINISHED'}

# =============================================================================
# UI PANEL
# =============================================================================

class VESPER_PT_SmartHomePanel(bpy.types.Panel):
    """VESPER Smart Home control panel"""
    bl_label = "Smart Home"
    bl_idname = "VESPER_PT_smart_home_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'VESPER'
    
    def draw(self, context):
        layout = self.layout
        
        # Header
        row = layout.row()
        row.label(text=" VESPER Smart Home", icon='HOME')
        
        # Status section
        if not REQUESTS_AVAILABLE:
            box = layout.box()
            box.alert = True
            box.label(text=" Limited Mode", icon='ERROR')
            box.label(text="Missing: requests module")
            box.label(text="Install: pip install requests")
        
        # Docker services section
        box = layout.box()
        box.label(text=" Docker Services:", icon='PREFERENCES')
        
        row = box.row(align=True)
        row.operator("vesper_smart.check_services", icon='CHECKMARK')
        row.operator("vesper_smart.start_docker", icon='CONSOLE', text="Help")
        
        layout.separator()
        
        # Device management section
        box = layout.box()
        box.label(text=" Add Devices:", icon='ADD')
        
        box.operator("vesper_smart.add_motion_sensor", icon='OUTLINER_OB_LIGHT', text="Motion Sensor")
        box.operator("vesper_smart.add_item_sensor", icon='OUTLINER_OB_MESH', text="Item Sensor")
        
        layout.separator()
        
        # Device control section
        box = layout.box()
        box.label(text=" Control:", icon='SETTINGS')
        
        row = box.row(align=True)
        row.operator("vesper_smart.trigger_device", icon='PLAY', text="Trigger")
        row.operator("vesper_smart.remove_device", icon='X', text="Remove")
        
        layout.separator()
        
        # Info section
        obj = context.active_object
        if obj and "vesper_device_id" in obj:
            box = layout.box()
            box.label(text=" Selected Device:", icon='INFO')
            box.label(text=f"ID: {obj['vesper_device_id']}")
            box.label(text=f"Type: {obj['vesper_device_type']}")
            if "vesper_room" in obj:
                box.label(text=f"Room: {obj['vesper_room']}")
        else:
            box = layout.box()
            box.label(text=" Instructions:", icon='QUESTION')
            box.label(text="1. Position 3D cursor")
            box.label(text="2. Add devices")
            box.label(text="3. Select & trigger device")

# =============================================================================
# REGISTRATION
# =============================================================================

classes = [
    VESPER_OT_CheckServices,
    VESPER_OT_AddMotionSensor,
    VESPER_OT_AddItemSensor,
    VESPER_OT_TriggerDevice,
    VESPER_OT_RemoveDevice,
    VESPER_OT_StartDockerServices,
    VESPER_PT_SmartHomePanel
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    print(" VESPER Smart Home Integration registered")

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    print(" VESPER Smart Home Integration unregistered")

if __name__ == "__main__":
    register()
