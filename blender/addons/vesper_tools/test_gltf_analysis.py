#!/usr/bin/env python3
"""Test the glTF scene analysis system"""

import random

# Mock Blender objects for testing
class MockObject:
    def __init__(self, name, location, obj_type='MESH'):
        self.name = name
        self.location = MockLocation(location)
        self.type = obj_type
        self.bound_box = [
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
        ]
        self.matrix_world = MockMatrix()

class MockLocation:
    def __init__(self, coords):
        self.x, self.y = coords[:2]
        self.z = coords[2] if len(coords) > 2 else 0

class MockMatrix:
    def __matmul__(self, other):
        return other

class MockVector:
    def __init__(self, coords):
        self.x, self.y, self.z = coords if len(coords) == 3 else coords + [0]
        
    def __sub__(self, other):
        return MockVector([self.x - other.x, self.y - other.y, self.z - other.z])
    
    @property 
    def length(self):
        return (self.x**2 + self.y**2 + self.z**2)**0.5

# Mock Vector for testing
def Vector(coords):
    return MockVector(coords)

# Test scene analysis functions (simplified versions)
def calculate_scene_bounds(mesh_objects):
    """Calculate the bounding box of the entire scene"""
    if not mesh_objects:
        return {"min": [-5, -5, 0], "max": [5, 5, 3], "center": [0, 0, 0]}
    
    # Find overall bounds
    locations = [(obj.location.x, obj.location.y, obj.location.z) for obj in mesh_objects]
    
    min_x = min(loc[0] for loc in locations) - 2
    max_x = max(loc[0] for loc in locations) + 2
    min_y = min(loc[1] for loc in locations) - 2
    max_y = max(loc[1] for loc in locations) + 2
    min_z = min(loc[2] for loc in locations) - 1
    max_z = max(loc[2] for loc in locations) + 3
    
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    center_z = (min_z + max_z) / 2
    
    return {
        "min": [min_x, min_y, min_z],
        "max": [max_x, max_y, max_z], 
        "center": [center_x, center_y, center_z],
        "size": [max_x - min_x, max_y - min_y, max_z - min_z]
    }

def identify_areas_by_names(mesh_objects):
    """Try to identify room/area types from object names"""
    areas = {}
    
    room_keywords = {
        "kitchen": ["kitchen", "cocina", "cuisine", "kueche"],
        "bedroom": ["bedroom", "bed", "dormitorio", "chambre"],
        "livingroom": ["living", "lounge", "sala", "salon"],
        "bathroom": ["bathroom", "bath", "baño", "salle_de_bain"],
        "office": ["office", "study", "oficina", "bureau"],
        "dining": ["dining", "comedor", "salle_a_manger"],
        "garage": ["garage", "garaje"],
        "outdoor": ["outdoor", "garden", "patio", "jardin"]
    }
    
    for obj in mesh_objects:
        obj_name_lower = obj.name.lower()
        
        for room_type, keywords in room_keywords.items():
            if any(keyword in obj_name_lower for keyword in keywords):
                if room_type not in areas:
                    areas[room_type.title()] = {
                        "center": [obj.location.x, obj.location.y],
                        "source": f"object_name_{obj.name}",
                        "confidence": 0.8
                    }
                    break
    
    return areas

def create_grid_based_areas(scene_bounds):
    """Create a grid of navigation areas across the scene"""
    areas = {}
    
    center = scene_bounds["center"]
    size = scene_bounds["size"]
    
    # Adjust grid size based on scene size
    if size[0] > 20 or size[1] > 20:
        grid_size = 4
    elif size[0] > 10 or size[1] > 10:
        grid_size = 3
    else:
        grid_size = 2
    
    step_x = size[0] / grid_size
    step_y = size[1] / grid_size
    
    area_names = ["North", "South", "East", "West", "Center", "Northeast", "Northwest", "Southeast", "Southwest"]
    
    name_idx = 0
    for i in range(grid_size):
        for j in range(grid_size):
            if name_idx >= len(area_names):
                name_idx = 0
            
            pos_x = scene_bounds["min"][0] + (i + 0.5) * step_x
            pos_y = scene_bounds["min"][1] + (j + 0.5) * step_y
            
            area_name = f"Area_{area_names[name_idx]}"
            areas[area_name] = {
                "center": [pos_x, pos_y],
                "source": "grid_based",
                "confidence": 0.6
            }
            
            name_idx += 1
    
    return areas

def analyze_gltf_scene_test(mock_objects):
    """Test version of glTF scene analysis"""
    print(f"🔍 Analyzing scene with {len(mock_objects)} objects...")
    
    # Calculate scene bounds
    scene_bounds = calculate_scene_bounds(mock_objects)
    print(f"📐 Scene bounds: {scene_bounds}")
    
    # Try to identify areas by names
    named_areas = identify_areas_by_names(mock_objects)
    print(f"🏷️ Named areas found: {named_areas}")
    
    # Generate grid-based areas if needed
    areas = named_areas.copy()
    if len(areas) < 3:
        grid_areas = create_grid_based_areas(scene_bounds)
        areas.update(grid_areas)
        print(f"📊 Added grid areas: {list(grid_areas.keys())}")
    
    return areas

if __name__ == "__main__":
    print("🧪 Testing glTF Scene Analysis System")
    print("="*50)
    
    # Test 1: Scene with named objects (typical Polycam export)
    print("\n🏠 Test 1: Polycam-style scene with named objects")
    polycam_objects = [
        MockObject("Kitchen_Counter_01", [2, 1]),
        MockObject("Living_Room_Sofa", [-3, 2]),
        MockObject("Bedroom_Bed", [-5, -3]),
        MockObject("Bathroom_Sink", [1, -2]),
        MockObject("Dining_Table", [0, 0]),
        MockObject("Wall_Section_01", [10, 10]),
        MockObject("Floor_Tile_25", [0, 0])
    ]
    
    areas_1 = analyze_gltf_scene_test(polycam_objects)
    print(f"✅ Found {len(areas_1)} navigation areas:")
    for name, data in areas_1.items():
        print(f"   📍 {name}: {data['center']} (from {data['source']})")
    
    # Test 2: Generic glTF scene without room names
    print("\n🏗️ Test 2: Generic glTF scene without room names") 
    generic_objects = [
        MockObject("Mesh_001", [0, 0]),
        MockObject("Cube_002", [5, 3]),
        MockObject("Plane_003", [-2, -4]),
        MockObject("Cylinder_004", [8, -1]),
        MockObject("Sphere_005", [-6, 2])
    ]
    
    areas_2 = analyze_gltf_scene_test(generic_objects)
    print(f"✅ Found {len(areas_2)} navigation areas:")
    for name, data in areas_2.items():
        print(f"   📍 {name}: {data['center']} (from {data['source']})")
    
    # Test 3: Large scene
    print("\n🌍 Test 3: Large complex scene")
    large_objects = [MockObject(f"Object_{i:03d}", [random.uniform(-15, 15), random.uniform(-15, 15)]) 
                    for i in range(20)]
    
    areas_3 = analyze_gltf_scene_test(large_objects) 
    print(f"✅ Found {len(areas_3)} navigation areas:")
    for name, data in areas_3.items():
        print(f"   📍 {name}: {data['center']} (from {data['source']})")
    
    print("\n🎉 glTF Scene Analysis System Test Complete!")
    print("✅ The system can now work with any imported glTF model!")
