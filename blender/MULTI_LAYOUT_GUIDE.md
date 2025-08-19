# Multi-Layout glTF Support for VESPER Navigation

This document explains how to use the VESPER navigation system with different glTF 2.0 house layouts.

## Overview

The enhanced navigation system now automatically detects when new glTF layouts are imported and sets up the navigation components with **consistent naming** for easier testing across different house layouts:

- **Actor**: Always named "Actor" (automatically renamed from any suitable object)
- **Camera**: Always named "BirdEyeCamera" (automatically renamed from any camera)

This ensures that no matter what glTF layout you import, the navigation system will work consistently.

## Quick Start Guide

### 1. Verify Current Setup
```
# In Blender Text Editor, run:
blender/verify_multi_layout_setup.py
```

### 2. Import New glTF Layout
1. **File → Import → glTF 2.0 (.glb/.gltf)**
2. Select your house layout file
3. Import with default settings

### 3. Run Navigation System
1. Load `llm_bge_navigation.py` in Blender Text Editor
2. Run the script (it will auto-detect the new layout)
3. Look for console message: `"Setting up navigation for new layout..."`

### 4. Test Navigation
1. Press **P** to start BGE
2. The actor should spawn automatically inside the house
3. Navigation should work with the new layout

## Multi-Layout Features

### Automatic Detection
The system automatically detects when a new layout has been imported by analyzing:
- Object count changes
- Scene structure modifications
- New mesh objects in the scene

### Actor Management
- **find_or_create_actor()**: Ensures there's always an object named "Actor"
- Searches for objects with keywords: 'player', 'character', 'human', 'person', 'cube'
- **Automatically renames** suitable objects to "Actor" for consistency
- Positions actor at scene center if needed

### Camera Setup
- **find_navigation_camera()**: Ensures there's always a camera named "BirdEyeCamera"
- Searches for cameras with keywords: 'camera', 'cam', 'view', 'top', 'bird'
- **Automatically renames** cameras to "BirdEyeCamera" for consistency
- Sets up proper positioning for navigation screenshots

### Scene Analysis
- **analyze_scene_layout()**: Calculates scene bounds and structure
- Determines safe positioning areas for actor spawning
- Provides layout information for VLM navigation

### Automatic Setup
- **setup_navigation_for_new_layout()**: Comprehensive setup function
- Handles actor positioning, camera setup, and scene preparation
- Ensures navigation works consistently across different layouts

## Console Messages

Watch for these messages to verify proper setup:

```
🏠 Setting up navigation for new layout...
📊 Scene Analysis: Objects: 45, Cameras: 2
✅ Renamed 'Cube.001' to 'Actor' for consistent naming
✅ Renamed 'Camera.001' to 'BirdEyeCamera' for consistent naming
📐 Layout bounds: X: -10.5 to 12.3, Y: -8.7 to 15.2
🎯 Positioned actor at center: (0.9, 3.25)
✅ Navigation setup complete for new layout!
```

## Testing Workflow

### Use the Layout Tester
```
# Run this for comprehensive testing guidance:
python blender/gltf_layout_tester.py
```

This creates:
- `layout_test_checklist.md`: Step-by-step testing checklist
- `layout_test_report_template.json`: Template for documenting test results

### Manual Testing Steps

1. **Pre-Import**
   - Backup current .blend file
   - Note current setup

2. **Import glTF**
   - Import new house layout
   - Verify objects loaded correctly

3. **Navigation Setup**
   - Run navigation script
   - Check console messages
   - Verify auto-setup completion

4. **Testing**
   - Start BGE (Press P)
   - Test actor movement
   - Verify boundary respect
   - Test room identification

5. **Validation**
   - Actor stays within house
   - Screenshots capture properly
   - VLM navigation works
   - Timeout handling functions

## Supported glTF Layouts

The system works with any glTF 2.0 house layout that includes:
- ✅ Mesh objects for house structure
- ✅ At least one movable object (can be used as actor)
- ✅ Reasonable scale (typical house dimensions)
- ✅ Enclosed interior spaces

### Recommended Layout Features
- 🎯 Named rooms (helps VLM identification)
- 🎯 Top-down camera (for bird's eye screenshots)
- 🎯 Actor/character object (for movement)
- 🎯 Clear navigation paths between rooms

## Troubleshooting

### Actor Spawns in Wall
```
# Manually adjust after import:
actor.location = Vector((x, y, 0))  # Replace x, y with safe coordinates
```

### No Camera Found
- Add a camera positioned above the house
- The system will automatically rename it to 'BirdEyeCamera'

### Navigation Not Working
1. Check VLM server is running: `http://100.98.151.66:1234/v1`
2. Verify screenshots are being saved: `bge_XXX.png`
3. Check console for VLM timeout errors
4. Ensure objects are named 'Actor' and 'BirdEyeCamera'

### Room Identification Issues
- Ensure rooms have distinct visual features
- Check lighting in the scene
- Verify bird's eye camera angle

## Integration with Existing System

### Backward Compatibility
- Works with existing house layouts
- Preserves all current navigation features
- Maintains VLM optimization (1-2 calls per step)

### Error Handling
- Timeout handling: Uses "STAY" instead of "UP" on VLM failure
- Graceful fallback if auto-setup fails
- Detailed console logging for debugging

### Performance
- Minimal overhead for layout detection
- Efficient scene analysis
- Optimized VLM communication maintained

## File Structure

```
blender/
├── llm_bge_navigation.py              # Main navigation with multi-layout support
├── llm_bge_navigation_BACKUP_multi_call.py  # Backup of original system
├── gltf_layout_tester.py              # Testing utility and guidance
├── verify_multi_layout_setup.py      # Setup verification script
└── [your_house_layouts.glb]          # Your glTF house files
```

## Best Practices

### Before Importing New Layout
1. ✅ Backup your current .blend file
2. ✅ Note any custom actor positions
3. ✅ Verify VLM server is running

### After Importing New Layout
1. ✅ Run navigation script immediately
2. ✅ Check console for setup messages
3. ✅ Test navigation before complex tasks

### For Optimal Results
1. ✅ Use glTF files with named objects
2. ✅ Include top-down camera in layout
3. ✅ Ensure enclosed house boundaries
4. ✅ Test with simple navigation first

## Support

If you encounter issues:
1. Check console messages for detailed error info
2. Use `verify_multi_layout_setup.py` to diagnose problems
3. Use `gltf_layout_tester.py` for systematic testing
4. Review the backup system if needed: `llm_bge_navigation_BACKUP_multi_call.py`

The multi-layout system is designed to work seamlessly with any properly structured glTF 2.0 house layout while maintaining all the optimization and error handling improvements from the current navigation system.
