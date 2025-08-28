"""
VESPER Screenshot Analysis Tool
Help identify the best screenshots for few-shot examples
"""

import os
import json
from PIL import Image
import base64

def analyze_screenshots(captures_dir):
    """
    Analyze available screenshots and categorize them for few-shot selection
    """
    screenshots = []
    
    for filename in sorted(os.listdir(captures_dir)):
        if filename.endswith('.png'):
            filepath = os.path.join(captures_dir, filename)
            try:
                # Get basic image info
                with Image.open(filepath) as img:
                    width, height = img.size
                    
                screenshots.append({
                    'filename': filename,
                    'path': filepath,
                    'size': (width, height),
                    'filesize': os.path.getsize(filepath)
                })
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    
    return screenshots

def suggest_few_shot_candidates(screenshots):
    """
    Suggest which screenshots might be good few-shot candidates
    Based on file size (complexity) and chronological spread
    """
    if len(screenshots) < 5:
        return screenshots
    
    # Sort by file size (larger files often have more visual content)
    by_size = sorted(screenshots, key=lambda x: x['filesize'], reverse=True)
    
    # Get a good spread across the capture session
    total = len(screenshots)
    indices = [
        0,  # First capture
        total // 4,  # Quarter way
        total // 2,  # Halfway
        3 * total // 4,  # Three quarters
        total - 1  # Last capture
    ]
    
    candidates = []
    for i in indices:
        candidates.append(screenshots[i])
    
    # Add a few high-complexity images
    for img in by_size[:3]:
        if img not in candidates:
            candidates.append(img)
    
    return candidates[:8]  # Max 8 candidates

def create_few_shot_template(candidates, output_file):
    """
    Create a template file for manually creating few-shot examples
    """
    template = {
        "instructions": "Fill in the examples below with actual task scenarios and expected responses",
        "examples": []
    }
    
    for i, candidate in enumerate(candidates):
        example_template = {
            "image_file": candidate['filename'],
            "image_path": candidate['path'],
            "task": f"[FILL IN: e.g., 'Go to kitchen', 'Rest in bedroom']",
            "gold_response": {
                "current_room": "[KITCHEN/BATHROOM/BEDROOM/LIVING_ROOM/UNKNOWN]",
                "furniture_visible": "[List furniture you can see in the image]",
                "task_complete": "[true/false]",
                "movement_sequence": ["[UP/DOWN/LEFT/RIGHT/STAY]"],
                "reasoning": "[Brief explanation of the decision]"
            },
            "notes": f"Image size: {candidate['size']}, File size: {candidate['filesize']} bytes"
        }
        template["examples"].append(example_template)
    
    with open(output_file, 'w') as f:
        json.dump(template, f, indent=2)
    
    print(f"Template created: {output_file}")
    print("Edit this file to create your few-shot examples")

def encode_image_for_api(image_path):
    """
    Encode image as base64 for API calls (if needed)
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

if __name__ == "__main__":
    captures_dir = r"C:\Users\hbui11\Desktop\vesper_llm\blender\captures"
    
    print("Analyzing screenshots...")
    screenshots = analyze_screenshots(captures_dir)
    print(f"Found {len(screenshots)} screenshots")
    
    print("\nSuggesting few-shot candidates...")
    candidates = suggest_few_shot_candidates(screenshots)
    
    print("\nRecommended screenshots for few-shot examples:")
    for i, candidate in enumerate(candidates, 1):
        print(f"{i}. {candidate['filename']} - Size: {candidate['size']}, {candidate['filesize']} bytes")
    
    # Create template
    template_file = os.path.join(os.path.dirname(captures_dir), "few_shot_template.json")
    create_few_shot_template(candidates, template_file)
    
    print(f"\n✅ Template created at: {template_file}")
    print("\nNext steps:")
    print("1. Open the template file")
    print("2. For each screenshot, add the appropriate task and expected response")
    print("3. Focus on diverse scenarios: different rooms, clear navigation decisions")
    print("4. Include at least one 'STAY' example (when already at destination)")
    print("5. Include examples that discourage unnecessary 'STAY' usage")
