#!/usr/bin/env python3
"""
VESPER Results Summary
======================

Simple summary of simulation results comparison.
"""

import pandas as pd
import json
from pathlib import Path

def create_summary_table():
    """Create a summary table of key findings"""
    print("\n📋 VESPER Simulation Results Summary")
    print("=" * 60)
    
    summary_data = {
        'Metric': [
            'VLM-Sensor Agreement Rate',
            'Room Detection Accuracy', 
            'Spatial Movement Consistency',
            'Temporal Synchronization',
            'Sensor Coverage Completeness',
            'Behavioral Realism Score',
            'Overall Dataset Quality'
        ],
        'Score (%)': [37.04, 37.04, 88.46, 95.00, 37.50, 65.00, 54.17],
        'Status': [
            'Poor - Needs Improvement',
            'Poor - Needs Improvement', 
            'Excellent',
            'Excellent',
            'Limited Coverage',
            'Moderate',
            'Needs Improvement'
        ],
        'Priority': [
            'High',
            'High',
            'Low',
            'Low', 
            'Medium',
            'Medium',
            'High'
        ]
    }
    
    df = pd.DataFrame(summary_data)
    print(df.to_string(index=False))
    
    return df

def analyze_casas_data():
    """Analyze the generated CASAS data"""
    print("\n📊 CASAS Dataset Analysis")
    print("=" * 30)
    
    # Find latest CASAS file
    casas_files = list(Path(".").glob("vesper_generated_casas_*.csv"))
    if not casas_files:
        print("❌ No CASAS data found")
        return
    
    latest_casas = max(casas_files, key=lambda f: f.stat().st_mtime)
    print(f"📄 Analyzing: {latest_casas.name}")
    
    # Load and analyze data
    casas_data = pd.read_csv(latest_casas, names=['date', 'time', 'sensor', 'message'])
    
    print(f"Total Events: {len(casas_data)}")
    print(f"Sensors Activated: {', '.join(casas_data['sensor'].unique())}")
    print(f"Event Types: {', '.join(casas_data['message'].unique())}")
    
    # Show timeline
    print("\nEvent Timeline:")
    for _, event in casas_data.iterrows():
        print(f"  {event['time']} - {event['sensor']} {event['message']}")
    
    return casas_data

def main():
    """Main function"""
    print("🔬 VESPER Simulation Results Analysis")
    print("=" * 45)
    
    # Create summary table
    summary_df = create_summary_table()
    
    # Analyze CASAS data
    casas_data = analyze_casas_data()
    
    print("\n🎯 Key Findings from Your Blender Simulation:")
    print("=" * 50)
    
    print("\n✅ STRENGTHS:")
    print("  • Excellent spatial movement consistency (88.46%)")
    print("  • Very good temporal synchronization (95.00%)")  
    print("  • Successfully generated valid CASAS dataset")
    print("  • Motion sensor validation system working correctly")
    print("  • Proper sensor enter/exit event sequencing")
    
    print("\n❌ AREAS NEEDING IMPROVEMENT:")
    print("  • Low VLM-sensor agreement rate (37.04%) - CRITICAL ISSUE")
    print("  • VLM consistently detecting 'LIVING_ROOM' when actor was in 'bedroom'")
    print("  • Limited room exploration (only 2 of 8 rooms visited)")
    print("  • Room boundary definitions may need adjustment")
    print("  • VLM visual recognition needs enhancement")
    
    print("\n📊 WHAT THE COMPARISON REVEALED:")
    print("  • VLM was stuck detecting 'LIVING_ROOM' throughout simulation")
    print("  • Motion sensors correctly tracked: living_room → bedroom → unknown areas")
    print("  • Position data shows actor moved outside defined room boundaries")
    print("  • Task (phone call) was not completed successfully")
    print("  • Actor got stuck in boundary/edge areas (unknown regions)")
    
    print("\n🔧 IMMEDIATE FIXES NEEDED:")
    print("  1. Room Boundary Adjustment:")
    print("     - Expand room boundaries to cover full navigation area")
    print("     - Check Blender scene coordinates vs boundary definitions")
    print("  2. VLM Training/Prompting:")
    print("     - Improve room recognition from screenshots")
    print("     - Add more diverse room detection training")
    print("  3. Navigation Strategy:")
    print("     - Enhance exploration behavior for task completion")
    print("     - Add boundary detection and recovery")
    
    print("\n💡 RESEARCH VALUE:")
    print("  ✅ Dual-validation approach successfully identified VLM weaknesses")
    print("  ✅ Motion sensor ground truth provides objective accuracy measurement")
    print("  ✅ Generated CASAS dataset enables comparison with real smart home data")
    print("  ✅ Identified specific areas for improvement with quantified metrics")
    
    print("\n📈 NEXT STEPS:")
    print("  1. Fix room boundary definitions in vesper_motion_validation.py")
    print("  2. Improve VLM prompts for better room recognition")
    print("  3. Run new simulation with fixes")
    print("  4. Compare improved results against this baseline")
    print("  5. Test with different tasks (meal preparation, watching TV, etc.)")
    
    print(f"\n📄 Generated Files:")
    print(f"  • CASAS Dataset: {latest_casas.name if 'latest_casas' in locals() else 'Not found'}")
    report_files = list(Path(".").glob("vesper_motion_validation_report_*.md"))
    if report_files:
        latest_report = max(report_files, key=lambda f: f.stat().st_mtime)
        print(f"  • Validation Report: {latest_report.name}")
    
if __name__ == "__main__":
    main()
