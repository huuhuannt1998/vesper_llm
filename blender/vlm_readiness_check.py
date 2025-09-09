"""
Quick VLM Motion Testing Readiness Check
Run this in Blender's Script Editor to check scene setup
"""

import bpy

def check_vlm_readiness():
    print("🔍 VLM Motion Testing Readiness Check")
    print("=" * 50)
    
    # Check for Actor
    actor = None
    for obj in bpy.data.objects:
        if "actor" in obj.name.lower():
            actor = obj
            break
    
    if actor:
        print(f"✅ Actor found: {actor.name} at {[f'{v:.1f}' for v in actor.location]}")
    else:
        print("❌ No Actor object found")
        print("   → Add a cube and name it 'Actor'")
    
    # Check for Motion Sensors
    motion_sensors = []
    for obj in bpy.data.objects:
        if "motion" in obj.name.lower() and "sensor" in obj.name.lower():
            motion_sensors.append(obj)
    
    print(f"\n📡 Motion Sensors: {len(motion_sensors)} found")
    for sensor in motion_sensors:
        print(f"   ✅ {sensor.name} at {[f'{v:.1f}' for v in sensor.location]}")
    
    if len(motion_sensors) == 0:
        print("   ❌ No motion sensors found")
        print("   → Use VESPER panel to add motion sensors")
    
    # Check for Detection Areas
    detection_areas = []
    for obj in bpy.data.objects:
        if "detection" in obj.name.lower() and "area" in obj.name.lower():
            detection_areas.append(obj)
    
    print(f"\n🔍 Detection Areas: {len(detection_areas)} found")
    for area in detection_areas:
        print(f"   ✅ {area.name}")
    
    # Check for BGE Controller
    controller = None
    for obj in bpy.data.objects:
        if "controller" in obj.name.lower() and "motion" in obj.name.lower():
            controller = obj
            break
    
    if controller:
        print(f"\n🎮 BGE Controller: ✅ {controller.name}")
        
        # Check BGE logic bricks
        if hasattr(controller, 'game'):
            sensors_count = len(controller.game.sensors)
            controllers_count = len(controller.game.controllers)
            actuators_count = len(controller.game.actuators)
            print(f"   Logic Bricks: {sensors_count} sensors, {controllers_count} controllers, {actuators_count} actuators")
        
    else:
        print("\n🎮 BGE Controller: ❌ Not found")
        print("   → Use 'Create Controller' button in VESPER panel")
    
    # Check for BGE script
    bge_script = bpy.data.texts.get("bge_motion_detection.py")
    if bge_script:
        print(f"\n📜 BGE Script: ✅ Found in Text Editor")
    else:
        print(f"\n📜 BGE Script: ❌ Not found")
        print("   → Use 'Setup BGE' button in VESPER panel")
    
    # Overall readiness
    print("\n" + "=" * 50)
    ready_components = [
        actor is not None,
        len(motion_sensors) > 0,
        controller is not None,
        bge_script is not None
    ]
    
    readiness_score = sum(ready_components)
    total_components = len(ready_components)
    
    if readiness_score == total_components:
        print("🎉 READY FOR VLM TESTING!")
        print("   → Press P to enter Game Engine")
        print("   → Move Actor to test motion detection")
    else:
        print(f"⚠️ SETUP INCOMPLETE: {readiness_score}/{total_components} components ready")
        print("   → Complete missing components above")
    
    return readiness_score == total_components

# Run the check
if __name__ == "__main__":
    check_vlm_readiness()
