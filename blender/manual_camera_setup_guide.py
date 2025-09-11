"""
VESPER First-Person Camera Setup Guide
======================================

Step-by-step instructions for creating a first-person camera attached to the actor.
"""

def manual_camera_setup_instructions():
    print("🎥 MANUAL FIRST-PERSON CAMERA SETUP")
    print("=" * 50)
    print()
    
    print("📋 STEP-BY-STEP INSTRUCTIONS:")
    print()
    
    print("1️⃣  SELECT THE ACTOR:")
    print("   • In Blender 3D viewport, click on your Actor object")
    print("   • Make sure it's highlighted/selected (orange outline)")
    print()
    
    print("2️⃣  ADD A CAMERA:")
    print("   • Press Shift+A to open Add menu")
    print("   • Select Camera (or go to Add > Camera)")
    print("   • A new camera will be created at the 3D cursor location")
    print()
    
    print("3️⃣  RENAME THE CAMERA:")
    print("   • With camera selected, press F2 or double-click name")
    print("   • Rename it to 'Actor_FPCamera' or similar")
    print("   • This helps identify it as the first-person camera")
    print()
    
    print("4️⃣  POSITION THE CAMERA:")
    print("   • Move camera to actor's position (G key to grab/move)")
    print("   • Raise it to eye level: Z-axis + 1.6 units")
    print("   • Position: Actor.location + (0, 0, 1.6)")
    print("   • This simulates human eye height")
    print()
    
    print("5️⃣  ORIENT THE CAMERA:")
    print("   • Press R to rotate camera")
    print("   • Match actor's facing direction")
    print("   • Camera should point where actor is looking")
    print("   • Use R + X/Y/Z for axis-specific rotation")
    print()
    
    print("6️⃣  PARENT CAMERA TO ACTOR:")
    print("   • Select camera first, then actor (actor should be bright orange)")
    print("   • Press Ctrl+P to open parenting menu")
    print("   • Choose 'Object' from the parenting options")
    print("   • Camera will now follow actor movement automatically")
    print()
    
    print("7️⃣  CONFIGURE CAMERA PROPERTIES:")
    print("   • In Properties panel, click Camera tab (camera icon)")
    print("   • Set Lens > Focal Length to 35mm (natural field of view)")
    print("   • Set Lens > Sensor Width to 36mm (full frame)")
    print("   • These settings give realistic human-like perspective")
    print()
    
    print("8️⃣  TEST THE CAMERA:")
    print("   • Select the first-person camera")
    print("   • Press Ctrl+Numpad 0 to set as active camera")
    print("   • Press Numpad 0 to switch to camera view")
    print("   • Move actor around - camera should follow!")
    print()
    
    print("✅ VERIFICATION CHECKLIST:")
    checks = [
        "□ Camera is named 'Actor_FPCamera'",
        "□ Camera is positioned 1.6 units above actor",
        "□ Camera is parented to actor",
        "□ Camera follows actor movement",
        "□ Camera view shows actor's perspective",
        "□ Focal length is set to 35mm",
        "□ Camera is set as active camera"
    ]
    
    for check in checks:
        print(f"   {check}")
    
    print()

if __name__ == "__main__":
    manual_camera_setup_instructions()
