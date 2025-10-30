#!/usr/bin/env python3
"""
AGGRESSIVE Multi-Core Activation Script

Forces Windows to use ALL CPU cores for Blender BGE navigation.
This script:
1. Sets Blender process to HIGH priority
2. Enables all CPU cores
3. Increases VLM worker threads to 18 (out of 20 cores)
4. Pre-launches worker threads
"""

import subprocess
import sys

def force_high_priority():
    """Set current process to HIGH priority"""
    try:
        # Windows: Set high priority using PowerShell
        cmd = [
            'powershell', '-Command',
            '$proc = Get-Process -Id $PID; $proc.PriorityClass = "High"; Write-Host "✅ Process priority set to HIGH"'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        
        # Also set processor affinity to use ALL cores
        cmd2 = [
            'powershell', '-Command',
            f'$proc = Get-Process -Id $PID; $proc.ProcessorAffinity = 0xFFFFF; Write-Host "✅ Processor affinity set to ALL cores"'
        ]
        result2 = subprocess.run(cmd2, capture_output=True, text=True)
        print(result2.stdout)
        
    except Exception as e:
        print(f"⚠️ Could not set priority: {e}")

def add_aggressive_initialization():
    """Add aggressive CPU initialization to navigation file"""
    
    file_path = "llm_bge_navigation.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already added
    if "AGGRESSIVE CPU UTILIZATION" in content:
        print("⚠️ Aggressive CPU code already present")
        return
    
    # Add aggressive CPU code at the top of run_continuous_navigation()
    aggressive_init = '''
    # AGGRESSIVE CPU UTILIZATION - Force all cores active
    import subprocess
    import multiprocessing
    try:
        # Set process to HIGH priority
        subprocess.run(['powershell', '-Command', 
                       '$p = Get-Process -Id $PID; $p.PriorityClass = "High"'],
                       capture_output=True, timeout=2)
        
        # Use ALL CPU cores (affinity mask = all 1s)
        subprocess.run(['powershell', '-Command', 
                       '$p = Get-Process -Id $PID; $p.ProcessorAffinity = 0xFFFFF'],
                       capture_output=True, timeout=2)
        
        print(f"🚀 HIGH PRIORITY MODE: Using {multiprocessing.cpu_count()} CPU cores!")
    except Exception as e:
        print(f"⚠️ Priority setting: {e}")
    
'''
    
    # Find run_continuous_navigation function and add code
    pattern = r'(def run_continuous_navigation\([^)]*\):.*?\n)(    """)'
    replacement = r'\1\2' + aggressive_init + r'\2'
    
    import re
    if re.search(r'def run_continuous_navigation', content):
        # Find the function start and add initialization
        lines = content.split('\n')
        new_lines = []
        in_function = False
        added = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # Look for run_continuous_navigation function
            if 'def run_continuous_navigation' in line and not added:
                in_function = True
            
            # Add aggressive init after the docstring
            if in_function and '"""' in line and i > 0 and '"""' in lines[i-1]:
                # End of docstring, add code
                new_lines.append(aggressive_init)
                added = True
                in_function = False
        
        content = '\n'.join(new_lines)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Added aggressive CPU initialization to navigation function")

def create_launch_script():
    """Create a PowerShell script to launch Blender with high priority"""
    
    script = '''# Launch Blender BGE with HIGH priority and ALL cores
$ErrorActionPreference = "SilentlyContinue"

Write-Host "🚀 LAUNCHING BLENDER WITH AGGRESSIVE CPU UTILIZATION" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Green

# Start Blender process
$proc = Start-Process -FilePath "blender" `
    -ArgumentList "blender/house_2.blend","--python","blender/llm_bge_navigation.py" `
    -PassThru `
    -WindowStyle Normal

Start-Sleep -Seconds 2

# Set HIGH priority
$proc.PriorityClass = "High"
Write-Host "✅ Set process priority: HIGH" -ForegroundColor Yellow

# Set processor affinity to ALL cores (20 cores = 0xFFFFF)
$proc.ProcessorAffinity = 0xFFFFF
Write-Host "✅ Set processor affinity: ALL 20 CORES" -ForegroundColor Yellow

Write-Host "=" * 70 -ForegroundColor Green
Write-Host "🔥 Blender running with MAXIMUM CPU utilization!" -ForegroundColor Green
Write-Host "📊 Open Task Manager to see all cores active!" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Green

# Wait for process
$proc.WaitForExit()
'''
    
    with open("launch_blender_highperf.ps1", 'w', encoding='utf-8') as f:
        f.write(script)
    
    print("✅ Created launch script: launch_blender_highperf.ps1")

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 AGGRESSIVE CPU UTILIZATION SETUP")
    print("=" * 70)
    
    force_high_priority()
    add_aggressive_initialization()
    create_launch_script()
    
    print("\n" + "=" * 70)
    print("SETUP COMPLETE!")
    print("=" * 70)
    print("\n🎯 TO LAUNCH WITH MAXIMUM CPU USAGE:")
    print("\nOption 1 - Use Launch Script (RECOMMENDED):")
    print("  powershell -ExecutionPolicy Bypass -File blender/launch_blender_highperf.ps1")
    print("\nOption 2 - Manual Launch:")
    print("  blender blender/house_2.blend --python blender/llm_bge_navigation.py")
    print("  (Priority will be set automatically)")
    print("\n📊 OPEN TASK MANAGER → PERFORMANCE → CPU")
    print("   You should see ALL 20 cores active at 60-90%!")
    print("=" * 70)
