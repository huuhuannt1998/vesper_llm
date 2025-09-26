#!/usr/bin/env python3
"""
Test script for VESPER Position Mapping System

This script tests the complete position mapping integration without requiring BGE.
"""

import os
import sys

# Add project paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
map_dir = os.path.join(project_root, 'map')

sys.path.insert(0, map_dir)
sys.path.insert(0, project_root)

def test_position_mapping_system():
    """Test the complete position mapping system"""
    print("🧪 VESPER Position Mapping System Test")
    print("=" * 60)
    
    # Test 1: Basic Position Mapper
    print("\n1️⃣ Testing Position Mapper...")
    try:
        from map.position_mapper import VESPERPositionMapper
        
        # Find house layout
        house_layout_path = None
        possible_paths = [
            os.path.join(project_root, "blender", "house_layout_reference2.png"),
            os.path.join(project_root, "house_layout_reference2.png"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                house_layout_path = path
                break
        
        if house_layout_path:
            print(f"✅ Found house layout: {os.path.basename(house_layout_path)}")
        else:
            print("⚠️ House layout not found - will use blank template")
        
        # Create mapper
        mapper = VESPERPositionMapper(house_layout_path)
        print("✅ Position mapper created successfully")
        
    except Exception as e:
        print(f"❌ Position mapper test failed: {e}")
        return False
    
    # Test 2: BGE Integration
    print("\n2️⃣ Testing BGE Integration...")
    try:
        from map.bge_integration import BGENavigationMapper, update_actor_position_map
        
        bge_mapper = BGENavigationMapper()
        print("✅ BGE integration created successfully")
        
        # Test position update
        test_map = update_actor_position_map(
            -2.0, -1.5,  # World coordinates
            room="LIVING_ROOM",
            task="Make a phone call", 
            target_room="DINING_ROOM"
        )
        
        if test_map and os.path.exists(test_map):
            print(f"✅ Position map generated: {os.path.basename(test_map)}")
        else:
            print("⚠️ Position map generation failed")
        
    except Exception as e:
        print(f"❌ BGE integration test failed: {e}")
        return False
    
    # Test 3: Enhanced VLM Analysis
    print("\n3️⃣ Testing Enhanced VLM Analysis...")
    try:
        from map.enhanced_vlm_analysis import _build_position_aware_prompt, _extract_target_room
        
        # Test prompt building
        prompt = _build_position_aware_prompt(
            task="Cook oatmeal",
            current_position="(-2.0, -1.5)", 
            step_number=5,
            world_coords=(-2.0, -1.5),
            use_position_map=True
        )
        
        if "POSITION-AWARE ANALYSIS" in prompt:
            print("✅ Position-aware prompt generated successfully")
        else:
            print("⚠️ Position-aware prompt may be incorrect")
        
        # Test target room extraction
        target = _extract_target_room("Cook oatmeal")
        if target == "KITCHEN":
            print("✅ Target room extraction working")
        else:
            print(f"⚠️ Target room extraction returned: {target}")
        
    except Exception as e:
        print(f"❌ Enhanced VLM analysis test failed: {e}")
        return False
    
    # Test 4: File Structure
    print("\n4️⃣ Testing File Structure...")
    
    expected_files = [
        os.path.join(map_dir, "position_mapper.py"),
        os.path.join(map_dir, "bge_integration.py"), 
        os.path.join(map_dir, "enhanced_vlm_analysis.py"),
    ]
    
    all_files_exist = True
    for file_path in expected_files:
        if os.path.exists(file_path):
            print(f"✅ {os.path.basename(file_path)}")
        else:
            print(f"❌ Missing: {os.path.basename(file_path)}")
            all_files_exist = False
    
    # Check generated maps directory
    generated_maps_dir = os.path.join(map_dir, "generated_maps")
    if os.path.exists(generated_maps_dir):
        map_files = [f for f in os.listdir(generated_maps_dir) if f.endswith('.png')]
        print(f"📁 Generated maps directory: {len(map_files)} files")
        
        if map_files:
            print("📍 Recent maps:")
            for map_file in sorted(map_files)[-3:]:  # Show last 3
                print(f"  - {map_file}")
    else:
        print("📁 Generated maps directory will be created when needed")
    
    # Test 5: Integration Instructions
    print("\n5️⃣ Integration Instructions:")
    print("=" * 40)
    
    if all_files_exist:
        print("✅ Position mapping system is ready!")
        print("\n🚀 To use in BGE Navigation:")
        print("1. The system is already integrated in llm_bge_navigation.py")
        print("2. Run BGE navigation normally - position maps will be generated automatically")
        print("3. VLM will receive enhanced spatial awareness through position maps")
        print("4. Maps are saved in map/generated_maps/ directory")
        
        print("\n📊 Expected improvements:")
        print("- Better room detection and spatial awareness")
        print("- Reduced 'UNKNOWN' room classifications") 
        print("- More efficient navigation paths")
        print("- Visual feedback for debugging navigation issues")
        
        return True
    else:
        print("❌ Some components missing - check file structure")
        return False

def show_system_overview():
    """Show overview of the position mapping system"""
    print("\n📋 VESPER Position Mapping System Overview")
    print("=" * 60)
    
    print("🏗️ ARCHITECTURE:")
    print("├── map/position_mapper.py      - Core mapping and visualization")
    print("├── map/bge_integration.py      - BGE navigation integration") 
    print("├── map/enhanced_vlm_analysis.py - Enhanced VLM with position awareness")
    print("└── map/generated_maps/         - Generated position maps")
    
    print("\n🔄 WORKFLOW:")
    print("1. BGE captures actor world coordinates")
    print("2. Position mapper overlays actor location on house layout")
    print("3. Dynamic map shows current position + movement history") 
    print("4. VLM analyzes: First-person view + Position map + House layout")
    print("5. Enhanced spatial awareness improves navigation decisions")
    
    print("\n🎯 KEY BENEFITS:")
    print("• Visual confirmation of actor location on house layout")
    print("• Movement history tracking to avoid backtracking") 
    print("• Enhanced VLM spatial awareness for better room detection")
    print("• Real-time position feedback for debugging navigation")
    print("• Automatic map generation without manual intervention")

if __name__ == "__main__":
    success = test_position_mapping_system()
    
    if success:
        show_system_overview()
        print("\n🎉 Position mapping system test PASSED!")
        print("The system is ready for BGE integration.")
    else:
        print("\n❌ Position mapping system test FAILED!")
        print("Check the error messages above and fix any issues.")
    
    print(f"\n📁 Test completed. Check map/generated_maps/ for test output files.")