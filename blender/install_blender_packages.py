"""
Install PyAutoGUI and Pillow for Blender BGE
==========================================

This script provides multiple methods to install the required packages
for the external first-person capture system.
"""

import subprocess
import sys
import os

def method_1_blender_python():
    """Method 1: Use Blender's built-in Python (Recommended)"""
    print("🔍 Method 1: Using Blender's built-in Python")
    
    # Common Blender Python paths
    blender_python_paths = [
        r"C:\Program Files\Blender Foundation\Blender 4.0\4.0\python\bin\python.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.6\3.6\python\bin\python.exe", 
        r"C:\Program Files\Blender Foundation\Blender 3.5\3.5\python\bin\python.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.4\3.4\python\bin\python.exe",
        r"C:\Users\{}\AppData\Local\Programs\Blender Foundation\Blender 4.0\4.0\python\bin\python.exe".format(os.environ.get('USERNAME', '')),
        r"C:\Users\{}\AppData\Local\Programs\Blender Foundation\Blender 3.6\3.6\python\bin\python.exe".format(os.environ.get('USERNAME', '')),
    ]
    
    # Find Blender Python
    blender_python = None
    for path in blender_python_paths:
        if os.path.exists(path):
            blender_python = path
            print(f"✅ Found Blender Python: {path}")
            break
    
    if not blender_python:
        print("❌ Blender Python not found in common locations")
        print("💡 Try Method 2 or find your Blender installation manually")
        return False
    
    # Install packages
    packages = ["pillow", "pyautogui"]
    
    for package in packages:
        try:
            print(f"📦 Installing {package}...")
            result = subprocess.run([blender_python, "-m", "pip", "install", package], 
                                  capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print(f"✅ {package} installed successfully")
            else:
                print(f"❌ {package} installation failed:")
                print(result.stderr)
                
        except Exception as e:
            print(f"❌ Error installing {package}: {e}")
    
    return True

def method_2_blender_console():
    """Method 2: Instructions for Blender Console"""
    print("\n🔍 Method 2: Install via Blender Console")
    print("=" * 40)
    
    console_commands = '''
# Run these commands in Blender's Python Console (Window > Toggle System Console)

import subprocess
import sys

# Get Blender's Python executable path
python_exe = sys.executable
print(f"Blender Python: {python_exe}")

# Install pillow
subprocess.check_call([python_exe, "-m", "pip", "install", "pillow"])

# Install pyautogui  
subprocess.check_call([python_exe, "-m", "pip", "install", "pyautogui"])

print("✅ Installation complete!")
'''
    
    print(console_commands)
    return True

def method_3_manual_find():
    """Method 3: Help user find Blender Python manually"""
    print("\n🔍 Method 3: Manual Blender Python Discovery")
    print("=" * 40)
    
    instructions = '''
1. Open Blender
2. Go to Window > Toggle System Console
3. In Blender's Python Console, run:
   
   import sys
   print(sys.executable)
   
4. Copy the path shown
5. Open PowerShell/Command Prompt as Administrator
6. Run these commands:

   "C:\\path\\to\\blender\\python.exe" -m pip install pillow
   "C:\\path\\to\\blender\\python.exe" -m pip install pyautogui

Replace "C:\\path\\to\\blender\\python.exe" with the actual path from step 4.
'''
    
    print(instructions)
    return True

def method_4_addon_install():
    """Method 4: Create a Blender addon to install packages"""
    print("\n🔍 Method 4: Blender Addon Installation")
    print("=" * 40)
    
    addon_code = '''
# Save this as "install_packages.py" in your Blender addons folder
# Then enable it in Preferences > Add-ons

bl_info = {
    "name": "Install External Packages",
    "blender": (3, 0, 0),
    "category": "System",
}

import bpy
import subprocess
import sys

class SYSTEM_OT_install_packages(bpy.types.Operator):
    bl_idname = "system.install_packages"
    bl_label = "Install PIL and PyAutoGUI"
    
    def execute(self, context):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyautogui"])
            self.report({'INFO'}, "Packages installed successfully!")
        except Exception as e:
            self.report({'ERROR'}, f"Installation failed: {e}")
        return {'FINISHED'}

class SYSTEM_PT_install_panel(bpy.types.Panel):
    bl_label = "Package Installer"
    bl_idname = "SYSTEM_PT_install"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("system.install_packages")

def register():
    bpy.utils.register_class(SYSTEM_OT_install_packages)
    bpy.utils.register_class(SYSTEM_PT_install_panel)

def unregister():
    bpy.utils.unregister_class(SYSTEM_OT_install_packages)
    bpy.utils.unregister_class(SYSTEM_PT_install_panel)

if __name__ == "__main__":
    register()
'''
    
    print("📝 Blender Addon Code:")
    print(addon_code)
    
    print("\n📋 Instructions:")
    print("1. Save the code above as 'install_packages.py'")
    print("2. In Blender: Edit > Preferences > Add-ons > Install...")
    print("3. Select the .py file and enable the addon")
    print("4. Find 'Package Installer' in the sidebar and click the button")
    
    return True

def test_installation():
    """Test if packages are available in current Python"""
    print("\n🧪 Testing Current Python Environment")
    print("=" * 40)
    
    packages = ["PIL", "pyautogui"]
    
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package} is available")
        except ImportError:
            print(f"❌ {package} is NOT available")

def main():
    print("🎯 INSTALL PILLOW & PYAUTOGUI FOR BLENDER")
    print("=" * 50)
    
    print("Choose installation method:")
    print("1. Auto-detect Blender Python (Recommended)")
    print("2. Blender Console Instructions") 
    print("3. Manual Discovery Instructions")
    print("4. Blender Addon Method")
    print("5. Test Current Environment")
    
    while True:
        try:
            choice = input("\nEnter choice (1-5): ").strip()
            
            if choice == "1":
                method_1_blender_python()
                break
            elif choice == "2":
                method_2_blender_console()
                break
            elif choice == "3":
                method_3_manual_find()
                break
            elif choice == "4":
                method_4_addon_install()
                break
            elif choice == "5":
                test_installation()
                break
            else:
                print("❌ Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Installation cancelled")
            break

if __name__ == "__main__":
    main()