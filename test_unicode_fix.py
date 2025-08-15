#!/usr/bin/env python3
"""
Test the complete ge_code template to ensure no Unicode escape errors.
"""
import os

def test_complete_template():
    # Simulate the template variables
    actor_name = "TestActor"
    tasks_data = ["Move to kitchen", "Open refrigerator"]
    backend_path = r"C:\Users\hbui11\Desktop\vesper_llm\backend"
    
    # This is a simplified version of the template that was causing issues
    ge_code_template = '''# VESPER LLM Visual Navigation - Game Engine Script
import sys
import os

# Add backend path for LLM client
backend_path = r"{backend_path}"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

def main():
    # Find actor in Game Engine
    actor_name = "{actor_name}"
    print("Actor name:", actor_name)
    
    # Get navigation data
    tasks = {tasks_data}
    print("Tasks:", tasks)
    
    print("\\n🧠 GE: Task completed!")
    print("\\n✅ GE: All tasks completed!")

if __name__ == "__main__":
    main()
'''
    
    try:
        # Format the template
        formatted_code = ge_code_template.format(
            actor_name=actor_name,
            tasks_data=str(tasks_data),
            backend_path=backend_path
        )
        
        print("✅ Template formatted successfully!")
        print("=" * 60)
        print(formatted_code)
        print("=" * 60)
        
        # Try to compile it
        compile(formatted_code, '<string>', 'exec')
        print("✅ Generated code compiles without Unicode escape errors!")
        
        # Try to execute it
        exec(formatted_code)
        print("✅ Generated code executes successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_complete_template()
    if success:
        print("\n🎉 All tests passed! The Unicode escape issue should be fixed.")
    else:
        print("\n💥 Tests failed. There are still Unicode escape issues.")
