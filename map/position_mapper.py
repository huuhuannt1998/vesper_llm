#!/usr/bin/env python3
"""
Dynamic Actor Position Mapping System for VESPER Navigation

This module creates dynamic maps showing the actor's current position on the house layout,
providing enhanced spatial awareness for VLM navigation decisions.

Features:
- Overlay actor position marker on house layout
- Track movement history and path  
- Generate position-aware maps for VLM analysis
- Support different map styles (current position, path history, target areas)
"""

import os
import sys
import json
import time
import math
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import numpy as np

class VESPERPositionMapper:
    """Dynamic mapping system for VESPER actor position visualization"""
    
    def __init__(self, house_layout_path=None, map_output_dir=None):
        """Initialize the position mapper
        
        Args:
            house_layout_path: Path to house_layout_reference2.png
            map_output_dir: Directory to save generated maps
        """
        # Set up paths
        if map_output_dir is None:
            map_output_dir = os.path.join(os.path.dirname(__file__), "generated_maps")
        
        self.map_output_dir = map_output_dir
        os.makedirs(self.map_output_dir, exist_ok=True)
        
        # Load base house layout
        if house_layout_path is None:
            # Default path relative to project structure
            house_layout_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "blender",
                "house_layout_reference2.png"
            )
        
        self.house_layout_path = house_layout_path
        self.base_map = None
        self.map_width = 800
        self.map_height = 600
        
        # Actor tracking
        self.current_position = [0, 0]
        self.position_history = []
        self.current_room = "UNKNOWN"
        self.target_room = "UNKNOWN"
        self.current_task = ""
        
        # Map generation settings
        self.actor_marker_size = 40  # Increased from 12 to make human figure bigger
        self.path_line_width = 3
        self.room_label_font_size = 16
        
        # Colors (RGB)
        self.colors = {
            'actor_current': (255, 0, 0),      # Red - current position
            'actor_history': (255, 165, 0),    # Orange - position history  
            'path_line': (0, 255, 0),          # Green - movement path
            'target_area': (0, 0, 255),        # Blue - target room highlight
            'text_bg': (255, 255, 255),        # White - text background
            'text_fg': (0, 0, 0),              # Black - text foreground
        }
        
        # Load and prepare base map
        self._load_base_map()
        
        print(f"≡ƒôì VESPER Position Mapper initialized")
        print(f"≡ƒù║∩╕Å Base map: {os.path.basename(self.house_layout_path) if self.house_layout_path else 'None'}")
        print(f"≡ƒôü Output directory: {self.map_output_dir}")
    
    def _load_base_map(self):
        """Load and prepare the base house layout image"""
        try:
            if self.house_layout_path and os.path.exists(self.house_layout_path):
                self.base_map = Image.open(self.house_layout_path).convert('RGB')
                self.map_width, self.map_height = self.base_map.size
                print(f"Γ£à Base map loaded: {self.map_width}x{self.map_height}")
            else:
                print(f"ΓÜá∩╕Å House layout not found: {self.house_layout_path}")
                print("≡ƒô¥ Creating blank map template")
                self._create_blank_map()
        except Exception as e:
            print(f"Γ¥î Error loading base map: {e}")
            self._create_blank_map()
    
    def _create_blank_map(self):
        """Create a blank map template if house layout is unavailable"""
        self.base_map = Image.new('RGB', (self.map_width, self.map_height), (240, 240, 240))
        draw = ImageDraw.Draw(self.base_map)
        
        # Draw simple room outlines
        # This is a fallback - real house layout should be used
        rooms = [
            {'name': 'LIVING_ROOM', 'rect': (50, 50, 350, 300), 'color': (220, 220, 255)},
            {'name': 'KITCHEN', 'rect': (350, 50, 550, 200), 'color': (255, 220, 220)},
            {'name': 'BEDROOM', 'rect': (350, 200, 550, 350), 'color': (220, 255, 220)},
            {'name': 'BATHROOM', 'rect': (550, 200, 650, 300), 'color': (255, 255, 220)},
        ]
        
        for room in rooms:
            draw.rectangle(room['rect'], fill=room['color'], outline=(100, 100, 100), width=2)
            
            # Add room labels
            label_x = room['rect'][0] + 10
            label_y = room['rect'][1] + 10
            draw.text((label_x, label_y), room['name'], fill=(0, 0, 0))
    
    def update_actor_position(self, world_x, world_y, room=None, task=None, target_room=None, orientation=None):
        """Update actor's current position and context
        
        Args:
            world_x: Actor's world X coordinate from BGE
            world_y: Actor's world Y coordinate from BGE  
            room: Current room name (optional)
            task: Current task name (optional)
            target_room: Target room for current task (optional)
            orientation: Actor's facing angle in radians (optional)
        """
        # Debug logging for orientation
        if orientation is not None:
            import math
            print(f"≡ƒº¡ DEBUG Orientation: {orientation:.4f} rad = {math.degrees(orientation):.1f}┬░")
        
        # Convert world coordinates to map coordinates
        map_x, map_y = self._world_to_map_coordinates(world_x, world_y)
        
        # Store previous position in history
        if self.current_position != [0, 0]:
            self.position_history.append({
                'position': self.current_position.copy(),
                'room': self.current_room,
                'timestamp': time.time(),
                'orientation': getattr(self, 'current_orientation', None)
            })
        
        # Update current state
        self.current_position = [map_x, map_y]
        if room:
            self.current_room = room
        if task:
            self.current_task = task  
        if target_room:
            self.target_room = target_room
        if orientation is not None:
            self.current_orientation = orientation
        
        orientation_deg = orientation * (180 / 3.14159) if orientation is not None else 0
        print(f"≡ƒôì Actor position updated: World({world_x:.2f}, {world_y:.2f}) ΓåÆ Map({map_x}, {map_y}), Facing: {orientation_deg:.1f}┬░")
        print(f"≡ƒÅá Current room: {self.current_room} | Target: {self.target_room}")
    
    def _world_to_map_coordinates(self, world_x, world_y):
        """Convert BGE world coordinates to map pixel coordinates
        
        This function needs to be calibrated based on your specific house model
        and the coordinate system used in BGE vs the house layout image.
        """
        
        # CALIBRATION NEEDED: These values should be adjusted based on your house
        # You'll need to determine the relationship between BGE world coords and map pixels
        
        # Example calibration (adjust these values):
        world_bounds = {
            'min_x': -10.0,   # Leftmost world coordinate  
            'max_x': 10.0,    # Rightmost world coordinate
            'min_y': -8.0,    # Bottom world coordinate (BGE Y)
            'max_y': 8.0,     # Top world coordinate (BGE Y)
        }
        
        # Map the world coordinates to map pixel coordinates
        normalized_x = (world_x - world_bounds['min_x']) / (world_bounds['max_x'] - world_bounds['min_x'])
        normalized_y = (world_y - world_bounds['min_y']) / (world_bounds['max_y'] - world_bounds['min_y'])
        
        # Convert to map pixel coordinates  
        map_x = int(normalized_x * self.map_width)
        map_y = int((1.0 - normalized_y) * self.map_height)  # Flip Y axis (image coords)
        
        # Clamp to map bounds
        map_x = max(0, min(self.map_width - 1, map_x))
        map_y = max(0, min(self.map_height - 1, map_y))
        
        return map_x, map_y
    
    def generate_current_position_map(self, include_history=True):
        """Generate a map showing current actor position
        
        Args:
            include_history: Whether to show movement path history
            
        Returns:
            Path to generated map image
        """
        if not self.base_map:
            print("Γ¥î No base map available for position mapping")
            return None
        
        # Create working copy of base map
        map_image = self.base_map.copy()
        draw = ImageDraw.Draw(map_image)
        
        # Draw position history path
        if include_history and len(self.position_history) > 0:
            self._draw_position_history(draw)
        
        # Draw current position marker
        self._draw_current_position_marker(draw)
        
        # Add information overlay
        self._draw_info_overlay(draw)
        
        # Save map
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"actor_position_map_{timestamp}.png"
        output_path = os.path.join(self.map_output_dir, filename)
        
        map_image.save(output_path)
        print(f"≡ƒù║∩╕Å Position map generated: {filename}")
        
        return output_path
    
    def _draw_position_history(self, draw):
        """Draw the movement history path on the map with human-like indicators"""
        if len(self.position_history) < 1:
            return
        
        # Draw path lines between historical positions
        path_points = [pos['position'] for pos in self.position_history[-10:]]  # Last 10 positions
        if self.current_position != [0, 0]:
            path_points.append(self.current_position)
        
        # Draw path as a trail
        for i in range(len(path_points) - 1):
            x1, y1 = path_points[i]
            x2, y2 = path_points[i + 1]
            
            # Draw path line with gradient effect
            line_width = max(1, self.path_line_width - i // 3)  # Fade older paths
            draw.line([(x1, y1), (x2, y2)], fill=self.colors['path_line'], width=line_width)
        
        # Draw historical position markers as footprints or small human figures
        for i, pos_data in enumerate(self.position_history[-5:]):  # Last 5 positions
            x, y = pos_data['position']
            
            # Calculate age-based scaling (newer = larger)
            age_factor = (i + 1) / len(self.position_history[-5:])
            marker_scale = 0.3 + (age_factor * 0.4)  # Scale between 0.3 and 0.7
            
            self._draw_footprint(draw, x, y, marker_scale, age_factor)
    
    def _draw_footprint(self, draw, x, y, scale, age_factor):
        """Draw a footprint marker for historical positions"""
        
        # Footprint size based on scale
        foot_length = int(8 * scale)
        foot_width = int(4 * scale)
        
        # Color gets more transparent/faded with age
        alpha = int(100 + (age_factor * 155))  # 100-255 alpha range
        foot_color = (*self.colors['actor_history'], alpha) if len(self.colors['actor_history']) == 3 else self.colors['actor_history']
        
        # Draw simple footprint shape (oval)
        draw.ellipse([
            x - foot_width//2, y - foot_length//2,
            x + foot_width//2, y + foot_length//2
        ], fill=foot_color, outline=(100, 100, 100), width=1)
        
        # Add small toe marks for more realistic footprint
        toe_y = y - foot_length//3
        for toe_offset in [-1, 0, 1]:
            toe_x = x + toe_offset * 2
            draw.ellipse([
                toe_x - 1, toe_y - 1,
                toe_x + 1, toe_y + 1
            ], fill=foot_color, outline=None)
    
    def _draw_current_position_marker(self, draw):
        """Draw the current actor position marker with orientation arrow"""
        if self.current_position == [0, 0]:
            return
        
        x, y = self.current_position
        size = self.actor_marker_size
        
        # Draw orientation arrow/triangle showing facing direction
        orientation = getattr(self, 'current_orientation', 0)
        self._draw_orientation_arrow(draw, x, y, size, orientation)
        
        # Add position label
        self._draw_position_label(draw, x, y)
    
    def _draw_human_indicator(self, draw, x, y, size):
        """Draw a human-like figure to represent the actor"""
        
        # Scale factor for human proportions
        scale = size / 12.0
        
        # Human figure components
        head_radius = int(3 * scale)
        body_height = int(6 * scale) 
        body_width = int(2 * scale)
        arm_length = int(3 * scale)
        leg_length = int(4 * scale)
        
        # Colors
        head_color = (255, 220, 177)  # Skin tone
        body_color = (0, 100, 200)    # Blue shirt
        outline_color = (0, 0, 0)     # Black outline
        
        # Draw head (circle)
        head_x, head_y = x, y - int(4 * scale)
        draw.ellipse([
            head_x - head_radius, head_y - head_radius,
            head_x + head_radius, head_y + head_radius
        ], fill=head_color, outline=outline_color, width=1)
        
        # Draw body (rectangle)
        body_top = head_y + head_radius
        body_bottom = body_top + body_height
        body_left = x - body_width // 2
        body_right = x + body_width // 2
        
        draw.rectangle([
            body_left, body_top,
            body_right, body_bottom
        ], fill=body_color, outline=outline_color, width=1)
        
        # Draw arms (lines extending from upper body)
        arm_y = body_top + int(1 * scale)
        # Left arm
        draw.line([
            (body_left, arm_y),
            (body_left - arm_length, arm_y + int(1 * scale))
        ], fill=head_color, width=2)
        # Right arm  
        draw.line([
            (body_right, arm_y),
            (body_right + arm_length, arm_y + int(1 * scale))
        ], fill=head_color, width=2)
        
        # Draw legs (lines extending from lower body)
        leg_start_y = body_bottom
        leg_end_y = leg_start_y + leg_length
        # Left leg
        draw.line([
            (body_left + 1, leg_start_y),
            (body_left - int(1 * scale), leg_end_y)
        ], fill=outline_color, width=2)
        # Right leg
        draw.line([
            (body_right - 1, leg_start_y), 
            (body_right + int(1 * scale), leg_end_y)
        ], fill=outline_color, width=2)
        
        # Add direction indicator (small arrow pointing forward)
        self._draw_direction_arrow(draw, x, head_y - head_radius - 3, scale)
    
    def _draw_direction_arrow(self, draw, x, y, scale):
        """Draw a small arrow indicating the actor's facing direction"""
        arrow_size = int(4 * scale)
        arrow_color = (255, 0, 0)  # Red arrow
        
        # Simple upward-pointing arrow (indicating "forward" direction)
        points = [
            (x, y - arrow_size),           # Arrow tip
            (x - arrow_size//2, y),        # Left base
            (x + arrow_size//2, y)         # Right base
        ]
        
        # Draw arrow as polygon
        draw.polygon(points, fill=arrow_color, outline=(0, 0, 0), width=1)
    
    def _convert_bge_to_screen_coordinates(self, orientation_radians):
        """Convert BGE Game Engine orientation to map screen coordinates
        
        CRITICAL: Two different coordinate systems need to be synchronized:
        
        1. BGE GAME ENGINE SYSTEM (First-person navigation):
           - Actor turns LEFT/RIGHT and moves FORWARD (like real person)
           - Z-axis rotation: 0 = facing +Y direction (Blender forward)
           - This is how the actor actually moves in the game
        
        2. MAP COORDINATE SYSTEM (VLM spatial understanding):
           - Uses NORTH/SOUTH/EAST/WEST for clear spatial reference
           - Screen coordinates: 0┬░ = North (up), 90┬░ = East (right)
           - This helps VLM understand layout and directions
        
        CONVERSION STRATEGY:
        - BGE forward (+Y) should map to NORTH (up on screen) 
        - Need to account for coordinate system differences between Game Engine and Editor
        - Based on the images: actor faces sofa (should be WEST) but shows as EAST
        - This indicates we need to flip the direction by ╧Ç (180┬░)
        """
        
        # COORDINATE SYSTEM ANALYSIS from the provided images:
        # - First-person view: Actor faces sofa (this should be WEST on map)
        # - Current map: Shows arrow pointing EAST (wrong direction)
        # - Test results show we need different conversion logic
        
        # FINAL SOLUTION based on coordinate system analysis:
        # BGE coordinate system needs to be mapped to screen coordinates as follows:
        # BGE 0┬░ (forward) ΓåÆ WEST (270┬░ on screen)
        # BGE 90┬░ (left) ΓåÆ NORTH (0┬░ on screen) 
        # BGE 180┬░ (back) ΓåÆ EAST (90┬░ on screen)
        # BGE 270┬░ (right) ΓåÆ SOUTH (180┬░ on screen)
        
        # Mathematical conversion: rotate by 3╧Ç/2 and negate angle
        screen_angle = (3 * math.pi / 2) - orientation_radians
        
        # Normalize angle to [0, 2╧Ç] range
        while screen_angle < 0:
            screen_angle += 2 * math.pi
        while screen_angle >= 2 * math.pi:
            screen_angle -= 2 * math.pi
            
        return screen_angle
    
    def _draw_orientation_arrow(self, draw, x, y, size, orientation_radians):
        """Draw a large orientation arrow/triangle showing actor's facing direction
        
        Args:
            draw: PIL ImageDraw object
            x, y: Center position on map
            size: Base size for the arrow
            orientation_radians: Actor's facing angle in radians (0 = East, ╧Ç/2 = North in BGE)
        """
        import math
        
        # Arrow dimensions (smaller size)
        arrow_length = size * 1.3  # Reduced from 2.0
        arrow_width = size * 0.8   # Reduced from 1.2
        
        # COORDINATE SYSTEM SYNCHRONIZATION FIX:
        # Convert Game Engine orientation to Map coordinates
        angle = self._convert_bge_to_screen_coordinates(orientation_radians)
        
        # ENHANCED DEBUG: Show detailed coordinate conversion
        orientation_deg = math.degrees(orientation_radians)
        screen_deg = math.degrees(angle)
        
        # Determine facing direction for verification
        direction_name = "UNKNOWN"
        if 315 <= screen_deg or screen_deg < 45:
            direction_name = "NORTH (Γåæ)"
        elif 45 <= screen_deg < 135:
            direction_name = "EAST (ΓåÆ)"
        elif 135 <= screen_deg < 225:
            direction_name = "SOUTH (Γåô)"
        elif 225 <= screen_deg < 315:
            direction_name = "WEST (ΓåÉ)"
        
        print(f"≡ƒº¡ BGE Raw Orientation: {orientation_radians:.4f} rad = {orientation_deg:.1f}┬░")
        print(f"≡ƒÄ¿ Map Display Angle: {angle:.4f} rad = {screen_deg:.1f}┬░ ΓåÆ {direction_name}")
        print(f"≡ƒöä Coordinate System: Game Engine ΓåÆ Map Conversion Applied")
        
        # Calculate arrow points (triangle)
        # Tip of arrow
        tip_x = x + arrow_length * math.cos(angle)
        tip_y = y + arrow_length * math.sin(angle)
        
        # DEBUG: Show arrow tip position
        print(f"≡ƒÄ¿ Arrow tip: ({tip_x:.1f}, {tip_y:.1f}) relative to center ({x}, {y})")
        
        # Base corners (perpendicular to direction)
        perp_angle_1 = angle + math.pi * 0.75  # 135┬░ from direction
        perp_angle_2 = angle - math.pi * 0.75  # -135┬░ from direction
        
        base_1_x = x + arrow_width * math.cos(perp_angle_1)
        base_1_y = y + arrow_width * math.sin(perp_angle_1)
        
        base_2_x = x + arrow_width * math.cos(perp_angle_2)
        base_2_y = y + arrow_width * math.sin(perp_angle_2)
        
        # Draw filled triangle
        points = [
            (int(tip_x), int(tip_y)),
            (int(base_1_x), int(base_1_y)),
            (int(base_2_x), int(base_2_y))
        ]
        
        # Red arrow with black outline
        draw.polygon(points, fill=(255, 50, 50), outline=(0, 0, 0), width=3)
        
        # Draw center circle (smaller)
        circle_radius = int(size * 0.4)  # Reduced from 0.6
        draw.ellipse([
            x - circle_radius, y - circle_radius,
            x + circle_radius, y + circle_radius
        ], fill=(255, 100, 100), outline=(0, 0, 0), width=2)
    
    def _draw_position_label(self, draw, x, y):
        """Draw position label next to the human indicator"""
        try:
            font = ImageFont.load_default()
            
            # Position text
            label_text = f"ACTOR"
            if self.current_room != "UNKNOWN":
                label_text += f"\n{self.current_room}"
            
            # Calculate label position (offset from human figure)
            label_x = x + self.actor_marker_size + 5
            label_y = y - 10
            
            # Draw background for text
            text_size = draw.textsize(label_text, font=font)
            text_bg_padding = 2
            
            draw.rectangle([
                label_x - text_bg_padding, 
                label_y - text_bg_padding,
                label_x + text_size[0] + text_bg_padding,
                label_y + text_size[1] + text_bg_padding
            ], fill=(255, 255, 255, 200), outline=(0, 0, 0), width=1)
            
            # Draw text
            draw.text((label_x, label_y), label_text, fill=(0, 0, 0), font=font)
            
        except Exception as e:
            # Fallback: simple text
            draw.text((x + 10, y - 5), "ACTOR", fill=(0, 0, 0))
    
    def _draw_info_overlay(self, draw):
        """Draw information overlay on the map"""
        try:
            # Try to load a font, fallback to default
            try:
                font = ImageFont.truetype("arial.ttf", self.room_label_font_size)
            except:
                font = ImageFont.load_default()
            
            # Prepare info text with orientation
            orientation_deg = self.current_orientation * (180 / 3.14159) if self.current_orientation is not None else 0
            
            # Determine cardinal direction from orientation
            if orientation_deg >= -22.5 and orientation_deg < 22.5:
                cardinal = "EAST ΓåÆ"
            elif orientation_deg >= 22.5 and orientation_deg < 67.5:
                cardinal = "NORTHEAST Γåù"
            elif orientation_deg >= 67.5 and orientation_deg < 112.5:
                cardinal = "NORTH Γåæ"
            elif orientation_deg >= 112.5 and orientation_deg < 157.5:
                cardinal = "NORTHWEST Γåû"
            elif orientation_deg >= 157.5 or orientation_deg < -157.5:
                cardinal = "WEST ΓåÉ"
            elif orientation_deg >= -157.5 and orientation_deg < -112.5:
                cardinal = "SOUTHWEST ΓåÖ"
            elif orientation_deg >= -112.5 and orientation_deg < -67.5:
                cardinal = "SOUTH Γåô"
            else:
                cardinal = "SOUTHEAST Γåÿ"
            
            info_lines = [
                f"≡ƒÄ» TASK: {self.current_task[:35]}..." if len(self.current_task) > 35 else f"≡ƒÄ» TASK: {self.current_task}",
                f"≡ƒôì Current: {self.current_room}",
                f"≡ƒÄ¬ Target: {self.target_room}",
                f"≡ƒº¡ Facing: {cardinal} ({orientation_deg:.1f}┬░)",
                f"≡ƒôè Position: ({self.current_position[0]}, {self.current_position[1]})",
                f"≡ƒôê Moves: {len(self.position_history)}"
            ]
            
            # Draw info box background
            info_x, info_y = 10, 10
            
            # Get text dimensions (compatible with different PIL versions)
            try:
                max_text_width = max([draw.textsize(line, font=font)[0] for line in info_lines])
                text_height = draw.textsize("A", font=font)[1]
            except AttributeError:
                # Fallback for newer PIL versions
                bbox = draw.textbbox((0, 0), "A", font=font)
                text_height = bbox[3] - bbox[1]
                max_text_width = max([draw.textbbox((0, 0), line, font=font)[2] for line in info_lines])
            
            box_width = max_text_width + 20
            box_height = len(info_lines) * (text_height + 4) + 10
            
            draw.rectangle([
                info_x - 5, info_y - 5,
                info_x + box_width, info_y + box_height
            ], fill=self.colors['text_bg'], outline=(0, 0, 0), width=1)
            
            # Draw info text
            for i, line in enumerate(info_lines):
                text_y = info_y + i * (text_height + 4)
                draw.text((info_x, text_y), line, fill=self.colors['text_fg'], font=font)
                
        except Exception as e:
            print(f"ΓÜá∩╕Å Error drawing info overlay: {e}")
            # Simple fallback - just draw basic position info
            draw.text((10, 10), f"Room: {self.current_room}", fill=(0, 0, 0))
            draw.text((10, 30), f"Target: {self.target_room}", fill=(0, 0, 0))
    
    def generate_navigation_context_map(self):
        """Generate a map specifically for VLM navigation context
        
        This creates a clean map with current position and target area highlighted
        for optimal VLM analysis.
        
        Returns:
            Path to generated navigation context map
        """
        if not self.base_map:
            return None
        
        # Create clean copy for navigation
        map_image = self.base_map.copy()
        draw = ImageDraw.Draw(map_image)
        
        # Highlight target room area if known
        self._highlight_target_area(draw)
        
        # Draw simplified path (last few positions only)
        if len(self.position_history) > 0:
            recent_positions = self.position_history[-3:]  # Last 3 positions
            for pos_data in recent_positions:
                x, y = pos_data['position']
                draw.ellipse([x-3, y-3, x+3, y+3], fill=self.colors['actor_history'])
        
        # Draw prominent current position
        self._draw_current_position_marker(draw)
        
        # Add minimal info overlay
        self._draw_minimal_info_overlay(draw)
        
        # Save navigation context map with sequential numbering
        map_number = self._get_next_map_number()
        filename = f"navigation_context_{map_number:03d}.png"
        output_path = os.path.join(self.map_output_dir, filename)
        
        map_image.save(output_path)
        print(f"≡ƒº¡ Navigation context map generated: {filename}")
        
        # PRESERVE ALL MAPS: Cleanup disabled to keep complete navigation history
        # To re-enable cleanup, uncomment the line below:
        # self._cleanup_old_maps(keep_last=10)
        
        return output_path
    
    def _highlight_target_area(self, draw):
        """Highlight the target room area on the map"""
        # This would need to be customized based on your house layout
        # For now, we'll add a simple target room indicator
        if self.target_room and self.target_room != "UNKNOWN":
            # Add target room highlight logic here
            # This requires knowing the room boundaries on the map
            pass
    
    def _draw_minimal_info_overlay(self, draw):
        """Draw minimal info overlay for navigation context"""
        try:
            font = ImageFont.load_default()
            
            info_text = f"Current: {self.current_room} ΓåÆ Target: {self.target_room}"
            draw.text((10, self.map_height - 25), info_text, fill=(0, 0, 0), font=font)
            
        except Exception as e:
            print(f"ΓÜá∩╕Å Error drawing minimal overlay: {e}")
    
    def save_position_data(self):
        """Save current position tracking data to JSON file"""
        data = {
            'current_position': self.current_position,
            'current_room': self.current_room,
            'target_room': self.target_room,
            'current_task': self.current_task,
            'position_history': self.position_history[-20:],  # Keep last 20 positions
            'timestamp': time.time(),
            'map_bounds': {
                'width': self.map_width,
                'height': self.map_height
            }
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"position_data_{timestamp}.json"
        output_path = os.path.join(self.map_output_dir, filename)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"≡ƒÆ╛ Position data saved: {filename}")
        return output_path

    def _get_next_map_number(self):
        """Get the next sequential map number based on existing files"""
        try:
            if not os.path.exists(self.map_output_dir):
                return 1
            
            # Find all navigation context maps with numbers
            existing_numbers = []
            for filename in os.listdir(self.map_output_dir):
                if filename.startswith("navigation_context_") and filename.endswith(".png"):
                    # Extract number from filename like navigation_context_001.png
                    try:
                        number_part = filename.replace("navigation_context_", "").replace(".png", "")
                        if number_part.isdigit():
                            existing_numbers.append(int(number_part))
                    except:
                        continue
            
            # Return next number in sequence
            if existing_numbers:
                return max(existing_numbers) + 1
            else:
                return 1
                
        except Exception as e:
            print(f"ΓÜá∩╕Å Error getting map number, using 1: {e}")
            return 1

    def _cleanup_old_maps(self, keep_last=10):
        """Keep only the last N navigation context maps to prevent directory clutter"""
        try:
            if not os.path.exists(self.map_output_dir):
                return
            
            # Find all numbered navigation context maps
            numbered_maps = []
            for filename in os.listdir(self.map_output_dir):
                if filename.startswith("navigation_context_") and filename.endswith(".png"):
                    try:
                        number_part = filename.replace("navigation_context_", "").replace(".png", "")
                        if number_part.isdigit():
                            filepath = os.path.join(self.map_output_dir, filename)
                            numbered_maps.append((filepath, int(number_part)))
                    except:
                        continue
            
            # If we have more than keep_last maps, delete the oldest ones
            if len(numbered_maps) > keep_last:
                numbered_maps.sort(key=lambda x: x[1])  # Sort by number
                maps_to_delete = numbered_maps[:-keep_last]  # Keep only the last N
                
                for filepath, number in maps_to_delete:
                    try:
                        os.remove(filepath)
                        print(f"≡ƒùæ∩╕Å Cleaned up old map: navigation_context_{number:03d}.png")
                    except:
                        pass
                        
        except Exception as e:
            print(f"ΓÜá∩╕Å Error cleaning up old maps: {e}")

    def manual_cleanup_maps(self, keep_last=None):
        """Manually clean up old maps (since auto-cleanup is disabled)
        
        Args:
            keep_last: Number of recent maps to keep. If None, shows count only.
        """
        try:
            if not os.path.exists(self.map_output_dir):
                print("≡ƒôü Map output directory doesn't exist")
                return
            
            # Find all numbered navigation context maps
            numbered_maps = []
            for filename in os.listdir(self.map_output_dir):
                if filename.startswith("navigation_context_") and filename.endswith(".png"):
                    try:
                        number_part = filename.replace("navigation_context_", "").replace(".png", "")
                        if number_part.isdigit():
                            filepath = os.path.join(self.map_output_dir, filename)
                            numbered_maps.append((filepath, int(number_part)))
                    except:
                        continue
            
            total_maps = len(numbered_maps)
            print(f"≡ƒôè Found {total_maps} navigation context maps")
            
            if keep_last is None:
                print("≡ƒÆí To clean up, call: mapper.manual_cleanup_maps(keep_last=20)")
                return total_maps
            
            if total_maps <= keep_last:
                print(f"Γ£à No cleanup needed - only {total_maps} maps (keeping {keep_last})")
                return total_maps
            
            # Sort by number and delete oldest ones
            numbered_maps.sort(key=lambda x: x[1])
            maps_to_delete = numbered_maps[:-keep_last]
            
            print(f"≡ƒùæ∩╕Å Cleaning up {len(maps_to_delete)} old maps (keeping last {keep_last})")
            deleted_count = 0
            
            for filepath, number in maps_to_delete:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                    print(f"  ≡ƒùæ∩╕Å Deleted: navigation_context_{number:03d}.png")
                except Exception as e:
                    print(f"  ΓÜá∩╕Å Failed to delete map {number:03d}: {e}")
            
            print(f"Γ£à Cleanup complete! Deleted {deleted_count}/{len(maps_to_delete)} old maps")
            return total_maps - deleted_count
            
        except Exception as e:
            print(f"Γ¥î Error during manual cleanup: {e}")
            return 0

# Convenience functions for easy integration
def create_position_mapper(house_layout_path=None):
    """Create a new position mapper instance"""
    return VESPERPositionMapper(house_layout_path)

def generate_position_map(world_x, world_y, room=None, task=None, target_room=None, mapper=None):
    """Generate a position map with current actor location
    
    Args:
        world_x, world_y: Actor's world coordinates
        room: Current room name
        task: Current task
        target_room: Target room
        mapper: Existing mapper instance (optional)
    
    Returns:
        Path to generated map image
    """
    if mapper is None:
        mapper = create_position_mapper()
    
    mapper.update_actor_position(world_x, world_y, room, task, target_room)
    return mapper.generate_current_position_map()

if __name__ == "__main__":
    # Test the mapping system
    print("≡ƒº¬ Testing VESPER Position Mapping System")
    
    mapper = create_position_mapper()
    
    # Simulate some actor movements
    test_positions = [
        (-2.0, -1.0, "LIVING_ROOM", "Make a phone call", "DINING_ROOM"),
        (-1.5, 0.0, "LIVING_ROOM", "Make a phone call", "DINING_ROOM"), 
        (-1.0, 1.0, "HALLWAY", "Make a phone call", "DINING_ROOM"),
        (0.0, 2.0, "KITCHEN", "Make a phone call", "DINING_ROOM"),
    ]
    
    for i, (x, y, room, task, target) in enumerate(test_positions):
        print(f"\n≡ƒôì Test position {i+1}: ({x}, {y}) in {room}")
        mapper.update_actor_position(x, y, room, task, target)
        
        if i == len(test_positions) - 1:  # Last position
            map_path = mapper.generate_current_position_map()
            nav_path = mapper.generate_navigation_context_map()
            data_path = mapper.save_position_data()
            
            print(f"Γ£à Generated files:")
            print(f"  ≡ƒôì Position map: {os.path.basename(map_path) if map_path else 'None'}")
            print(f"  ≡ƒº¡ Navigation map: {os.path.basename(nav_path) if nav_path else 'None'}")
            print(f"  ≡ƒÆ╛ Position data: {os.path.basename(data_path) if data_path else 'None'}")
    
    print("\n≡ƒÄë Position mapping test completed!")
