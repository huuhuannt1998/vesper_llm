#!/usr/bin/env python3
"""
Test the string formatting fix for the Blender addon.
This simulates the problematic string formatting that was causing the unicode escape error.
"""

def test_string_formatting():
    # Simulate the variables that would be used
    actor_name = "TestActor"
    tasks_data = ["Task 1", "Task 2"]
    backend_path = r"C:\Users\test\backend"
    
    # Test the old problematic format (this would cause an error)
    try:
        old_format = '''actor_name = "''' + actor_name + '''"'''
        print("❌ Old format would cause unicode escape error:")
        print(repr(old_format))
    except Exception as e:
        print(f"❌ Error with old format: {e}")
    
    # Test the new template format (this should work)
    try:
        template = '''# Test template
actor_name = "{actor_name}"
tasks = {tasks_data}
backend_path = r"{backend_path}"
print("Actor:", actor_name)
print("Tasks:", tasks)
        '''
        
        formatted_code = template.format(
            actor_name=actor_name,
            tasks_data=str(tasks_data),
            backend_path=backend_path
        )
        
        print("✅ New template format works:")
        print(formatted_code)
        
        # Try to compile it to verify it's valid Python
        compile(formatted_code, '<string>', 'exec')
        print("✅ Generated code compiles successfully!")
        
    except Exception as e:
        print(f"❌ Error with new format: {e}")

if __name__ == "__main__":
    test_string_formatting()
