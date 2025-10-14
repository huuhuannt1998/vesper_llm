#!/usr/bin/env python3
"""
Verify llm_bge_navigation.py syntax and integration points
"""

import ast
import sys

def verify_syntax(filepath):
    """Check if Python file has valid syntax"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
        
        # Try to parse as AST
        ast.parse(code)
        print("✅ SYNTAX CHECK PASSED")
        print(f"   File: {filepath}")
        print(f"   No syntax errors found")
        return True
        
    except SyntaxError as e:
        print("❌ SYNTAX ERROR FOUND")
        print(f"   File: {filepath}")
        print(f"   Line {e.lineno}: {e.msg}")
        print(f"   Text: {e.text}")
        return False
    except Exception as e:
        print(f"⚠️  Error reading file: {e}")
        return False

def check_integration_points(filepath):
    """Verify all integration points are present"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    checks = {
        "Import statement": "from interaction_system.vesper_interaction_integration import",
        "Initialize system": "initialize_interaction_system_for_bge()",
        "Start task": "interaction_system.start_task_with_interactions(",
        "Update state": "interaction_system.update_interaction_state(actor)",
        "Complete task (success)": "interaction_system.complete_task(success=True)",
        "Complete task (failure)": "interaction_system.complete_task(success=False)",
        "Export data": "interaction_system.export_all_data()"
    }
    
    print("\n" + "="*70)
    print("INTEGRATION POINTS VERIFICATION")
    print("="*70)
    
    all_found = True
    for name, marker in checks.items():
        if marker in content:
            print(f"✅ {name:30s} FOUND")
        else:
            print(f"❌ {name:30s} NOT FOUND")
            all_found = False
    
    print("="*70)
    
    if all_found:
        print("\n✅ ALL INTEGRATION POINTS VERIFIED")
        return True
    else:
        print("\n⚠️  SOME INTEGRATION POINTS MISSING")
        return False

if __name__ == "__main__":
    filepath = r"C:\Users\hbui11\Desktop\vesper_llm\blender\llm_bge_navigation.py"
    
    print("="*70)
    print("VESPER Integration Verification")
    print("="*70)
    
    # Check syntax
    syntax_ok = verify_syntax(filepath)
    
    # Check integration points
    integration_ok = check_integration_points(filepath)
    
    # Final result
    print("\n" + "="*70)
    if syntax_ok and integration_ok:
        print("🎉 SUCCESS! File is ready to run.")
        print("="*70)
        sys.exit(0)
    else:
        print("⚠️  ISSUES FOUND - Please review above")
        print("="*70)
        sys.exit(1)
