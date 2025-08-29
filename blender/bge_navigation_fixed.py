#!/usr/bin/env python3
"""
BGE Navigation with Python Path Fix
This version adds the VESPER project to Python path before imports
"""

import bge
import sys
import os

# CRITICAL: Add VESPER project to Python path before any backend imports
def setup_python_path():
    """Add VESPER project to Python path for backend imports"""
    vesper_root = r"C:\Users\hbui11\Desktop\vesper_llm"
    if vesper_root not in sys.path:
        sys.path.insert(0, vesper_root)
        print(f"🔧 BGE: Added to Python path: {vesper_root}")

# Setup path before any imports
setup_python_path()

# Now import the original navigation script
try:
    print("🔍 BGE: Importing navigation modules...")
    from blender.llm_bge_navigation import main as navigation_main
    print("✅ BGE: Navigation modules imported successfully")
    
    # Call the original main function
    def main():
        """Wrapper main function that ensures path is set"""
        print("🚀 BGE: Starting navigation with path fix...")
        navigation_main()
        
except ImportError as e:
    print(f"❌ BGE: Import error: {e}")
    print("🔍 BGE: Python path:")
    for i, path in enumerate(sys.path):
        print(f"   {i+1}. {path}")
    
    def main():
        """Fallback main function"""
        print("❌ BGE: Navigation failed to import - check Python path")
        
except Exception as e:
    print(f"💥 BGE: Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    
    def main():
        """Error fallback main function"""
        print("💥 BGE: Critical error during import")

# BGE entry point
if __name__ == "__main__":
    main()
