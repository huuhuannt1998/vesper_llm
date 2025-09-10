#!/usr/bin/env python3
"""
VESPER ADL System - Quick Start Guide

This script provides a quick start guide and initialization for the VESPER ADL Enhancement system
integrated with your existing Blender BGE navigation setup.

🎯 QUICK START:
1. Run this script in Blender to initialize VESPER ADL
2. Use F5-F8 keys for quick testing
3. Call bge.logic.vesper_run_test() for full testing

🔧 INTEGRATION:
- Extends existing llm_bge_navigation.py
- Works with existing Actor object and scene setup
- Integrates with existing evaluation framework
"""

import bge
import sys
import os
from pathlib import Path

def quick_start_vesper_adl():
    """
    Quick start function for VESPER ADL system.
    This is the main entry point for initialization.
    """
    
    print("\n" + "🚀" * 20)
    print("   VESPER ADL Enhancement System")
    print("   Quick Start & Integration")
    print("🚀" * 20 + "\n")
    
    # Initialize startup system
    from vesper_adl_startup import main as startup_main
    
    startup_success = startup_main()
    
    if startup_success:
        print("\n✨ VESPER ADL QUICK START COMPLETE!")
        print("=" * 50)
        
        # Show available functions
        show_available_functions()
        
        # Show integration status
        show_integration_status()
        
        # Show quick test option
        show_quick_test_options()
        
        return True
    else:
        print("\n❌ VESPER ADL QUICK START FAILED!")
        print("Please check the error messages above.")
        return False

def show_available_functions():
    """Show available VESPER ADL functions"""
    
    print("\n📋 Available Functions:")
    print("-" * 30)
    
    if hasattr(bge.logic, 'vesper_adl_functions'):
        print("✅ bge.logic.vesper_run_test() - Full test suite")
        print("✅ bge.logic.vesper_quick_test() - Quick test")
        print("✅ run_vesper_adl_demo() - Interactive demo")
        print("✅ Individual task functions available")
    else:
        print("❌ VESPER ADL functions not available")

def show_integration_status():
    """Show integration status with existing systems"""
    
    print("\n🔗 Integration Status:")
    print("-" * 30)
    
    scene = bge.logic.getCurrentScene()
    
    # Check existing navigation components
    has_actor = 'Actor' in scene.objects
    has_evaluation = hasattr(bge.logic, 'evaluation_log')
    has_vesper_ready = hasattr(bge.logic, 'vesper_adl_ready') and bge.logic.vesper_adl_ready
    
    print(f"Actor Object: {'✅ Found' if has_actor else '❌ Missing'}")
    print(f"Evaluation System: {'✅ Active' if has_evaluation else '❌ Not found'}")
    print(f"VESPER ADL Ready: {'✅ Ready' if has_vesper_ready else '❌ Not ready'}")
    
    if has_vesper_ready:
        # Show CASAS objects detected
        if hasattr(bge.logic, 'vesper_scene_objects'):
            casas_count = len(bge.logic.vesper_scene_objects)
            print(f"CASAS Objects: ✅ {casas_count} detected")
        else:
            print("CASAS Objects: ❌ None detected")

def show_quick_test_options():
    """Show quick test options"""
    
    print("\n🧪 Quick Test Options:")
    print("-" * 30)
    print("F5 Key: Quick ADL Test")
    print("F6 Key: Cooking Task Demo")
    print("F7 Key: Medication Task Demo")
    print("F8 Key: Communication Task Demo")
    print("\nPython Commands:")
    print("bge.logic.vesper_quick_test()")
    print("run_vesper_adl_demo()")

def run_integration_test():
    """Run a simple integration test"""
    
    print("\n🧪 Running Integration Test...")
    print("-" * 40)
    
    try:
        # Import test function
        from vesper_adl_bge_test import quick_vesper_adl_test
        
        result = quick_vesper_adl_test()
        
        if result:
            print("✅ Integration Test: PASSED")
            print("🎉 VESPER ADL is ready for use!")
        else:
            print("❌ Integration Test: FAILED")
            print("⚠️  Check system setup and try again")
            
        return result
        
    except Exception as e:
        print(f"❌ Integration Test Error: {e}")
        return False

def show_help():
    """Show help information"""
    
    print("\n📖 VESPER ADL Help")
    print("=" * 50)
    print("VESPER ADL Enhancement transforms basic navigation into")
    print("comprehensive Activities of Daily Living (ADL) execution.")
    print("")
    print("🎯 Goals:")
    print("- Increase CASAS similarity from 13.8% to 70%+")
    print("- Enable human-level ADL task execution")
    print("- Integrate with existing BGE navigation")
    print("")
    print("🔧 Key Components:")
    print("- Object Interaction System (CASAS objects)")
    print("- ADL Task Execution (cooking, medication, communication)")
    print("- VLM Intelligence Enhancement")
    print("- Integrated System Orchestration")
    print("")
    print("📊 Testing:")
    print("- Integration tests with existing BGE")
    print("- ADL task execution verification")
    print("- CASAS compatibility validation")
    print("- Performance and stability testing")
    print("")
    print("🚀 Getting Started:")
    print("1. Run quick_start_vesper_adl()")
    print("2. Test with F5-F8 keys")
    print("3. Run full test with bge.logic.vesper_run_test()")
    print("4. Use run_vesper_adl_demo() for interactive demo")

# Make key functions available globally
def make_global_functions():
    """Make key functions available globally in BGE"""
    
    # Add to BGE logic
    bge.logic.quick_start_vesper_adl = quick_start_vesper_adl
    bge.logic.run_integration_test = run_integration_test
    bge.logic.show_vesper_help = show_help
    
    # Import demo function
    try:
        from vesper_adl_startup import run_vesper_adl_demo
        bge.logic.run_vesper_adl_demo = run_vesper_adl_demo
    except ImportError:
        pass

# Main execution when script is run
if __name__ == "__main__":
    # Auto-start when run directly
    quick_start_vesper_adl()
    
elif 'bge' in globals():
    # Make functions available when imported in BGE
    make_global_functions()
    
    print("\n✨ VESPER ADL Quick Start Script Loaded!")
    print("Run: quick_start_vesper_adl() to begin")
    print("Help: show_help() for more information")

# Module exports
__all__ = [
    'quick_start_vesper_adl',
    'run_integration_test', 
    'show_help',
    'show_available_functions',
    'show_integration_status'
]
