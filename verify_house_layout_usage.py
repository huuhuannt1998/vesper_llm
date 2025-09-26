#!/usr/bin/env python3
"""
Verify which generated maps are using the real house layout
"""

import os
from PIL import Image

def analyze_generated_maps():
    """Analyze the generated maps to see which ones use real vs test layouts"""
    
    maps_dir = "map/generated_maps"
    if not os.path.exists(maps_dir):
        print(f"❌ Maps directory not found: {maps_dir}")
        return
    
    print("📊 Analyzing Generated Maps")
    print("=" * 40)
    
    # Get all PNG files
    map_files = [f for f in os.listdir(maps_dir) if f.endswith('.png')]
    map_files.sort()
    
    # Analyze each map
    for map_file in map_files:
        map_path = os.path.join(maps_dir, map_file)
        
        try:
            with Image.open(map_path) as img:
                size = img.size
                
                # Determine likely source based on size
                if size == (800, 600):
                    layout_type = "🧪 Test Layout (B102.png)"
                elif size == (978, 1038):
                    layout_type = "🏠 Real House Layout (house_layout_reference2.png)"
                else:
                    layout_type = f"❓ Unknown ({size[0]}x{size[1]})"
                
                print(f"  {map_file}")
                print(f"    Size: {size[0]}x{size[1]}")
                print(f"    Type: {layout_type}")
                print()
                
        except Exception as e:
            print(f"  ❌ {map_file}: Error - {e}")
    
    print("🎯 Summary:")
    test_maps = [f for f in map_files if "153415" in f or "153317" in f or "153719" in f or "151714" in f]
    real_maps = [f for f in map_files if "154111" in f]
    
    print(f"  Test Layout Maps: {len(test_maps)} files")
    for f in test_maps:
        print(f"    - {f}")
    
    print(f"  Real House Layout Maps: {len(real_maps)} files")
    for f in real_maps:
        print(f"    - {f}")
    
    if len(real_maps) > 0:
        print(f"\n✅ Success! {len(real_maps)} maps are now using the real house layout!")
    else:
        print(f"\n⚠️  No maps found using the real house layout yet.")

if __name__ == "__main__":
    analyze_generated_maps()