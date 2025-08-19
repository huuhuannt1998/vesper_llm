#!/usr/bin/env python3
"""
VLM Navigation Diagnostic - Test what the VLM actually sees and understands
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_vlm_understanding():
    """Test what the VLM actually understands from the bird's eye view"""
    try:
        from app.llm.client import chat_completion_with_vision
        
        # Find latest screenshot
        captures_dir = Path("blender/captures")
        if not captures_dir.exists():
            print("❌ No captures folder")
            return
        
        png_files = [f for f in captures_dir.glob("bge_*.png")]
        if not png_files:
            print("❌ No screenshots found")
            return
        
        # Use the most recent screenshot
        png_files.sort()
        latest = png_files[-1]
        print(f"📸 Testing with: {latest.name}")
        
        # Test 1: Basic visual understanding
        print("\n=== Test 1: What does the VLM see? ===")
        prompt1 = """Look at this bird's eye view image carefully. Describe what you see:
1. What does the colored dot represent?
2. What do the dark gray/black areas represent?
3. What do the light gray/beige areas represent?
4. Can you identify any doorways or openings?
5. What rooms or areas can you identify?

Be specific and detailed."""

        response1 = chat_completion_with_vision(prompt1, image_path=str(latest))
        print("VLM Response:")
        print(response1)
        
        # Test 2: Navigation understanding
        print("\n=== Test 2: Navigation Analysis ===")
        prompt2 = """Looking at this image, analyze the navigation possibilities:
1. Where is the actor (colored dot) currently positioned?
2. What directions can the actor move WITHOUT hitting walls?
3. Are there any walls blocking movement in any direction?
4. What would happen if the actor moved RIGHT from current position?
5. What would happen if the actor moved UP from current position?

Focus on collision detection and pathfinding."""

        response2 = chat_completion_with_vision(prompt2, image_path=str(latest))
        print("VLM Response:")
        print(response2)
        
        # Test 3: Room identification
        print("\n=== Test 3: Room and Task Analysis ===")
        prompt3 = """For the task "Go to living room":
1. Can you identify where the living room is in this layout?
2. What is the best path from the actor's current position to the living room?
3. What obstacles or walls need to be avoided?
4. What direction should the actor move FIRST to start toward the living room?

Provide a step-by-step navigation plan."""

        response3 = chat_completion_with_vision(prompt3, image_path=str(latest))
        print("VLM Response:")
        print(response3)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vlm_understanding()
