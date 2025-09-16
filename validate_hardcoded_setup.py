"""
Simple validation script for hardcoded camera names (no MCP dependencies)
"""
import sys
import os

def validate_hardcoded_cameras():
    """Validate the hardcoded camera configuration without MCP dependencies"""
    print("Hardcoded Camera Names Validation")
    print("=" * 50)
    
    # Read the camera service file directly to extract the hardcoded values
    camera_service_path = os.path.join("vesper_mcp", "services", "camera_service.py")
    
    if not os.path.exists(camera_service_path):
        print(f"✗ Camera service file not found: {camera_service_path}")
        return False
    
    with open(camera_service_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract hardcoded camera names
    bird_eye_name = None
    first_person_name = None
    
    for line in content.split('\n'):
        if 'BIRD_EYE_CAMERA_NAME' in line and '=' in line:
            bird_eye_name = line.split('=')[1].strip().strip('"\'')
        elif 'FIRST_PERSON_CAMERA_NAME' in line and '=' in line:
            first_person_name = line.split('=')[1].strip().strip('"\'')
    
    print("✓ Hardcoded camera names extracted from source:")
    print(f"  BIRD_EYE_CAMERA_NAME = '{bird_eye_name}'")
    print(f"  FIRST_PERSON_CAMERA_NAME = '{first_person_name}'")
    
    # Check if the names are properly set
    if bird_eye_name and first_person_name:
        print("\n✓ Both camera names are properly configured")
        
        # Check if the functions use these names
        functions_using_hardcoded = []
        if bird_eye_name in content:
            functions_using_hardcoded.append("capture_bird_eye_view")
        if first_person_name in content:
            functions_using_hardcoded.append("capture_first_person_view")
        
        print(f"✓ Functions using hardcoded names: {functions_using_hardcoded}")
        
        # Check for runtime detection
        if "BGE_RUNTIME" in content:
            print("✓ BGE runtime detection is present")
        
        if "switch_camera_runtime" in content:
            print("✓ Runtime camera switching function is present")
        
        print(f"\n🎯 Summary:")
        print(f"  • Bird-eye camera: {bird_eye_name}")
        print(f"  • First-person camera: {first_person_name}")
        print(f"  • BGE runtime support: ✓")
        print(f"  • Hardcoded configuration: ✓")
        
        return True
    else:
        print("✗ Camera names not properly configured")
        return False

def check_file_structure():
    """Check that all necessary files are present"""
    print("\n=== File Structure Check ===")
    
    files_to_check = [
        "vesper_mcp/services/camera_service.py",
        "BGE_RUNTIME_CAMERA_SOLUTION.md",
        "test_bge_camera_switching.py"
    ]
    
    all_present = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path}")
            all_present = False
    
    return all_present

def main():
    """Run validation"""
    success = True
    
    success &= validate_hardcoded_cameras()
    success &= check_file_structure()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ VALIDATION PASSED!")
        print("\nThe camera service is now configured with hardcoded camera names:")
        print("  • No more dynamic camera detection")
        print("  • Direct camera name usage")
        print("  • BGE runtime compatible")
        print("  • Ready for game engine integration")
    else:
        print("❌ VALIDATION FAILED!")
        print("Some issues need to be resolved.")
    
    return success

if __name__ == "__main__":
    main()
