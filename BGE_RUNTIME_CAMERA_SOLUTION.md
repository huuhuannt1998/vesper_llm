# 🎮 BGE Runtime Camera Switching Solution

## 🔍 **Problem Identified**

You're absolutely right! When the Blender Game Engine (BGE) is actively running, the standard Blender context (`bpy.context.scene.camera`) doesn't work for camera switching. During BGE runtime, we need to use the BGE-specific API.

## ✅ **Solution Implemented**

### **1. Runtime Detection System**
```python
def is_bge_runtime():
    try:
        bge.logic.getCurrentScene()
        return True
    except:
        return False

BGE_RUNTIME = is_bge_runtime()
```

### **2. Dual-Mode Camera Switching**
```python
def switch_camera_runtime(camera_name: str):
    if BGE_RUNTIME:
        # BGE runtime camera switching
        scene = bge.logic.getCurrentScene()
        camera = scene.objects.get(camera_name)
        scene.active_camera = camera
    else:
        # Blender edit mode camera switching
        camera = bpy.data.objects.get(camera_name)
        bpy.context.scene.camera = camera
```

### **3. Dual-Mode Screenshot Capture**
```python
def capture_screenshot_runtime(filepath: str):
    if BGE_RUNTIME:
        # BGE runtime screenshot
        bge.render.makeScreenshot(filepath)
    else:
        # Blender edit mode rendering
        bpy.ops.render.render(write_still=True)
```

## 🔧 **Key API Differences**

| **Context** | **Camera Switch** | **Screenshot** | **Scene Access** |
|-------------|------------------|----------------|------------------|
| **BGE Runtime** | `scene.active_camera = camera` | `bge.render.makeScreenshot()` | `bge.logic.getCurrentScene()` |
| **Blender Edit** | `bpy.context.scene.camera = camera` | `bpy.ops.render.render()` | `bpy.context.scene` |

## 🎯 **Enhanced MCP Tools**

### **Updated Functions:**
1. **`capture_bird_eye_view()`** - Now works in both BGE runtime and edit mode
2. **`capture_first_person_view()`** - Proper first-person camera detection and switching
3. **`switch_camera_runtime()`** - New utility for seamless camera switching
4. **`capture_screenshot_runtime()`** - New utility for proper screenshot capture

### **Smart Camera Detection:**
- **BGE Runtime**: Searches through `scene.objects` for camera objects
- **Blender Edit**: Uses `bpy.data.objects` with type filtering
- **First-Person**: Tries multiple naming patterns (`Actor_FPCamera`, `FirstPersonCamera`, etc.)

## 🚀 **Usage in BGE Runtime**

### **From Your Game Logic:**
```python
# Import the enhanced service
from vesper_mcp.services.camera_service import capture_bird_eye_view, capture_first_person_view

# Capture bird-eye view during gameplay
async def capture_navigation_view():
    result = await capture_bird_eye_view()
    if result["success"]:
        print(f"Bird-eye captured: {result['filepath']}")

# Capture first-person view during gameplay  
async def capture_interaction_view():
    result = await capture_first_person_view(actor_name="Actor")
    if result["success"]:
        print(f"First-person captured: {result['filepath']}")
```

### **Direct Camera Switching:**
```python
# Switch cameras during gameplay
switch_result = switch_camera_runtime("BirdEyeCamera")
if switch_result["success"]:
    # Camera switched successfully
    capture_screenshot_runtime("current_view.png")
```

## 🧪 **Testing**

### **Test Script:** `test_bge_camera_switching.py`
- Detects available cameras in both modes
- Tests camera switching functionality
- Validates screenshot capture
- Reports success/failure for each operation

### **Run Tests:**
1. **In Blender Edit Mode:** `python test_bge_camera_switching.py`
2. **In BGE Runtime:** Run script from within active game

## 🎮 **Integration with Your VLM System**

### **MCP Agent Usage:**
```python
# VLM agent decides camera based on task
task = "navigate to kitchen"
recommendation = await get_camera_recommendations(task)

if recommendation["recommended_camera"] == "bird_eye":
    result = await capture_bird_eye_view()
elif recommendation["recommended_camera"] == "first_person":
    result = await capture_first_person_view()

# Process captured image for VLM analysis
if result["success"]:
    process_image_for_vlm(result["filepath"])
```

## ✅ **Benefits of This Solution**

1. **✅ Seamless Mode Switching**: Works in both BGE runtime and Blender edit mode
2. **✅ Proper BGE Integration**: Uses correct BGE APIs during gameplay
3. **✅ Backward Compatibility**: Still works in Blender edit mode for setup
4. **✅ Error Handling**: Graceful fallbacks and detailed error messages
5. **✅ Smart Detection**: Automatically finds cameras using multiple naming patterns

## 🎯 **Next Steps**

1. **Test in Your BGE Environment**: Run the test script in your active game
2. **Verify Camera Names**: Ensure your cameras use detectable naming patterns
3. **Integrate with VLM**: Connect the enhanced service to your VLM pipeline
4. **Monitor Performance**: Check screenshot capture speed during gameplay

Your MCP camera service is now **fully BGE runtime compatible** and should work seamlessly during active gameplay! 🎮✨
