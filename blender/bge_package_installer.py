"""
BGE Package Installer
====================

Run this directly in BGE console to install required packages.
"""

def install_packages_in_bge():
    """Install packages directly in BGE environment"""
    
    print("🔧 Installing packages for BGE...")
    
    import sys
    import subprocess
    import os
    
    # Show current Python
    print(f"📍 BGE Python: {sys.executable}")
    
    # Install packages
    packages = ["pillow", "pyautogui"]
    
    for package in packages:
        try:
            print(f"📦 Installing {package}...")
            
            # Try different installation methods
            methods = [
                [sys.executable, "-m", "pip", "install", package],
                [sys.executable, "-m", "pip", "install", "--user", package],
                [sys.executable, "-c", f"import subprocess; subprocess.check_call(['pip', 'install', '{package}'])"]
            ]
            
            success = False
            for method in methods:
                try:
                    result = subprocess.run(method, capture_output=True, text=True, timeout=60)
                    if result.returncode == 0:
                        print(f"✅ {package} installed successfully")
                        success = True
                        break
                    else:
                        print(f"⚠️ Method failed: {result.stderr[:100]}...")
                except Exception as e:
                    print(f"⚠️ Method error: {e}")
                    continue
            
            if not success:
                print(f"❌ All installation methods failed for {package}")
                
        except Exception as e:
            print(f"❌ Error with {package}: {e}")
    
    # Test installation
    print("\n🧪 Testing installation...")
    test_packages()

def test_packages():
    """Test if packages are available"""
    
    packages = [
        ("PIL", "Pillow (PIL)"),
        ("pyautogui", "PyAutoGUI")
    ]
    
    for package, name in packages:
        try:
            __import__(package)
            print(f"✅ {name} is available")
        except ImportError as e:
            print(f"❌ {name} is NOT available: {e}")

def check_environment():
    """Check BGE environment details"""
    
    import sys
    import platform
    
    print("🔍 BGE Environment Info:")
    print(f"   Python: {sys.version}")
    print(f"   Executable: {sys.executable}")
    print(f"   Platform: {platform.platform()}")
    print(f"   Python Path: {sys.path[:3]}...")

# Auto-run when imported
print("🎯 BGE PACKAGE INSTALLER")
print("=" * 30)

check_environment()
print()

# Ask user what to do
print("Options:")
print("1. install_packages_in_bge() - Install pillow and pyautogui")
print("2. test_packages() - Test if packages are available")
print("3. check_environment() - Show environment info")

print("\n💡 Example usage:")
print("   install_packages_in_bge()")
print("   test_packages()")