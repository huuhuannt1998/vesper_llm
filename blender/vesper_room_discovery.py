"""
VESPER Room Discovery System
===========================

Automatically discovers room layout from Blender scene objects
Maps rooms to CASAS sensor positions for accurate validation
"""

import bge
import os
import json
from typing import Dict, List, Tuple, Optional

class VESPERRoomDiscovery:
    """Automatically discover room layout from Blender scene"""
    
    def __init__(self):
        self.discovered_rooms = {}
        self.room_objects = {}
        self.room_centers = {}
        
        # CASAS sensor mapping (exact from dataset)
        self.casas_room_sensors = {
            'living_room': ['M01', 'M02'],
            'dining_room': ['M03', 'M04', 'M05'], 
            'kitchen': ['M13', 'M14', 'M15'],
            'bedroom': ['M07', 'M08'],
            'bathroom': ['M09', 'M10'],
            'hallway': ['M11', 'M12'],
            'office': ['M16', 'M17'],
            'garage': ['M18', 'M19']
        }
        
        print("🔍 VESPER Room Discovery initialized")
    
    def discover_rooms_from_blender_scene(self) -> Dict[str, Dict]:
        """Discover rooms by analyzing Blender scene objects"""
        scene = bge.logic.getCurrentScene()
        discovered_rooms = {}
        
        print("🏠 Discovering rooms from Blender scene...")
        
        # Method 1: Look for room marker objects
        room_markers = self._find_room_markers(scene)
        if room_markers:
            print(f"   📍 Found {len(room_markers)} room markers")
            for room_name, marker_obj in room_markers.items():
                pos = marker_obj.worldPosition
                discovered_rooms[room_name] = {
                    'center': (pos.x, pos.y),
                    'marker_object': marker_obj.name,
                    'method': 'marker'
                }
        
        # Method 2: Analyze furniture placement to infer rooms
        furniture_rooms = self._infer_rooms_from_furniture(scene)
        if furniture_rooms:
            print(f"   🪑 Inferred {len(furniture_rooms)} rooms from furniture")
            for room_name, room_info in furniture_rooms.items():
                if room_name not in discovered_rooms:
                    discovered_rooms[room_name] = room_info
        
        # Method 3: Use predefined layout if no automatic discovery
        if not discovered_rooms:
            print("   📐 Using reference layout coordinates")
            discovered_rooms = self._get_reference_layout()
        
        # Calculate boundaries for each room
        for room_name, room_info in discovered_rooms.items():
            boundaries = self._calculate_room_boundaries(room_name, room_info['center'])
            room_info['boundaries'] = boundaries
            room_info['casas_sensors'] = self.casas_room_sensors.get(room_name, [f'M{hash(room_name) % 26 + 1:02d}'])
        
        self.discovered_rooms = discovered_rooms
        print(f"✅ Room discovery complete: {len(discovered_rooms)} rooms found")
        
        return discovered_rooms
    
    def _find_room_markers(self, scene) -> Dict[str, object]:
        """Look for objects named like 'RoomMarker_Kitchen' or 'Kitchen_Center'"""
        room_markers = {}
        
        room_keywords = ['living', 'kitchen', 'dining', 'bedroom', 'bathroom', 'hallway', 'office', 'garage']
        marker_keywords = ['marker', 'center', 'sensor', 'room']
        
        for obj in scene.objects:
            obj_name_lower = obj.name.lower()
            
            # Check if this looks like a room marker
            is_room_marker = any(marker in obj_name_lower for marker in marker_keywords)
            
            if is_room_marker:
                # Find which room this marker belongs to
                for room_keyword in room_keywords:
                    if room_keyword in obj_name_lower:
                        room_name = f"{room_keyword}_room" if room_keyword != 'kitchen' else 'kitchen'
                        room_markers[room_name] = obj
                        print(f"   📍 Found marker: {obj.name} → {room_name}")
                        break
        
        return room_markers
    
    def _infer_rooms_from_furniture(self, scene) -> Dict[str, Dict]:
        """Infer room locations based on furniture placement"""
        furniture_groups = {
            'kitchen': ['stove', 'sink', 'fridge', 'counter', 'cabinet'],
            'living_room': ['sofa', 'couch', 'tv', 'chair', 'table'],
            'dining_room': ['table', 'chair', 'dining'],
            'bedroom': ['bed', 'dresser', 'nightstand'],
            'bathroom': ['toilet', 'shower', 'bath', 'sink'],
            'office': ['desk', 'computer', 'bookshelf', 'office'],
            'garage': ['car', 'garage', 'tool']
        }
        
        room_furniture = {room: [] for room in furniture_groups.keys()}
        
        # Analyze all objects in scene
        for obj in scene.objects:
            obj_name_lower = obj.name.lower()
            
            # Skip non-furniture objects
            if any(skip in obj_name_lower for skip in ['actor', 'camera', 'light', 'plane', 'cube']):
                continue
            
            # Categorize furniture by room type
            for room_type, furniture_list in furniture_groups.items():
                if any(furniture in obj_name_lower for furniture in furniture_list):
                    room_furniture[room_type].append(obj)
                    print(f"   🪑 {obj.name} → {room_type}")
                    break
        
        # Calculate room centers based on furniture clusters
        inferred_rooms = {}
        for room_type, furniture_objects in room_furniture.items():
            if furniture_objects:  # Only if we found furniture for this room
                # Calculate center of furniture cluster
                total_x = sum(obj.worldPosition.x for obj in furniture_objects)
                total_y = sum(obj.worldPosition.y for obj in furniture_objects)
                center_x = total_x / len(furniture_objects)
                center_y = total_y / len(furniture_objects)
                
                inferred_rooms[room_type] = {
                    'center': (center_x, center_y),
                    'furniture_count': len(furniture_objects),
                    'method': 'furniture_inference'
                }
        
        return inferred_rooms
    
    def _get_reference_layout(self) -> Dict[str, Dict]:
        """Fallback: Use layout from reference image coordinates"""
        # Based on your house_layout_reference2.png
        reference_layout = {
            'living_room': {'center': (-1, -1), 'method': 'reference'},
            'kitchen': {'center': (5, 1), 'method': 'reference'},
            'dining_room': {'center': (1, 4), 'method': 'reference'},
            'bedroom': {'center': (-4, 4), 'method': 'reference'},
            'bathroom': {'center': (6, 6), 'method': 'reference'},
            'hallway': {'center': (0, 1), 'method': 'reference'},
            'office': {'center': (-6, 0), 'method': 'reference'},
            'garage': {'center': (8, -2), 'method': 'reference'}
        }
        
        return reference_layout
    
    def _calculate_room_boundaries(self, room_name: str, center: Tuple[float, float]) -> Dict[str, float]:
        """Calculate room boundaries based on center point and typical room sizes"""
        cx, cy = center
        
        # Room size estimates (can be refined based on actual layout)
        room_sizes = {
            'living_room': (3, 3),    # 6x6 area
            'kitchen': (3, 3),        # 6x6 area  
            'dining_room': (3, 2),    # 6x4 area
            'bedroom': (2, 2),        # 4x4 area
            'bathroom': (2, 2),       # 4x4 area
            'hallway': (2, 2),        # 4x4 area
            'office': (2, 2),         # 4x4 area
            'garage': (2, 2)          # 4x4 area
        }
        
        half_width, half_height = room_sizes.get(room_name, (2, 2))
        
        return {
            'x_min': cx - half_width,
            'x_max': cx + half_width,
            'y_min': cy - half_height,
            'y_max': cy + half_height
        }
    
    def save_discovered_layout(self) -> str:
        """Save discovered room layout to file"""
        vesper_root = r"C:\Users\hbui11\Desktop\vesper_llm"
        layout_file = os.path.join(vesper_root, "blender", "discovered_room_layout.json")
        
        layout_data = {
            'discovered_rooms': self.discovered_rooms,
            'casas_sensor_mapping': self.casas_room_sensors,
            'discovery_method': 'automatic',
            'timestamp': bge.logic.getRandomFloat()  # Simple timestamp substitute
        }
        
        try:
            with open(layout_file, 'w') as f:
                json.dump(layout_data, f, indent=2)
            
            print(f"💾 Room layout saved: {layout_file}")
            return layout_file
        except Exception as e:
            print(f"⚠️ Failed to save layout: {e}")
            return ""
    
    def get_motion_sensor_positions(self) -> Dict[str, Dict]:
        """Get optimal motion sensor positions for each room"""
        sensor_positions = {}
        
        for room_name, room_info in self.discovered_rooms.items():
            center_x, center_y = room_info['center']
            boundaries = room_info['boundaries']
            casas_sensors = room_info['casas_sensors']
            
            # For multiple sensors per room, distribute them
            sensor_coords = []
            if len(casas_sensors) == 1:
                sensor_coords = [(center_x, center_y)]
            elif len(casas_sensors) == 2:
                # Place sensors at opposite corners
                sensor_coords = [
                    (boundaries['x_min'] + 0.5, boundaries['y_min'] + 0.5),
                    (boundaries['x_max'] - 0.5, boundaries['y_max'] - 0.5)
                ]
            else:
                # Distribute evenly across room
                for i, sensor_id in enumerate(casas_sensors):
                    offset_x = (i % 2 - 0.5) * 1.0
                    offset_y = (i // 2 - 0.5) * 1.0
                    sensor_coords.append((center_x + offset_x, center_y + offset_y))
            
            sensor_positions[room_name] = {
                'sensors': dict(zip(casas_sensors, sensor_coords)),
                'room_center': (center_x, center_y),
                'boundaries': boundaries
            }
        
        return sensor_positions

# Integration function for the motion validation system
def discover_room_layout_from_blender() -> Dict[str, Dict]:
    """Main function to discover room layout from Blender scene"""
    discovery_system = VESPERRoomDiscovery()
    room_layout = discovery_system.discover_rooms_from_blender_scene()
    
    # Save for future reference
    layout_file = discovery_system.save_discovered_layout()
    
    return room_layout

def get_optimal_sensor_positions() -> Dict[str, Dict]:
    """Get optimal motion sensor positions based on discovered layout"""
    discovery_system = VESPERRoomDiscovery()
    room_layout = discovery_system.discover_rooms_from_blender_scene()
    sensor_positions = discovery_system.get_motion_sensor_positions()
    
    return sensor_positions
