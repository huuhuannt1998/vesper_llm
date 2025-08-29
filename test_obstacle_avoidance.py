#!/usr/bin/env python3
"""
Validate Obstacle Avoidance Enhancements
Check if key safety prompts are properly integrated
"""

import os

def check_obstacle_avoidance_prompts():
    """Check if obstacle avoidance prompts are properly integrated"""
    bge_file = r"C:\Users\hbui11\Desktop\vesper_llm\blender\llm_bge_navigation.py"
    
    print("🔍 Checking Obstacle Avoidance Integration...")
    
    with open(bge_file, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Key safety prompts to verify
    safety_checks = [
        "OBSTACLE & BOUNDARY CHECK",
        "STAY INSIDE THE HOUSE",
        "AVOID FURNITURE OVERLAP", 
        "RESPECT PHYSICAL BARRIERS",
        "NAVIGATE AROUND OBSTACLES",
        "COLLISION AVOIDANCE",
        "Check for clear movement paths",
        "MOVEMENT SAFETY REQUIREMENTS",
        "OBSTACLES: [any blocking furniture/walls]",
        "SAFE PATH: [clear direction or blocked]"
    ]
    
    print("📋 Safety Prompt Integration:")
    missing = []
    for check in safety_checks:
        if check in code:
            print(f"   ✅ {check}")
        else:
            print(f"   ❌ {check} - MISSING")
            missing.append(check)
    
    # Check boundary enforcement
    boundary_checks = [
        "HOUSE_BOUNDS",
        "x_min': -5.5",
        "BOUNDARY VIOLATION PREVENTED",
        "position_history",
        "distance_moved",
        "Unusually large movement detected"
    ]
    
    print("\n🏠 Boundary & Collision Detection:")
    for check in boundary_checks:
        if check in code:
            print(f"   ✅ {check}")
        else:
            print(f"   ❌ {check} - MISSING")
            missing.append(check)
    
    if missing:
        print(f"\n❌ {len(missing)} safety features missing!")
        return False
    else:
        print(f"\n✅ All {len(safety_checks + boundary_checks)} safety features integrated!")
        return True

def main():
    print("🚀 VESPER Obstacle Avoidance Validation")
    print("=" * 45)
    
    if check_obstacle_avoidance_prompts():
        print("\n🎉 OBSTACLE AVOIDANCE SYSTEM READY!")
        print("\n📋 Enhanced Safety Features:")
        print("  • VLM prompted to check obstacles before movement")
        print("  • Explicit furniture collision avoidance instructions")
        print("  • House boundary enforcement with safety margins")
        print("  • Position history tracking for collision detection")
        print("  • Multi-layer safety checking (AI + code level)")
        
        print("\n🧪 Testing Recommendations:")
        print("1. Run BGE navigation and monitor console for:")
        print("   - 'OBSTACLES:' mentions in VLM reasoning")
        print("   - 'BOUNDARY VIOLATION PREVENTED' warnings")
        print("   - 'Unusually large movement detected' alerts")
        print("2. Verify actor stays within house walls")
        print("3. Check that pink dot doesn't clip through furniture")
        
    else:
        print("\n⚠️ Some safety features not properly integrated")
        print("Check the missing items above")

if __name__ == "__main__":
    main()
