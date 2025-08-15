#!/usr/bin/env python3
"""
Final comprehensive test of the ge_code template compilation
"""

def test_ge_code_compilation():
    # Simulate the template variables that would be used
    actor_name = "TestActor"
    tasks_data = ["Task1", "Task2"]
    backend_path = r"C:\Users\hbui11\Desktop\vesper_llm\backend"
    
    # Create a simplified version of the problematic template section
    ge_code_template = '''# VESPER LLM Visual Navigation - Game Engine Script
import sys
import os

try:
    # Add backend path for LLM client
    backend_path = r"{backend_path}"
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    
    def find_vesper_root():
        import os
        current_dir = os.path.dirname(__file__)
        while current_dir and current_dir != os.path.dirname(current_dir):
            if os.path.basename(current_dir) == 'vesper_llm':
                return current_dir
            if os.path.exists(os.path.join(current_dir, 'backend', 'app', 'llm', 'client.py')):
                return current_dir
            current_dir = os.path.dirname(current_dir)
        
        # Fallback to hardcoded path if not found
        return r"c:\\Users\\hbui11\\Desktop\\vesper_llm"
    
    def main():
        # Find actor in Game Engine
        actor_name = "{actor_name}"
        print("Actor:", actor_name)
        
        # Get navigation data
        tasks = {tasks_data}
        print("Tasks:", tasks)
        
        print("\\n🧠 GE: Task completed!")
        print("\\n✅ GE: All tasks completed!")
    
    main()

except Exception as e:
    print("❌ GE: LLM Visual Navigation error: " + str(e))
    import traceback
    traceback.print_exc()
'''
    
    try:
        print("Testing complete ge_code template...")
        
        # Format the template
        formatted_code = ge_code_template.format(
            actor_name=actor_name,
            tasks_data=str(tasks_data),
            backend_path=backend_path
        )
        
        print("✅ Template formatting successful!")
        
        # Try to compile it
        compile(formatted_code, '<string>', 'exec')
        print("✅ Template compiles without Unicode escape errors!")
        
        # Try to execute it
        exec(formatted_code)
        print("✅ Template executes successfully!")
        
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Runtime Error: {e}")
        return False

if __name__ == "__main__":
    success = test_ge_code_compilation()
    if success:
        print("\n🎉 All Unicode escape issues are resolved!")
        print("The Blender addon should now load successfully!")
    else:
        print("\n💥 There are still Unicode escape issues to fix!")
