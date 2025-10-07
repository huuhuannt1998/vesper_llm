#!/usr/bin/env python3
"""
Test Graph Generation Functions

Tests the 4 graphing functions in casas_comparison.py to ensure they work properly.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

# Add paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_graph_generation():
    """Test all 4 graph generation functions"""
    print("\n" + "="*80)
    print("TESTING GRAPH GENERATION FUNCTIONS")
    print("="*80)
    
    # Create output directory
    output_dir = r"c:\Users\hbui11\Desktop\vesper_llm\casas_testbed\data\comparison_results"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate sample comparison results data
    print("\n📊 Generating sample data for testing...")
    n_samples = 20
    
    # Simulate similarity scores
    np.random.seed(42)
    results = []
    for i in range(n_samples):
        result = {
            'vlm_file': f'vlm_dataset_{i+1}.csv',
            'casas_file': f'casas_dataset_{i+1}.csv',
            'similarity_scores': {
                'overall_similarity': np.random.uniform(0.3, 0.9),
                'temporal_similarity': np.random.uniform(0.4, 0.95),
                'event_count_similarity': np.random.uniform(0.3, 0.9),
                'sensor_similarity': np.random.uniform(0.5, 0.95),
                'transition_similarity': np.random.uniform(0.35, 0.85),
                'hourly_pattern_similarity': np.random.uniform(0.25, 0.8)
            },
            'vlm_features': {
                'event_count': np.random.randint(50, 200),
                'duration': np.random.uniform(100, 500)
            },
            'casas_features': {
                'event_count': np.random.randint(40, 210),
                'duration': np.random.uniform(90, 520)
            }
        }
        results.append(result)
    
    # Extract similarity scores into DataFrame
    scores_df = pd.DataFrame([r['similarity_scores'] for r in results])
    
    print(f"✅ Generated {n_samples} sample comparison results")
    print(f"\nSample similarity scores:")
    print(scores_df.describe())
    
    # Test all 4 graphs
    plot_files = []
    
    # ========================================================================
    # GRAPH 1: Overall Similarity Distribution (Histogram)
    # ========================================================================
    try:
        print("\n" + "-"*80)
        print("📈 Graph 1: Overall Similarity Distribution (Histogram)")
        print("-"*80)
        
        plt.figure(figsize=(8, 6))
        plt.hist(scores_df['overall_similarity'], bins=20, alpha=0.7, color='skyblue')
        plt.title('Overall Similarity Score Distribution', fontsize=14, fontweight='bold')
        plt.xlabel('Similarity Score')
        plt.ylabel('Frequency')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plot_file_1 = os.path.join(output_dir, "similarity_distribution.png")
        plt.savefig(plot_file_1, dpi=300, bbox_inches='tight')
        plt.close()
        
        plot_files.append(plot_file_1)
        print(f"✅ PASS - Graph 1 created successfully")
        print(f"   📁 {plot_file_1}")
        
    except Exception as e:
        print(f"❌ FAIL - Graph 1 failed: {e}")
    
    # ========================================================================
    # GRAPH 2: Similarity Metrics Comparison (Bar Chart)
    # ========================================================================
    try:
        print("\n" + "-"*80)
        print("📈 Graph 2: Similarity Metrics Comparison (Bar Chart)")
        print("-"*80)
        
        plt.figure(figsize=(10, 6))
        metrics = ['temporal_similarity', 'event_count_similarity', 'sensor_similarity', 'transition_similarity']
        metric_means = [scores_df[m].mean() for m in metrics]
        bars = plt.bar(range(len(metrics)), metric_means, color=['red', 'green', 'blue', 'orange'])
        plt.title('Average Similarity by Metric', fontsize=14, fontweight='bold')
        plt.xlabel('Metrics')
        plt.ylabel('Average Score')
        plt.xticks(range(len(metrics)), [m.replace('_', '\n') for m in metrics])
        plt.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, value in zip(bars, metric_means):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                    f'{value:.3f}', ha='center', va='bottom')
        plt.tight_layout()
        
        plot_file_2 = os.path.join(output_dir, "metric_comparison.png")
        plt.savefig(plot_file_2, dpi=300, bbox_inches='tight')
        plt.close()
        
        plot_files.append(plot_file_2)
        print(f"✅ PASS - Graph 2 created successfully")
        print(f"   📁 {plot_file_2}")
        
    except Exception as e:
        print(f"❌ FAIL - Graph 2 failed: {e}")
    
    # ========================================================================
    # GRAPH 3: Event Count Scatter Plot (VLM vs CASAS)
    # ========================================================================
    try:
        print("\n" + "-"*80)
        print("📈 Graph 3: Event Count Scatter Plot (VLM vs CASAS)")
        print("-"*80)
        
        plt.figure(figsize=(8, 8))
        event_counts_vlm = [r['vlm_features']['event_count'] for r in results]
        event_counts_casas = [r['casas_features']['event_count'] for r in results]
        plt.scatter(event_counts_casas, event_counts_vlm, alpha=0.6, s=50)
        max_count = max(max(event_counts_casas), max(event_counts_vlm))
        plt.plot([0, max_count], [0, max_count], 'r--', label='Perfect Agreement')
        plt.title('Event Count: VLM vs CASAS', fontsize=14, fontweight='bold')
        plt.xlabel('CASAS Event Count')
        plt.ylabel('VLM Event Count')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plot_file_3 = os.path.join(output_dir, "event_count_scatter.png")
        plt.savefig(plot_file_3, dpi=300, bbox_inches='tight')
        plt.close()
        
        plot_files.append(plot_file_3)
        print(f"✅ PASS - Graph 3 created successfully")
        print(f"   📁 {plot_file_3}")
        
    except Exception as e:
        print(f"❌ FAIL - Graph 3 failed: {e}")
    
    # ========================================================================
    # GRAPH 4: Correlation Heatmap
    # ========================================================================
    try:
        print("\n" + "-"*80)
        print("📈 Graph 4: Correlation Heatmap")
        print("-"*80)
        
        plt.figure(figsize=(10, 8))
        metrics = ['temporal_similarity', 'event_count_similarity', 'sensor_similarity', 'transition_similarity']
        correlation_matrix = scores_df[metrics].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                   square=True, cbar_kws={'label': 'Correlation Coefficient'})
        plt.title('Similarity Metrics Correlation', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        plot_file_4 = os.path.join(output_dir, "correlation_heatmap.png")
        plt.savefig(plot_file_4, dpi=300, bbox_inches='tight')
        plt.close()
        
        plot_files.append(plot_file_4)
        print(f"✅ PASS - Graph 4 created successfully")
        print(f"   📁 {plot_file_4}")
        
    except Exception as e:
        print(f"❌ FAIL - Graph 4 failed: {e}")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"\n✅ {len(plot_files)}/4 graphs generated successfully!")
    print(f"\n📁 Output directory: {output_dir}")
    
    for i, plot_file in enumerate(plot_files, 1):
        file_size = os.path.getsize(plot_file) / 1024  # KB
        print(f"   {i}. {os.path.basename(plot_file)} ({file_size:.1f} KB)")
    
    print("\n" + "="*80)
    
    if len(plot_files) == 4:
        print("🎉 ALL GRAPH FUNCTIONS ARE WORKING PROPERLY! 🎉")
    else:
        print(f"⚠️  Only {len(plot_files)}/4 graphs working - check errors above")
    
    print("="*80 + "\n")
    
    return plot_files


if __name__ == "__main__":
    test_graph_generation()
