"""
VESPER BGE-MCP Startup Script
============================

Complete startup script for running the VESPER system with BGE and MCP integration.
"""

import subprocess
import sys
import os
import time
import json
import signal
from pathlib import Path
from typing import List, Dict, Optional

class VESPERStartupManager:
    """Manages startup of VESPER BGE-MCP integrated system"""
    
    def __init__(self, vesper_root: str = None):
        self.vesper_root = vesper_root or r"C:\Users\hbui11\Desktop\vesper_llm"
        self.processes: Dict[str, subprocess.Popen] = {}
        self.startup_order = [
            "mcp_services",
            "vlm_training",
            "blender_bge"
        ]
        self.shutdown_handlers = []
    
    def setup_environment(self):
        """Setup environment variables and paths"""
        
        print("🔧 Setting up environment...")
        
        # Set VESPER environment variables
        os.environ["VESPER_ROOT"] = self.vesper_root
        os.environ["VESPER_MCP_ENABLED"] = "true"
        os.environ["VESPER_BGE_INTEGRATION"] = "true"
        
        # Add paths
        blender_path = os.path.join(self.vesper_root, "blender")
        if blender_path not in sys.path:
            sys.path.insert(0, blender_path)
        
        print("✅ Environment setup complete")
    
    def start_mcp_services(self) -> bool:
        """Start MCP microservices"""
        
        print("🚀 Starting MCP microservices...")
        
        script_path = os.path.join(self.vesper_root, "launch_mcp_services.py")
        
        if not os.path.exists(script_path):
            print(f"❌ MCP launcher not found: {script_path}")
            return False
        
        try:
            process = subprocess.Popen([
                sys.executable, script_path
            ], cwd=self.vesper_root, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0)
            
            self.processes["mcp_services"] = process
            
            # Wait for services to start
            print("⏳ Waiting for MCP services to initialize...")
            time.sleep(10)
            
            # Check if process is still running
            if process.poll() is None:
                print("✅ MCP services started successfully")
                return True
            else:
                print("❌ MCP services failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start MCP services: {str(e)}")
            return False
    
    def start_vlm_training_system(self) -> bool:
        """Start VLM training system in background"""
        
        print("🧠 Starting VLM training system...")
        
        # Check if training should be started
        train_config_path = os.path.join(self.vesper_root, "vlm_config.py")
        
        if not os.path.exists(train_config_path):
            print("⚠️ VLM training config not found - skipping training")
            return True
        
        try:
            # Start VLM training in background monitoring mode
            vlm_script = os.path.join(self.vesper_root, "vlm_training_pipeline.py")
            
            if os.path.exists(vlm_script):
                process = subprocess.Popen([
                    sys.executable, vlm_script, "--monitor-mode"
                ], cwd=self.vesper_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0)
                
                self.processes["vlm_training"] = process
                print("✅ VLM training system started")
            else:
                print("⚠️ VLM training script not found - continuing without training")
            
            return True
            
        except Exception as e:
            print(f"⚠️ VLM training startup issue: {str(e)}")
            return True  # Non-critical, continue anyway
    
    def start_blender_bge(self, blend_file: str = None, headless: bool = False) -> bool:
        """Start Blender with BGE navigation"""
        
        print("🎮 Starting Blender BGE navigation...")
        
        # Default blend file
        if blend_file is None:
            blend_files = ["house_3.blend", "house_2.blend", "house.blend"]
            blender_dir = os.path.join(self.vesper_root, "blender")
            
            for bf in blend_files:
                bf_path = os.path.join(blender_dir, bf)
                if os.path.exists(bf_path):
                    blend_file = bf_path
                    break
        
        if not blend_file or not os.path.exists(blend_file):
            print("❌ No suitable blend file found")
            return False
        
        # BGE navigation script
        bge_script = os.path.join(self.vesper_root, "blender", "llm_bge_navigation.py")
        
        if not os.path.exists(bge_script):
            print(f"❌ BGE navigation script not found: {bge_script}")
            return False
        
        try:
            # Build Blender command
            blender_cmd = ["blender", blend_file]
            
            if headless:
                blender_cmd.extend(["-b", "--python", bge_script])
            else:
                blender_cmd.extend(["--python", bge_script])
            
            print(f"🎯 Starting Blender with: {' '.join(blender_cmd)}")
            
            process = subprocess.Popen(
                blender_cmd,
                cwd=os.path.join(self.vesper_root, "blender"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes["blender_bge"] = process
            print("✅ Blender BGE started")
            
            return True
            
        except FileNotFoundError:
            print("❌ Blender executable not found in PATH")
            print("💡 Please ensure Blender is installed and in your PATH")
            return False
        except Exception as e:
            print(f"❌ Failed to start Blender BGE: {str(e)}")
            return False
    
    def check_dependencies(self) -> bool:
        """Check if required dependencies are available"""
        
        print("🔍 Checking dependencies...")
        
        dependencies = {
            "python": "Python interpreter",
            "blender": "Blender 3D (optional for headless mode)"
        }
        
        missing_deps = []
        
        for dep, description in dependencies.items():
            try:
                if dep == "python":
                    # Python is obviously available if we're running this
                    continue
                elif dep == "blender":
                    # Check if blender is in PATH
                    subprocess.run([dep, "--version"], capture_output=True, check=True)
                
                print(f"  ✅ {dep}: {description}")
                
            except (subprocess.CalledProcessError, FileNotFoundError):
                if dep == "blender":
                    print(f"  ⚠️ {dep}: {description} (optional - can run headless)")
                else:
                    print(f"  ❌ {dep}: {description}")
                    missing_deps.append(dep)
        
        if missing_deps:
            print(f"❌ Missing critical dependencies: {missing_deps}")
            return False
        
        print("✅ Dependencies check completed")
        return True
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        
        def signal_handler(signum, frame):
            print(f"\n🛑 Received signal {signum}")
            self.shutdown_all()
            sys.exit(0)
        
        if sys.platform != "win32":
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
        
        self.shutdown_handlers.append(signal_handler)
    
    def shutdown_process(self, process_name: str):
        """Shutdown a specific process"""
        
        if process_name in self.processes:
            process = self.processes[process_name]
            
            try:
                if sys.platform == "win32":
                    os.kill(process.pid, signal.CTRL_BREAK_EVENT)
                else:
                    process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                
                print(f"✅ Stopped {process_name}")
                
            except Exception as e:
                print(f"⚠️ Error stopping {process_name}: {str(e)}")
            
            del self.processes[process_name]
    
    def shutdown_all(self):
        """Shutdown all running processes"""
        
        print("🛑 Shutting down VESPER system...")
        
        # Shutdown in reverse order
        shutdown_order = list(reversed(self.startup_order))
        
        for process_name in shutdown_order:
            if process_name in self.processes:
                self.shutdown_process(process_name)
        
        print("✅ VESPER system shutdown complete")
    
    def start_full_system(self, headless_blender: bool = False, blend_file: str = None) -> bool:
        """Start the complete VESPER BGE-MCP system"""
        
        print("🚀 Starting VESPER BGE-MCP Integrated System")
        print("=" * 60)
        
        # Setup
        self.setup_environment()
        self.setup_signal_handlers()
        
        # Check dependencies
        if not self.check_dependencies():
            return False
        
        # Start components in order
        startup_success = True
        
        try:
            # 1. Start MCP services
            if not self.start_mcp_services():
                print("❌ Failed to start MCP services")
                startup_success = False
            
            # 2. Start VLM training system
            if startup_success and not self.start_vlm_training_system():
                print("⚠️ VLM training issues, but continuing...")
            
            # 3. Start Blender BGE
            if startup_success and not self.start_blender_bge(blend_file, headless_blender):
                print("❌ Failed to start Blender BGE")
                startup_success = False
            
            if startup_success:
                print("\n✅ VESPER BGE-MCP System Started Successfully!")
                print("=" * 60)
                print("🎮 Blender BGE is running with MCP integration")
                print("🔗 MCP microservices are active")
                print("🧠 VLM training system is monitoring")
                print("\n📋 Press Ctrl+C to shutdown system")
                
                # Keep main process alive
                try:
                    while True:
                        # Monitor processes
                        for name, process in list(self.processes.items()):
                            if process.poll() is not None:
                                print(f"⚠️ Process {name} terminated unexpectedly")
                        
                        time.sleep(5)
                        
                except KeyboardInterrupt:
                    print("\n🛑 Keyboard interrupt received")
                
                return True
            else:
                print("❌ System startup failed")
                self.shutdown_all()
                return False
                
        except Exception as e:
            print(f"❌ Startup error: {str(e)}")
            self.shutdown_all()
            return False

def main():
    """Main startup function"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="VESPER BGE-MCP Startup Manager")
    parser.add_argument("--headless", action="store_true", help="Run Blender in headless mode")
    parser.add_argument("--blend-file", type=str, help="Specific blend file to use")
    parser.add_argument("--vesper-root", type=str, help="VESPER root directory")
    
    args = parser.parse_args()
    
    manager = VESPERStartupManager(args.vesper_root)
    
    success = manager.start_full_system(
        headless_blender=args.headless,
        blend_file=args.blend_file
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
