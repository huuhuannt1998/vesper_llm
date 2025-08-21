#!/usr/bin/env python3
"""
Test VLM decision making with actual screenshots
"""
import sys
import os
import base64

# Add the backend path to import the LLM client
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app'))

# Change to current directory first to ensure proper imports
os.chdir(os.path.dirname(__file__))

try:
    from backend.app.llm.client import chat_completion_with_vision
except ImportError:
    # Fallback import method
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'app'))
    from llm.client import chat_completion_with_vision

def test_vlm_decision(image_path):
    """Test VLM decision making with a screenshot"""
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    # Read and encode image
    with open(image_path, 'rb') as img_file:
        image_data = base64.b64encode(img_file.read()).decode('utf-8')
    
    # Create navigation prompt
    prompt = """You are controlling a pink diamond-shaped actor in a house environment from a bird's eye view.

CURRENT TASK: Navigate to the kitchen to cook

The pink diamond in the center represents the actor you control.
Analyze the image and respond with ONLY a JSON object in this format:
{
    "action": "UP/DOWN/LEFT/RIGHT", 
    "reasoning": "brief explanation of why this direction was chosen"
}

Look for:
- Kitchen areas (usually have counters, appliances, sinks)
- Open pathways to move through
- Avoid walls (dark/black areas)
- Move toward spaces that look like a kitchen

Respond with valid JSON only."""

    try:
        print(f"🧠 Testing VLM with image: {image_path}")
        response = chat_completion_with_vision(prompt, image_base64=image_data)
        print(f"🎯 VLM Response: {response}")
        
        # Try to parse as JSON
        import json
        try:
            # Clean the response - remove markdown code blocks if present
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            clean_response = clean_response.strip()
            
            decision = json.loads(clean_response)
            print(f"✅ Valid JSON - Action: {decision.get('action')}, Reasoning: {decision.get('reasoning')}")
            return decision
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON response: {response}")
            return None
            
    except Exception as e:
        print(f"❌ VLM Error: {e}")
        return None

if __name__ == "__main__":
    # Test with a sample screenshot
    test_image = "blender/captures/bge_001.png"
    if len(sys.argv) > 1:
        test_image = sys.argv[1]
    
    print(f"🔍 Testing VLM decision making...")
    result = test_vlm_decision(test_image)
