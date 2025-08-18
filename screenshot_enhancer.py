#!/usr/bin/env python3
"""
Enhanced Screenshot System with Annotations
Improves VLM analysis by adding visual annotations to screenshots
"""

import os
import sys
import time
from PIL import Image, ImageDraw, ImageFont

def add_annotations_to_screenshot(screenshot_path, actor_position=None, room_labels=None, save_annotated=True):
    """Add helpful annotations to screenshots for better VLM analysis"""
    
    try:
        # Open the image
        img = Image.open(screenshot_path)
        draw = ImageDraw.Draw(img)
        
        # Try to load a font (fallback to default if not available)
        try:
            font_large = ImageFont.truetype("arial.ttf", 24)
            font_medium = ImageFont.truetype("arial.ttf", 18)
            font_small = ImageFont.truetype("arial.ttf", 14)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Get image dimensions
        width, height = img.size
        
        # Add coordinate grid (helps with navigation)
        grid_color = (100, 100, 100, 128)  # Semi-transparent gray
        grid_spacing = width // 10
        
        for x in range(0, width, grid_spacing):
            draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
        for y in range(0, height, grid_spacing):
            draw.line([(0, y), (width, y)], fill=grid_color, width=1)
        
        # Add coordinate labels
        coord_color = (255, 255, 255, 200)  # White with transparency
        for i, x in enumerate(range(0, width, grid_spacing)):
            draw.text((x+5, 5), f"X{i}", fill=coord_color, font=font_small)
        for i, y in enumerate(range(0, height, grid_spacing)):
            draw.text((5, y+5), f"Y{i}", fill=coord_color, font=font_small)
        
        # Add actor position marker (if provided)
        if actor_position:
            # Convert world coordinates to screen coordinates (approximate)
            # This is a simplified conversion - you may need to adjust based on your camera setup
            screen_x = int(width * 0.5 + actor_position[0] * 20)  # Approximate scaling
            screen_y = int(height * 0.5 - actor_position[1] * 20)  # Y is inverted in screen coordinates
            
            # Ensure coordinates are within image bounds
            screen_x = max(10, min(width-10, screen_x))
            screen_y = max(10, min(height-10, screen_y))
            
            # Draw actor marker
            actor_color = (255, 0, 0)  # Red
            marker_size = 8
            draw.ellipse([
                screen_x - marker_size, screen_y - marker_size,
                screen_x + marker_size, screen_y + marker_size
            ], fill=actor_color, outline=(255, 255, 255), width=2)
            
            # Add actor label
            draw.text((screen_x + 12, screen_y - 10), "ACTOR", fill=(255, 255, 255), font=font_medium)
            draw.text((screen_x + 12, screen_y + 8), f"({actor_position[0]:.1f}, {actor_position[1]:.1f})", 
                     fill=(255, 255, 255), font=font_small)
        
        # Add room labels (if provided)
        if room_labels:
            label_color = (0, 255, 0)  # Green
            for room_name, position in room_labels.items():
                screen_x = int(width * 0.5 + position[0] * 20)
                screen_y = int(height * 0.5 - position[1] * 20)
                
                # Ensure coordinates are within bounds
                screen_x = max(10, min(width-50, screen_x))
                screen_y = max(10, min(height-10, screen_y))
                
                # Draw room label background
                text_bbox = draw.textbbox((screen_x, screen_y), room_name.upper(), font=font_medium)
                draw.rectangle(text_bbox, fill=(0, 0, 0, 180), outline=label_color)
                
                # Draw room label text
                draw.text((screen_x, screen_y), room_name.upper(), fill=label_color, font=font_medium)
        
        # Add title and timestamp
        title_color = (255, 255, 0)  # Yellow
        title_text = "HOUSE LAYOUT - BIRD'S EYE VIEW"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        draw.text((10, height - 60), title_text, fill=title_color, font=font_large)
        draw.text((10, height - 35), f"Captured: {timestamp}", fill=(255, 255, 255), font=font_small)
        
        # Add navigation compass
        compass_x = width - 80
        compass_y = 30
        compass_size = 30
        
        # Draw compass circle
        draw.ellipse([
            compass_x - compass_size, compass_y - compass_size,
            compass_x + compass_size, compass_y + compass_size
        ], outline=(255, 255, 255), width=2)
        
        # Draw compass directions
        draw.text((compass_x - 5, compass_y - compass_size - 15), "N", fill=(255, 255, 255), font=font_medium)
        draw.text((compass_x + compass_size + 5, compass_y - 5), "E", fill=(255, 255, 255), font=font_medium)
        draw.text((compass_x - 5, compass_y + compass_size + 5), "S", fill=(255, 255, 255), font=font_medium)
        draw.text((compass_x - compass_size - 15, compass_y - 5), "W", fill=(255, 255, 255), font=font_medium)
        
        # Save annotated version
        if save_annotated:
            base_name = os.path.splitext(screenshot_path)[0]
            annotated_path = f"{base_name}_annotated.png"
            img.save(annotated_path)
            print(f"📝 Saved annotated screenshot: {annotated_path}")
            return annotated_path
        else:
            return img
            
    except Exception as e:
        print(f"❌ Error annotating screenshot: {e}")
        return None

def create_enhanced_screenshot_with_context(screenshot_path, context_info):
    """Create an enhanced screenshot with contextual information"""
    
    actor_pos = context_info.get("actor_position")
    current_task = context_info.get("current_task", "Unknown")
    step_number = context_info.get("step_number", 0)
    
    # Define approximate room locations (you may need to adjust these based on your house layout)
    room_labels = {
        "KITCHEN": [-1.5, 3.8],
        "BATHROOM": [-5.5, 4.2],
        "BEDROOM": [-3.0, 1.5],
        "LIVING ROOM": [-2.5, 2.8]
    }
    
    # Add annotations
    annotated_path = add_annotations_to_screenshot(
        screenshot_path, 
        actor_position=actor_pos, 
        room_labels=room_labels
    )
    
    if annotated_path:
        # Add task-specific overlay
        try:
            img = Image.open(annotated_path)
            draw = ImageDraw.Draw(img)
            
            try:
                font_large = ImageFont.truetype("arial.ttf", 20)
            except:
                font_large = ImageFont.load_default()
            
            # Add current task information
            task_text = f"STEP {step_number}: {current_task}"
            task_color = (255, 255, 0)  # Yellow
            
            # Draw task background
            text_bbox = draw.textbbox((10, 10), task_text, font=font_large)
            draw.rectangle(text_bbox, fill=(0, 0, 0, 180), outline=task_color)
            draw.text((10, 10), task_text, fill=task_color, font=font_large)
            
            # Save enhanced version
            enhanced_path = annotated_path.replace("_annotated.png", "_enhanced.png")
            img.save(enhanced_path)
            print(f"🎯 Saved enhanced screenshot: {enhanced_path}")
            return enhanced_path
            
        except Exception as e:
            print(f"⚠️ Could not add task overlay: {e}")
            return annotated_path
    
    return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        screenshot_path = sys.argv[1]
        
        # Test context
        test_context = {
            "actor_position": [-2.98, 3.24],
            "current_task": "Go to kitchen",
            "step_number": 5
        }
        
        enhanced_path = create_enhanced_screenshot_with_context(screenshot_path, test_context)
        if enhanced_path:
            print(f"✅ Enhanced screenshot created: {enhanced_path}")
        else:
            print("❌ Failed to create enhanced screenshot")
    else:
        print("Usage: python screenshot_enhancer.py <screenshot_path>")
