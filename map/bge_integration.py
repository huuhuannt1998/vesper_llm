#!/usr/bin/env python3
"""
VESPER BGE Navigation Integration with Dynamic Position Mapping

This module integrates the dynamic position mapping system with the BGE navigation,
automatically generating position-aware maps for enhanced VLM spatial awareness.
"""

import os
import sys

# Add map module to path
current_dir = os.path.dirname(os.path.abspath(__file__))
map_dir = os.path.join(os.path.dirname(current_dir), 'map')
if map_dir not in sys.path:
    sys.path.insert(0, map_dir)

try:
    from position_mapper import VESPERPositionMapper
    MAPPING_AVAILABLE = True
    print("Γ£à Position mapping system available")
except ImportError as e:
    MAPPING_AVAILABLE = False
    print(f"ΓÜá∩╕Å Position mapping not available: {e}")

class BGENavigationMapper:
    """Integration class for BGE navigation with position mapping"""
    
    def __init__(self):
        self.mapper = None
        self.last_map_path = None
        self.map_update_interval = 1  # Generate new map every step for synchronization
        self.step_counter = 0
        
        if MAPPING_AVAILABLE:
            self._initialize_mapper()
    
    def _initialize_mapper(self):
        """Initialize the position mapper with house layout"""
        try:
            # Find house layout path
            house_layout_path = self._find_house_layout()
            
            if house_layout_path:
                self.mapper = VESPERPositionMapper(
                    house_layout_path=house_layout_path,
                    map_output_dir=os.path.join(os.path.dirname(__file__), "generated_maps")
                )
                print("Γ£à BGE Navigation Mapper initialized")
            else:
                print("ΓÜá∩╕Å House layout not found - using fallback mapping")
                self.mapper = VESPERPositionMapper()
                
        except Exception as e:
            print(f"Γ¥î Failed to initialize position mapper: {e}")
            self.mapper = None
    
    def _find_house_layout(self):
        """Find the house layout reference image"""
        # Use only the highlighted room layout
        house_layout_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "blender", "house_layout_reference2.png")
        
        if os.path.exists(house_layout_path):
            print(f"≡ƒÅá Found house layout: {house_layout_path}")
            return house_layout_path
        
        print("ΓÜá∩╕Å House layout reference2.png not found in blender directory")
        return None
    
    def update_position(self, world_x, world_y, room=None, task=None, target_room=None, orientation=None):
        """Update actor position and generate map if needed
        
        Args:
            world_x, world_y: Actor's world coordinates from BGE
            room: Current room detection from VLM
            task: Current CASAS task
            target_room: Target room for current task
            orientation: Actor's facing angle in radians
            
        Returns:
            Path to generated position map (if created), None otherwise
        """
        if not self.mapper:
            return None
        
        try:
            # Update position in mapper
            self.mapper.update_actor_position(world_x, world_y, room, task, target_room, orientation)
            
            self.step_counter += 1
            
            # Generate new map at intervals or when room changes
            should_generate_map = (
                self.step_counter % self.map_update_interval == 0 or  # Regular interval
                room and room != "UNKNOWN" or  # Room detected
                not self.last_map_path  # First map
            )
            
            if should_generate_map:
                map_path = self.mapper.generate_navigation_context_map()
                if map_path:
                    self.last_map_path = map_path
                    print(f"≡ƒù║∩╕Å Updated navigation map: {os.path.basename(map_path)}")
                    return map_path
            
        except Exception as e:
            print(f"Γ¥î Error updating position map: {e}")
        
        return self.last_map_path  # Return last generated map
    
    def get_current_map(self):
        """Get the current navigation context map"""
        return self.last_map_path
    
    def generate_full_history_map(self):
        """Generate a complete map with full movement history"""
        if not self.mapper:
            return None
        
        try:
            return self.mapper.generate_current_position_map(include_history=True)
        except Exception as e:
            print(f"Γ¥î Error generating history map: {e}")
            return None

# Global navigation mapper instance
_global_navigation_mapper = None

def get_navigation_mapper():
    """Get or create the global navigation mapper instance"""
    global _global_navigation_mapper
    if _global_navigation_mapper is None:
        _global_navigation_mapper = BGENavigationMapper()
    return _global_navigation_mapper

def update_actor_position_map(world_x, world_y, room=None, task=None, target_room=None, orientation=None):
    """Convenient function to update actor position and get map
    
    This function can be called directly from llm_bge_navigation.py
    
    Args:
        orientation: Actor's facing angle in radians (Z-axis rotation in BGE)
    
    Returns:
        Path to position-aware navigation map
    """
    mapper = get_navigation_mapper()
    return mapper.update_position(world_x, world_y, room, task, target_room, orientation)

def get_current_position_map():
    """Get the current position map for VLM analysis"""
    mapper = get_navigation_mapper()
    return mapper.get_current_map()

def generate_session_summary_map():
    """Generate a complete session map with full history"""
    mapper = get_navigation_mapper()
    return mapper.generate_full_history_map()

# Test functions
def test_bge_integration():
    """Test the BGE integration system"""
    print("≡ƒº¬ Testing BGE Navigation Mapping Integration")
    
    mapper = get_navigation_mapper()
    
    if not mapper.mapper:
        print("Γ¥î Mapper not available for testing")
        return
    
    # Simulate BGE navigation sequence
    test_sequence = [
        (-1.92, -2.61, "LIVING_ROOM", "Make a phone call", "DINING_ROOM"),
        (-2.36, -1.95, "LIVING_ROOM", "Make a phone call", "DINING_ROOM"),
        (-2.80, -1.30, "HALLWAY", "Make a phone call", "DINING_ROOM"),
        (-3.20, -0.50, "KITCHEN", "Make a phone call", "DINING_ROOM"),
        (-2.90, 0.20, "DINING_ROOM", "Make a phone call", "DINING_ROOM"),
    ]
    
    for i, (x, y, room, task, target) in enumerate(test_sequence):
        print(f"\n≡ƒôì Step {i+1}: Actor at ({x:.2f}, {y:.2f}) in {room}")
        
        map_path = update_actor_position_map(x, y, room, task, target)
        
        if map_path:
            print(f"  ≡ƒù║∩╕Å Generated map: {os.path.basename(map_path)}")
        
        # Simulate task completion
        if room == target and i == len(test_sequence) - 1:
            print(f"Γ£à Task '{task}' completed in {room}")
            summary_map = generate_session_summary_map()
            if summary_map:
                print(f"≡ƒôè Session summary map: {os.path.basename(summary_map)}")

if __name__ == "__main__":
    test_bge_integration()
