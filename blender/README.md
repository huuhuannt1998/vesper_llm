# VESPER Navigation System – Complete Guide

This README consolidates setup instructions, multi-layout support, optimization notes, and backup/recovery steps for the VESPER UPBGE navigation system.

---

## 📦 File Structure

```
blender/
├── game/
│   ├── llm_bge_navigation.py              # Main BGE navigation script (optimized version)
│   ├── llm_bge_navigation_BACKUP_multi_call.py  # Backup multi-call system
│   ├── actor_controller.py                # Alternative HTTP-based controller
│   ├── bootstrap.py                       # BGE startup script
│   ├── setup_bge_logic.py                 # Automatic setup helper
│   ├── verify_multi_layout_setup.py       # Verification script
│   ├── gltf_layout_tester.py              # Multi-layout testing utility
└── addons/vesper_tools/
    ├── __init__.py
    └── llm_visual_nav.py                  # Visual navigation class
```

---

## 🎮 UPBGE LLM Navigation Setup

### Requirements
- UPBGE 0.44 (Blender 4.4.3 base)
- Actor object in scene
- BirdEyeCamera for screenshots
- VLM backend running (`http://100.98.151.66:1234/v1`)

### Quick Setup (for new `.blend` files)
1. Load scripts in Blender Text Editor:
   - `llm_bge_navigation.py`
   - `setup_bge_logic.py`
2. Run `setup_bge_logic.py` → It will:
   - Create/find **Actor**
   - Create/find **BirdEyeCamera**
   - Setup Logic Bricks
   - Connect navigation script
3. Press **P** to start navigation.

✅ Console should show:
```
🔧 Setting up BGE Logic for VESPER Navigation...
✅ Found Actor
✅ Found BirdEyeCamera
✅ Connected navigation script
```

---

## 🏠 Multi-Layout glTF Support

The system auto-detects imported **glTF 2.0 layouts** and ensures consistent naming:

- Actor → always `"Actor"`
- Camera → always `"BirdEyeCamera"`

### Workflow
1. Import new `.glb` or `.gltf` layout
2. Run `llm_bge_navigation.py`
3. Console shows:
```
🏠 Setting up navigation for new layout...
✅ Renamed Cube.001 → Actor
✅ Renamed Camera.001 → BirdEyeCamera
```
4. Press **P** → Actor spawns and navigates inside new layout.

### Utilities
- `verify_multi_layout_setup.py` – setup verification
- `gltf_layout_tester.py` – generates `layout_test_checklist.md` and `layout_test_report_template.json`

---

## ⚡ VLM Navigation Optimization

### Old Multi-Call System
- 5 VLM calls/step
- Reliable collision detection
- Slower, unstable at times

### Optimized Single-Call System
- **1–2 calls/step** (60–80% reduction)
- Faster, lighter on Blender
- Comprehensive **safety analysis** in JSON response:
```json
{
  "next_direction": "UP",
  "alternatives": ["LEFT", "RIGHT"],
  "safety_analysis": {
    "UP": "CLEAR",
    "DOWN": "BLOCKED",
    "LEFT": "CLEAR",
    "RIGHT": "BLOCKED"
  },
  "reasoning": "Path to kitchen is open"
}
```

✅ Faster decisions, ✅ fewer crashes, ✅ wall-collision prevention preserved.

---

## 🔄 Backup & Recovery Instructions

If optimized version causes issues, you can revert:

### Option 1 – File Replacement
```powershell
cd c:\Users\hbui11\Desktop\vesper_llm\blender
copy llm_bge_navigation.py llm_bge_navigation_OPTIMIZED_backup.py
copy llm_bge_navigation_BACKUP_multi_call.py llm_bge_navigation.py
```

### Option 2 – Rename Files
```powershell
ren llm_bge_navigation.py llm_bge_navigation_OPTIMIZED.py
ren llm_bge_navigation_BACKUP_multi_call.py llm_bge_navigation.py
```

Console will confirm:
```
echo "Reverted to multi-call collision detection system"
```

---

## 🔧 Debugging Tips

- **LLM client not available** → Check backend server  
- **No Actor/Camera** → Ensure objects named `"Actor"` and `"BirdEyeCamera"`  
- **Actor doesn’t move** → Verify physics enabled (Dynamic)  
- **No screenshots captured** → Confirm BirdEyeCamera is above scene  

---

## 📊 Performance Notes

- LLM Response Time: ~0.5s/decision  
- Frequency: 1 step/sec  
- Memory: minimal  
- Stability: greatly improved under optimized mode  

---

## ✅ Best Practices

- Always backup `.blend` before importing layouts  
- Run `setup_bge_logic.py` after new imports  
- Use glTF files with **named rooms** and **top-down cameras**  
- Start with **simple navigation tasks** before complex routines  

---

## 🚀 Testing Workflow

1. Import layout → Run setup  
2. Start navigation → Press **P**  
3. Monitor console:
   ```
   🧠 BGE: LLM Decision → RIGHT
   🎮 BGE: Actor moved from [-2.8, -2.5] to [-2.6, -2.5]
   ```
4. Validate:
   - Actor avoids walls
   - Stays within house
   - Proper screenshots generated  

---

## 📝 Summary

- Use **optimized system** for speed and stability  
- Fall back to **multi-call backup** if collision detection fails  
- System supports **any glTF 2.0 house layout**  
- Tools like `setup_bge_logic.py` and `gltf_layout_tester.py` simplify setup and testing  
