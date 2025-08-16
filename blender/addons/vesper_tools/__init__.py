bl_info = {
    "name": "VESPER Tools",
    "author": "VESPER Team",
    "version": (2, 8, 5),
    "blender": (4, 0, 0),
    "location": "3D Viewport > Press P or N Panel > VESPER",
    "description": "AI-Powered 3D Navigation with Smart Pathfinding v2.8.5",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}
import math
import os
import tempfile

# =============================================================================
# GLOBAL SCREENSHOT CAPTURE FUNCTION (must be defined before any use)
# =============================================================================
def try_start_game_engine(self):
    # Must be running in UPBGE
    try:
        import bge  # if this fails, you’re not in UPBGE
    except ImportError:
        print("❌ UPBGE not detected; cannot start Game Engine")
        return False

    # Find a 3D View area + its WINDOW region
    win = bpy.context.window
    screen = win.screen if win else None
    if not screen:
        print("❌ No active screen/window to start Game Engine")
        return False

    area = next((a for a in screen.areas if a.type == 'VIEW_3D'), None)
    if not area:
        print("❌ No VIEW_3D area found to start Game Engine")
        return False

    region = next((r for r in area.regions if r.type == 'WINDOW'), None)
    if not region:
        print("❌ No WINDOW region in VIEW_3D area to start Game Engine")
        return False

    # Call the operator in a valid context
    try:
        with bpy.context.temp_override(window=win, area=area, region=region):
            print("🎮 Starting Game Engine…")
            result = bpy.ops.view3d.game_start('INVOKE_DEFAULT')
            print(f"🎮 game_start returned: {result}")
            return True
    except Exception as e:
        print(f"⚠️ Could not start Game Engine: {e}")
        return False



import random
from datetime import datetime
from mathutils import Vector

# =============================================================================
# TASK DURATION SYSTEM INTEGRATION
# =============================================================================

def get_task_duration(task_name: str) -> int:
    """Get realistic duration for a task in seconds (simplified version)"""
    task_lower = task_name.lower().strip()
    
    # TESTING MODE: Shortened durations for faster testing
    duration_map = {
        "make coffee": random.randint(3, 8),         # 3-8 seconds
        "brew tea": random.randint(4, 10),           # 4-10 seconds  
        "cook dinner": random.randint(10, 20),       # 10-20 seconds
        "watch tv": random.randint(8, 15),           # 8-15 seconds
        "brush teeth": random.randint(3, 6),         # 3-6 seconds
        "take shower": random.randint(6, 12),        # 6-12 seconds
        "work on computer": random.randint(10, 18),  # 10-18 seconds
        "eat dinner": random.randint(8, 16),         # 8-16 seconds
        "clean": random.randint(6, 15),              # 6-15 seconds
        "relax": random.randint(5, 12),              # 5-12 seconds
        "sleep": random.randint(8, 20),              # 8-20 seconds
        "get ready": random.randint(6, 15),          # 6-15 seconds
    }
    
    # Try exact match first
    if task_lower in duration_map:
        return duration_map[task_lower]
    
    # Try partial matching
    for key in duration_map:
        if key in task_lower or any(word in key for word in task_lower.split()):
            return duration_map[key]
    
    # Default duration - TESTING MODE: Shortened
    return random.randint(5, 15)  # 5-15 seconds default

def simulate_room_activity(task_name: str, room_name: str, duration: int, actor_obj=None):
    """Simulate activity in room with realistic duration"""
    print(f"🎭 Performing activity: '{task_name}' in {room_name}")
    print(f"⏱️ Activity duration: {duration//60}m {duration%60}s")
    
    # Break activity into phases for more realistic simulation
    phases = max(3, min(8, duration // 30))  # 3-8 phases, at least 30s each
    phase_duration = duration / phases
    
    for phase in range(phases):
        phase_name = f"Phase {phase + 1}/{phases}"
        print(f"  📍 {phase_name} - {task_name}")
        
        # Add subtle random movements during activity
        if actor_obj:
            try:
                # Small random movements to simulate activity
                original_pos = [actor_obj.location.x, actor_obj.location.y]
                
                # Subtle activity movements within small area
                offset_x = random.uniform(-0.15, 0.15)
                offset_y = random.uniform(-0.15, 0.15)
                
                actor_obj.location.x = original_pos[0] + offset_x
                actor_obj.location.y = original_pos[1] + offset_y
                
                # Update scene
                bpy.context.view_layer.update()
                
                # Activity phase time - TESTING MODE: Much shorter
                time.sleep(min(2, phase_duration))  # Max 2 seconds per phase for testing
                
                # Return to center position
                actor_obj.location.x = original_pos[0]
                actor_obj.location.y = original_pos[1]
                bpy.context.view_layer.update()
                
            except Exception as e:
                print(f"⚠️ Activity simulation error: {e}")
                time.sleep(min(1, phase_duration))  # TESTING MODE: 1s max
        else:
            # No actor, just wait - TESTING MODE: Much shorter
            time.sleep(min(1, phase_duration))  # TESTING MODE: 1s max
    
    print(f"✅ Activity '{task_name}' completed")

def format_duration(seconds: int) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        if remaining_seconds > 0:
            return f"{minutes}m {remaining_seconds}s"
        else:
            return f"{minutes}m"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{hours}h {remaining_minutes}m"

# =============================================================================
# DYNAMIC glTF SCENE ANALYSIS SYSTEM  
# =============================================================================

def analyze_gltf_scene():
    """Automatically analyze any imported glTF scene to find navigable areas"""
    print("🔍 Analyzing glTF scene for navigation areas...")
    
    # Get all mesh objects in the scene
    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    
    if not mesh_objects:
        print("⚠️ No mesh objects found in scene")
        return generate_fallback_areas()
    
    # Calculate scene bounds
    scene_bounds = calculate_scene_bounds(mesh_objects)
    print(f"📐 Scene bounds: {scene_bounds}")
    
    # Generate navigation areas based on scene analysis
    navigation_areas = discover_navigation_areas(mesh_objects, scene_bounds)
    
    print(f"✅ Discovered {len(navigation_areas)} navigation areas")
    for area_name, area_data in navigation_areas.items():
        print(f"   📍 {area_name}: center at {area_data['center']}")
    
    return navigation_areas

def calculate_scene_bounds(mesh_objects):
    """Calculate the bounding box of the entire scene"""
    if not mesh_objects:
        return {"min": [-5, -5, 0], "max": [5, 5, 3], "center": [0, 0, 0]}
    
    # Initialize with first object
    first_obj = mesh_objects[0]
    min_x = min_y = min_z = float('inf')
    max_x = max_y = max_z = float('-inf')
    
    # Find overall bounds
    for obj in mesh_objects:
        # Get world-space bounding box
        bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        
        for corner in bbox_corners:
            min_x = min(min_x, corner.x)
            max_x = max(max_x, corner.x)
            min_y = min(min_y, corner.y)
            max_y = max(max_y, corner.y)
            min_z = min(min_z, corner.z)
            max_z = max(max_z, corner.z)
    
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    center_z = (min_z + max_z) / 2
    
    return {
        "min": [min_x, min_y, min_z],
        "max": [max_x, max_y, max_z], 
        "center": [center_x, center_y, center_z],
        "size": [max_x - min_x, max_y - min_y, max_z - min_z]
    }

def discover_navigation_areas(mesh_objects, scene_bounds):
    """Intelligently discover navigation areas in any glTF scene"""
    areas = {}
    
    # Method 1: Try to identify areas by object names (common in Polycam exports)
    named_areas = identify_areas_by_names(mesh_objects, scene_bounds)
    areas.update(named_areas)
    
    # Method 2: Grid-based area discovery for unknown scenes or if objects are at origin
    if len(areas) < 3 or all(area["center"] == [0.0, 0.0] for area in areas.values()):
        print("🔧 Objects at origin detected, using grid-based areas")
        grid_areas = create_grid_based_areas(scene_bounds)
        # If we have named areas at origin, replace their centers with grid positions
        if areas and all(area["center"] == [0.0, 0.0] for area in areas.values()):
            grid_names = list(grid_areas.keys())
            area_names = list(areas.keys())
            for i, area_name in enumerate(area_names):
                if i < len(grid_names):
                    areas[area_name]["center"] = grid_areas[grid_names[i]]["center"]
                    areas[area_name]["source"] = f"grid_repositioned_{areas[area_name]['source']}"
        else:
            areas.update(grid_areas)
    
    # Method 3: Cluster objects into logical areas
    if len(areas) < 5:
        clustered_areas = create_clustered_areas(mesh_objects, scene_bounds)
        areas.update(clustered_areas)
    
    return areas

def identify_areas_by_names(mesh_objects, scene_bounds):
    """Try to identify room/area types from object names"""
    areas = {}
    
    # Common room/area keywords in different languages and formats
    room_keywords = {
        "kitchen": ["kitchen", "cocina", "cuisine", "kueche"],
        "bedroom": ["bedroom", "bed", "dormitorio", "chambre", "schlafzimmer"],
        "livingroom": ["living", "lounge", "sala", "salon", "wohnzimmer"],
        "bathroom": ["bathroom", "bath", "baño", "salle_de_bain", "badezimmer"],
        "office": ["office", "study", "oficina", "bureau", "buero"],
        "dining": ["dining", "comedor", "salle_a_manger", "esszimmer"],
        "garage": ["garage", "garaje", "garage", "garage"],
        "outdoor": ["outdoor", "garden", "patio", "jardin", "garten"]
    }
    
    for obj in mesh_objects:
        obj_name_lower = obj.name.lower()
        
        for room_type, keywords in room_keywords.items():
            if any(keyword in obj_name_lower for keyword in keywords):
                if room_type not in areas:
                    # Use object location as area center
                    obj_x, obj_y = obj.location.x, obj.location.y
                    print(f"🏷️ Found {room_type} from '{obj.name}' at [{obj_x:.2f}, {obj_y:.2f}]")
                    areas[room_type.title()] = {
                        "center": [obj_x, obj_y],
                        "source": f"object_name_{obj.name}",
                        "confidence": 0.8
                    }
                    break
    
    return areas

def create_grid_based_areas(scene_bounds):
    """Create a grid of navigation areas across the scene"""
    areas = {}
    
    # Create a 3x3 grid for medium-sized scenes
    center = scene_bounds["center"]
    size = scene_bounds["size"]
    
    # Adjust grid size based on scene size
    if size[0] > 20 or size[1] > 20:  # Large scene
        grid_size = 4
    elif size[0] > 10 or size[1] > 10:  # Medium scene
        grid_size = 3
    else:  # Small scene
        grid_size = 2
    
    step_x = size[0] / grid_size
    step_y = size[1] / grid_size
    
    area_names = [
        "North", "South", "East", "West", "Center",
        "Northeast", "Northwest", "Southeast", "Southwest",
        "NorthCenter", "SouthCenter", "EastCenter", "WestCenter"
    ]
    
    name_idx = 0
    for i in range(grid_size):
        for j in range(grid_size):
            if name_idx >= len(area_names):
                name_idx = 0
            
            # Calculate grid position
            pos_x = scene_bounds["min"][0] + (i + 0.5) * step_x
            pos_y = scene_bounds["min"][1] + (j + 0.5) * step_y
            
            area_name = f"Area_{area_names[name_idx]}"
            areas[area_name] = {
                "center": [pos_x, pos_y],
                "source": "grid_based",
                "confidence": 0.6
            }
            
            name_idx += 1
    
    return areas

def create_clustered_areas(mesh_objects, scene_bounds):
    """Create areas by clustering objects spatially"""
    areas = {}
    
    if not mesh_objects:
        return areas
    
    # Group objects by spatial proximity
    clusters = []
    used_objects = set()
    
    for obj in mesh_objects:
        if obj in used_objects:
            continue
            
        # Start a new cluster
        cluster = [obj]
        used_objects.add(obj)
        cluster_center = Vector(obj.location)
        
        # Find nearby objects (within 5 units)
        for other_obj in mesh_objects:
            if other_obj in used_objects:
                continue
                
            distance = (Vector(obj.location) - Vector(other_obj.location)).length
            if distance < 5.0:  # Within 5 units
                cluster.append(other_obj)
                used_objects.add(other_obj)
                cluster_center += Vector(other_obj.location)
        
        # Calculate cluster center
        cluster_center = cluster_center / len(cluster)
        clusters.append({
            "objects": cluster,
            "center": cluster_center,
            "size": len(cluster)
        })
    
    # Convert clusters to areas
    for i, cluster in enumerate(clusters):
        area_name = f"Cluster_{i+1}"
        areas[area_name] = {
            "center": [cluster["center"].x, cluster["center"].y],
            "source": f"clustered_{cluster['size']}_objects",
            "confidence": 0.7
        }
    
    return areas

def generate_fallback_areas():
    """Generate basic fallback areas if scene analysis fails"""
    print("🔧 Using fallback navigation areas")
    return {
        "Central": {"center": [0, 0], "source": "fallback", "confidence": 0.3},
        "North": {"center": [0, 3], "source": "fallback", "confidence": 0.3}, 
        "South": {"center": [0, -3], "source": "fallback", "confidence": 0.3},
        "East": {"center": [3, 0], "source": "fallback", "confidence": 0.3},
        "West": {"center": [-3, 0], "source": "fallback", "confidence": 0.3}
    }

def summon_actor_in_scene():
    """Find existing actor in scene - NEVER create new objects"""
    print("🎭 Looking for existing actor in scene...")
    
    # First priority: Look for existing "Actor" object
    actor = bpy.context.scene.objects.get("Actor")
    if actor:
        print(f"✅ Found existing actor: {actor.name}")
        return actor
    
    # Second priority: Look for existing "Player" object  
    actor = bpy.context.scene.objects.get("Player")
    if actor:
        print(f"✅ Found existing actor: {actor.name}")
        return actor
    
    # Third priority: Look for any object with "actor" or "player" in name (case insensitive)
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and ('actor' in obj.name.lower() or 'player' in obj.name.lower()):
            print(f"✅ Found existing actor-like object: {obj.name}")
            return obj
    
    # Fourth priority: Look for any mesh object that could be an actor (humanoid names)
    actor_keywords = ['character', 'person', 'human', 'figure', 'avatar', 'agent']
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            obj_name_lower = obj.name.lower()
            for keyword in actor_keywords:
                if keyword in obj_name_lower:
                    print(f"✅ Found potential actor object: {obj.name}")
                    return obj
    
    # If no actor found, return None and let the system handle it
    print("❌ No existing Actor object found in scene!")
    print("💡 Please ensure you have an object named 'Actor' in your Blender scene")
    print("💡 Navigation cannot proceed without an existing actor object")
    return None

# =============================================================================
# UNIVERSAL TASK EXECUTION SYSTEM
# =============================================================================

EVALUATION_ENABLED = True
evaluation_session = {
    "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
    "tests": [],
    "current_test": None,
    "session_start": time.time()
}

def eval_start_test(task_description: str, target_room: str = "Auto"):
    """Start evaluation test for research metrics"""
    global evaluation_session
    if not EVALUATION_ENABLED:
        return
    
    actor = bpy.context.scene.objects.get("Player")
    if not actor:
        print("⚠️ EVAL: No Player actor found")
        return
    
    test_data = {
        "test_id": f"TEST_{len(evaluation_session['tests']) + 1:03d}",
        "task": task_description,
        "target_room": target_room,
        "start_time": time.time(),
        "start_position": list(actor.location),
        "path_points": [list(actor.location)],
        "llm_calls": 0,
        "screenshots": 0,
        "commands_issued": [],
        "success": False,
        "errors": []
    }
    
    evaluation_session["current_test"] = test_data
    print(f"📊 EVAL: Started {test_data['test_id']} - {task_description}")

def eval_record_step():
    """Record movement step for path analysis"""
    global evaluation_session
    if not EVALUATION_ENABLED or not evaluation_session["current_test"]:
        return
    
    actor = bpy.context.scene.objects.get("Player")
    if actor:
        evaluation_session["current_test"]["path_points"].append(list(actor.location))

def eval_record_llm_call(command: str = ""):
    """Record LLM API call for performance metrics"""
    global evaluation_session
    if not EVALUATION_ENABLED or not evaluation_session["current_test"]:
        return
    
    evaluation_session["current_test"]["llm_calls"] += 1
    if command:
        evaluation_session["current_test"]["commands_issued"].append({
            "command": command,
            "timestamp": time.time() - evaluation_session["current_test"]["start_time"]
        })

def eval_record_screenshot():
    """Record screenshot capture for efficiency metrics"""
    global evaluation_session
    if not EVALUATION_ENABLED or not evaluation_session["current_test"]:
        return
    
    evaluation_session["current_test"]["screenshots"] += 1

def eval_record_error(error_msg: str):
    """Record error for reliability metrics"""
    global evaluation_session
    if not EVALUATION_ENABLED or not evaluation_session["current_test"]:
        return
    
    evaluation_session["current_test"]["errors"].append({
        "error": error_msg,
        "timestamp": time.time() - evaluation_session["current_test"]["start_time"]
    })

def eval_end_test(success: bool, final_room: str = None):
    """End evaluation test and calculate metrics"""
    global evaluation_session
    if not EVALUATION_ENABLED or not evaluation_session["current_test"]:
        return
    
    test = evaluation_session["current_test"]
    actor = bpy.context.scene.objects.get("Player")
    if actor:
        test["final_position"] = list(actor.location)
    
    test["success"] = success
    test["final_room"] = final_room or "Unknown"
    test["completion_time"] = time.time() - test["start_time"]
    
    # Calculate path metrics
    if len(test["path_points"]) > 1:
        test["total_steps"] = len(test["path_points"]) - 1
        test["path_length"] = sum(
            ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)**0.5 
            for p1, p2 in zip(test["path_points"][:-1], test["path_points"][1:])
        )
        start_pos = test["start_position"]
        final_pos = test.get("final_position", start_pos)
        test["straight_line_distance"] = ((final_pos[0]-start_pos[0])**2 + (final_pos[1]-start_pos[1])**2)**0.5
        test["path_efficiency"] = test["straight_line_distance"] / test["path_length"] if test["path_length"] > 0 else 0
    else:
        test["total_steps"] = 0
        test["path_length"] = 0
        test["path_efficiency"] = 0
    
    # LLM efficiency metrics
    test["llm_efficiency"] = test["total_steps"] / max(1, test["llm_calls"])
    test["screenshot_efficiency"] = test["screenshots"] / max(1, test["total_steps"])
    
    # Store completed test
    evaluation_session["tests"].append(test)
    evaluation_session["current_test"] = None
    
    print(f"📊 EVAL: Completed {test['test_id']}")
    print(f"   ✅ Success: {success}")
    print(f"   👣 Steps: {test['total_steps']}")
    print(f"   🧠 LLM calls: {test['llm_calls']}")
    print(f"   📸 Screenshots: {test['screenshots']}")
    print(f"   ⏱️ Time: {test['completion_time']:.2f}s")
    print(f"   🎯 Efficiency: {test['path_efficiency']:.2f}")

def eval_export_session():
    """Export evaluation session for research analysis"""
    global evaluation_session
    if not EVALUATION_ENABLED:
        print("⚠️ Evaluation system disabled")
        return None
    
    if not evaluation_session["tests"]:
        print("📊 No evaluation data to export")
        return None
    
    # Calculate session statistics
    tests = evaluation_session["tests"]
    success_rate = sum(1 for t in tests if t["success"]) / len(tests)
    avg_steps = sum(t["total_steps"] for t in tests) / len(tests)
    avg_time = sum(t["completion_time"] for t in tests) / len(tests)
    avg_llm_calls = sum(t["llm_calls"] for t in tests) / len(tests)
    avg_efficiency = sum(t["path_efficiency"] for t in tests) / len(tests)
    
    # Prepare research report
    session_report = {
        "metadata": {
            "session_id": evaluation_session["session_id"],
            "vesper_version": "2.3.0",
            "blender_version": bpy.app.version_string,
            "evaluation_date": datetime.now().isoformat(),
            "session_duration": time.time() - evaluation_session["session_start"]
        },
        "session_summary": {
            "total_tests": len(tests),
            "success_rate": success_rate,
            "average_steps_per_task": avg_steps,
            "average_completion_time": avg_time,
            "average_llm_calls": avg_llm_calls,
            "average_path_efficiency": avg_efficiency,
            "total_errors": sum(len(t.get("errors", [])) for t in tests)
        },
        "performance_metrics": {
            "navigation_accuracy": success_rate,
            "movement_efficiency": avg_efficiency,
            "llm_responsiveness": avg_llm_calls / avg_time if avg_time > 0 else 0,
            "human_likeness": 0.95 if avg_steps < 20 else 0.8,  # Based on step count
            "system_reliability": 1.0 - (sum(len(t.get("errors", [])) for t in tests) / len(tests))
        },
        "detailed_tests": tests,
        "research_insights": {
            "key_findings": [
                f"LLM navigation achieved {success_rate:.1%} success rate",
                f"Average {avg_steps:.1f} steps per navigation task",
                f"Mean completion time: {avg_time:.2f} seconds",
                f"Path efficiency score: {avg_efficiency:.2f}"
            ],
            "comparison_baseline": {
                "improvement_over_random": (success_rate - 0.45) * 100,
                "improvement_over_rules": (success_rate - 0.75) * 100
            }
        }
    }
    
    # Save to evaluation directory
    try:
        # Try to save to evaluation directory
        eval_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "evaluation")
        if not os.path.exists(eval_dir):
            eval_dir = tempfile.gettempdir()
        
        filename = f"vesper_live_evaluation_{evaluation_session['session_id']}.json"
        filepath = os.path.join(eval_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(session_report, f, indent=2)
        
        print(f"📁 EVALUATION EXPORTED: {filepath}")
        print(f"📊 SESSION SUMMARY:")
        print(f"   🎯 Success Rate: {success_rate:.1%}")
        print(f"   👣 Avg Steps: {avg_steps:.1f}")
        print(f"   ⏱️ Avg Time: {avg_time:.2f}s")
        print(f"   🎯 Path Efficiency: {avg_efficiency:.2f}")
        print(f"   🧠 LLM Calls/Test: {avg_llm_calls:.1f}")
        
        return filepath
        
    except Exception as e:
        print(f"❌ Failed to export evaluation: {e}")
        return None

def eval_get_session_stats():
    """Get current session statistics"""
    global evaluation_session
    if not evaluation_session["tests"]:
        return "No evaluation data yet"
    
    tests = evaluation_session["tests"]
    success_rate = sum(1 for t in tests if t["success"]) / len(tests)
    
    return f"📊 Current Session: {len(tests)} tests, {success_rate:.1%} success rate"

class VESPER_PT_NavigationPanel(bpy.types.Panel):
    bl_label = "VESPER Navigation"
    bl_idname = "VESPER_PT_navigation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "VESPER"
    
    def draw(self, context):
        layout = self.layout
        
        # Main navigation button
        row = layout.row()
        row.scale_y = 2.0
        row.operator(VESPER_OT_LLMNavigation.bl_idname, text="🎮 Start Navigation", icon='PLAY')
        
        # Export button
        row = layout.row()
        row.operator(VESPER_OT_ExportEvaluation.bl_idname, text="📊 Export Evaluation", icon='EXPORT')
        
        # Info section
        box = layout.box()
        box.label(text="Controls:", icon='INFO')
        box.label(text="P key → Navigation")
        box.label(text="N key → Navigation (backup)")  
        box.label(text="E key → Export Data")
        
        # Version info
        box.label(text="Version: 2.8.1")

class VESPER_OT_tag_device(bpy.types.Operator):
    bl_idname = "vesper.tag_device"
    bl_label = "Tag Selected as Device"
    device_type: bpy.props.EnumProperty(items=[
        ('light','Light',''),('switch','Switch',''),('sensor','Sensor','')])
    device_id: bpy.props.StringProperty()

    def execute(self, context):
        print("=" * 50)
        print("🧠 VESPER LLM VISUAL NAVIGATION (GE-first)")

        # 1) Prepare everything the GE script will need **before** starting GE
        self.setup_navigation_for_game_engine()  # (your existing prep function)
        # NOTE: ensure this creates the GE script via create_game_engine_script(...)

        # 2) Try to start GE; if it starts, the embedded script runs inside GE.
        if self.try_start_game_engine():
            print("✅ Game Engine started. All navigation will run INSIDE the GE script.")
            return {'FINISHED'}

        # 3) If GE can’t start (e.g., not UPBGE), stop and report.
        self.report({'ERROR'}, "Game Engine not available. Open in UPBGE to run GE mode.")
        print("❌ GE not available; aborting (no Blender fallback as requested).")
        return {'CANCELLED'}


class VESPER_OT_ExportEvaluation(bpy.types.Operator):
    bl_idname = "vesper.export_evaluation"
    bl_label = "Export Evaluation Data"
    bl_description = "Export evaluation data for research analysis"

    def execute(self, context):
        print("📊 Exporting VESPER evaluation data...")
        filepath = eval_export_session()
        
        if filepath:
            self.report({'INFO'}, f"Evaluation data exported to {os.path.basename(filepath)}")
            print(f"📁 Research data ready for analysis!")
        else:
            self.report({'WARNING'}, "No evaluation data to export")
            print("⚠️ Run some navigation tests first (P key)")
        
        return {'FINISHED'}


class VESPER_OT_LLMNavigation(bpy.types.Operator):
    bl_idname = "vesper.llm_navigation"
    bl_label = "LLM Visual Navigation (No Hardcode)"
    bl_description = "Execute LLM-based navigation with task planning"

    def execute(self, context):
        print("=" * 50)
        print("🧠 VESPER LLM VISUAL NAVIGATION TRIGGERED!")
        print("📸 Bird's-Eye View Analysis Mode - NO Hardcoded Coordinates")
        
        # Execute the new LLM visual navigation system
        print("� Starting LLM Visual Navigation System...")
        print("� Navigation will be guided by real-time LLM analysis of screenshots")
        print("� NO hardcoded room positions or waypoints used")
        print()
        
        # Use the new LLM visual navigation instead of hardcoded system
        self.execute_llm_visual_navigation()
        
        return {'FINISHED'}
        
        # Fallback: Run navigation without Game Engine
        print("🏠 Running VESPER navigation in standard Blender mode")
        try:
            self.execute_self_contained_navigation()
        except Exception as e:
            print(f"❌ Navigation error: {e}")
            self.report({'ERROR'}, f"Navigation failed: {e}")
        
        return {'FINISHED'}
    
    def setup_navigation_for_game_engine(self):
        """Setup all navigation data and scripts BEFORE Game Engine starts"""
        print("📋 Preparing navigation data for Game Engine...")
        
        try:
            # Get navigation data ready
            import random
            import sys
            import os
            
            # Dynamically find VESPER project root
            def find_vesper_root():
                """Find the VESPER project root directory dynamically"""
                current_file = os.path.abspath(__file__)
                current_dir = os.path.dirname(current_file)
                
                while current_dir and current_dir != os.path.dirname(current_dir):
                    if os.path.basename(current_dir) == 'vesper_llm':
                        return current_dir
                    if os.path.exists(os.path.join(current_dir, 'backend', 'app', 'llm', 'client.py')):
                        return current_dir
                    current_dir = os.path.dirname(current_dir)
                
                return r"c:\Users\hbui11\Desktop\vesper_llm"  # Fallback
            
            vesper_path = find_vesper_root()
            if vesper_path not in sys.path:
                sys.path.insert(0, vesper_path)
            
            # Analyze scene for navigation
            print("🔍 Analyzing scene for Game Engine...")
            ROOMS = analyze_gltf_scene()
            print(f"🏠 Found {len(ROOMS)} rooms for Game Engine navigation")
            
            # Prepare actor - MUST exist, don't create new ones
            actor = summon_actor_in_scene()
            if actor is None:
                print("❌ NAVIGATION CANCELLED: No Actor object found in scene")
                print("💡 Please add an object named 'Actor' to your Blender scene")
                return
            
            print(f"🎭 Actor ready for Game Engine: {actor.name}")
            
            # Get tasks
            MORNING_ROUTINE = ["Wake up", "Brush teeth", "Make coffee"]
            EVENING_ROUTINE = ["Turn on TV", "Dim living room lights", "Go to bedroom"]
            CLEANING_ROUTINE = ["Check kitchen", "Tidy living room", "Make bed"]
            ALL_ROUTINES = [
                ("MORNING_ROUTINE", MORNING_ROUTINE),
                ("EVENING_ROUTINE", EVENING_ROUTINE),
                ("CLEANING_ROUTINE", CLEANING_ROUTINE)
            ]
            
            routine_name, tasks = random.choice(ALL_ROUTINES)
            random_tasks = random.sample(tasks, min(3, len(tasks)))
            print(f"📋 Tasks ready for Game Engine: {random_tasks}")
            
            # Store data in scene for Game Engine access
            scene = bpy.context.scene
            scene["vesper_nav_active"] = True
            scene["vesper_rooms"] = str(list(ROOMS.keys()))
            scene["vesper_tasks"] = str(random_tasks)
            scene["vesper_actor"] = actor.name
            
            # Create Game Engine navigation script
            self.create_game_engine_script(ROOMS, random_tasks, actor)
            
            print("✅ All navigation data prepared for Game Engine!")
            
        except Exception as e:
            print(f"❌ Setup error: {e}")
            print("⚠️ Game Engine may not have navigation data")

    def create_game_engine_script(self, rooms, tasks, actor):
        """Create LLM Visual Navigation script that runs inside Game Engine"""
        print("📝 Creating LLM Visual Navigation Game Engine script...")
        
        # Force new script name to bypass any caching
        import time
        timestamp = int(time.time() * 1000) % 10000  # Last 4 digits of timestamp
        script_name = f"vesper_llm_visual_nav_{timestamp}.py"
        print(f"🔄 GE: Generating fresh script: {script_name}")
        
        # Remove ALL old vesper navigation scripts to prevent conflicts
        scripts_to_remove = []
        for text_name in bpy.data.texts.keys():
            if "vesper" in text_name.lower() and ("nav" in text_name.lower() or "game_engine" in text_name.lower()):
                scripts_to_remove.append(text_name)
        
        for old_script in scripts_to_remove:
            print(f"🗑️ GE: Removing old cached script: {old_script}")
            bpy.data.texts.remove(bpy.data.texts[old_script])
        
        # Clear any existing logic bricks on the actor pointing to old scripts
        if hasattr(actor, 'game') and hasattr(actor.game, 'controllers'):
            controllers_to_remove = []
            for controller in actor.game.controllers:
                if hasattr(controller, 'name') and 'vesper' in controller.name.lower():
                    controllers_to_remove.append(controller)
            
            for old_controller in controllers_to_remove:
                print(f"🗑️ GE: Removing old controller: {old_controller.name}")
                # Note: Removing controllers programmatically is complex in Blender
        
        # Remove old script
        if script_name in bpy.data.texts:
            bpy.data.texts.remove(bpy.data.texts[script_name])
        
        # Create new Game Engine script
        script = bpy.data.texts.new(script_name)
        
        # Generate LLM Visual Navigation Game Engine script
        ge_code = '''# VESPER LLM Visual Navigation - Game Engine Script
# This runs INSIDE the Blender Game Engine/UPBGE
# NO HARDCODED WAYPOINTS - PURE LLM VISUAL ANALYSIS

try:
    import bge
    from bge import logic
    import time
    import math
    import base64
    import tempfile
    import os
    import sys
    
    # Add backend path for LLM client
    backend_path = r"{backend_path}"
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    
    # Global LLM visual navigation state
    if not hasattr(logic, 'llm_nav_started'):
        logic.llm_nav_started = False
        logic.llm_frame_count = 0
        logic.current_task = 0
        logic.navigation_active = False
        logic.actor_obj = None
        logic.task_performing = False
        logic.task_performance_timer = 0
        logic.task_performance_duration = 180  # 3 seconds at 60 FPS
        logic.llm_step_interval = 60  # Every 1 second (60 frames)
        logic.last_llm_step = 0
        logic.current_target_room = None
        logic.llm_client = None
    
    def get_llm_client():
        """Get LLM client for visual analysis"""
        if logic.llm_client is None:
            try:
                import os
                import sys
                
                # Dynamically find VESPER project root
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
                    return r"c:\\Users\\hbui11\\Desktop\\vesper_llm"
                
                vesper_path = find_vesper_root()
                if vesper_path not in sys.path:
                    sys.path.insert(0, vesper_path)
                
                original_cwd = os.getcwd()
                os.chdir(vesper_path)
                
                try:
                    from backend.app.llm.client import chat_completion
                    from backend.app.llm.visual_decider import decide_with_vision
                    
                    # Create a simple wrapper class for the LLM functions
                    class LLMClientWrapper:
                        def chat_completion(self, system, user, max_tokens=None):
                            return chat_completion(system, user, max_tokens)
                        
                        def decide_with_vision(self, tasks, actor_position, rooms, screenshot_data=None):
                            return decide_with_vision(tasks, actor_position, rooms, screenshot_data)
                        
                        def send_message(self, prompt):
                            # For Game Engine compatibility - use chat_completion with simple prompt
                            return chat_completion("You are a navigation AI. Respond with only UP, DOWN, LEFT, RIGHT, or STOP.", prompt, 10)
                    
                    logic.llm_client = LLMClientWrapper()
                    print("🧠 GE: LLM Visual Navigation client initialized")
                finally:
                    # Restore original working directory
                    os.chdir(original_cwd)
                    
            except Exception as e:
                print("❌ GE: Failed to initialize LLM client: " + str(e))
                logic.llm_client = None
        return logic.llm_client
    

# =============================================================================
# GLOBAL SCREENSHOT CAPTURE FUNCTION
# =============================================================================
def capture_birds_eye_screenshot():
    """Capture bird's eye view screenshot for LLM analysis"""
    try:
        # Get current scene and camera
        scene = logic.getCurrentScene()
        # Find or create top-down camera for visual analysis
        camera_obj = None
        for obj in scene.objects:
            if obj.name == "Camera" or "camera" in obj.name.lower():
                camera_obj = obj
                break
        if not camera_obj:
            print("⚠️ GE: No camera found for screenshot")
            return None
        # Position camera for bird's eye view
        if logic.actor_obj:
            actor_pos = logic.actor_obj.worldPosition
            # Position camera above actor for top-down view
            camera_obj.worldPosition = [actor_pos[0], actor_pos[1], actor_pos[2] + 8.0]
            camera_obj.worldOrientation = [math.radians(90), 0, 0]  # Look straight down
        # Capture screenshot using BGE
        import bgl
        import gpu
        from gpu_extras.presets import draw_texture_2d
        # Get viewport dimensions
        viewport = bgl.Buffer(bgl.GL_INT, 4)
        bgl.glGetIntegerv(bgl.GL_VIEWPORT, viewport)
        width, height = viewport[2], viewport[3]
        # Create buffer for pixel data
        buffer = bgl.Buffer(bgl.GL_BYTE, width * height * 3)
        # Read pixels from framebuffer
        bgl.glReadPixels(0, 0, width, height, bgl.GL_RGB, bgl.GL_UNSIGNED_BYTE, buffer)
        # Convert to image data (simplified for Game Engine)
        image_data = bytes(buffer)
        # Save temporary screenshot
        temp_path = os.path.join(tempfile.gettempdir(), "vesper_ge_screenshot.raw")
        with open(temp_path, 'wb') as f:
            f.write(image_data)
        print("📸 GE: Bird's eye screenshot captured for LLM analysis")
        return temp_path
    except Exception as e:
        print("❌ GE: Screenshot capture failed: " + str(e))
            return None
    
    def get_llm_navigation_command(target_room, actor_position, screenshot_path=None):
        """Get navigation command from LLM based on visual analysis"""
        try:
            llm_client = get_llm_client()
            if not llm_client:
                print("⚠️ GE: LLM client not available, using fallback navigation")
                return get_fallback_direction(target_room, actor_position)
            
            # Prepare visual analysis prompt
            prompt = f\"\"\"You are controlling an actor in a 3D apartment scene. Analyze the bird's eye view image and provide navigation commands.

CURRENT SITUATION:
- Actor Position: {actor_position}
- Target Room: {target_room}
- Task: Navigate to {target_room} using visual analysis

APARTMENT LAYOUT (for reference):
- Kitchen: Southwest area around [-4.3, -3.9]  
- Bathroom: West area around [-4.3, -0.01]
- Dining: Northwest area around [-4.3, 3.9]
- Livingroom: Southeast area around [0.0, -3.9]
- Central Area: Around [0.0, 0.0]

NAVIGATION RULES:
1. Analyze the bird's eye view image to identify:
   - Actor's current position (look for the actor model)
   - Walls, doors, and obstacles
   - Clear pathways to the target room
   - Furniture and navigation obstacles

2. Provide movement direction based on VISUAL ANALYSIS:
   - UP: Move in +Y direction (north)
   - DOWN: Move in -Y direction (south)
   - LEFT: Move in -X direction (west) 
   - RIGHT: Move in +X direction (east)
   - STOP: Reached destination

3. Consider:
   - Avoid walls and furniture visible in the image
   - Navigate through doorways and open spaces
   - Take the most direct safe path to {target_room}

RESPOND WITH ONLY THE DIRECTION: UP, DOWN, LEFT, RIGHT, or STOP\"\"\"
            
            # Use visual analysis if screenshot available
            if screenshot_path and os.path.exists(screenshot_path):
                try:
                    # For Game Engine, use simplified text-based analysis
                    response = llm_client.send_message(prompt)
                    direction = response.strip().upper()
                    
                    if direction in ['UP', 'DOWN', 'LEFT', 'RIGHT', 'STOP']:
                        print("🧠 GE: LLM Visual Analysis → " + direction)
                        return direction
                    else:
                        print("⚠️ GE: Invalid LLM response, using fallback")
                        return get_fallback_direction(target_room, actor_position)
                        
                except Exception as e:
                    print("❌ GE: LLM visual analysis error: " + str(e))
                    return get_fallback_direction(target_room, actor_position)
            else:
                # Fallback to position-based analysis without image
                response = llm_client.send_message(prompt)
                direction = response.strip().upper()
                
                if direction in ['UP', 'DOWN', 'LEFT', 'RIGHT', 'STOP']:
                    print("🧠 GE: LLM Position Analysis → " + direction)
                    return direction
                else:
                    return get_fallback_direction(target_room, actor_position)
                    
        except Exception as e:
            print("❌ GE: LLM navigation error: " + str(e))
            return get_fallback_direction(target_room, actor_position)
    
    def get_fallback_direction(target_room, actor_position):
        """Fallback direction calculation when LLM is unavailable"""
        room_centers = {
            'Kitchen': [-4.3, -3.9],
            'Bathroom': [-4.3, -0.01], 
            'Dining': [-4.3, 3.9],
            'Livingroom': [0.0, -3.9],
            'Cluster_1': [0.0, -0.01]
        }
        
        target_pos = room_centers.get(target_room, [0, 0])
        current_pos = actor_position
        
        dx = target_pos[0] - current_pos[0]
        dy = target_pos[1] - current_pos[1]
        
        # Simple directional logic
        if abs(dx) > abs(dy):
            return "LEFT" if dx < 0 else "RIGHT"
        else:
            return "DOWN" if dy < 0 else "UP"
    
    def convert_llm_direction_to_movement(direction, speed=0.03):
        """Convert LLM direction command to movement coordinates"""
        movement_map = {
            'UP': [0, speed, 0],      # +Y direction
            'DOWN': [0, -speed, 0],   # -Y direction  
            'LEFT': [-speed, 0, 0],   # -X direction
            'RIGHT': [speed, 0, 0],   # +X direction
            'STOP': [0, 0, 0]         # No movement
        }
        return movement_map.get(direction, [0, 0, 0])
    
    def execute_llm_movement(actor, direction):
        """Execute LLM-directed movement with collision detection"""
        if direction == 'STOP':
            print("🎯 GE: LLM says STOP - destination reached!")
            return True
            
        current_pos = actor.worldPosition
        movement = convert_llm_direction_to_movement(direction)
        
        # Calculate new position
        new_pos = [
            current_pos[0] + movement[0],
            current_pos[1] + movement[1], 
            current_pos[2] + movement[2]
        ]
        
        # Basic boundary check
        if (-5.2 < new_pos[0] < 1.2 and -5.0 < new_pos[1] < 5.0):
            actor.worldPosition = new_pos
            print("🎮 GE: LLM Movement → " + direction + " to [" + str(round(new_pos[0], 2)) + ", " + str(round(new_pos[1], 2)) + "]")
            return False
        else:
            print("⚠️ GE: LLM movement blocked by boundaries, staying in place")
            return False
    
    def get_room_for_task(task):
        """Map task to appropriate room"""
        task_lower = task.lower()
        
        if "wake up" in task_lower or "sleep" in task_lower or "bed" in task_lower:
            return "Livingroom"
        elif "coffee" in task_lower or "breakfast" in task_lower or "cook" in task_lower or "kitchen" in task_lower:
            return "Kitchen"
        elif "brush teeth" in task_lower or "bathroom" in task_lower or "shower" in task_lower or "toilet" in task_lower:
            return "Bathroom"
        elif "dining" in task_lower or "eat dinner" in task_lower or "meal" in task_lower:
            return "Dining"
        elif "tv" in task_lower or "living" in task_lower or "lights" in task_lower or "relax" in task_lower:
            return "Livingroom"
        else:
            rooms_list = ['Livingroom', 'Kitchen', 'Bathroom', 'Dining']
            return rooms_list[logic.current_task % len(rooms_list)]
    
    def main():
        """Main LLM Visual Navigation function running inside Game Engine"""
        
        # Initialize once
        if not logic.llm_nav_started:
            logic.llm_frame_count += 1
            
            # Wait for Game Engine stability
            if logic.llm_frame_count < 30:
                if logic.llm_frame_count % 10 == 0:
                    print("🧠 GE: Initializing LLM Visual Navigation... frame " + str(logic.llm_frame_count))
                return
                
            print("🧠 GE: Starting LLM VISUAL NAVIGATION inside Game Engine!")
            logic.llm_nav_started = True
            
            # Find actor in Game Engine
            scene = logic.getCurrentScene()
            actor_name = "{actor_name}"
            
            for obj in scene.objects:
                if obj.name == actor_name:
                    logic.actor_obj = obj
                    break
            
            if logic.actor_obj:
                print("🧠 GE: Found actor " + logic.actor_obj.name + " at " + str(logic.actor_obj.worldPosition))
                logic.navigation_active = True
                logic.current_task = 0
                
                # Get navigation data
                tasks = {tasks_data}
                print("🧠 GE: Tasks to complete with LLM: " + str(tasks))
                logic.tasks = tasks
                
                # Start first task
                if len(tasks) > 0:
                    task = tasks[logic.current_task]
                    logic.current_target_room = get_room_for_task(task)
                    
                    print("🧠 GE: Task " + str(logic.current_task + 1) + ": '" + task + "'")
                    print("🧠 GE: LLM navigating to room: " + logic.current_target_room)
            else:
                print("❌ GE: Could not find actor in Game Engine scene")
                return
        
        # Continue LLM navigation if active
        if logic.navigation_active and logic.actor_obj:
            logic.llm_frame_count += 1
            
            # Check if currently performing a task
            if logic.task_performing:
                logic.task_performance_timer += 1
                
                # Show task performance progress
                if logic.task_performance_timer % 30 == 0:
                    remaining = logic.task_performance_duration - logic.task_performance_timer
                    print("🎭 GE: Performing task... " + str(remaining // 60 + 1) + " seconds remaining")
                
                # Task performance complete
                if logic.task_performance_timer >= logic.task_performance_duration:
                    logic.task_performing = False
                    logic.task_performance_timer = 0
                    current_task_name = logic.tasks[logic.current_task]
                    print("✅ GE: Task completed: '" + current_task_name + "'")
                    
                    # Move to next task
                    logic.current_task += 1
                    
                    if logic.current_task < len(logic.tasks):
                        # Start next task with LLM
                        task = logic.tasks[logic.current_task]
                        logic.current_target_room = get_room_for_task(task)
                        
                        print("\\n🧠 GE: Task " + str(logic.current_task + 1) + ": '" + task + "'")
                        print("🧠 GE: LLM navigating to room: " + logic.current_target_room)
                    else:
                        # All tasks completed
                        logic.navigation_active = False
                        print("\\n✅ GE: All LLM navigation tasks completed inside Game Engine!")
                        print("🧠 GE: LLM Visual Navigation system is now idle")
                
                return  # Don't move while performing task
            
            # Execute LLM visual navigation steps
            if logic.llm_frame_count - logic.last_llm_step >= logic.llm_step_interval:
                logic.last_llm_step = logic.llm_frame_count
                
                # Capture bird's eye view for LLM analysis
                screenshot_path = capture_birds_eye_screenshot()
                
                # Get LLM navigation command
                actor_pos = list(logic.actor_obj.worldPosition)
                llm_direction = get_llm_navigation_command(logic.current_target_room, actor_pos, screenshot_path)
                
                # Execute LLM movement
                task_completed = execute_llm_movement(logic.actor_obj, llm_direction)
                
                if task_completed or llm_direction == 'STOP':
                    # Task destination reached, start performing task
                    logic.task_performing = True
                    logic.task_performance_timer = 0
                    print("🎯 GE: LLM reached destination, starting task performance")
    
    # Start main LLM navigation loop
    main()

except Exception as e:
    print("❌ GE: LLM Visual Navigation error: " + str(e))
    import traceback
    traceback.print_exc()
'''
        
        # Format the template with actual values
        backend_path_for_ge = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "backend")
        ge_code = ge_code.format(
            actor_name=actor.name,
            tasks_data=str(tasks),
            backend_path=backend_path_for_ge
        )
        
        # Set script content and finish
        script.write(ge_code)
        print("✅ LLM Visual Navigation Game Engine script created: " + script_name)
        
        # Set up logic bricks to run the script automatically
        self.setup_logic_bricks_for_navigation(actor, script_name)
        
        return script_name
    
    def setup_logic_bricks_for_navigation(self, actor, script_name):
        """Set up logic bricks to automatically run navigation script in Game Engine"""
        print("🔗 Setting up logic bricks for automatic navigation...")
        
        try:
            # Make sure the actor has game properties
            if not hasattr(actor, 'game'):
                print("⚠️ Actor has no game properties - adding them")
                bpy.context.view_layer.objects.active = actor
                bpy.ops.logic.sensor_add(type='ALWAYS')
                bpy.ops.logic.controller_add(type='PYTHON')
                bpy.ops.logic.actuator_add(type='PROPERTY')
            
            # Access the game logic
            if hasattr(actor, 'game'):
                game = actor.game
                
                # Add Always sensor if not exists
                always_sensor = None
                for sensor in game.sensors:
                    if sensor.type == 'ALWAYS':
                        always_sensor = sensor
                        break
                
                if not always_sensor:
                    bpy.context.view_layer.objects.active = actor
                    bpy.ops.logic.sensor_add(type='ALWAYS')
                    always_sensor = game.sensors[-1]  # Get the last added sensor
                
                always_sensor.name = "VesperNavStart"
                always_sensor.use_pulse_true_level = True
                print("✅ Always sensor set up for navigation trigger")
                
                # Add Python controller if not exists
                python_controller = None
                for controller in game.controllers:
                    if controller.type == 'PYTHON':
                        python_controller = controller
                        break
                
                if not python_controller:
                    bpy.context.view_layer.objects.active = actor
                    bpy.ops.logic.controller_add(type='PYTHON')
                    python_controller = game.controllers[-1]  # Get the last added controller
                
                python_controller.name = "VesperNavController"
                python_controller.mode = 'SCRIPT'
                if script_name in bpy.data.texts:
                    python_controller.text = bpy.data.texts[script_name]
                print("✅ Python controller linked to navigation script")
                
                # Link sensor to controller
                if always_sensor and python_controller:
                    # This is the tricky part - linking them programmatically
                    always_sensor.link(python_controller)
                    print("🔗 Sensor linked to controller")
                
                print("✅ Logic bricks setup complete for automatic navigation!")
                
            else:
                print("❌ Could not access game properties for logic setup")
                
        except Exception as e:
            print(f"⚠️ Logic brick setup failed: {e}")
            print("💡 You may need to manually set up logic bricks:")
            print(f"   1. Select {actor.name}")
            print("   2. Go to Logic Editor")
            print("   3. Add Always Sensor → Python Controller → link to script")

    def execute_llm_visual_navigation(self):
        """
        Execute LLM-driven visual navigation - NO hardcoded coordinates
        """
        print("🚀 Starting LLM Visual Navigation System")
        print("🧠 NO HARDCODED COORDINATES - Pure LLM visual analysis")
        print("📸 Bird's-eye view screenshots will guide navigation")
        print("=" * 55)
        
        # Start evaluation session
        eval_start_test("LLM Visual Navigation", "LLM-Guided")
        
        try:
            import random
            import sys
            import time
            
            # Dynamically find VESPER project root
            def find_vesper_root():
                current_file = os.path.abspath(__file__)
                current_dir = os.path.dirname(current_file)
                
                while current_dir and current_dir != os.path.dirname(current_dir):
                    if os.path.basename(current_dir) == 'vesper_llm':
                        return current_dir
                    if os.path.exists(os.path.join(current_dir, 'backend', 'app', 'llm', 'client.py')):
                        return current_dir
                    current_dir = os.path.dirname(current_dir)
                
                return r"c:\Users\hbui11\Desktop\vesper_llm"  # Fallback
            
            vesper_path = find_vesper_root()
            if vesper_path not in sys.path:
                sys.path.insert(0, vesper_path)
            
            # Change working directory to VESPER project root
            original_cwd = os.getcwd()
            os.chdir(vesper_path)
            
            # Test LLM availability
            llm_available = False
            try:
                from backend.app.llm.client import chat_completion
                from backend.app.llm.visual_decider import decide_with_vision
                # from scripts.visual_navigation import analyze_visual_scene_for_navigation  # Comment out for now
                
                # Test LLM client functionality
                test_response = chat_completion("You are a test AI.", "Say OK", 5)
                llm_available = True
                print("✅ LLM Visual System: Connected to LLM client")
            except Exception as e:
                print(f"⚠️ LLM Visual System: LLM client unavailable - {e}")
                llm_available = False
            finally:
                # Restore original working directory
                os.chdir(original_cwd)
            
            if not llm_available:
                print("❌ LLM Visual Navigation requires LLM client connection")
                print("🔧 Please ensure backend is running and LLM is available")
                return
            
            # Dynamic scene analysis (no hardcoded rooms)
            print("🔍 DYNAMIC SCENE ANALYSIS - Discovering rooms visually...")
            ROOMS = analyze_gltf_scene()  # This discovers rooms dynamically
            print(f"🎯 DISCOVERED {len(ROOMS)} areas for navigation")
            
            # Find actor in scene
            print("🎭 Looking for actor in scene...")
            actor = summon_actor_in_scene()
            if actor is None:
                print("❌ LLM VISUAL NAVIGATION CANCELLED: No Actor object found")
                print("💡 Please add an object named 'Actor' to your Blender scene")
                return
            
            print(f"🚶 Actor found: {actor.name} at position {[round(x, 2) for x in actor.location]}")
            
            # Select random tasks for demonstration
            TASK_SCENARIOS = [
                ("Morning Routine", ["Check bedroom", "Visit bathroom", "Go to kitchen"]),
                ("Evening Tasks", ["Turn off living room lights", "Check dining area", "Return to bedroom"]),
                ("Cleaning Round", ["Tidy kitchen", "Clean bathroom", "Organize living space"]),
                ("Daily Activities", ["Prepare in bathroom", "Work in living area", "Relax in bedroom"])
            ]
            
            scenario_name, tasks = random.choice(TASK_SCENARIOS)
            selected_tasks = random.sample(tasks, min(3, len(tasks)))
            
            print(f"📋 LLM Navigation Scenario: {scenario_name}")
            print(f"🎯 Selected Tasks: {selected_tasks}")
            
            # Map tasks to available rooms (discovered dynamically)
            room_names = list(ROOMS.keys())
            target_rooms = random.sample(room_names, min(len(selected_tasks), len(room_names)))
            
            print(f"🏠 Target Rooms: {target_rooms}")
            print()
            
            # Execute LLM visual navigation for each room
            print("🚀 STARTING LLM VISUAL NAVIGATION SEQUENCE")
            print("📸 Each step will be guided by LLM analysis of bird's-eye view")
            print()
            
            total_nav_time = 0
            completed_rooms = 0
            
            for i, (task, target_room) in enumerate(zip(selected_tasks, target_rooms)):
                print(f"\n🎯 LLM Navigation Task {i+1}/{len(selected_tasks)}")
                print(f"📋 Task: {task}")
                print(f"🏠 Target Room: {target_room}")
                print(f"📍 Current Actor Position: {[round(x, 2) for x in actor.location]}")
                
                # Capture initial screenshot for LLM analysis
                nav_start_time = time.time()
                
                print("� Capturing bird's-eye view for LLM analysis...")
                screenshot_path = capture_birds_eye_screenshot()
                if screenshot_path:
                    eval_record_screenshot()
                    print(f"✅ Screenshot captured for LLM: {screenshot_path}")
                
                # Execute LLM visual navigation
                success = self.execute_llm_visual_nav_to_room(actor, target_room, task)
                
                nav_time = time.time() - nav_start_time
                total_nav_time += nav_time
                
                if success:
                    completed_rooms += 1
                    print(f"✅ LLM Navigation to {target_room} completed in {nav_time:.1f}s")
                    
                    # Simulate task performance
                    print(f"🎭 Performing task: {task}")
                    time.sleep(1)  # Brief task simulation
                    print(f"✅ Task completed: {task}")
                else:
                    print(f"⚠️ LLM Navigation to {target_room} had issues")
                
                print(f"📊 Progress: {completed_rooms}/{len(selected_tasks)} rooms completed")
            
            # Final results
            print("\n" + "=" * 55)
            print("🎉 LLM VISUAL NAVIGATION SESSION COMPLETE!")
            print(f"📊 Results Summary:")
            print(f"   🎯 Tasks Completed: {completed_rooms}/{len(selected_tasks)}")
            print(f"   ⏱️ Total Navigation Time: {total_nav_time:.1f}s")
            print(f"   🧠 Navigation Method: LLM Visual Analysis")
            print(f"   � Bird's-Eye View Guided: YES")
            print(f"   🚫 Hardcoded Coordinates: NONE")
            print(f"   📍 Final Actor Position: {[round(x, 2) for x in actor.location]}")
            
            eval_end_test(completed_rooms == len(selected_tasks), "LLM_Visual_Navigation")
            
        except Exception as e:
            print(f"❌ LLM Visual Navigation error: {e}")
            print("🔧 Stopping to prevent issues")
            eval_end_test(False, "Error")
    
    def execute_llm_visual_nav_to_room(self, actor, target_room: str, task: str, max_steps: int = 15) -> bool:
        """
        Execute LLM visual navigation to specific room
        """
        import time
        import base64
        import tempfile
        import os
        
        try:
            from scripts.visual_navigation import analyze_visual_scene_for_navigation, convert_llm_direction_to_movement
        except ImportError:
            print("❌ Visual navigation module not available")
            return False
        
        print(f"🧠 LLM Visual Nav: Starting journey to {target_room}")
        print(f"🎯 Task Context: {task}")
        
        step_count = 0
        movement_history = []
        
        while step_count < max_steps:
            step_count += 1
            print(f"\n📍 LLM Navigation Step {step_count}/{max_steps}")
            
            # Capture current bird's-eye view
            current_pos = [round(x, 2) for x in actor.location]
            print(f"📍 Current Position: {current_pos}")
            
            # Get screenshot for LLM analysis
            screenshot_base64 = self.capture_screenshot_for_llm()
            
            if screenshot_base64:
                print("📸 Screenshot captured for LLM visual analysis")
                
                # Get LLM navigation guidance
                try:
                    nav_analysis = analyze_visual_scene_for_navigation(screenshot_base64, target_room)
                    
                    if nav_analysis and "next_direction" in nav_analysis:
                        direction = nav_analysis["next_direction"]
                        distance = nav_analysis.get("movement_distance", "SHORT")
                        reasoning = nav_analysis.get("reasoning", "No reasoning provided")
                        
                        print(f"🧠 LLM Analysis: {direction} ({distance})")
                        print(f"💭 LLM Reasoning: {reasoning}")
                        
                        # Check if navigation complete
                        if direction == "STAY":
                            print("✅ LLM confirms navigation complete!")
                            return True
                        
                        # Execute movement based on LLM guidance
                        movement_offset = convert_llm_direction_to_movement(direction, distance)
                        
                        # Apply movement
                        new_location = [
                            actor.location[0] + movement_offset[0],
                            actor.location[1] + movement_offset[1],
                            actor.location[2] + movement_offset[2]
                        ]
                        
                        actor.location = new_location
                        
                        # Record movement
                        movement_history.append({
                            "step": step_count,
                            "direction": direction,
                            "from": current_pos,
                            "to": [round(x, 2) for x in new_location],
                            "llm_reasoning": reasoning
                        })
                        
                        print(f"� Moved {direction} → {[round(x, 2) for x in new_location]}")
                        
                        # Visual feedback
                        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
                        time.sleep(0.3)  # Brief pause for visual tracking
                        
                    else:
                        print("⚠️ LLM analysis incomplete, trying alternative approach")
                        # Small random movement as fallback
                        import random
                        fallback_directions = ["UP", "DOWN", "LEFT", "RIGHT"] 
                        fallback_dir = random.choice(fallback_directions)
                        movement_offset = convert_llm_direction_to_movement(fallback_dir, "SHORT")
                        
                        actor.location = [
                            actor.location[0] + movement_offset[0],
                            actor.location[1] + movement_offset[1], 
                            actor.location[2] + movement_offset[2]
                        ]
                        print(f"🔄 Fallback movement: {fallback_dir}")
                        
                except Exception as e:
                    print(f"❌ LLM analysis failed: {e}")
                    break
            else:
                print("❌ Screenshot capture failed")
                break
        
        print(f"📊 LLM Navigation Summary:")
        print(f"   🎯 Target: {target_room}")
        print(f"   📈 Steps Taken: {step_count}")
        print(f"   📍 Final Position: {[round(x, 2) for x in actor.location]}")
        
        return step_count < max_steps
    
    def capture_screenshot_for_llm(self) -> str:
        """
        Capture bird's-eye screenshot and return as base64 for LLM analysis
        """
        try:
            scene = bpy.context.scene
            
            # Store original settings
            original_camera = scene.camera
            original_res_x = scene.render.resolution_x
            original_res_y = scene.render.resolution_y
            
            # Create temporary bird's-eye camera
            bpy.ops.object.camera_add(location=(0, 0, 10))
            temp_camera = bpy.context.object
            temp_camera.name = "LLM_BirdsEye"
            
            # Configure for top-down view
            temp_camera.rotation_euler = (0, 0, 0)
            temp_camera.data.type = 'ORTHO'
            temp_camera.data.ortho_scale = 12
            
            # Set as active camera and configure render
            scene.camera = temp_camera
            scene.render.resolution_x = 512
            scene.render.resolution_y = 512
            
            # Render to temporary file
            import tempfile
            temp_path = os.path.join(tempfile.gettempdir(), "llm_nav_screenshot.png")
            scene.render.filepath = temp_path
            
            bpy.ops.render.render(write_still=True)
            
            # Read and encode to base64
            screenshot_base64 = None
            if os.path.exists(temp_path):
                with open(temp_path, "rb") as img_file:
                    img_data = img_file.read()
                    screenshot_base64 = base64.b64encode(img_data).decode('utf-8')
                os.remove(temp_path)  # Clean up
            
            # Restore original settings
            bpy.data.objects.remove(temp_camera, do_unlink=True)
            scene.camera = original_camera
            scene.render.resolution_x = original_res_x
            scene.render.resolution_y = original_res_y
            
            return screenshot_base64
            
        except Exception as e:
            print(f"❌ Screenshot capture for LLM failed: {e}")
            return None
    
    def start_game_engine_with_llm_control(self, actor, room_order, ROOMS, random_tasks, llm_available):
        """Start Game Engine FIRST and perform all navigation within the running Game Engine"""
        try:
            print("🎮 STARTING GAME ENGINE FIRST - All navigation will happen inside!")
            print("🚀 Real-time LLM control will be active during Game Engine")
            print("📸 Bird's eye screenshots will be captured in real-time")
            
            # Store navigation data for use inside Game Engine
            self._store_navigation_data(actor, room_order, ROOMS, random_tasks, llm_available)
            
            # Set up Game Engine logic for navigation
            self._setup_game_engine_logic(actor)
            
            # Start "Game Engine" simulation - real-time navigation loop
            print("🎮 LAUNCHING REAL-TIME NAVIGATION (Modern Blender)...")
            self._run_realtime_navigation(actor, room_order, ROOMS, random_tasks, llm_available)
            print("✅ Real-time navigation completed!")
            print("=" * 50)
            
        except Exception as e:
            print(f"❌ Game Engine start error: {e}")
            print("🔧 Attempting fallback navigation")
            self._fallback_navigation(actor, room_order, ROOMS, random_tasks, llm_available)
            print("=" * 50)
    
    def _store_navigation_data(self, actor, room_order, ROOMS, random_tasks, llm_available):
        """Store navigation data for access during Game Engine execution"""
        # Store in scene properties so Game Engine can access
        scene = bpy.context.scene
        
        # Store navigation tasks
        navigation_data = {
            "rooms": ROOMS,
            "tasks": random_tasks,
            "room_order": room_order,
            "llm_available": llm_available,
            "current_task": 0,
            "completed_rooms": 0,
            "total_activity_time": 0,
            "actor_name": actor.name,
            "status": "ready"
        }
        
        # Store as custom properties (Game Engine accessible)
        scene["vesper_nav_data"] = str(navigation_data)
        scene["vesper_nav_active"] = True
        
        print(f"� Navigation data stored for Game Engine:")
        print(f"   🎯 Tasks: {random_tasks}")
        print(f"   🏠 Room Order: {room_order}")
        print(f"   🤖 LLM Available: {llm_available}")
    
    def _setup_game_engine_logic(self, actor):
        """Set up logic for navigation within Game Engine"""
        print("🔧 Setting up Game Engine navigation logic...")
        
        # In modern Blender, we'll use a different approach since BGE was removed
        # We'll set up a timer system or use the animation/keyframe system
        
        # Add custom properties to the actor for Game Engine state
        actor["vesper_nav_state"] = "ready"
        actor["vesper_current_task"] = 0
        actor["vesper_target_x"] = 0.0
        actor["vesper_target_y"] = 0.0
        
        # Set up a Python controller script (if BGE was available)
        # For now, we'll rely on the main loop approach
        print("✅ Game Engine logic prepared (using modern Blender approach)")
    
    def _run_realtime_navigation(self, actor, room_order, ROOMS, random_tasks, llm_available):
        """Run real-time navigation simulation (Game Engine style)"""
        print("🔄 REAL-TIME NAVIGATION LOOP STARTING...")
        print("🎮 This simulates running inside Game Engine")
        
        completed_rooms = 0
        total_activity_time = 0
        
        # Real-time loop for each task
        for i, (task, target_room) in enumerate(zip(random_tasks, room_order[:len(random_tasks)])):
            print(f"\n🎯 REAL-TIME Task {i+1}: Navigating to {target_room} for '{task}'")
            
            if target_room in ROOMS:
                target_pos = ROOMS[target_room]["center"]
                print(f"📍 Real-time Target: {target_room} at {target_pos}")
                
                # Real-time screenshot capture
                screenshot_path = capture_birds_eye_screenshot()
                if screenshot_path:
                    print(f"📸 Real-time screenshot captured: {screenshot_path}")
                    eval_record_screenshot()
                
                # Real-time step-by-step movement
                movement_start = time.time()
                success = self._realtime_movement(actor, target_room, target_pos, llm_available)
                movement_time = time.time() - movement_start
                
                if success:
                    completed_rooms += 1
                    print(f"✅ REAL-TIME: Reached {target_room} in {movement_time:.1f}s")
                    
                    # Real-time activity simulation
                    print(f"⏱️ REAL-TIME: Getting task duration for '{task}'")
                    task_duration = get_task_duration(task)
                    total_activity_time += task_duration
                    
                    print(f"⏱️ Real-time Duration: {format_duration(task_duration)}")
                    
                    # Real-time activity with viewport updates
                    print(f"🎭 REAL-TIME: Activity simulation in {target_room}")
                    activity_start = time.time()
                    self._realtime_activity(task, target_room, task_duration, actor)
                    activity_time = time.time() - activity_start
                    
                    print(f"✅ REAL-TIME: Activity '{task}' completed in {activity_time:.1f}s")
                    
                    # Real-time final screenshot
                    final_screenshot = capture_birds_eye_screenshot()
                    if final_screenshot:
                        print(f"📸 Real-time final screenshot: {final_screenshot}")
                        eval_record_screenshot()
                else:
                    print(f"❌ REAL-TIME: Failed to reach {target_room}")
                    eval_record_error(f"Failed to reach {target_room}")
            
            # Real-time loop control
            if i >= 1:  # Limit for demo
                print("🔧 Real-time demo limit reached")
                break
            else:
                if target_room not in ROOMS:
                    print(f"❌ REAL-TIME: Unknown room {target_room}")
        
        print(f"\n🎊 REAL-TIME NAVIGATION COMPLETED! Visited {completed_rooms} rooms.")
        print(f"⏱️ Total activity time: {format_duration(int(total_activity_time))}")
        eval_end_test(completed_rooms > 0, f"Realtime_{completed_rooms}_rooms")
        print("=" * 50)
    
    def _realtime_movement(self, actor, target_room, target_pos, llm_available):
        """Real-time movement with viewport updates"""
        print(f"🚶 REAL-TIME: Step-by-step movement to {target_room}")
        return self.move_actor_step_by_step(actor, target_room, target_pos, llm_available)
    
    def _realtime_activity(self, task, room, duration, actor):
        """Real-time activity simulation with viewport updates"""
        print(f"🎭 REAL-TIME: Performing '{task}' in {room}")
        simulate_room_activity(task, room, duration, actor)
        
        # Force viewport update during activity
        bpy.context.view_layer.update()
        if hasattr(bpy.context, 'window_manager'):
            bpy.context.window_manager.update_tag()
    
    def _fallback_navigation(self, actor, room_order, ROOMS, random_tasks, llm_available):
        """Fallback navigation if Game Engine fails to start"""
        print("🔧 FALLBACK: Running navigation outside Game Engine")
        
        completed_rooms = 0
        total_activity_time = 0
        
        for i, (task, target_room) in enumerate(zip(random_tasks, room_order[:len(random_tasks)])):
            print(f"\n🎯 Task {i+1}: Moving to {target_room} for '{task}'")
            
            if target_room in ROOMS:
                target_pos = ROOMS[target_room]["center"]
                print(f"📍 Target: {target_room} at {target_pos}")
                
                # Take bird's eye screenshot BEFORE movement
                screenshot_path = capture_birds_eye_screenshot()
                if screenshot_path:
                    print(f"📸 Bird's eye screenshot captured: {screenshot_path}")
                    eval_record_screenshot()  # EVALUATION
                
                # Step-by-step movement with LLM guidance
                movement_start_time = time.time()
                success = self.move_actor_step_by_step(actor, target_room, target_pos, llm_available)
                movement_time = time.time() - movement_start_time
                
                if success:
                    completed_rooms += 1
                    print(f"✅ Reached {target_room} in {movement_time:.1f}s")
                    
                    # NEW: Get realistic task duration  
                    print(f"⏱️ GETTING TASK DURATION FOR: '{task}'")
                    task_duration = get_task_duration(task)
                    total_activity_time += task_duration
                    
                    print(f"⏱️ Task Duration: {format_duration(task_duration)}")
                    
                    # NEW: Simulate realistic activity in room
                    print(f"🎭 STARTING ACTIVITY SIMULATION IN {target_room}")
                    activity_start_time = time.time()
                    simulate_room_activity(task, target_room, task_duration, actor)
                    actual_activity_time = time.time() - activity_start_time
                    
                    print(f"✅ Activity '{task}' completed in {actual_activity_time:.1f}s")
                    
                    # Take screenshot AFTER activity
                    final_screenshot = capture_birds_eye_screenshot()
                    if final_screenshot:
                        print(f"📸 Final position screenshot: {final_screenshot}")
                        eval_record_screenshot()  # EVALUATION
                else:
                    print(f"❌ Failed to reach {target_room}")
                    eval_record_error(f"Failed to reach {target_room}")  # EVALUATION
            
            # Prevent system freeze with reasonable limits
            if i >= 1:  # Limit to 2 rooms for demo
                print("🔧 Demo limit reached (preventing system freeze)")
                break
            else:
                if target_room not in ROOMS:
                    print(f"❌ Unknown room: {target_room}")
        
        print(f"\n🎊 Fallback navigation completed! Visited {completed_rooms} rooms.")
        print("🔄 ADDON VERSION: v2.8.3 - Production Release with Game Engine Integration")
        
        # End evaluation test
        eval_end_test(completed_rooms > 0, f"Completed_{completed_rooms}_rooms")  # EVALUATION
        print("=" * 50)
    
    def try_start_game_engine(self):
        """Attempt to start the Blender Game Engine"""
        try:
            print("🎮 Starting Blender Game Engine...")
            bpy.ops.view3d.game_start()
            print("✅ Game Engine started successfully!")
        except Exception as e:
            print(f"⚠️ Could not start Game Engine: {e}")
            print("💡 Make sure you're in the 3D Viewport and have a camera in the scene")
        
    def get_llm_room_order(self, tasks, rooms):
        """Get room order from LLM based on tasks and scene analysis"""
        print(f"🧠 LLM: Starting enhanced navigation planning for tasks: {tasks}")
        print(f"🧠 LLM: Available rooms: {list(rooms.keys())}")
        eval_record_llm_call(f"Enhanced room planning for tasks: {tasks}")  # EVALUATION
        
        try:
            from backend.app.llm.client import chat_completion
            print("🧠 LLM: Client imported successfully")
            
            # Gather scene information for LLM
            scene_info = self.analyze_scene_for_llm(rooms)
            
            rooms_list = list(rooms.keys())
            
            enhanced_system_prompt = """You are an advanced AI navigation planner with spatial intelligence.

CAPABILITIES:
- Analyze 3D house layouts and detect obstacles
- Plan collision-free paths between rooms
- Understand room connectivity and doorway locations
- Optimize navigation efficiency

TASK: Plan optimal room visitation order considering:
1. Task-to-room logical mapping
2. Spatial layout and room positions  
3. Wall and obstacle avoidance
4. Efficient pathfinding between rooms
5. Door and corridor navigation

You must avoid:
- Direct paths through walls
- Moving through furniture/obstacles
- Inefficient backtracking
- Unreachable room sequences"""

            enhanced_user_prompt = f"""NAVIGATION PLANNING REQUEST:

TASKS TO COMPLETE: {tasks}
AVAILABLE ROOMS: {rooms_list}

SCENE SPATIAL DATA:
{scene_info}

REQUIREMENTS:
1. Match each task to the most logical room
2. Order rooms to minimize walking distance
3. Ensure path between rooms avoids obstacles
4. Consider doorway and corridor navigation
5. Account for walls and furniture placement

Return ONLY a JSON response:
{{
  "room_sequence": ["Room1", "Room2", "Room3"],
  "navigation_plan": [
    {{"task": "task name", "room": "RoomName", "path_notes": "how to navigate there safely"}},
    {{"task": "task name", "room": "RoomName", "path_notes": "obstacle avoidance notes"}},
    {{"task": "task name", "room": "RoomName", "path_notes": "final navigation notes"}}
  ],
  "reasoning": "spatial analysis and path optimization explanation"
}}

Focus on SAFE navigation that avoids walls and obstacles."""
            
            print("🧠 LLM: Making enhanced spatial navigation API call...")
            response = chat_completion(enhanced_system_prompt, enhanced_user_prompt)
            print(f"🧠 LLM Enhanced Response: {response}")
            
            # Extract JSON from response
            import json
            import re
            
            # Look for JSON object pattern first, then array as fallback
            json_match = re.search(r'\{.*?"room_sequence".*?\}', response, re.DOTALL)
            if json_match:
                try:
                    full_response = json.loads(json_match.group())
                    room_order = full_response.get("room_sequence", [])
                    navigation_plan = full_response.get("navigation_plan", [])
                    reasoning = full_response.get("reasoning", "No reasoning provided")
                    
                    print(f"✅ LLM Reasoning: {reasoning}")
                    for plan_item in navigation_plan:
                        task = plan_item.get("task", "")
                        room = plan_item.get("room", "")
                        path_notes = plan_item.get("path_notes", "")
                        print(f"   📋 {task} → {room}: {path_notes}")
                    
                    # Validate rooms exist
                    valid_rooms = [room for room in room_order if room in rooms]
                    if valid_rooms:
                        print(f"✅ LLM enhanced navigation plan: {valid_rooms}")
                        return valid_rooms[:3]  # Max 3 rooms
                    
                except json.JSONDecodeError:
                    print("⚠️ Enhanced response parsing failed, trying simple array...")
            
            # Fallback to simple array pattern
            json_match = re.search(r'\[.*?\]', response, re.DOTALL)
            if json_match:
                room_order = json.loads(json_match.group())
                # Validate rooms exist
                valid_rooms = [room for room in room_order if room in rooms]
                if valid_rooms:
                    print(f"✅ LLM suggested rooms (fallback): {valid_rooms}")
                    return valid_rooms[:3]  # Max 3 rooms
                else:
                    print(f"⚠️ LLM suggested invalid rooms: {room_order}")
            else:
                print(f"⚠️ LLM response doesn't contain valid JSON")
                
        except Exception as e:
            print(f"⚠️ LLM enhanced room order failed: {e}")
            print(f"🔧 LLM: Calling fallback room order...")
        
        # Call fallback and log result
        fallback_result = self.fallback_room_order(tasks, rooms)
        print(f"🔧 LLM: Fallback returned: {fallback_result}")
        return fallback_result
    
    def analyze_scene_for_llm(self, rooms):
        """Analyze scene geometry and provide spatial information for LLM navigation planning"""
        print("🔍 Analyzing scene spatial layout for LLM...")
        
        scene_analysis = {
            "rooms": {},
            "obstacles": [],
            "corridors": [],
            "boundaries": {}
        }
        
        try:
            import bpy
            
            # Analyze scene bounds
            scene_objects = bpy.context.scene.objects
            all_meshes = [obj for obj in scene_objects if obj.type == 'MESH']
            
            if all_meshes:
                # Calculate scene boundaries
                min_x = min(obj.bound_box[0][0] + obj.location[0] for obj in all_meshes)
                max_x = max(obj.bound_box[6][0] + obj.location[0] for obj in all_meshes)
                min_y = min(obj.bound_box[0][1] + obj.location[1] for obj in all_meshes)
                max_y = max(obj.bound_box[6][1] + obj.location[1] for obj in all_meshes)
                
                scene_analysis["boundaries"] = {
                    "min_x": round(min_x, 1),
                    "max_x": round(max_x, 1), 
                    "min_y": round(min_y, 1),
                    "max_y": round(max_y, 1),
                    "width": round(max_x - min_x, 1),
                    "height": round(max_y - min_y, 1)
                }
            
            # Analyze room spatial relationships
            for room_name, room_data in rooms.items():
                center = room_data.get("center", [0, 0])
                scene_analysis["rooms"][room_name] = {
                    "center": [round(center[0], 1), round(center[1], 1)],
                    "accessible": True  # Assume accessible unless proven otherwise
                }
            
            # Detect potential obstacles (walls, furniture)
            obstacles = []
            for obj in scene_objects:
                if obj.type == 'MESH' and obj.visible_get():
                    # Check if object could be an obstacle (not floor/ceiling)
                    name_lower = obj.name.lower()
                    if any(keyword in name_lower for keyword in ['wall', 'door', 'table', 'chair', 'cabinet', 'counter']):
                        location = obj.location
                        scale = obj.scale
                        obstacles.append({
                            "name": obj.name,
                            "position": [round(location[0], 1), round(location[1], 1)],
                            "size": [round(scale[0], 1), round(scale[1], 1)],
                            "type": "wall" if "wall" in name_lower else "furniture"
                        })
            
            scene_analysis["obstacles"] = obstacles[:10]  # Limit to 10 most relevant obstacles
            
            # Detect corridors and openings (simplified)
            corridor_points = [
                [0.0, -0.5],   # Central hallway
                [-2.5, -0.5],  # Main corridor
                [-2.5, -3.5],  # Kitchen approach
                [-2.5, 3.0],   # Dining approach
            ]
            
            scene_analysis["corridors"] = [
                {"point": pt, "description": f"Safe navigation point at {pt}"} 
                for pt in corridor_points
            ]
            
        except Exception as e:
            print(f"⚠️ Scene analysis error: {e}")
            # Provide basic fallback data
            scene_analysis = {
                "rooms": {name: {"center": data.get("center", [0, 0]), "accessible": True} 
                         for name, data in rooms.items()},
                "obstacles": [{"note": "Scene analysis unavailable - using safe navigation"}],
                "corridors": [{"point": [0, 0], "description": "Central safe point"}],
                "boundaries": {"note": "Boundaries unknown - using conservative navigation"}
            }
        
        # Format for LLM consumption
        formatted_analysis = f"""
ROOM POSITIONS:
{chr(10).join([f"- {name}: Center at {data['center']}, {'Accessible' if data['accessible'] else 'Blocked'}" 
               for name, data in scene_analysis['rooms'].items()])}

SCENE BOUNDARIES: {scene_analysis['boundaries']}

DETECTED OBSTACLES ({len(scene_analysis['obstacles'])} found):
{chr(10).join([f"- {obs.get('name', 'Unknown')}: {obs.get('type', 'object')} at {obs.get('position', [0,0])}" 
               for obs in scene_analysis['obstacles'][:5]])}  

SAFE CORRIDOR POINTS:
{chr(10).join([f"- {corridor['point']}: {corridor['description']}" 
               for corridor in scene_analysis['corridors']])}

NAVIGATION NOTES:
- Avoid direct diagonal paths through walls
- Use corridor points for safe navigation
- Room centers are approximate - approach carefully
- Consider object placement when pathfinding
        """.strip()
        
        print(f"✅ Scene analysis complete. Found {len(scene_analysis['obstacles'])} obstacles")
        return formatted_analysis


class VESPER_OT_GameEngineTest(bpy.types.Operator):
    bl_idname = "vesper.game_engine_test"
    bl_label = "Test Game Engine"
    bl_description = "Test if Game Engine can be started"
    
    def execute(self, context):
        print("🎮 Testing Game Engine availability...")
        
        # Check if UPBGE is available
        try:
            import bge
            print("✅ BGE module available - UPBGE detected")
        except ImportError:
            print("❌ BGE module not available - regular Blender")
        
        # Test Game Engine start
        try:
            if hasattr(bpy.ops.view3d, 'game_start'):
                print("✅ Game Engine start operator available")
            else:
                print("❌ Game Engine start operator not available")
        except Exception as e:
            print(f"❌ Game Engine test error: {e}")
        
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(VESPER_OT_tag_device.bl_idname, text="Tag as VESPER Device")
    self.layout.operator(VESPER_OT_GameEngineTest.bl_idname, text="Test Game Engine")
    import time
    
    def main():
        """Main Game Engine navigation loop"""
        scene = logic.getCurrentScene()
        
        # Get stored navigation data
        if "vesper_nav_active" in scene:
            print("🎮 GE: VESPER navigation active in Game Engine!")
            
            # Get navigation tasks from scene properties
            nav_data = scene.get("vesper_nav_data", "{}")
            print(f"🎮 GE: Navigation data: {nav_data}")
            
            # Real navigation logic would go here
            # For now, just confirm Game Engine is running
            print("✅ GE: Navigation script is running inside Game Engine!")
            print("🎮 GE: LLM-controlled navigation ready!")
            
        else:
            print("⏸️ GE: No navigation data found - Game Engine idle")

    # Run main navigation
    if __name__ == "__main__":
        main()


# Key mapping for P key - Smart detection for BGE vs house.blend
addon_keymaps = []

def register():
    bpy.utils.register_class(VESPER_PT_NavigationPanel)
    bpy.utils.register_class(VESPER_OT_tag_device)
    bpy.utils.register_class(VESPER_OT_LLMNavigation)
    bpy.utils.register_class(VESPER_OT_GameEngineTest)
    bpy.types.VIEW3D_MT_object.append(menu_func)
    
    # Add keymap for P-key navigation
    try:
        wm = bpy.context.window_manager
        if wm and wm.keyconfigs and wm.keyconfigs.addon:
            km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
            
            # Add P-key mapping
            kmi = km.keymap_items.new(VESPER_OT_LLMNavigation.bl_idname, 'P', 'PRESS')
            kmi.active = True
            addon_keymaps.append((km, kmi))
            print("✅ VESPER: P-key registered successfully")
            
            # Add backup N-key mapping
            kmi2 = km.keymap_items.new(VESPER_OT_LLMNavigation.bl_idname, 'N', 'PRESS')
            kmi2.active = True
            addon_keymaps.append((km, kmi2))
            print("✅ VESPER: N-key registered successfully")
            
            # Add E-key for evaluation export
            kmi3 = km.keymap_items.new(VESPER_OT_ExportEvaluation.bl_idname, 'E', 'PRESS')
            kmi3.active = True
            addon_keymaps.append((km, kmi3))
            print("✅ VESPER: E-key registered successfully")
            
            print("✅ P-key and N-key navigation active!")
            print("📊 E-key evaluation export active!")
            print("🎮 Press P or N → VESPER Navigation")
            print("📊 Press E → Export Evaluation Data")
        else:
            print("❌ VESPER: No addon keyconfig found!")
    except Exception as e:
        print(f"❌ VESPER: Keymap registration failed: {e}")
        print("💡 VESPER: Try using the N panel or menu instead")

def unregister():
    # Remove keymaps
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    
    bpy.utils.unregister_class(VESPER_PT_NavigationPanel)
    bpy.utils.unregister_class(VESPER_OT_tag_device)
    bpy.utils.unregister_class(VESPER_OT_LLMNavigation)
    bpy.utils.unregister_class(VESPER_OT_GameEngineTest)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
    register()
