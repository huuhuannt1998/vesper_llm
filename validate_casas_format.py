"""
CASAS Format Validator
Verify that generated logs match CASAS dataset format
"""

import os
import re
from datetime import datetime

def validate_casas_motion_log(file_path):
    """
    Validate motion sensor log format
    Expected: YYYY-MM-DD HH:MM:SS.mmm SENSORID SENSORNAME EVENT
    """
    print(f"\n{'='*70}")
    print(f"VALIDATING MOTION SENSOR LOG: {os.path.basename(file_path)}")
    print(f"{'='*70}\n")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    # CASAS format pattern
    pattern = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} M\d{3} \w+ (ON|OFF)$'
    
    valid_count = 0
    invalid_count = 0
    sensor_ids = set()
    
    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            if re.match(pattern, line):
                valid_count += 1
                # Extract sensor ID
                parts = line.split()
                sensor_id = parts[2]
                sensor_ids.add(sensor_id)
                
                if line_num <= 5:  # Show first 5 lines
                    print(f"✅ Line {line_num}: {line}")
            else:
                invalid_count += 1
                print(f"❌ Line {line_num}: Invalid format: {line}")
    
    print(f"\n{'='*70}")
    print(f"VALIDATION RESULTS")
    print(f"{'='*70}")
    print(f"✅ Valid lines: {valid_count}")
    print(f"❌ Invalid lines: {invalid_count}")
    print(f"📊 Total lines: {valid_count + invalid_count}")
    print(f"🎯 Unique sensors: {len(sensor_ids)} - {sorted(sensor_ids)}")
    print(f"{'='*70}\n")
    
    success = invalid_count == 0
    if success:
        print("🎉 Motion sensor log is CASAS-compatible!")
    else:
        print("⚠️ Motion sensor log has format issues")
    
    return success


def validate_casas_item_log(file_path):
    """
    Validate item sensor log format
    Expected: YYYY-MM-DD HH:MM:SS.mmm SENSORID ITEMNAME EVENT
    """
    print(f"\n{'='*70}")
    print(f"VALIDATING ITEM SENSOR LOG: {os.path.basename(file_path)}")
    print(f"{'='*70}\n")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    # CASAS format pattern
    pattern = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} I\d{3} \w+ (ON|OFF)$'
    
    valid_count = 0
    invalid_count = 0
    sensor_ids = set()
    items = set()
    
    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            if re.match(pattern, line):
                valid_count += 1
                # Extract sensor ID and item name
                parts = line.split()
                sensor_id = parts[2]
                item_name = parts[3]
                sensor_ids.add(sensor_id)
                items.add(item_name)
                
                if line_num <= 5:  # Show first 5 lines
                    print(f"✅ Line {line_num}: {line}")
            else:
                invalid_count += 1
                print(f"❌ Line {line_num}: Invalid format: {line}")
    
    print(f"\n{'='*70}")
    print(f"VALIDATION RESULTS")
    print(f"{'='*70}")
    print(f"✅ Valid lines: {valid_count}")
    print(f"❌ Invalid lines: {invalid_count}")
    print(f"📊 Total lines: {valid_count + invalid_count}")
    print(f"🎯 Unique sensors: {len(sensor_ids)} - {sorted(sensor_ids)}")
    print(f"🏷️  Items tracked: {sorted(items)}")
    print(f"{'='*70}\n")
    
    success = invalid_count == 0
    if success:
        print("🎉 Item sensor log is CASAS-compatible!")
    else:
        print("⚠️ Item sensor log has format issues")
    
    return success


def find_latest_logs(dataset_dir):
    """Find most recent VESPER logs in dataset directory"""
    print(f"\n{'='*70}")
    print(f"SEARCHING FOR LOGS IN: {dataset_dir}")
    print(f"{'='*70}\n")
    
    if not os.path.exists(dataset_dir):
        print(f"❌ Directory not found: {dataset_dir}")
        return None, None
    
    motion_logs = []
    item_logs = []
    
    for filename in os.listdir(dataset_dir):
        if filename.startswith("motion_sensor_log_") and filename.endswith(".txt"):
            motion_logs.append(os.path.join(dataset_dir, filename))
        elif filename.startswith("item_sensor_log_") and filename.endswith(".txt"):
            item_logs.append(os.path.join(dataset_dir, filename))
    
    # Get most recent
    latest_motion = max(motion_logs, key=os.path.getmtime) if motion_logs else None
    latest_item = max(item_logs, key=os.path.getmtime) if item_logs else None
    
    if latest_motion:
        print(f"✅ Found motion log: {os.path.basename(latest_motion)}")
    else:
        print(f"⚠️ No motion sensor logs found")
    
    if latest_item:
        print(f"✅ Found item log: {os.path.basename(latest_item)}")
    else:
        print(f"⚠️ No item sensor logs found")
    
    return latest_motion, latest_item


def validate_timestamp_chronology(file_path):
    """Verify timestamps are in chronological order"""
    print(f"\n{'='*70}")
    print(f"CHECKING TIMESTAMP CHRONOLOGY")
    print(f"{'='*70}\n")
    
    timestamps = []
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) >= 2:
                timestamp_str = f"{parts[0]} {parts[1]}"
                try:
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
                    timestamps.append(timestamp)
                except:
                    pass
    
    if not timestamps:
        print("⚠️ No timestamps found")
        return False
    
    # Check if chronological
    is_chronological = all(timestamps[i] <= timestamps[i+1] for i in range(len(timestamps)-1))
    
    if is_chronological:
        print(f"✅ All {len(timestamps)} timestamps are in chronological order")
        print(f"   Start: {timestamps[0]}")
        print(f"   End: {timestamps[-1]}")
        duration = (timestamps[-1] - timestamps[0]).total_seconds()
        print(f"   Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    else:
        print(f"❌ Timestamps are NOT in chronological order!")
        # Find first out-of-order timestamp
        for i in range(len(timestamps)-1):
            if timestamps[i] > timestamps[i+1]:
                print(f"   Out of order at index {i}: {timestamps[i]} > {timestamps[i+1]}")
                break
    
    return is_chronological


if __name__ == "__main__":
    # Default dataset directory
    dataset_dir = r"C:\Users\hbui11\Desktop\vesper_llm\casas_testbed\vesper_datasets"
    
    print("\n" + "="*70)
    print("CASAS FORMAT VALIDATION TOOL")
    print("="*70)
    
    # Find latest logs
    motion_log, item_log = find_latest_logs(dataset_dir)
    
    all_valid = True
    
    # Validate motion sensor log
    if motion_log:
        motion_valid = validate_casas_motion_log(motion_log)
        if motion_valid:
            chrono_valid = validate_timestamp_chronology(motion_log)
            all_valid = all_valid and chrono_valid
        all_valid = all_valid and motion_valid
    
    # Validate item sensor log
    if item_log:
        item_valid = validate_casas_item_log(item_log)
        if item_valid:
            chrono_valid = validate_timestamp_chronology(item_log)
            all_valid = all_valid and chrono_valid
        all_valid = all_valid and item_valid
    
    # Final summary
    print("\n" + "="*70)
    print("FINAL VALIDATION SUMMARY")
    print("="*70)
    
    if all_valid and motion_log and item_log:
        print("🎉 All logs are CASAS-compatible and ready for comparison!")
        print("\n✅ You can now:")
        print("   1. Compare with CASAS ground truth datasets")
        print("   2. Run activity recognition algorithms")
        print("   3. Calculate accuracy metrics")
        print("   4. Publish research results")
    elif motion_log or item_log:
        print("⚠️ Some validation issues found - check logs above")
    else:
        print("❌ No logs found - run BGE simulation first")
    
    print("="*70 + "\n")
