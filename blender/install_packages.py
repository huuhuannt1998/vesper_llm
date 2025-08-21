"""
Blender Package Installer for VESPER
Run this script in Blender's Python console to install required packages
"""

import subprocess
import sys
import bpy

def install_packages():
    """Install required packages for VESPER navigation"""
    packages = ["ollama", "requests", "python-dotenv"]
    
    print("🔧 Installing packages for VESPER navigation...")
    
    # Get Blender's Python executable
    python_exe = sys.executable
    print(f"📍 Using Python: {python_exe}")
    
    for package in packages:
        try:
            print(f"📦 Installing {package}...")
            subprocess.check_call([python_exe, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
        except Exception as e:
            print(f"⚠️ Error installing {package}: {e}")
    
    print("\n🎉 Package installation complete!")
    print("🔄 Restart Blender and run your navigation script")

def test_imports():
    """Test if required modules can be imported"""
    print("\n🧪 Testing imports...")
    
    modules = ["ollama", "requests", "dotenv"]
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module} - OK")
        except ImportError:
            print(f"❌ {module} - Missing")
    
    print("🔄 If any modules are missing, run install_packages() first")

if __name__ == "__main__":
    # Check if running in Blender
    try:
        import bpy
        print("🎮 Running in Blender environment")
        
        # Ask user what to do
        print("\n📋 Available actions:")
        print("1. install_packages() - Install required packages")
        print("2. test_imports() - Test if packages are available")
        print("\n💡 Copy and paste one of the above functions in Blender's console")
        
    except ImportError:
        print("⚠️ Not running in Blender - this script is for Blender's Python console")
