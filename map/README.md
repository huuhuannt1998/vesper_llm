# VESPER Dynamic Position Mapping System

This system provides enhanced spatial awareness for VESPER VLM navigation by generating dynamic maps that show the actor's current position on the house layout.

## 🎯 **Overview**

The position mapping system addresses a key limitation identified in the evaluation logs: **poor room detection and spatial awareness**. By providing the VLM with visual position context, navigation decisions become more accurate and efficient.

### **Problem Solved:**
- VLM showing all rooms as "UNKNOWN" 
- Poor spatial awareness leading to inefficient navigation
- Lack of visual feedback for debugging navigation issues
- Difficulty understanding movement progress and history

### **Solution Provided:**
- Real-time position overlay on house layout
- Movement history tracking with visual path
- Enhanced VLM prompts with position awareness
- Automatic map generation integrated with BGE navigation

## 🏗️ **System Architecture**

```
📁 map/
├── position_mapper.py          # Core mapping and visualization engine
├── bge_integration.py          # BGE navigation system integration  
├── enhanced_vlm_analysis.py    # Position-aware VLM analysis
└── generated_maps/             # Auto-generated position maps
    ├── navigation_context_*.png    # Clean maps for VLM analysis
    ├── actor_position_map_*.png    # Detailed maps with full history
    └── position_data_*.json        # Position tracking data
```

## 🔄 **Workflow**

1. **Position Capture**: BGE provides actor's world coordinates (x, y)
2. **Coordinate Mapping**: World coords converted to map pixel coordinates  
3. **Map Generation**: Actor position overlaid on house layout with history
4. **VLM Analysis**: Enhanced analysis using First-person view + Position map
5. **Navigation Decision**: Improved spatial awareness leads to better choices

## 🎨 **Generated Map Types**

### **Navigation Context Maps**
- Clean maps optimized for VLM analysis
- Current position marker (red dot)
- Recent movement history (orange dots)
- Minimal information overlay
- Perfect for real-time navigation decisions

### **Full Position Maps**  
- Detailed maps with complete movement history
- Full path visualization with connecting lines
- Comprehensive information overlay
- Ideal for debugging and analysis

### **Position Data Files**
- JSON files with coordinate history
- Room detection tracking
- Task completion progress
- Timestamp and session information

## 🚀 **Integration with BGE Navigation**

The system is **automatically integrated** with `llm_bge_navigation.py`:

```python
# Automatic position mapping (no code changes needed)
if POSITION_MAPPING_AVAILABLE and actor:
    navigation_result = enhanced_analyze_dual_image_navigation(
        fp_image_path, house_layout_path, current_task,
        current_position, step_number, 
        world_coords=(actor.worldPosition[0], actor.worldPosition[1])
    )
```

### **Enhanced VLM Analysis**
The VLM now receives:
- 📷 **Image 1**: First-person view (unchanged)
- 🗺️ **Image 2**: **NEW** - Position map showing actor location  
- 📋 **Image 3**: Original house layout reference

### **Improved Prompts**
```
🎯 POSITION MAP ANALYSIS (CRITICAL):
1. **LOCATE ACTOR ON MAP**: Find the RED MARKER showing your exact current position
2. **ANALYZE MOVEMENT HISTORY**: Orange markers show where you've been
3. **IDENTIFY CURRENT ROOM**: Based on position marker location on the map  
4. **PLAN EFFICIENT ROUTE**: Use the map to navigate toward target room
```

## ⚙️ **Configuration & Calibration**

### **Coordinate System Mapping**
The system needs calibration to map BGE world coordinates to house layout pixels:

```python
# In position_mapper.py - _world_to_map_coordinates()
world_bounds = {
    'min_x': -10.0,   # Adjust based on your house model
    'max_x': 10.0,    # Rightmost coordinate in BGE
    'min_y': -8.0,    # Bottommost coordinate in BGE  
    'max_y': 8.0,     # Topmost coordinate in BGE
}
```

### **Visual Customization**
```python
# Marker and path appearance
self.actor_marker_size = 12        # Size of position marker
self.path_line_width = 3           # Width of movement path lines
self.map_update_interval = 2       # Generate map every N steps

# Colors (RGB)
self.colors = {
    'actor_current': (255, 0, 0),  # Red - current position
    'actor_history': (255, 165, 0), # Orange - movement history
    'path_line': (0, 255, 0),       # Green - connecting path lines
}
```

## 🧪 **Testing & Validation**

### **Run System Test**
```bash
cd /path/to/vesper_llm
python test_position_mapping.py
```

**Expected Output:**
```
✅ Position mapper created successfully
✅ BGE integration created successfully  
✅ Position map generated: navigation_context_20250926_143052.png
✅ Position-aware prompt generated successfully
✅ Target room extraction working
```

### **Manual Testing**
```python
from map.bge_integration import update_actor_position_map

# Test position mapping
map_path = update_actor_position_map(
    world_x=-2.0, world_y=1.5,
    room="LIVING_ROOM", 
    task="Cook oatmeal",
    target_room="KITCHEN"
)
```

## 📊 **Expected Improvements**

Based on evaluation log analysis, this system should address:

### **Room Detection Issues** 
- **Before**: All rooms showing as "UNKNOWN"
- **After**: Accurate room identification using position context

### **Navigation Efficiency**
- **Before**: Endless turning, inefficient paths
- **After**: Direct navigation using position awareness

### **Spatial Understanding**
- **Before**: Poor understanding of house layout
- **After**: Clear visual reference of position and surroundings

### **Debugging Capabilities**
- **Before**: No visual feedback on navigation progress  
- **After**: Real-time position maps showing movement history

## 🔧 **Troubleshooting**

### **No Maps Generated**
- Check if `house_layout_reference2.png` exists in `blender/` directory
- Verify PIL (Pillow) is installed: `pip install Pillow`
- Check write permissions for `map/generated_maps/` directory

### **Incorrect Position Mapping**
- Calibrate coordinate bounds in `_world_to_map_coordinates()`
- Compare BGE world coordinates with expected map positions
- Adjust `world_bounds` values to match your house model scale

### **VLM Not Using Position Maps**
- Check that `POSITION_MAPPING_AVAILABLE = True` in navigation logs
- Verify position map files are being created in `generated_maps/`
- Ensure VLM server supports multiple image analysis

### **Performance Issues**
- Adjust `map_update_interval` to generate maps less frequently
- Reduce image resolution if maps are too large
- Clean old map files periodically

## 🎉 **Usage in BGE**

Once integrated, the system works automatically:

1. **Start BGE Navigation**: Load `llm_bge_navigation.py` and press P
2. **Automatic Mapping**: Position maps generated every few steps  
3. **Enhanced Analysis**: VLM receives position-aware context
4. **Better Navigation**: Improved room detection and path planning
5. **Visual Debugging**: Check generated maps to see movement progress

**No additional setup required** - the system integrates seamlessly with existing VESPER navigation!

## 📈 **Results Monitoring**

Monitor improvements in:
- Room detection accuracy (fewer "UNKNOWN" classifications)
- Navigation efficiency (fewer steps to complete tasks)
- Task completion rates (higher success percentage)  
- Movement patterns (less backtracking, more direct paths)

Check the generated maps in `map/generated_maps/` to visually verify navigation progress and debug any issues.