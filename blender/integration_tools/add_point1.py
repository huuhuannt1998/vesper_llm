#!/usr/bin/env python3
"""Add Point 1: Initialize Interaction System"""

import os

nav_file = r"C:\Users\hbui11\Desktop\vesper_llm\blender\llm_bge_navigation.py"

# Read file
with open(nav_file, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# Find the line after CASAS logger initialization
insertion_point = None
for i, line in enumerate(lines):
    if 'Failed to initialize CASAS logger' in line:
        insertion_point = i + 1
        break

if insertion_point:
    # Add the initialization code
    new_lines = [
        "\n",
        "        # Initialize VESPER Interaction System (Item Sensors + Virtual Devices + Time)\n",
        "        if INTERACTION_SYSTEM_AVAILABLE and not hasattr(bge.logic, 'interaction_system'):\n",
        "            try:\n",
        "                initialize_interaction_system_for_bge()\n",
        '                print("✅ VESPER Interaction System initialized (Item Sensors + Devices + Time)")\n',
        "            except Exception as e:\n",
        '                print(f"⚠️ Failed to initialize interaction system: {e}")\n',
    ]
    
    # Insert the new lines
    lines = lines[:insertion_point] + new_lines + lines[insertion_point:]
    
    # Write back
    with open(nav_file, 'w', encoding='utf-8', errors='ignore') as f:
        f.writelines(lines)
    
    print("✅ Added Point 1: Initialize Interaction System")
    print(f"   Inserted at line {insertion_point + 1}")
else:
    print("❌ Could not find insertion point")
