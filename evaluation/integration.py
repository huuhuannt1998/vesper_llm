"""
VESPER Evaluation Integration for Blender Addon
==============================================

Add this code to your VESPER addon to enable real-time evaluation.
"""

# Add to your blender/addons/vesper_tools/__init__.py

# =============================================================================
# EVALUATION INTEGRATION (Add this section to your addon)
# =============================================================================

EVALUATION_INTEGRATION_CODE = '''
# Add at the top of your __init__.py, after other imports
import sys
import os
from datetime import datetime

# Evaluation system integration
EVALUATION_ENABLED = False
try:
    # Add evaluation path
    eval_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "evaluation")
    if eval_path not in sys.path:
        sys.path.append(eval_path)
    
    # Import evaluation functions (these won't fail in Blender)
    EVALUATION_ENABLED = True
    
    # Evaluation data storage
    evaluation_session = {
        "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "tests": [],
        "current_test": None
    }
    
    def eval_start_test(task_description: str, target_room: str):
        """Start evaluation test"""
        global evaluation_session
        if not EVALUATION_ENABLED:
            return
        
        actor = bpy.context.scene.objects.get("Player")
        if not actor:
            return
        
        test_data = {
            "test_id": f"TEST_{len(evaluation_session['tests']) + 1:03d}",
            "task": task_description,
            "target_room": target_room,
            "start_time": bpy.context.scene.frame_current,
            "start_position": list(actor.location),
            "path_points": [list(actor.location)],
            "llm_calls": 0,
            "screenshots": 0,
            "success": False
        }
        
        evaluation_session["current_test"] = test_data
        print(f"📊 EVAL: Started test {test_data['test_id']} - {task_description}")
    
    def eval_record_step():
        """Record movement step"""
        global evaluation_session
        if not EVALUATION_ENABLED or not evaluation_session["current_test"]:
            return
        
        actor = bpy.context.scene.objects.get("Player")
        if actor:
            evaluation_session["current_test"]["path_points"].append(list(actor.location))
    
    def eval_record_llm_call():
        """Record LLM API call"""
        global evaluation_session
        if not EVALUATION_ENABLED or not evaluation_session["current_test"]:
            return
        
        evaluation_session["current_test"]["llm_calls"] += 1
    
    def eval_record_screenshot():
        """Record screenshot capture"""
        global evaluation_session
        if not EVALUATION_ENABLED or not evaluation_session["current_test"]:
            return
        
        evaluation_session["current_test"]["screenshots"] += 1
    
    def eval_end_test(success: bool, final_room: str = None):
        """End evaluation test"""
        global evaluation_session
        if not EVALUATION_ENABLED or not evaluation_session["current_test"]:
            return
        
        test = evaluation_session["current_test"]
        test["success"] = success
        test["final_room"] = final_room
        test["end_time"] = bpy.context.scene.frame_current
        test["duration"] = test["end_time"] - test["start_time"]
        
        # Calculate metrics
        test["total_steps"] = len(test["path_points"]) - 1
        test["steps_per_llm_call"] = test["total_steps"] / max(1, test["llm_calls"])
        
        # Add to session
        evaluation_session["tests"].append(test)
        evaluation_session["current_test"] = None
        
        print(f"📊 EVAL: Completed {test['test_id']} - Success: {success}")
        print(f"   Steps: {test['total_steps']}, LLM calls: {test['llm_calls']}")
    
    def eval_export_session():
        """Export evaluation session data"""
        global evaluation_session
        if not EVALUATION_ENABLED:
            return None
        
        filename = f"vesper_evaluation_{evaluation_session['session_id']}.json"
        filepath = os.path.join(bpy.path.abspath("//"), filename)
        
        # Calculate session summary
        tests = evaluation_session["tests"]
        if tests:
            success_rate = sum(1 for t in tests if t["success"]) / len(tests)
            avg_steps = sum(t["total_steps"] for t in tests) / len(tests)
            avg_llm_calls = sum(t["llm_calls"] for t in tests) / len(tests)
            
            summary = {
                "session_summary": {
                    "total_tests": len(tests),
                    "success_rate": success_rate,
                    "average_steps": avg_steps,
                    "average_llm_calls": avg_llm_calls
                },
                "detailed_tests": tests
            }
            
            with open(filepath, 'w') as f:
                json.dump(summary, f, indent=2)
            
            print(f"📁 Evaluation data exported: {filename}")
            print(f"📊 Session Summary - Success: {success_rate:.1%}, Avg Steps: {avg_steps:.1f}")
            
            return filepath
        
        return None

except Exception as e:
    print(f"⚠️ Evaluation system not available: {e}")
    EVALUATION_ENABLED = False
    
    # Define dummy functions
    def eval_start_test(*args): pass
    def eval_record_step(): pass  
    def eval_record_llm_call(): pass
    def eval_record_screenshot(): pass
    def eval_end_test(*args): pass
    def eval_export_session(): return None
'''

# =============================================================================
# INTEGRATION INSTRUCTIONS
# =============================================================================

INTEGRATION_INSTRUCTIONS = """
To integrate evaluation with your VESPER addon:

1. Add the EVALUATION_INTEGRATION_CODE to your vesper_tools/__init__.py

2. Modify your existing functions:

   In navigate_with_llm():
   ```python
   def navigate_with_llm(self, task):
       eval_start_test(task, "Auto-detected")  # Start evaluation
       
       # Your existing code...
       
       eval_end_test(success, detected_room)   # End evaluation
   ```

   In move_actor_step_by_step():
   ```python
   def move_actor_step_by_step(self, target_x, target_y, step_size=0.12, max_steps=25):
       eval_record_step()  # Record each step
       
       # Your existing movement code...
   ```

   In get_llm_room_order():
   ```python
   def get_llm_room_order(self, task):
       eval_record_llm_call()  # Record LLM call
       
       # Your existing LLM code...
   ```

   In capture_birds_eye_view():
   ```python
   def capture_birds_eye_view(self):
       eval_record_screenshot()  # Record screenshot
       
       # Your existing screenshot code...
   ```

3. Add evaluation export to your P key handler:
   ```python
   elif event.type == 'E' and event.value == 'PRESS':
       eval_export_session()  # Export evaluation data
       return {'FINISHED'}
   ```

4. The evaluation system will automatically track:
   - Navigation success rates
   - Step counts and efficiency
   - LLM response patterns
   - Screenshot usage
   - Time-to-completion metrics

5. Export data using the 'E' key for analysis
"""

def get_integration_code():
    """Get the integration code for copying into VESPER addon"""
    return EVALUATION_INTEGRATION_CODE

def get_integration_instructions():
    """Get detailed integration instructions"""
    return INTEGRATION_INSTRUCTIONS

if __name__ == "__main__":
    print("🔧 VESPER Evaluation Integration Helper")
    print("=" * 50)
    print(INTEGRATION_INSTRUCTIONS)
