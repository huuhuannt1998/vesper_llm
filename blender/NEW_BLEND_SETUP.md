# BGE Navigation Setup for New Blend Files

When you open a new blend file, the VESPER navigation system needs to be set up before it will work. Here's how:

## Quick Setup Steps

### **Step 1: Load the Scripts**
1. Open **Text Editor** in Blender
2. **Open** → Navigate to `c:\Users\hbui11\Desktop\vesper_llm\blender\`
3. Load **`llm_bge_navigation.py`** (main navigation script)
4. Load **`setup_bge_logic.py`** (setup helper)

### **Step 2: Run the Setup Script**
1. In Text Editor, select **`setup_bge_logic.py`**
2. Click **Run Script** (or Alt+P)
3. Check console for setup messages

### **Step 3: Start Navigation**
1. Press **P** to start BGE
2. Navigation should begin automatically
3. Check console for navigation messages

## What the Setup Script Does

✅ **Creates/finds Actor object** (renames to "Actor")
✅ **Creates/finds camera** (renames to "BirdEyeCamera")  
✅ **Sets up BGE Logic Bricks** (Always sensor → Python controller)
✅ **Connects navigation script** to the logic system
✅ **Configures physics** for actor movement

## Manual Setup (Alternative)

If the automatic setup doesn't work, you can set it up manually:

### **1. Prepare Objects:**
- Have a movable object named **"Actor"**
- Have a camera named **"BirdEyeCamera"** positioned above the scene

### **2. Logic Editor Setup:**
1. Select the Actor object
2. Switch to **Logic Editor**
3. Add **Always** sensor (set to pulse)
4. Add **Python** controller 
5. Set controller script to **`llm_bge_navigation.py`**
6. Connect sensor to controller

### **3. Test:**
1. Press **P** to start BGE
2. Navigation should begin

## Troubleshooting

### **"Nothing happens when I press P"**
- Check that Logic Bricks are connected (Always sensor → Python controller)
- Make sure `llm_bge_navigation.py` is loaded in Text Editor
- Verify the Python controller is set to use the navigation script

### **"Script errors in console"**
- Check that Actor object exists and is named "Actor"
- Check that BirdEyeCamera exists and is named "BirdEyeCamera"
- Verify VLM server is running at `http://100.98.151.66:1234/v1`

### **"Actor doesn't move"**
- Check console for VLM connection messages
- Verify Actor has physics enabled (Dynamic physics type)
- Check that screenshots are being captured in `captures/` folder

### **"No screenshots captured"**
- Position BirdEyeCamera above the scene looking down
- Check camera is named exactly "BirdEyeCamera"
- Verify `captures/` directory can be created

## For Different glTF Layouts

When importing a new glTF house layout:

1. **Import the glTF** (File → Import → glTF 2.0)
2. **Run setup script** again (it will auto-rename objects)
3. **Press P** to start navigation
4. System will auto-detect new layout and position actor

## Files You Need

Make sure these files are in your blender folder:
- ✅ `llm_bge_navigation.py` - Main navigation system
- ✅ `setup_bge_logic.py` - Automatic setup helper  
- ✅ `verify_consistent_naming.py` - Verification tool
- ✅ `MULTI_LAYOUT_GUIDE.md` - Complete documentation

## Quick Verification

After setup, you should see in console:
```
🔧 Setting up BGE Logic for VESPER Navigation...
✅ Found existing Actor: Actor
✅ Found existing BirdEyeCamera: BirdEyeCamera  
✅ Connected navigation script: llm_bge_navigation.py
✅ BGE Logic setup complete!
```

Then when you press P:
```
🧠 BGE: VESPER Navigation initialized!
📋 BGE: Tasks: ['Go to bedroom', 'Go to kitchen', 'Go to living room']
📍 BGE: LLM Available: True
```

The system is designed to work consistently across different blend files and glTF layouts with this setup process!
