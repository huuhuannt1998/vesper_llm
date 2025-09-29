#!/usr/bin/env python3
"""
Image Management Utility for VESPER Navigation System
Helps manage both first-person screenshots and navigation context maps
"""

import os
import sys
from datetime import datetime

def count_images():
    """Count images in both directories"""
    print("📊 VESPER Image Inventory")
    print("=" * 50)
    
    # First-person screenshots
    fp_dir = r"C:\Users\hbui11\Desktop\vesper_llm\blender\captures"
    if os.path.exists(fp_dir):
        fp_files = [f for f in os.listdir(fp_dir) if f.startswith("fp_view_") and f.endswith(".png")]
        print(f"📷 First-person screenshots: {len(fp_files)}")
        if fp_files:
            fp_files.sort()
            print(f"   Range: {fp_files[0]} → {fp_files[-1]}")
            
            # Calculate total size
            total_size = sum(os.path.getsize(os.path.join(fp_dir, f)) for f in fp_files)
            print(f"   Total size: {total_size / (1024*1024):.1f} MB")
    else:
        print("📷 First-person screenshots: Directory not found")
    
    # Navigation context maps
    nav_dir = r"C:\Users\hbui11\Desktop\vesper_llm\map\generated_maps"
    if os.path.exists(nav_dir):
        nav_files = [f for f in os.listdir(nav_dir) if f.startswith("navigation_context_") and f.endswith(".png")]
        print(f"🗺️  Navigation context maps: {len(nav_files)}")
        if nav_files:
            nav_files.sort()
            print(f"   Range: {nav_files[0]} → {nav_files[-1]}")
            
            # Calculate total size
            total_size = sum(os.path.getsize(os.path.join(nav_dir, f)) for f in nav_files)
            print(f"   Total size: {total_size / (1024*1024):.1f} MB")
    else:
        print("🗺️  Navigation context maps: Directory not found")

def cleanup_old_images(keep_fp=50, keep_nav=50):
    """Clean up old images, keeping the most recent ones
    
    Args:
        keep_fp: Number of first-person screenshots to keep
        keep_nav: Number of navigation maps to keep
    """
    print(f"🧹 Cleaning up images (keeping last {keep_fp} FP, {keep_nav} NAV)")
    print("=" * 60)
    
    # Clean up first-person screenshots
    fp_dir = r"C:\Users\hbui11\Desktop\vesper_llm\blender\captures"
    if os.path.exists(fp_dir):
        fp_files = []
        for filename in os.listdir(fp_dir):
            if filename.startswith("fp_view_") and filename.endswith(".png"):
                try:
                    number_part = filename.replace("fp_view_", "").replace(".png", "")
                    if number_part.isdigit():
                        filepath = os.path.join(fp_dir, filename)
                        fp_files.append((filepath, int(number_part)))
                except:
                    continue
        
        if len(fp_files) > keep_fp:
            fp_files.sort(key=lambda x: x[1])
            files_to_delete = fp_files[:-keep_fp]
            
            print(f"📷 Deleting {len(files_to_delete)} old FP screenshots...")
            deleted_fp = 0
            for filepath, number in files_to_delete:
                try:
                    os.remove(filepath)
                    deleted_fp += 1
                except:
                    pass
            print(f"   ✅ Deleted {deleted_fp} FP screenshots")
        else:
            print(f"📷 No FP cleanup needed ({len(fp_files)} ≤ {keep_fp})")
    
    # Clean up navigation maps
    nav_dir = r"C:\Users\hbui11\Desktop\vesper_llm\map\generated_maps"
    if os.path.exists(nav_dir):
        nav_files = []
        for filename in os.listdir(nav_dir):
            if filename.startswith("navigation_context_") and filename.endswith(".png"):
                try:
                    number_part = filename.replace("navigation_context_", "").replace(".png", "")
                    if number_part.isdigit():
                        filepath = os.path.join(nav_dir, filename)
                        nav_files.append((filepath, int(number_part)))
                except:
                    continue
        
        if len(nav_files) > keep_nav:
            nav_files.sort(key=lambda x: x[1])
            files_to_delete = nav_files[:-keep_nav]
            
            print(f"🗺️  Deleting {len(files_to_delete)} old navigation maps...")
            deleted_nav = 0
            for filepath, number in files_to_delete:
                try:
                    os.remove(filepath)
                    deleted_nav += 1
                except:
                    pass
            print(f"   ✅ Deleted {deleted_nav} navigation maps")
        else:
            print(f"🗺️  No NAV cleanup needed ({len(nav_files)} ≤ {keep_nav})")

def reset_counters():
    """Reset image numbering by deleting all existing images"""
    print("🔄 RESETTING ALL IMAGES - This will delete everything!")
    response = input("Are you sure? Type 'YES' to confirm: ")
    
    if response != 'YES':
        print("❌ Reset cancelled")
        return
    
    deleted_total = 0
    
    # Delete FP screenshots
    fp_dir = r"C:\Users\hbui11\Desktop\vesper_llm\blender\captures"
    if os.path.exists(fp_dir):
        fp_files = [f for f in os.listdir(fp_dir) if f.startswith("fp_view_") and f.endswith(".png")]
        for filename in fp_files:
            try:
                os.remove(os.path.join(fp_dir, filename))
                deleted_total += 1
            except:
                pass
        print(f"🗑️ Deleted {len(fp_files)} FP screenshots")
    
    # Delete navigation maps
    nav_dir = r"C:\Users\hbui11\Desktop\vesper_llm\map\generated_maps"
    if os.path.exists(nav_dir):
        nav_files = [f for f in os.listdir(nav_dir) if f.startswith("navigation_context_") and f.endswith(".png")]
        for filename in nav_files:
            try:
                os.remove(os.path.join(nav_dir, filename))
                deleted_total += 1
            except:
                pass
        print(f"🗑️ Deleted {len(nav_files)} navigation maps")
    
    print(f"✅ Reset complete! Deleted {deleted_total} total images")
    print("🔄 Next navigation session will start from 001")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage VESPER navigation images")
    parser.add_argument("--count", action="store_true", help="Count images in both directories")
    parser.add_argument("--cleanup", nargs=2, metavar=('FP', 'NAV'), type=int, 
                       help="Clean up old images (keep last N of each type)")
    parser.add_argument("--reset", action="store_true", help="Reset all images (DELETE ALL)")
    
    args = parser.parse_args()
    
    if args.count:
        count_images()
    elif args.cleanup:
        cleanup_old_images(args.cleanup[0], args.cleanup[1])
    elif args.reset:
        reset_counters()
    else:
        # Default: show count
        count_images()
        print("\n💡 Usage examples:")
        print("  python image_manager.py --count")
        print("  python image_manager.py --cleanup 50 20  # Keep 50 FP, 20 NAV")
        print("  python image_manager.py --reset          # Delete everything")

if __name__ == "__main__":
    main()