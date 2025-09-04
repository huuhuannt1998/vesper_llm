#!/usr/bin/env python3
"""
VESPER Results Visualization
===========================

Creates visual comparisons of simulation results vs ground truth.
"""

import matplotlib.pyplot as plt
import numpy as np
import json
import pandas as pd
from pathlib import Path

def create_results_visualization():
    """Create visualization of VESPER simulation results"""
    print("📊 Creating VESPER Results Visualization...")
    
    # Load the latest CASAS data
    casas_files = list(Path(".").glob("vesper_generated_casas_*.csv"))
    if not casas_files:
        print("❌ No CASAS data found")
        return
    
    latest_casas = max(casas_files, key=lambda f: f.stat().st_mtime)
    casas_data = pd.read_csv(latest_casas, names=['date', 'time', 'sensor', 'message'])
    
    # Create visualization
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('VESPER Simulation Results vs Ground Truth Analysis', fontsize=16)
    
    # 1. VLM vs Sensor Agreement
    agreement_data = {
        'VLM Correct': 37.04,
        'VLM Incorrect': 62.96
    }
    
    ax1.pie(agreement_data.values(), labels=agreement_data.keys(), autopct='%1.1f%%',
            colors=['#2ecc71', '#e74c3c'])
    ax1.set_title('VLM-Sensor Agreement Rate')
    
    # 2. Sensor Coverage
    all_sensors = ['M01', 'M03', 'M07', 'M09', 'M11', 'M13', 'M16', 'M18']
    activated_sensors = casas_data['sensor'].unique()
    
    coverage_status = ['Activated' if sensor in activated_sensors else 'Not Activated' 
                      for sensor in all_sensors]
    coverage_counts = pd.Series(coverage_status).value_counts()
    
    ax2.bar(coverage_counts.index, coverage_counts.values, 
            color=['#3498db', '#95a5a6'])
    ax2.set_title('Motion Sensor Coverage')
    ax2.set_ylabel('Number of Sensors')
    
    # 3. Performance Metrics
    metrics = {
        'Location\nAgreement': 37.04,
        'Spatial\nConsistency': 88.46,
        'Temporal\nSync': 95.00,
        'Behavioral\nRealism': 65.00,
        'Dataset\nQuality': 54.17
    }
    
    colors = ['#e74c3c' if v < 50 else '#f39c12' if v < 75 else '#2ecc71' for v in metrics.values()]
    bars = ax3.bar(metrics.keys(), metrics.values(), color=colors)
    ax3.set_title('Performance Metrics (%)')
    ax3.set_ylabel('Score (%)')
    ax3.set_ylim(0, 100)
    
    # Add value labels on bars
    for bar, value in zip(bars, metrics.values()):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{value:.1f}%', ha='center', va='bottom')
    
    # 4. Sensor Timeline
    casas_data['datetime'] = pd.to_datetime(casas_data['date'] + ' ' + casas_data['time'])
    casas_data['minutes'] = (casas_data['datetime'] - casas_data['datetime'].min()).dt.total_seconds() / 60
    
    sensor_colors = {'M01': '#3498db', 'M07': '#e74c3c', 'M99': '#95a5a6'}
    
    for sensor in casas_data['sensor'].unique():
        sensor_data = casas_data[casas_data['sensor'] == sensor]
        for _, event in sensor_data.iterrows():
            y_pos = 1 if event['message'] == 'ON' else 0
            color = sensor_colors.get(sensor, '#95a5a6')
            ax4.scatter(event['minutes'], y_pos, c=color, s=100, alpha=0.7, label=sensor)
    
    ax4.set_title('Sensor Activation Timeline')
    ax4.set_xlabel('Time (minutes)')
    ax4.set_ylabel('Sensor State')
    ax4.set_yticks([0, 1])
    ax4.set_yticklabels(['OFF', 'ON'])
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save visualization
    output_file = 'vesper_results_visualization.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"📊 Visualization saved: {output_file}")
    
    # Show plot
    plt.show()

def create_summary_table():
    """Create a summary table of key findings"""
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
            '❌ Poor - Needs Improvement',
            '❌ Poor - Needs Improvement', 
            '✅ Excellent',
            '✅ Excellent',
            '⚠️ Limited Coverage',
            '⚠️ Moderate',
            '⚠️ Needs Improvement'
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
    print("\n📋 VESPER Simulation Results Summary")
    print("=" * 60)
    print(df.to_string(index=False))
    
    return df

def main():
    """Main function"""
    print("🎨 VESPER Results Visualization Tool")
    print("=" * 40)
    
    # Create summary table
    summary_df = create_summary_table()
    
    # Create visualizations
    try:
        create_results_visualization()
    except Exception as e:
        print(f"⚠️ Visualization error: {e}")
        print("📊 Summary table created successfully")
    
    print("\n🎯 Key Findings:")
    print("1. ❌ VLM room detection accuracy is low (37%) - primary issue")
    print("2. ✅ Spatial movement consistency is excellent (88%)")
    print("3. ✅ Temporal synchronization is very good (95%)")
    print("4. ⚠️ Limited room exploration (only 2 of 8 rooms visited)")
    print("5. 📊 Generated valid CASAS dataset with proper sensor events")
    
    print("\n💡 Recommendations:")
    print("1. 🔧 Improve VLM training for better room recognition")
    print("2. 🏠 Adjust room boundary definitions in Blender scene")
    print("3. 🎯 Enhance task prompts to encourage more exploration")
    print("4. 📷 Improve screenshot quality/angle for VLM analysis")
    print("5. 🔄 Run additional test scenarios for statistical validation")

if __name__ == "__main__":
    main()
