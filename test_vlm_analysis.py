#!/usr/bin/env python3
"""
VLM House Layout Analysis Tool
Test the Vision Language Model's capability to analyze house screenshots
"""

import os
import sys
import glob
from backend.app.llm.client import chat_completion_with_vision

def analyze_single_screenshot(image_path, analysis_type="detailed"):
    """Analyze a single screenshot with different analysis types"""
    
    if analysis_type == "basic":
        system_prompt = "You are analyzing a bird's eye view of a house layout."
        user_prompt = "What do you see in this image? Describe the layout briefly."
        
    elif analysis_type == "rooms":
        system_prompt = "You are a house layout expert analyzing a bird's eye view."
        user_prompt = """Analyze this house layout image and identify:
1. What rooms can you see?
2. Where is the kitchen located?
3. Where is the bathroom located?
4. Where are other rooms (bedroom, living room, etc.)?
5. Can you see any actor/character in the image? If so, where?"""
        
    elif analysis_type == "navigation":
        system_prompt = "You are a navigation expert analyzing a house layout."
        user_prompt = """Look at this bird's eye view and provide navigation analysis:
1. What is the overall layout structure?
2. How would you navigate from the center to the kitchen?
3. How would you navigate from the center to the bathroom?
4. What are the main pathways and obstacles?
5. Are there walls, doors, or other barriers visible?"""
        
    elif analysis_type == "detailed":
        system_prompt = "You are a detailed visual analyst examining a house layout."
        user_prompt = """Provide a comprehensive analysis of this bird's eye house layout:

SPATIAL ANALYSIS:
- Describe the overall shape and size of the house
- Identify all visible rooms and their approximate locations
- Note any walls, doors, corridors, or barriers

ROOM IDENTIFICATION:
- Kitchen: Where is it? What features make it identifiable?
- Bathroom: Where is it? What features make it identifiable?
- Bedroom: Where is it? What features make it identifiable?
- Living areas: Where are they? What features make them identifiable?

NAVIGATION ASSESSMENT:
- If there's an actor/character visible, where is it located?
- What would be the best path to reach each room?
- Are there any obstacles or blocked pathways?

VISUAL QUALITY:
- How clear is the image?
- Can you distinguish between different room types?
- What improvements would help with navigation analysis?"""
    
    try:
        print(f"\n🔍 Analyzing: {os.path.basename(image_path)}")
        print(f"📊 Analysis Type: {analysis_type.upper()}")
        print("=" * 80)
        
        response = chat_completion_with_vision(
            system_prompt, 
            user_prompt, 
            image_path, 
            max_tokens=800,
            temperature=0.1
        )
        
        print(response)
        print("=" * 80)
        return response
        
    except Exception as e:
        print(f"❌ Error analyzing {image_path}: {e}")
        return None

def test_vlm_capabilities():
    """Test VLM capabilities with multiple analysis types"""
    
    captures_dir = os.path.join(os.path.dirname(__file__), "blender", "captures")
    
    if not os.path.exists(captures_dir):
        print(f"❌ Captures directory not found: {captures_dir}")
        return
    
    # Get the latest screenshots
    screenshots = glob.glob(os.path.join(captures_dir, "bge_screenshot_*.png"))
    
    if not screenshots:
        print(f"❌ No screenshots found in {captures_dir}")
        return
    
    # Sort by timestamp (newest first)
    screenshots.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    print(f"📸 Found {len(screenshots)} screenshots")
    print(f"🎯 Testing with latest 3 screenshots...")
    
    # Test different analysis types on recent screenshots
    analysis_types = ["basic", "rooms", "navigation", "detailed"]
    test_screenshots = screenshots[:3]  # Latest 3 screenshots
    
    for i, screenshot in enumerate(test_screenshots):
        print(f"\n" + "="*100)
        print(f"🖼️  SCREENSHOT {i+1}: {os.path.basename(screenshot)}")
        print(f"📅 Modified: {os.path.getctime(screenshot)}")
        print("="*100)
        
        for analysis_type in analysis_types:
            result = analyze_single_screenshot(screenshot, analysis_type)
            if result:
                print(f"\n✅ {analysis_type.upper()} analysis completed")
            else:
                print(f"\n❌ {analysis_type.upper()} analysis failed")
            
            # Add separator between analysis types
            print("\n" + "-"*60 + "\n")

def analyze_specific_screenshot(screenshot_path):
    """Analyze a specific screenshot with all analysis types"""
    
    if not os.path.exists(screenshot_path):
        print(f"❌ Screenshot not found: {screenshot_path}")
        return
    
    print(f"🎯 Analyzing specific screenshot: {screenshot_path}")
    analysis_types = ["basic", "rooms", "navigation", "detailed"]
    
    for analysis_type in analysis_types:
        result = analyze_single_screenshot(screenshot_path, analysis_type)
        print("\n" + "-"*80 + "\n")

def compare_vlm_vs_fallback():
    """Compare VLM decisions vs fallback navigation"""
    
    captures_dir = os.path.join(os.path.dirname(__file__), "blender", "captures")
    screenshots = glob.glob(os.path.join(captures_dir, "bge_screenshot_*.png"))
    
    if not screenshots:
        print("❌ No screenshots found")
        return
    
    # Test navigation decisions
    test_screenshot = screenshots[-1]  # Latest screenshot
    
    tasks = ["Go to kitchen", "Go to bathroom", "Go to bedroom", "Cook in kitchen"]
    
    for task in tasks:
        print(f"\n🎯 TASK: {task}")
        print("="*50)
        
        system_prompt = """You are controlling an actor in a house. Help navigate to complete the task.

MOVEMENT COMMANDS:
- "UP" = move forward (+Y direction)
- "DOWN" = move backward (-Y direction) 
- "LEFT" = move left (-X direction)
- "RIGHT" = move right (+X direction)
- "STAY" = stop (task complete)

RESPONSE FORMAT (JSON only):
{
  "next_direction": "UP|DOWN|LEFT|RIGHT|STAY",
  "reasoning": "why this direction helps complete the task"
}"""

        user_prompt = f"""Current Task: {task}
Actor Position: [unknown]

Look at the bird's eye view image and decide the next movement to complete this task. You can see the layout of the house, walls, doors, and rooms. The actor's current position should be visible in the image.

IMPORTANT: If the actor appears to be AT or VERY CLOSE to the target room/area for the task, respond with "STAY" to complete the task."""

        try:
            response = chat_completion_with_vision(
                system_prompt, 
                user_prompt, 
                test_screenshot, 
                max_tokens=200,
                temperature=0.1
            )
            print(f"🧠 VLM Decision: {response}")
            
        except Exception as e:
            print(f"❌ VLM Error: {e}")

if __name__ == "__main__":
    print("🏠 VLM House Layout Analysis Tool")
    print("="*50)
    
    if len(sys.argv) > 1:
        # Analyze specific screenshot
        screenshot_path = sys.argv[1]
        analyze_specific_screenshot(screenshot_path)
    else:
        # Run comprehensive test
        print("🔬 Running comprehensive VLM capability test...")
        test_vlm_capabilities()
        
        print("\n" + "="*100)
        print("🆚 Comparing VLM vs Fallback Navigation")
        print("="*100)
        compare_vlm_vs_fallback()
