#!/usr/bin/env python3
"""Remove BOM from llm_bge_navigation.py"""

import os

filepath = r"C:\Users\hbui11\Desktop\vesper_llm\blender\llm_bge_navigation.py"

# Read file
with open(filepath, 'r', encoding='utf-8-sig') as f:
    content = f.read()

# Write without BOM
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ Removed BOM from {filepath}")
print("File is now clean UTF-8 without BOM")
