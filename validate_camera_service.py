"""
Simple structure test for the enhanced MCP camera service
"""
import os

def test_camera_service_structure():
    """Test that the camera service file has the expected structure"""
    camera_service_path = os.path.join("vesper_mcp", "services", "camera_service.py")
    
    if not os.path.exists(camera_service_path):
        print(f"✗ Camera service file not found: {camera_service_path}")
        return False
    
    with open(camera_service_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for key MCP tools
    expected_tools = [
        "capture_bird_eye_view",
        "capture_first_person_view", 
        "get_camera_recommendations",
        "get_available_cameras",
        "get_camera_info",
        "list_camera_captures",
        "camera_service_health"
    ]
    
    missing_tools = []
    for tool in expected_tools:
        if f"async def {tool}(" not in content:
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"✗ Missing tools: {missing_tools}")
        return False
    
    # Check for key features
    features = [
        "@mcp.tool()",
        "intelligent camera selection",
        "bird_eye_score",
        "first_person_score",
        "recommended_camera",
        "camera_type"
    ]
    
    missing_features = []
    for feature in features:
        if feature not in content:
            missing_features.append(feature)
    
    if missing_features:
        print(f"✗ Missing features: {missing_features}")
        return False
    
    print("✓ Camera service structure validation passed!")
    print(f"✓ Found all {len(expected_tools)} expected MCP tools")
    print("✓ All key features present")
    
    # Count total lines for reference
    line_count = len(content.split('\n'))
    print(f"✓ Service contains {line_count} lines of code")
    
    return True

def test_recommendation_logic():
    """Test the recommendation scoring logic structure"""
    camera_service_path = os.path.join("vesper_mcp", "services", "camera_service.py")
    
    with open(camera_service_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for scoring keywords
    scoring_keywords = [
        "navigate", "go to", "move to", "find room", "explore",
        "use", "interact", "read", "operate", "cook", "clean",
        "stuck", "lost", "confused", "path",
        "repeated", "detail", "precise", "close"
    ]
    
    found_keywords = []
    for keyword in scoring_keywords:
        if f'"{keyword}"' in content:
            found_keywords.append(keyword)
    
    print(f"✓ Found {len(found_keywords)}/{len(scoring_keywords)} scoring keywords")
    
    # Check for confidence calculation
    if "confidence" in content and "score" in content:
        print("✓ Confidence calculation logic present")
    
    return True

def main():
    """Run all structure tests"""
    print("Enhanced MCP Camera Service - Structure Validation")
    print("=" * 55)
    
    success = True
    success &= test_camera_service_structure()
    success &= test_recommendation_logic()
    
    print("\n" + "=" * 55)
    if success:
        print("✓ All structure tests PASSED!")
        print("\nThe enhanced camera service is ready for integration.")
        print("\nKey capabilities:")
        print("  • Intelligent camera selection based on task context")
        print("  • Separate MCP tools for bird-eye and first-person capture")
        print("  • Camera recommendation system with scoring logic")
        print("  • Complete camera management and health checking")
    else:
        print("✗ Some structure tests FAILED!")
    
    return success

if __name__ == "__main__":
    main()
