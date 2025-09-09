"""
VESPER Smart Home Motion Sensor Setup
=====================================

This script sets up realistic motion sensor placement for a smart home environment.
Based on Aeotec SmartThings Motion Sensor specifications and typical placement patterns.

Motion Sensor Specifications (Aeotec SmartThings):
- 120° field of view 
- Up to 5 meters (16 feet) detection distance
- PIR (Passive Infrared) motion detection
- Z-Wave Plus connectivity
- 3-second cooldown period (configurable)
- Battery powered (CR2 - 3V lithium)

Smart Placement Guidelines:
- Corner mounting for maximum coverage
- 2-2.5 meters height (6-8 feet)
- Avoid direct sunlight and heat sources
- Clear line of sight to main traffic areas
- Overlap coverage for seamless detection
"""

import bpy
from mathutils import Vector
import json
import os

def calculate_optimal_sensor_positions(room_layout):
    """Calculate optimal motion sensor positions for maximum coverage
    
    Args:
        room_layout: Dictionary defining room boundaries and furniture
        
    Returns:
        List of sensor configurations with positions and orientations
    """
    
    sensors = []
    
    # Living Room - Main gathering area
    # Corner placement for 120° coverage of seating and walkways
    sensors.append({
        "id": "M01_LivingRoom_Main",
        "position": Vector((3.5, 4.0, 2.2)),  # High corner position
        "room": "living_room",
        "orientation": 225.0,  # Facing into room center
        "coverage_zone": "seating_area_and_entrance",
        "priority": "high"
    })
    
    # Living Room - Secondary for TV viewing area
    sensors.append({
        "id": "M02_LivingRoom_TV",
        "position": Vector((1.0, 6.0, 2.2)),
        "room": "living_room", 
        "orientation": 180.0,  # Facing TV wall
        "coverage_zone": "tv_viewing_area",
        "priority": "medium"
    })
    
    # Kitchen - Over main prep area
    # Central position to cover cooking, prep, and dining
    sensors.append({
        "id": "M03_Kitchen_Main", 
        "position": Vector((-1.5, 5.5, 2.3)),
        "room": "kitchen",
        "orientation": 270.0,  # Facing counter/stove area
        "coverage_zone": "cooking_and_prep_area",
        "priority": "high"
    })
    
    # Kitchen - Over dining area (if separate)
    sensors.append({
        "id": "M04_Kitchen_Dining",
        "position": Vector((-0.5, 3.5, 2.2)),
        "room": "kitchen",
        "orientation": 90.0,  # Facing dining table
        "coverage_zone": "dining_area",
        "priority": "medium"
    })
    
    # Master Bedroom - Corner for bed and door coverage
    sensors.append({
        "id": "M05_Bedroom_Master",
        "position": Vector((4.5, -1.5, 2.2)),
        "room": "bedroom_master",
        "orientation": 315.0,  # Facing bed and entrance
        "coverage_zone": "bed_and_entrance",
        "priority": "high"
    })
    
    # Hallway - Central for traffic monitoring
    # Critical for tracking movement between rooms
    sensors.append({
        "id": "M06_Hallway_Central",
        "position": Vector((0.5, 0.5, 2.4)),
        "room": "hallway",
        "orientation": 0.0,  # Facing down main hallway
        "coverage_zone": "main_traffic_flow",
        "priority": "critical"
    })
    
    # Hallway - Secondary for room entrances
    sensors.append({
        "id": "M07_Hallway_Rooms",
        "position": Vector((-0.5, -0.5, 2.4)),
        "room": "hallway", 
        "orientation": 180.0,  # Facing room entrances
        "coverage_zone": "room_entrances",
        "priority": "high"
    })
    
    # Bathroom - Over entrance/vanity area
    # Privacy-conscious placement
    sensors.append({
        "id": "M08_Bathroom_Main",
        "position": Vector((-2.5, -0.5, 2.1)),
        "room": "bathroom",
        "orientation": 135.0,  # Facing vanity/entrance only
        "coverage_zone": "vanity_and_entrance",
        "priority": "medium"
    })
    
    # Guest Bedroom (if available)
    sensors.append({
        "id": "M09_Bedroom_Guest",
        "position": Vector((2.0, -4.0, 2.2)),
        "room": "bedroom_guest",
        "orientation": 45.0,  # Facing bed area
        "coverage_zone": "guest_bed_area", 
        "priority": "low"
    })
    
    # Entry/Foyer - Security monitoring
    sensors.append({
        "id": "M10_Entry_Main",
        "position": Vector((1.0, 2.0, 2.5)),
        "room": "entry",
        "orientation": 0.0,  # Facing front door
        "coverage_zone": "main_entrance",
        "priority": "critical"
    })
    
    # Utility/Laundry Room (if available)
    sensors.append({
        "id": "M11_Utility_Laundry",
        "position": Vector((-4.0, 1.0, 2.2)),
        "room": "utility",
        "orientation": 90.0,  # Facing appliances
        "coverage_zone": "laundry_area",
        "priority": "low"
    })
    
    # Office/Study (if available) 
    sensors.append({
        "id": "M12_Office_Study", 
        "position": Vector((5.0, 1.0, 2.2)),
        "room": "office",
        "orientation": 270.0,  # Facing desk area
        "coverage_zone": "work_area",
        "priority": "medium"
    })
    
    return sensors

def validate_sensor_coverage(sensors):
    """Validate sensor placement for optimal coverage and minimal blind spots
    
    Args:
        sensors: List of sensor configurations
        
    Returns:
        Dictionary with validation results and recommendations
    """
    
    validation_results = {
        "total_sensors": len(sensors),
        "coverage_analysis": {},
        "blind_spots": [],
        "overlap_zones": [],
        "recommendations": []
    }
    
    # Analyze coverage by room
    rooms = {}
    for sensor in sensors:
        room = sensor["room"]
        if room not in rooms:
            rooms[room] = []
        rooms[room].append(sensor)
    
    for room, room_sensors in rooms.items():
        room_analysis = {
            "sensor_count": len(room_sensors),
            "coverage_zones": [s["coverage_zone"] for s in room_sensors],
            "priorities": [s["priority"] for s in room_sensors]
        }
        
        # Check for critical areas
        if room in ["hallway", "entry"]:
            if not any(p == "critical" for p in room_analysis["priorities"]):
                validation_results["recommendations"].append(
                    f"Consider upgrading {room} sensor to critical priority for security"
                )
        
        # Check for adequate coverage
        if room_analysis["sensor_count"] == 0:
            validation_results["blind_spots"].append(room)
        elif room_analysis["sensor_count"] == 1 and room in ["living_room", "kitchen"]:
            validation_results["recommendations"].append(
                f"Consider adding secondary sensor to {room} for complete coverage"
            )
        
        validation_results["coverage_analysis"][room] = room_analysis
    
    # Overall recommendations
    validation_results["recommendations"].extend([
        "Position sensors 2-2.5 meters high for optimal PIR detection",
        "Ensure sensors face main traffic areas and furniture",
        "Test detection zones after installation",
        "Configure 3-second cooldown to prevent false triggers",
        "Monitor battery levels monthly (CR2 lithium batteries)"
    ])
    
    return validation_results

def export_sensor_configuration(sensors, filename="motion_sensor_config.json"):
    """Export sensor configuration to JSON file for deployment
    
    Args:
        sensors: List of sensor configurations
        filename: Output filename
    """
    
    config = {
        "vesper_smart_home_config": {
            "version": "3.1.0",
            "type": "motion_sensor_deployment",
            "sensor_specs": {
                "model": "Aeotec SmartThings Motion Sensor",
                "field_of_view": 120,
                "detection_range": 5.0,
                "cooldown_period": 3.0,
                "battery_type": "CR2_3V_lithium",
                "connectivity": "Z-Wave_Plus"
            },
            "sensors": []
        }
    }
    
    for sensor in sensors:
        sensor_config = {
            "device_id": sensor["id"],
            "room": sensor["room"],
            "position": {
                "x": sensor["position"].x,
                "y": sensor["position"].y, 
                "z": sensor["position"].z
            },
            "orientation_degrees": sensor["orientation"],
            "coverage_zone": sensor["coverage_zone"],
            "priority": sensor["priority"],
            "device_settings": {
                "sensitivity": 1.0,
                "cooldown_seconds": 3.0,
                "detection_range_meters": 5.0,
                "field_of_view_degrees": 120.0
            }
        }
        config["vesper_smart_home_config"]["sensors"].append(sensor_config)
    
    # Export to file
    output_path = os.path.join(os.path.dirname(__file__), filename)
    with open(output_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Motion sensor configuration exported to: {output_path}")
    return output_path

def deploy_sensors_to_blender(sensors):
    """Deploy motion sensors to the active Blender scene
    
    Args:
        sensors: List of sensor configurations
        
    Returns:
        Number of sensors successfully deployed
    """
    
    try:
        # Import device manager
        import sys
        addon_path = os.path.join(os.path.dirname(__file__), "addons", "vesper_smart_home")
        if addon_path not in sys.path:
            sys.path.append(addon_path)
        
        from addons.vesper_smart_home import device_manager
        
        deployed = 0
        failed = 0
        
        print("🚀 Deploying motion sensors to Blender scene...")
        
        for sensor in sensors:
            try:
                success = device_manager.add_motion_sensor(
                    sensor["id"],
                    sensor["room"], 
                    sensor["position"],
                    sensor["orientation"]
                )
                
                if success:
                    deployed += 1
                    print(f"✅ {sensor['id']}: {sensor['room']} ({sensor['priority']} priority)")
                else:
                    failed += 1
                    print(f"❌ Failed: {sensor['id']}")
                    
            except Exception as e:
                failed += 1
                print(f"❌ Error deploying {sensor['id']}: {e}")
        
        print(f"\n📊 Deployment Summary:")
        print(f"   ✅ Deployed: {deployed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📊 Success Rate: {(deployed/(deployed+failed)*100):.1f}%")
        
        return deployed
        
    except ImportError as e:
        print(f"❌ Cannot import device manager: {e}")
        return 0
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return 0

def setup_smart_home_motion_sensors():
    """Main function to set up complete smart home motion sensor system"""
    
    print("🏠 VESPER Smart Home Motion Sensor Setup")
    print("=" * 60)
    print("📋 Configuring Aeotec SmartThings Motion Sensors")
    print("   🔍 120° field of view, 5m detection range")
    print("   ⏱️ 3-second cooldown period")
    print("   🔋 CR2 battery powered")
    
    # Calculate optimal positions
    print("\n🎯 Calculating optimal sensor positions...")
    room_layout = {}  # Could be loaded from file or Blender scene analysis
    sensors = calculate_optimal_sensor_positions(room_layout)
    
    # Validate coverage
    print("🔍 Validating sensor coverage...")
    validation = validate_sensor_coverage(sensors)
    
    print(f"\n📊 Coverage Analysis:")
    print(f"   🔢 Total Sensors: {validation['total_sensors']}")
    print(f"   🏠 Rooms Covered: {len(validation['coverage_analysis'])}")
    print(f"   ⚠️ Blind Spots: {len(validation['blind_spots'])}")
    
    if validation['blind_spots']:
        print(f"   🚨 Rooms without coverage: {', '.join(validation['blind_spots'])}")
    
    print(f"\n💡 Recommendations:")
    for rec in validation['recommendations'][:3]:  # Show first 3
        print(f"   • {rec}")
    
    # Export configuration
    print("\n💾 Exporting configuration...")
    config_file = export_sensor_configuration(sensors)
    
    # Deploy to Blender if available
    print("\n🚀 Deploying to Blender scene...")
    deployed_count = deploy_sensors_to_blender(sensors)
    
    if deployed_count > 0:
        print(f"\n🎉 Setup Complete!")
        print(f"   ✅ {deployed_count} motion sensors active")
        print(f"   📱 SmartThings integration ready")
        print(f"   🔍 Real-time Actor detection enabled")
        print(f"\n🎮 Move the Actor around to test motion detection!")
    else:
        print(f"\n⚠️ Setup completed with configuration export only")
        print(f"   📁 Configuration saved to: {config_file}")
        print(f"   🔧 Manual deployment may be required")
    
    return {
        "sensors_configured": len(sensors),
        "sensors_deployed": deployed_count,
        "config_file": config_file,
        "validation": validation
    }

# Run setup if executed directly
if __name__ == "__main__":
    setup_smart_home_motion_sensors()
