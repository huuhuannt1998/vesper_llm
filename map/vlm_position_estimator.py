#!/usr/bin/env python3
"""
VLM-Based Position Estimation System

Uses Vision Language Model to analyze first-person view + house layout
to estimate actor position without requiring coordinate calibration.

This solves the coordinate mapping problem by having the VLM determine
position visually based on landmarks and spatial features.
"""

import json
import time
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

class VLMPositionEstimator:
    """Uses VLM to estimate actor position from first-person view"""
    
    def __init__(self, house_layout_path=None):
        """
        Initialize VLM position estimator
        
        Args:
            house_layout_path: Path to house layout reference image
        """
        if house_layout_path is None:
            # Default path
            house_layout_path = Path(__file__).parent.parent / 'blender' / 'house_layout_reference2.png'
        
        self.house_layout_path = Path(house_layout_path)
        
        if not self.house_layout_path.exists():
            raise FileNotFoundError(f"House layout not found: {self.house_layout_path}")
        
        self.house_layout = Image.open(self.house_layout_path)
        self.map_width, self.map_height = self.house_layout.size
        
        # Position history for continuity checking
        self.position_history = []
        self.session_id = f"vlm_pos_{int(time.time())}"
        
        # Room landmarks for VLM reference
        self.room_landmarks = {
            'LIVING_ROOM': {
                'furniture': ['sofa', 'couch', 'tv', 'coffee table', 'dining table', 'chairs', 'bookshelf'],
                'description': 'Large open space with seating furniture, TV area, and dining table'
            },
            'KITCHEN': {
                'furniture': ['stove', 'oven', 'refrigerator', 'sink', 'cabinets', 'countertop', 'microwave'],
                'description': 'Cooking area with appliances along walls'
            },
            'BEDROOM': {
                'furniture': ['bed', 'nightstand', 'dresser', 'closet', 'desk'],
                'description': 'Sleeping area with bed as dominant furniture'
            },
            'BATHROOM': {
                'furniture': ['toilet', 'sink', 'bathtub', 'shower', 'mirror', 'tiles'],
                'description': 'Small private room with bathroom fixtures'
            },
            'HALLWAY': {
                'furniture': ['doors', 'walls', 'narrow corridor'],
                'description': 'Narrow connecting space between rooms'
            }
        }
        
        print(f"🎯 VLM Position Estimator initialized")
        print(f"🗺️ House layout: {self.house_layout_path.name} ({self.map_width}x{self.map_height})")
        print(f"📍 Session ID: {self.session_id}")
    
    def estimate_position(self, fp_view_path, task, vlm_func, previous_position=None):
        """
        Estimate actor position using VLM analysis
        
        Args:
            fp_view_path: Path to first-person screenshot
            task: Current navigation task
            vlm_func: VLM function to call (from llm_client)
            previous_position: Previous estimated position dict or None
            
        Returns:
            dict: {
                'room': str,
                'estimated_x_normalized': float (0-1),
                'estimated_y_normalized': float (0-1),
                'estimated_angle': float (0-360),
                'map_x': int (pixel coordinate),
                'map_y': int (pixel coordinate),
                'confidence': float (0-1),
                'landmarks_visible': list,
                'reasoning': str,
                'timestamp': float
            }
        """
        
        print(f"\n🔍 VLM Position Estimation...")
        print(f"📸 Analyzing: {Path(fp_view_path).name}")
        print(f"🎯 Task: {task}")
        
        # Create position estimation prompt
        prompt = self._create_position_prompt(task, previous_position)
        
        # Call VLM with both images
        images = [str(fp_view_path), str(self.house_layout_path)]
        
        try:
            response = vlm_func(prompt, images)
            
            if not response:
                print("❌ VLM returned empty response")
                return None
            
            # Parse VLM response
            position_data = self._parse_position_response(response)
            
            if position_data:
                # Convert normalized coordinates to map pixel coordinates
                position_data['map_x'] = int(position_data['estimated_x_normalized'] * self.map_width)
                position_data['map_y'] = int(position_data['estimated_y_normalized'] * self.map_height)
                position_data['timestamp'] = time.time()
                
                # Add to history
                self.position_history.append(position_data)
                
                # Keep only last 20 positions
                if len(self.position_history) > 20:
                    self.position_history = self.position_history[-20:]
                
                print(f"✅ Position estimated:")
                print(f"   🏠 Room: {position_data['room']}")
                print(f"   📍 Normalized: ({position_data['estimated_x_normalized']:.3f}, {position_data['estimated_y_normalized']:.3f})")
                print(f"   🗺️ Map pixels: ({position_data['map_x']}, {position_data['map_y']})")
                print(f"   🧭 Facing: {position_data['estimated_angle']:.1f}°")
                print(f"   📊 Confidence: {position_data['confidence']:.2%}")
                print(f"   🔍 Landmarks: {', '.join(position_data['landmarks_visible'][:3])}")
                
                return position_data
            
        except Exception as e:
            print(f"❌ Position estimation failed: {e}")
            import traceback
            traceback.print_exc()
        
        return None
    
    def _create_position_prompt(self, task, previous_position):
        """Create detailed VLM prompt for position estimation"""
        
        prompt = f"""You are a visual localization AI. Analyze the first-person view and house layout to determine the actor's exact position.

**YOUR TASK:**
Determine WHERE the actor is located in the house based on what they see in IMAGE 1 (first-person view) and the house layout shown in IMAGE 2.

**CURRENT TASK:** {task}

**IMAGE 1 (First-Person View):**
- Shows what the actor sees from their current position
- Contains visual landmarks (furniture, walls, doors, fixtures)
- Use this to identify the room and position within it

**IMAGE 2 (House Layout):**
- Top-down floor plan of the entire house
- Shows room boundaries and layout
- Use this as reference for coordinate estimation

**ROOM LANDMARKS GUIDE:**
"""
        
        # Add landmark information
        for room, info in self.room_landmarks.items():
            prompt += f"\n**{room}:** {info['description']}\n"
            prompt += f"  Furniture: {', '.join(info['furniture'])}\n"
        
        prompt += """
**POSITION ESTIMATION PROCESS:**

1. **Identify Room:** Match visible furniture/features in FP view to room landmarks
2. **Estimate Position Within Room:**
   - Normalized X: 0.0 = leftmost, 1.0 = rightmost (on the house layout image)
   - Normalized Y: 0.0 = topmost, 1.0 = bottommost (on the house layout image)
   - Look at where the room is on the layout image
   - Estimate where within that room the actor stands
3. **Determine Orientation:** Which direction is the actor facing?
   - 0° = Facing toward top of layout image (NORTH)
   - 90° = Facing toward right of layout image (EAST)
   - 180° = Facing toward bottom of layout image (SOUTH)
   - 270° = Facing toward left of layout image (WEST)
4. **Assess Confidence:** How certain are you? (0.0 = guessing, 1.0 = very confident)

**CRITICAL COORDINATE GUIDELINES:**
- X and Y are normalized (0.0 to 1.0) relative to the ENTIRE house layout image
- NOT relative to just the room - relative to the whole image
- If room is in top-left corner of layout, Y will be closer to 0.0
- If room is in bottom-right corner of layout, X and Y will be closer to 1.0
"""

        # Add previous position context if available
        if previous_position:
            prompt += f"""
**PREVIOUS POSITION (for continuity check):**
- Last room: {previous_position.get('room', 'UNKNOWN')}
- Last position: ({previous_position.get('estimated_x_normalized', 0.5):.3f}, {previous_position.get('estimated_y_normalized', 0.5):.3f})
- Last facing: {previous_position.get('estimated_angle', 0):.1f}°
- Note: Actor should be NEAR this position (people don't teleport)
"""
        
        prompt += """
**RESPONSE FORMAT (JSON ONLY):**
{
    "room": "LIVING_ROOM|KITCHEN|BEDROOM|BATHROOM|HALLWAY",
    "estimated_x_normalized": <float 0.0-1.0>,
    "estimated_y_normalized": <float 0.0-1.0>,
    "estimated_angle": <float 0-360>,
    "confidence": <float 0.0-1.0>,
    "landmarks_visible": ["landmark1", "landmark2", "landmark3"],
    "reasoning": "Detailed explanation of position estimation"
}

**EXAMPLE RESPONSE:**
{
    "room": "KITCHEN",
    "estimated_x_normalized": 0.65,
    "estimated_y_normalized": 0.30,
    "estimated_angle": 180.0,
    "confidence": 0.85,
    "landmarks_visible": ["stove", "refrigerator", "sink"],
    "reasoning": "First-person view shows a stove directly ahead with refrigerator to the right. Based on house layout, kitchen is in upper-right area of the image. The stove is on the north wall, actor facing south (180°). Estimated position at normalized (0.65, 0.30) which places actor in center of kitchen area on the layout."
}

Provide ONLY valid JSON, no additional text before or after.
"""
        
        return prompt
    
    def _parse_position_response(self, response):
        """Parse VLM response to extract position data"""
        
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON directly
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    print(f"❌ No JSON found in response")
                    print(f"Response: {response[:200]}...")
                    return None
            
            data = json.loads(json_str)
            
            # Validate required fields
            required = ['room', 'estimated_x_normalized', 'estimated_y_normalized', 
                       'estimated_angle', 'confidence']
            for field in required:
                if field not in data:
                    print(f"❌ Missing required field: {field}")
                    return None
            
            # Validate ranges
            if not (0.0 <= data['estimated_x_normalized'] <= 1.0):
                print(f"⚠️ X coordinate out of range: {data['estimated_x_normalized']}, clamping to [0,1]")
                data['estimated_x_normalized'] = max(0.0, min(1.0, data['estimated_x_normalized']))
            
            if not (0.0 <= data['estimated_y_normalized'] <= 1.0):
                print(f"⚠️ Y coordinate out of range: {data['estimated_y_normalized']}, clamping to [0,1]")
                data['estimated_y_normalized'] = max(0.0, min(1.0, data['estimated_y_normalized']))
            
            if not (0.0 <= data['estimated_angle'] <= 360.0):
                print(f"⚠️ Angle out of range: {data['estimated_angle']}, normalizing")
                data['estimated_angle'] = data['estimated_angle'] % 360.0
            
            if not (0.0 <= data['confidence'] <= 1.0):
                print(f"⚠️ Confidence out of range: {data['confidence']}, clamping to [0,1]")
                data['confidence'] = max(0.0, min(1.0, data['confidence']))
            
            # Ensure landmarks_visible is a list
            if 'landmarks_visible' not in data:
                data['landmarks_visible'] = []
            elif not isinstance(data['landmarks_visible'], list):
                data['landmarks_visible'] = [str(data['landmarks_visible'])]
            
            # Ensure reasoning exists
            if 'reasoning' not in data:
                data['reasoning'] = "No reasoning provided"
            
            return data
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"Failed to parse: {response[:300]}...")
            return None
        except Exception as e:
            print(f"❌ Error parsing response: {e}")
            return None
    
    def generate_position_map(self, position_data, output_path=None):
        """
        Generate navigation map with VLM-estimated position
        
        Args:
            position_data: Position dict from estimate_position()
            output_path: Where to save (auto-generated if None)
            
        Returns:
            str: Path to generated map
        """
        
        if not position_data:
            print("❌ No position data to generate map")
            return None
        
        # Create output path
        if output_path is None:
            output_dir = Path(__file__).parent / 'generated_maps'
            output_dir.mkdir(exist_ok=True)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path = output_dir / f'vlm_position_{timestamp}.png'
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create map image
        map_image = self.house_layout.copy()
        draw = ImageDraw.Draw(map_image)
        
        # Get position in pixels
        x = position_data['map_x']
        y = position_data['map_y']
        angle_deg = position_data['estimated_angle']
        
        # Draw path
        if len(self.position_history) > 1:
            # Draw path
            points = [(p['map_x'], p['map_y']) for p in self.position_history[-10:]]
            if len(points) > 1:
                for i in range(len(points) - 1):
                    draw.line([points[i], points[i+1]], fill='rgb(0,255,0)', width=3)
        
        # Draw human figure at current position
        self._draw_human_figure(draw, x, y, angle_deg, size=40)
        
        # Add text overlay with position info
        self._draw_info_overlay(draw, position_data)
        
        # Save map
        map_image.save(str(output_path))
        
        print(f"✅ VLM position map saved: {output_path.name}")
        
        return str(output_path)
    
    def _draw_human_figure(self, draw, x, y, angle_deg, size=40):
        """Draw human figure with orientation arrow"""
        
        # Convert angle to radians (0° = North/Up, clockwise)
        angle_rad = math.radians(angle_deg)
        
        # Draw body circle (red) - use RGB strings for PIL compatibility
        radius = size // 2
        draw.ellipse([x - radius, y - radius, x + radius, y + radius],
                    fill='rgb(255,0,0)', outline='rgb(200,0,0)', width=3)
        
        # Draw orientation arrow
        arrow_length = size * 1.5
        tip_x = x + arrow_length * math.sin(angle_rad)
        tip_y = y - arrow_length * math.cos(angle_rad)
        
        # Arrow triangle
        arrow_width = size * 0.6
        perp_angle_1 = angle_rad + math.pi * 0.75
        perp_angle_2 = angle_rad - math.pi * 0.75
        
        base_1_x = x + arrow_width * math.sin(perp_angle_1)
        base_1_y = y - arrow_width * math.cos(perp_angle_1)
        base_2_x = x + arrow_width * math.sin(perp_angle_2)
        base_2_y = y - arrow_width * math.cos(perp_angle_2)
        
        points = [(int(tip_x), int(tip_y)),
                 (int(base_1_x), int(base_1_y)),
                 (int(base_2_x), int(base_2_y))]
        
        draw.polygon(points, fill='rgb(255,0,0)', outline='rgb(255,0,0)', width=2)
        
        # Draw center dot
        dot_size = size // 6
        draw.ellipse([x - dot_size, y - dot_size, x + dot_size, y + dot_size],
                    fill='rgb(255,255,255)', outline='rgb(255,0,0)', width=1)
    
    def _draw_info_overlay(self, draw, position_data):
        """Draw information overlay on map"""
        
        try:
            # Use default font (PIL built-in)
            font = ImageFont.load_default()
        except:
            font = None
        
        # Create info text
        info_lines = [
            f"Room: {position_data['room']}",
            f"Position: ({position_data['estimated_x_normalized']:.2f}, {position_data['estimated_y_normalized']:.2f})",
            f"Facing: {position_data['estimated_angle']:.1f}°",
            f"Confidence: {position_data['confidence']:.0%}"
        ]
        
        # Draw semi-transparent background
        text_y = 10
        for line in info_lines:
            # Draw text with background (opaque white)
            draw.rectangle([5, text_y - 2, 350, text_y + 12],
                         fill='rgb(255,255,255)')
            draw.text((10, text_y), line, fill='rgb(0,0,0)', font=font)
            text_y += 15


# Standalone test function
def test_vlm_position_estimator():
    """Test VLM position estimation with a sample screenshot"""
    
    print("🧪 Testing VLM Position Estimator\n")
    
    # Mock VLM function for testing
    def mock_vlm(prompt, images):
        return '''{
            "room": "KITCHEN",
            "estimated_x_normalized": 0.65,
            "estimated_y_normalized": 0.25,
            "estimated_angle": 180.0,
            "confidence": 0.85,
            "landmarks_visible": ["stove", "refrigerator", "sink"],
            "reasoning": "Test position estimation"
        }'''
    
    # Initialize estimator
    estimator = VLMPositionEstimator()
    
    # Find a test screenshot
    captures_dir = Path(__file__).parent.parent / 'blender' / 'captures'
    if captures_dir.exists():
        screenshots = sorted(captures_dir.glob('fp_view_*.png'))
        if screenshots:
            test_screenshot = screenshots[-1]
            print(f"📸 Using: {test_screenshot}")
            
            # Estimate position
            position = estimator.estimate_position(
                test_screenshot,
                "Go to the kitchen",
                mock_vlm
            )
            
            if position:
                # Generate map
                map_path = estimator.generate_position_map(position)
                print(f"\n✅ Test complete! Map: {map_path}")
        else:
            print("❌ No screenshots found in captures/")
    else:
        print("❌ Captures directory not found")


if __name__ == '__main__':
    test_vlm_position_estimator()
