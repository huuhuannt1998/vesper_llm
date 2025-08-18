# VESPER BGE Navigation Setup Guide

## 🎮 UPBGE LLM Navigation System

This guide explains how to set up and use the LLM-powered navigation system in UPBGE (Unified Blender Game Engine).

### 📁 **File Structure:**
```
blender/
├── game/
│   ├── llm_bge_navigation.py       # Main BGE navigation script (NEW)
│   ├── actor_controller.py         # Alternative HTTP-based controller
│   └── bootstrap.py                # BGE startup script
└── addons/vesper_tools/
    ├── __init__.py                 # Main VESPER Tools add-on
    └── llm_visual_nav.py           # LLM visual navigation class
```

### 🚀 **Setup Instructions:**

#### **1. UPBGE Setup:**
- ✅ You already have UPBGE 0.44 running (based on Blender 4.4.3)
- ✅ Scene with Actor object is loaded
- ✅ Logic Editor is accessible

#### **2. Add LLM Navigation Script:**
1. **Copy the script content** from `llm_bge_navigation.py`
2. **In UPBGE Scripting tab:**
   - Create new text file: `llm_bge_navigation.py`
   - Paste the enhanced script content
   - Save the file

#### **3. Set Up Logic Bricks:**
1. **Select the Actor object**
2. **Open Logic Editor** (bottom panel)
3. **Add Logic Bricks:**
   - **Sensor:** Always (Pulse mode, Frequency: 1)
   - **Controller:** Python (Module: `llm_bge_navigation.main`)
   - **Connect:** Always sensor → Python controller

#### **4. Configure Navigation:**
In the script, you can modify:
```python
"current_task": "Navigate to kitchen",    # Change task
"max_steps": 30,                         # Max navigation steps
step_size=0.2                           # Movement distance per step
```

### 🧠 **LLM Integration Features:**

#### **Real LLM Navigation:**
- ✅ **Direct connection** to VESPER LLM client
- ✅ **Task-based navigation** (no hardcoded coordinates)
- ✅ **Scene facts analysis** (avoids HTTP 400 errors)
- ✅ **Visual screenshot capture** for enhanced analysis
- ✅ **Fallback navigation** when LLM unavailable

#### **Navigation Tasks:**
The system can handle tasks like:
- `"Navigate to kitchen"`
- `"Find bathroom"`
- `"Go to living room"`
- `"Explore dining area"`

### 🎯 **BGE Navigation Flow:**

```
1. BGE Startup → Initialize LLM client
2. Always Sensor → Trigger navigation step
3. Screenshot Capture → Bird's-eye view analysis  
4. LLM Analysis → Get movement direction
5. Actor Movement → Execute LLM decision
6. Repeat → Until task complete or max steps
```

### 🔧 **Debugging:**

#### **Check Console Output:**
Look for these messages in UPBGE console:
```
✅ BGE: LLM client connected successfully
🧠 BGE: LLM Navigation initialized!
🎯 BGE: Task: Navigate to kitchen
📸 GE: Bird's eye screenshot captured
🧠 BGE: LLM Decision → RIGHT
🎮 BGE: Moved RIGHT from [-2.8, -2.5] to [-2.6, -2.5]
```

#### **Common Issues:**
- **"LLM client not available"** → Check VESPER backend is running
- **"No Actor object found"** → Ensure object is named "Actor"
- **"No camera found"** → Ensure scene has a camera object
- **HTTP 400 errors** → Script uses scene facts instead of screenshots

### 🎮 **Testing Commands:**

#### **Start Navigation:**
Press **P** to start Game Engine with the navigation script running

#### **Stop Navigation:**
Press **Esc** to stop Game Engine

#### **Monitor Progress:**
Watch the console for LLM decisions and movement updates

### 🌟 **Advanced Features:**

#### **Dynamic Task Override:**
You can change tasks during runtime:
```python
logic.llm_nav_state["current_task"] = "Find bathroom"
logic.llm_nav_state["task_complete"] = False
```

#### **LLM Response Analysis:**
The system captures LLM reasoning:
```python
💭 BGE: LLM Reasoning → Moving right toward kitchen area based on...
```

#### **Movement History:**
Each step is logged for spatial learning and debugging

### 📊 **Performance Notes:**

- **LLM Response Time:** ~0.5 seconds per decision
- **Movement Frequency:** 1 step per second
- **Screenshot Capture:** Optional (disabled by default to avoid 400 errors)
- **Memory Usage:** Minimal (stateless except for navigation state)

### 🔄 **Integration with VESPER Tools:**

The BGE navigation script works alongside:
- **VESPER Tools Add-on** for manual navigation testing
- **Backend LLM Client** for consistent AI responses  
- **Visual Navigation Scripts** for scene analysis
- **Actor Controller** for HTTP-based remote control

This creates a complete LLM-powered navigation ecosystem within UPBGE!
