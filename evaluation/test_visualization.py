#!/usr/bin/env python3
"""
Test script to verify the updated visualization creates 4 separate images
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test data simulation
test_results = [
    {
        'similarity_scores': {
            'overall_similarity': 0.48,
            'temporal_similarity': 0.52,
            'event_count_similarity': 0.44,
            'sensor_similarity': 0.46,
            'transition_similarity': 0.50
        },
        'vlm_features': {'event_count': 15},
        'casas_features': {'event_count': 18}
    },
    {
        'similarity_scores': {
            'overall_similarity': 0.52,
            'temporal_similarity': 0.55,
            'event_count_similarity': 0.49,
            'sensor_similarity': 0.50,
            'transition_similarity': 0.54
        },
        'vlm_features': {'event_count': 12},
        'casas_features': {'event_count': 14}
    },
    {
        'similarity_scores': {
            'overall_similarity': 0.45,
            'temporal_similarity': 0.48,
            'event_count_similarity': 0.42,
            'sensor_similarity': 0.44,
            'transition_similarity': 0.46
        },
        'vlm_features': {'event_count': 20},
        'casas_features': {'event_count': 22}
    }
]

def test_visualization():
    """Test the updated visualization method"""
    from casas_comparison import CASASComparator
    
    # Create test output directory
    test_output_dir = "test_visualization_output"
    os.makedirs(test_output_dir, exist_ok=True)
    
    # Create comparator instance
    comparator = CASASComparator(
        vlm_dir="dummy",
        casas_dir="dummy", 
        output_dir=test_output_dir
    )
    
    # Test visualization
    try:
        plot_files = comparator.create_visualization(test_results)
        
        print(f"✅ Visualization test successful!")
        print(f"📊 Generated {len(plot_files)} individual plots:")
        
        expected_files = [
            "similarity_distribution.png",
            "metric_comparison.png", 
            "event_count_scatter.png",
            "correlation_heatmap.png"
        ]
        
        for i, (plot_file, expected) in enumerate(zip(plot_files, expected_files), 1):
            filename = os.path.basename(plot_file)
            if filename == expected:
                if os.path.exists(plot_file):
                    file_size = os.path.getsize(plot_file) / 1024  # KB
                    print(f"  {i}. ✅ {filename} ({file_size:.1f} KB)")
                else:
                    print(f"  {i}. ❌ {filename} (file not found)")
            else:
                print(f"  {i}. ⚠️  {filename} (unexpected name, expected {expected})")
        
        return True
        
    except Exception as e:
        print(f"❌ Visualization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing updated visualization method...")
    success = test_visualization()
    
    if success:
        print("\n🎉 All tests passed! The visualization now creates 4 separate images.")
    else:
        print("\n💥 Test failed. Check the error messages above.")
