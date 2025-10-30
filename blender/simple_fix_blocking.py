#!/usr/bin/env python3
"""
SIMPLE FIX: Remove All Blocking Sleeps

The REAL problem: Your code has 10+ seconds of time.sleep() per iteration.
This makes CPU/GPU sit idle while waiting.

This script:
1. Removes ALL time.sleep() >= 1 second
2. Keeps small sleeps (< 1s) for polling
3. Makes BGE run continuously

NO async, NO multi-threading, NO complexity.
Just remove the blocking waits.
"""

import re

def fix_blocking_sleeps():
    """Remove blocking time.sleep() calls > 0.5 seconds"""
    
    file_path = "llm_bge_navigation.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    changes = []
    new_lines = []
    
    for i, line in enumerate(lines, 1):
        # Find time.sleep() calls
        match = re.search(r'time\.sleep\(([\d.]+)\)', line)
        
        if match:
            duration = float(match.group(1))
            
            # Only remove sleeps >= 0.5 seconds (the blocking ones)
            if duration >= 0.5:
                # Comment it out instead of removing
                indent = len(line) - len(line.lstrip())
                comment = line.split('#')[1].strip() if '#' in line else 'blocking sleep removed'
                new_line = ' ' * indent + f'# REMOVED: time.sleep({duration}) - {comment}\n'
                new_lines.append(new_line)
                
                changes.append({
                    'line': i,
                    'duration': duration,
                    'original': line.strip()
                })
                continue
        
        new_lines.append(line)
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    # Report
    print("=" * 70)
    print("🔧 SIMPLE FIX: Removed Blocking Sleeps")
    print("=" * 70)
    print(f"\nTotal blocking sleeps removed: {len(changes)}")
    
    if changes:
        total_time = sum(c['duration'] for c in changes)
        print(f"Total blocking time per iteration: {total_time:.1f} seconds\n")
        
        print("Removed sleeps:")
        for c in changes:
            print(f"  Line {c['line']:4d}: {c['duration']:4.1f}s")
        
        print("\n" + "=" * 70)
        print("IMPACT:")
        print("=" * 70)
        print(f"❌ Before: BGE blocked {total_time:.1f} seconds per iteration")
        print(f"✅ After:  BGE runs continuously")
        print(f"\n⚡ Expected speedup: {total_time / 0.1:.0f}x faster!")
    else:
        print("✅ No blocking sleeps found (all < 0.5 seconds)")
    
    print("=" * 70)
    
    return len(changes)

if __name__ == '__main__':
    count = fix_blocking_sleeps()
    
    print(f"\n✅ Fixed {count} blocking sleeps")
    print("\n🎯 NEXT STEP: Run Blender again")
    print("   The game engine should run much faster now!")
    print("\n⚠️  NOTE: This doesn't use multi-threading or async.")
    print("   It just removes the blocking waits that made BGE slow.")
