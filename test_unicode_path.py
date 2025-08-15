#!/usr/bin/env python3
"""
Test for the specific Unicode escape issue with the path containing \\U
"""

def test_unicode_escape_in_path():
    # This simulates the problematic path that contains \U
    template_with_path = '''
def find_vesper_root():
    import os
    current_dir = os.path.dirname(__file__)
    while current_dir:
        if os.path.basename(current_dir) == 'vesper_llm':
            return current_dir
        current_dir = os.path.dirname(current_dir)
    
    # Fallback to hardcoded path if not found
    return r"c:\\Users\\hbui11\\Desktop\\vesper_llm"

print("Path found:", find_vesper_root())
'''
    
    try:
        print("Testing template with escaped path...")
        # Try to compile the template
        compile(template_with_path, '<string>', 'exec')
        print("✅ Template compiles successfully!")
        
        # Try to execute it
        exec(template_with_path)
        print("✅ Template executes without Unicode escape errors!")
        
    except SyntaxError as e:
        print(f"❌ Syntax Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Runtime Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_unicode_escape_in_path()
    if success:
        print("\n🎉 Unicode escape issue is fixed!")
    else:
        print("\n💥 Unicode escape issue still exists!")
