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
        
        print(f"📍 VESPER Position Mapper initialized")
        print(f"🗺️ Base map: {os.path.basename(self.house_layout_path) if self.house_layout_path else 'None'}")
        print(f"📁 Output directory: {self.map_output_dir}")
    
    def _load_base_map(self):
        """Load and prepare the base house layout image"""
        try:
            if self.house_layout_path and os.path.exists(self.house_layout_path):
                self.base_map = Image.open(self.house_layout_path).convert('RGB')
                self.map_width, self.map_height = self.base_map.size
                print(f"✅ Base map loaded: {self.map_width}x{self.map_height}")
            else:
                print(f"⚠️ House layout not found: {self.house_layout_path}")
                print("📝 Creating blank map template")
                self._create_blank_map()
        except Exception as e:
            print(f"❌ Error loading base map: {e}")
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
    
    def update_actor_position(self, world_x, world_y, room=None, task=None, target_room=None):
        """Update actor's current position and context
        
        Args:
            world_x: Actor's world X coordinate from BGE
            world_y: Actor's world Y coordinate from BGE  
            room: Current room name (optional)
            task: Current task name (optional)
            target_room: Target room for current task (optional)
        """
        # Convert world coordinates to map coordinates
        map_x, map_y = self._world_to_map_coordinates(world_x, world_y)
        
        # Store previous position in history
        if self.current_position != [0, 0]:
            self.position_history.append({
                'position': self.current_position.copy(),
                'room': self.current_room,
                'timestamp': time.time()
            })
        
        # Update current state
        self.current_position = [map_x, map_y]
        if room:
            self.current_room = room
        if task:
            self.current_task = task  
        if target_room:
            self.target_room = target_room
        
        print(f"📍 Actor position updated: World({world_x:.2f}, {world_y:.2f}) → Map({map_x}, {map_y})")
        print(f"🏠 Current room: {self.current_room} | Target: {self.target_room}")
    
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
            print("❌ No base map available for position mapping")
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
        print(f"🗺️ Position map generated: {filename}")
        
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
        """Draw the current actor position marker as a human-like indicator"""
        if self.current_position == [0, 0]:
            return
        
        x, y = self.current_position
        size = self.actor_marker_size
        
        # Draw human-like figure
        self._draw_human_indicator(draw, x, y, size)
        
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
            
            # Prepare info text
            info_lines = [
                f"Current Room: {self.current_room}",
                f"Target Room: {self.target_room}",
                f"Task: {self.current_task[:30]}..." if len(self.current_task) > 30 else f"Task: {self.current_task}",
                f"Position: ({self.current_position[0]}, {self.current_position[1]})",
                f"History: {len(self.position_history)} positions"
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
            print(f"⚠️ Error drawing info overlay: {e}")
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
        print(f"🧭 Navigation context map generated: {filename}")
        
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
            
            info_text = f"Current: {self.current_room} → Target: {self.target_room}"
            draw.text((10, self.map_height - 25), info_text, fill=(0, 0, 0), font=font)
            
        except Exception as e:
            print(f"⚠️ Error drawing minimal overlay: {e}")
    
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
        
        print(f"💾 Position data saved: {filename}")
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
            print(f"⚠️ Error getting map number, using 1: {e}")
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
                        print(f"🗑️ Cleaned up old map: navigation_context_{number:03d}.png")
                    except:
                        pass
                        
        except Exception as e:
            print(f"⚠️ Error cleaning up old maps: {e}")

    def manual_cleanup_maps(self, keep_last=None):
        """Manually clean up old maps (since auto-cleanup is disabled)
        
        Args:
            keep_last: Number of recent maps to keep. If None, shows count only.
        """
        try:
            if not os.path.exists(self.map_output_dir):
                print("📁 Map output directory doesn't exist")
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
            print(f"📊 Found {total_maps} navigation context maps")
            
            if keep_last is None:
                print("💡 To clean up, call: mapper.manual_cleanup_maps(keep_last=20)")
                return total_maps
            
            if total_maps <= keep_last:
                print(f"✅ No cleanup needed - only {total_maps} maps (keeping {keep_last})")
                return total_maps
            
            # Sort by number and delete oldest ones
            numbered_maps.sort(key=lambda x: x[1])
            maps_to_delete = numbered_maps[:-keep_last]
            
            print(f"🗑️ Cleaning up {len(maps_to_delete)} old maps (keeping last {keep_last})")
            deleted_count = 0
            
            for filepath, number in maps_to_delete:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                    print(f"  🗑️ Deleted: navigation_context_{number:03d}.png")
                except Exception as e:
                    print(f"  ⚠️ Failed to delete map {number:03d}: {e}")
            
            print(f"✅ Cleanup complete! Deleted {deleted_count}/{len(maps_to_delete)} old maps")
            return total_maps - deleted_count
            
        except Exception as e:
            print(f"❌ Error during manual cleanup: {e}")
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
    print("🧪 Testing VESPER Position Mapping System")
    
    mapper = create_position_mapper()
    
    # Simulate some actor movements
    test_positions = [
        (-2.0, -1.0, "LIVING_ROOM", "Make a phone call", "DINING_ROOM"),
        (-1.5, 0.0, "LIVING_ROOM", "Make a phone call", "DINING_ROOM"), 
        (-1.0, 1.0, "HALLWAY", "Make a phone call", "DINING_ROOM"),
        (0.0, 2.0, "KITCHEN", "Make a phone call", "DINING_ROOM"),
    ]
    
    for i, (x, y, room, task, target) in enumerate(test_positions):
        print(f"\n📍 Test position {i+1}: ({x}, {y}) in {room}")
        mapper.update_actor_position(x, y, room, task, target)
        
        if i == len(test_positions) - 1:  # Last position
            map_path = mapper.generate_current_position_map()
            nav_path = mapper.generate_navigation_context_map()
            data_path = mapper.save_position_data()
            
            print(f"✅ Generated files:")
            print(f"  📍 Position map: {os.path.basename(map_path) if map_path else 'None'}")
            print(f"  🧭 Navigation map: {os.path.basename(nav_path) if nav_path else 'None'}")
            print(f"  💾 Position data: {os.path.basename(data_path) if data_path else 'None'}")
    
    print("\n🎉 Position mapping test completed!")