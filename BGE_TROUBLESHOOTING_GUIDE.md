# BGE Navigation Troubleshooting Guide

## 🚨 Issue: Empty Log File (All Zeros)

Your log shows:
```json
{
  "session_id": "20250828_134413",
  "start_time": 1756403053.4642522,
  "tasks_completed": 0,
  "tasks_failed": 0,
  "total_steps": 0,
  "total_screenshots": 0,
  "total_llm_calls": 0,
  "task_details": []
}
```

This means BGE started but the navigation script failed to initialize.

## 🔍 Diagnosis Steps

### Step 1: Test with Minimal Script
1. **Open Blender** with `house.blend`
2. **Go to Logic Editor**
3. **Select Actor object**
4. **Change Python script** from `llm_bge_navigation.py` to `minimal_bge_test.py`
5. **Press P** to run BGE
6. **Check Blender console** for output

**Expected output if working:**
```
🚀 MINIMAL BGE TEST STARTED
✅ Scene name: Scene
✅ Actor found at position: <Vector ...>
✅ Test log created: bge_test_log.txt
🎯 MINIMAL TEST COMPLETED
```

### Step 2: Test with Debug Script
1. **Change Python script** to `bge_navigation_debug.py`
2. **Press P** to run BGE
3. **Check console** for detailed diagnostics

**Expected output:**
```
🚀 BGE NAVIGATION DIAGNOSTIC VERSION
🔧 Added to Python path: C:\Users\hbui11\Desktop\vesper_llm
✅ Actor found at: <Vector ...>
✅ backend.app.llm.client
✅ VESPERMetricsLogger initialized successfully!
🎯 DIAGNOSTIC COMPLETED
```

## 🛠️ Common Issues & Solutions

### Issue 1: No Console Output
**Problem**: Script not connected to logic bricks
**Solution**: 
- Select Actor object in Blender
- Go to Logic Editor
- Add Python controller if missing
- Connect sensor → controller → actuator

### Issue 2: Import Errors
**Problem**: `❌ backend.app.llm.client: No module named 'backend'`
**Solution**: Python path issue - debug script will fix this

### Issue 3: Actor Not Found
**Problem**: `❌ Actor object NOT FOUND!`
**Solution**: 
- Rename your character object to "Actor"
- Or modify script to use correct object name

### Issue 4: Script Syntax Error
**Problem**: Python compilation failure
**Solution**: Check original script syntax with validation

## 📋 Testing Sequence

1. **Minimal Test**: `minimal_bge_test.py`
   - Tests basic BGE functionality
   - Checks if Actor exists
   - Verifies file system access

2. **Debug Test**: `bge_navigation_debug.py`
   - Tests imports with path fixing
   - Comprehensive diagnostics
   - Creates detailed debug log

3. **Full Navigation**: `llm_bge_navigation.py`
   - Original navigation script
   - Run only after debug tests pass

## 🎯 Next Actions

Based on your test results:

### If Minimal Test Fails:
- Fix BGE setup (Actor object, logic bricks)
- Check Blender scene configuration

### If Minimal Test Works, Debug Test Fails:
- Import/path issues
- Check Python environment
- Verify backend server running

### If Both Tests Work:
- Original navigation script has issues
- Apply fixes from debug results
- Check for syntax errors

## 📊 Success Indicators

Working system should show:
- Console output during BGE run
- Log files being created in `evaluation_logs/`
- Non-zero counters in navigation log
- VLM analysis messages

## 🔧 Files Created for Testing:
- `blender/minimal_bge_test.py` - Basic functionality test
- `blender/bge_navigation_debug.py` - Comprehensive diagnostics

**Run these tests in order to isolate the exact failure point!**
