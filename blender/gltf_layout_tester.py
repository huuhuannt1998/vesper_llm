#!/usr/bin/env python3
"""
glTF Layout Testing Utility for VESPER Navigation

This script helps test the navigation system with different glTF 2.0 house layouts.
Use this to verify that the actor spawning and navigation work consistently across layouts.
"""

import os
import json

def create_layout_test_checklist():
    """Create a checklist for testing new glTF layouts"""
    
    checklist = {
        "pre_import": [
            "✅ Backup current .blend file",
            "✅ Note current actor position and camera setup",
            "✅ Clear existing navigation state if needed"
        ],
        "import_steps": [
            "✅ File → Import → glTF 2.0 (.glb/.gltf)",
            "✅ Select your new house layout file",
            "✅ Import with default settings",
            "✅ Verify objects are imported correctly"
        ],
        "navigation_setup": [
            "✅ Run navigation script (should auto-detect new layout)",
            "✅ Check console for 'Setting up navigation for new layout'",
            "✅ Verify actor is found/created automatically",
            "✅ Confirm camera setup for bird's eye screenshots",
            "✅ Check scene bounds analysis in console"
        ],
        "testing_steps": [
            "✅ Press P to start navigation",
            "✅ Verify actor stays within house bounds",
            "✅ Check screenshots are captured (bge_XXX.png)",
            "✅ Confirm VLM navigation works with new layout",
            "✅ Test with different task types (go to room, prepare, etc.)"
        ],
        "validation": [
            "✅ Actor doesn't walk through walls",
            "✅ Navigation adapts to new room layouts",
            "✅ Screenshots show proper bird's eye view",
            "✅ VLM correctly identifies rooms in new layout",
            "✅ System handles timeouts without leaving house"
        ]
    }
    
    return checklist

def generate_test_report_template():
    """Generate template for testing different layouts"""
    
    template = {
        "layout_info": {
            "file_name": "",
            "file_size": "",
            "import_date": "",
            "description": ""
        },
        "scene_analysis": {
            "total_objects": 0,
            "cameras_found": [],
            "actors_found": [],
            "scene_bounds": {
                "min_x": 0, "max_x": 0,
                "min_y": 0, "max_y": 0,
                "width": 0, "height": 0
            }
        },
        "navigation_tests": {
            "actor_spawning": "PASS/FAIL",
            "camera_setup": "PASS/FAIL", 
            "screenshot_capture": "PASS/FAIL",
            "vlm_navigation": "PASS/FAIL",
            "boundary_respect": "PASS/FAIL",
            "timeout_handling": "PASS/FAIL"
        },
        "room_identification": {
            "living_room": "FOUND/NOT_FOUND",
            "kitchen": "FOUND/NOT_FOUND",
            "bathroom": "FOUND/NOT_FOUND",
            "bedroom": "FOUND/NOT_FOUND"
        },
        "notes": [],
        "issues_found": [],
        "recommendations": []
    }
    
    return template

def print_testing_instructions():
    """Print comprehensive testing instructions"""
    
    print("🏠 glTF Layout Testing Guide for VESPER Navigation\n")
    
    checklist = create_layout_test_checklist()
    
    for phase, items in checklist.items():
        print(f"📋 {phase.replace('_', ' ').title()}:")
        for item in items:
            print(f"  {item}")
        print()
    
    print("🔧 Console Messages to Watch For:")
    print("  ✅ 'Setting up navigation for new layout...'")
    print("  ✅ 'Found existing actor: [name]' or 'Using object as actor: [name]'")
    print("  ✅ 'Scene Analysis: Objects: X, Cameras: Y'")
    print("  ✅ 'Layout bounds: X: ... Y: ...'")
    print("  ✅ 'Positioned actor at center: (X, Y)'")
    print("  ✅ 'Navigation setup complete for new layout!'")
    
    print("\n⚠️ Potential Issues and Solutions:")
    print("  🔸 No actor found → Script will use first movable object")
    print("  🔸 No camera found → Screenshots may fail, add top-down camera")
    print("  🔸 Actor spawns in wall → Manually adjust actor position")
    print("  🔸 Wrong room identification → Check VLM prompts work with layout")
    
    print("\n🎯 Success Criteria:")
    print("  ✅ Actor spawns inside house boundaries")
    print("  ✅ Navigation works without manual intervention")
    print("  ✅ Screenshots show clear bird's eye view")
    print("  ✅ VLM identifies rooms correctly in new layout")
    print("  ✅ System handles VLM timeouts gracefully")

def create_layout_test_files():
    """Create files for layout testing workflow"""
    
    # Create test checklist file
    checklist_file = "layout_test_checklist.md"
    with open(checklist_file, 'w') as f:
        f.write("# glTF Layout Testing Checklist\n\n")
        checklist = create_layout_test_checklist()
        for phase, items in checklist.items():
            f.write(f"## {phase.replace('_', ' ').title()}\n\n")
            for item in items:
                f.write(f"- [ ] {item[2:]}\n")  # Remove the ✅ emoji
            f.write("\n")
    
    # Create test report template
    report_template = generate_test_report_template()
    with open("layout_test_report_template.json", 'w') as f:
        json.dump(report_template, f, indent=2)
    
    print(f"✅ Created {checklist_file}")
    print(f"✅ Created layout_test_report_template.json")
    print("\nUse these files to track your testing progress with different glTF layouts!")

def main():
    print_testing_instructions()
    print("\n" + "="*60)
    print("📁 Creating Testing Files...")
    create_layout_test_files()

if __name__ == "__main__":
    main()
