"""
Virtual Time System Integration Script
Adds virtual time tracking to VESPER navigation logs
120x speed: 60 real minutes = 30 seconds virtual time
"""

import re
import os

# Get the path to llm_bge_navigation.py (one level up from time_system)
script_dir = os.path.dirname(os.path.abspath(__file__))
nav_file = os.path.join(os.path.dirname(script_dir), 'llm_bge_navigation.py')

# Read the file
with open(nav_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Change 1: Update _log_to_file method to include virtual time summary
old_log_to_file = '''    def _log_to_file(self):
        """Save current metrics to JSON file"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.session_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  METRICS: Failed to save log file - {e}")'''

new_log_to_file = '''    def _log_to_file(self):
        """Save current metrics to JSON file"""
        try:
            # Add virtual time summary if available
            if self.virtual_time_manager:
                self.session_data["virtual_time_summary"] = self.virtual_time_manager.get_time_summary()
            
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.session_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  METRICS: Failed to save log file - {e}")'''

# Also add virtual time log export
old_export_datasets = '''            import types
            metrics_logger._export_datasets = types.MethodType(_export_datasets, metrics_logger)
    
    return metrics_logger'''

new_export_datasets = '''            import types
            metrics_logger._export_datasets = types.MethodType(_export_datasets, metrics_logger)
    
    # Export virtual time log if available
    if metrics_logger.virtual_time_manager:
        metrics_logger.virtual_time_manager.export_time_log(metrics_logger.dataset_dir)
    
    return metrics_logger'''

print("=" * 80)
print("VIRTUAL TIME SYSTEM INTEGRATION")
print("=" * 80)
print()

# Apply changes
changes_made = 0

if old_log_to_file in content:
    content = content.replace(old_log_to_file, new_log_to_file)
    print("✅ Updated _log_to_file method to include virtual time summary")
    changes_made += 1
else:
    print("⚠️  Could not find _log_to_file method (may already be updated)")

if old_export_datasets in content:
    content = content.replace(old_export_datasets, new_export_datasets)
    print("✅ Added virtual time log export")
    changes_made += 1
else:
    print("⚠️  Could not find export_datasets section (may already be updated)")

if changes_made > 0:
    # Write back
    with open(nav_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print()
    print(f"✅ Applied {changes_made} changes successfully!")
else:
    print()
    print("ℹ️  No changes applied - file may already be up to date")

print()
print("=" * 80)
print("VIRTUAL TIME CONFIGURATION")
print("=" * 80)
print("⏱️  Time Scale: 120x")
print("   → 60 real minutes = 30 seconds in virtual environment")
print("   → 15 min phone call = 7.5 seconds real time")
print("   → 8 hour sleep = 4 minutes real time")
print()
print("📊 Logged Data:")
print("   - virtual_start_time: ISO 8601 timestamp")
print("   - virtual_end_time: ISO 8601 timestamp")
print("   - virtual_duration: Seconds in virtual time")
print("   - virtual_time_summary: Overall session time stats")
print()
print("📄 Output Files:")
print("   - vesper_metrics_p01_TIMESTAMP.json (includes virtual time)")
print("   - virtual_time_log.json (detailed time events)")
print()
print("=" * 80)
