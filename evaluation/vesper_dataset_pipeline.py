#!/usr/bin/env python3
"""
VESPER Dataset Generation and CASAS Comparison Suite

Complete pipeline for converting VLM evaluation logs to CASAS format
and performing comprehensive comparison with ground truth datasets.
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# Add evaluation directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vlm_to_casas_converter import VLMToCASASConverter
from casas_comparison import CASASComparator


class VESPERDatasetPipeline:
    """Complete pipeline for VESPER dataset generation and analysis"""
    
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            self.base_dir = Path(r"c:\Users\hbui11\Desktop\vesper_llm")
        else:
            self.base_dir = Path(base_dir)
        
        # Setup paths
        self.evaluation_logs_dir = self.base_dir / "blender" / "evaluation_logs"
        self.casas_ground_truth_dir = self.base_dir / "casas_testbed" / "data" / "casas_ground_truth"
        self.vesper_generated_dir = self.base_dir / "casas_testbed" / "data" / "vesper_generated"
        self.comparison_results_dir = self.base_dir / "casas_testbed" / "data" / "comparison_results"
        
        # Create directories if they don't exist
        self.vesper_generated_dir.mkdir(parents=True, exist_ok=True)
        self.comparison_results_dir.mkdir(parents=True, exist_ok=True)
    
    def convert_vlm_logs(self) -> dict:
        """Convert VLM evaluation logs to CASAS format"""
        print("🔄 Converting VLM evaluation logs to CASAS format...")
        
        converter = VLMToCASASConverter(
            str(self.evaluation_logs_dir),
            str(self.vesper_generated_dir)
        )
        
        converted_files = converter.convert_all_logs()
        summary_report = converter.generate_summary_report(converted_files)
        
        conversion_stats = {
            'total_files_converted': len(converted_files),
            'output_directory': str(self.vesper_generated_dir),
            'summary_report': summary_report,
            'converted_files': [os.path.basename(f) for f in converted_files]
        }
        
        print(f"✅ Converted {len(converted_files)} VLM logs to CASAS format")
        return conversion_stats
    
    def run_comparison_analysis(self) -> dict:
        """Run comprehensive comparison between VLM and CASAS datasets"""
        print("📊 Running comparison analysis with CASAS ground truth...")
        
        comparator = CASASComparator(
            str(self.vesper_generated_dir),
            str(self.casas_ground_truth_dir),
            str(self.comparison_results_dir)
        )
        
        results = comparator.run_comprehensive_comparison()
        
        if results:
            # Generate report and visualizations
            report_file = comparator.generate_comparison_report(results)
            plot_file = comparator.create_visualization(results)
            
            # Calculate summary statistics
            similarity_scores = [r['similarity_scores']['overall_similarity'] for r in results]
            
            analysis_stats = {
                'total_comparisons': len(results),
                'average_similarity': sum(similarity_scores) / len(similarity_scores),
                'best_similarity': max(similarity_scores),
                'worst_similarity': min(similarity_scores),
                'report_file': report_file,
                'visualization_file': plot_file,
                'output_directory': str(self.comparison_results_dir)
            }
            
            print(f"✅ Completed {len(results)} dataset comparisons")
            print(f"📈 Average similarity score: {analysis_stats['average_similarity']:.3f}")
            
            return analysis_stats
        else:
            print("❌ No comparison results generated")
            return {}
    
    def generate_research_summary(self, conversion_stats: dict, analysis_stats: dict) -> str:
        """Generate comprehensive research summary report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = self.comparison_results_dir / f"research_summary_{timestamp}.md"
        
        with open(summary_file, 'w') as f:
            f.write("# VESPER VLM Dataset Generation and CASAS Comparison\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Conversion Summary
            f.write("## Dataset Conversion Summary\n\n")
            f.write(f"- **VLM Logs Converted:** {conversion_stats.get('total_files_converted', 0)}\n")
            f.write(f"- **Output Directory:** `{conversion_stats.get('output_directory', 'N/A')}`\n")
            f.write(f"- **Source:** Blender evaluation logs from VLM navigation experiments\n\n")
            
            # Comparison Analysis
            if analysis_stats:
                f.write("## CASAS Ground Truth Comparison\n\n")
                f.write(f"- **Total Comparisons:** {analysis_stats.get('total_comparisons', 0)}\n")
                f.write(f"- **Average Similarity Score:** {analysis_stats.get('average_similarity', 0):.3f}\n")
                f.write(f"- **Best Match Similarity:** {analysis_stats.get('best_similarity', 0):.3f}\n")
                f.write(f"- **Worst Match Similarity:** {analysis_stats.get('worst_similarity', 0):.3f}\n\n")
                
                f.write("### Analysis Files Generated\n\n")
                f.write(f"- **Detailed Report:** `{os.path.basename(analysis_stats.get('report_file', ''))}`\n")
                f.write(f"- **Visualizations:** `{os.path.basename(analysis_stats.get('visualization_file', ''))}`\n\n")
            
            # Research Implications
            f.write("## Research Implications\n\n")
            f.write("### Key Findings\n\n")
            
            if analysis_stats:
                avg_sim = analysis_stats.get('average_similarity', 0)
                if avg_sim > 0.5:
                    f.write("- **High Similarity:** VLM-generated patterns show strong alignment with human behavior\n")
                elif avg_sim > 0.2:
                    f.write("- **Moderate Similarity:** VLM patterns partially match human behavior patterns\n")
                else:
                    f.write("- **Low Similarity:** VLM patterns differ significantly from human behavior\n")
                
                f.write(f"- **Behavioral Modeling:** Average similarity of {avg_sim:.3f} indicates ")
                f.write("room for improvement in VLM navigation modeling\n")
            
            f.write("- **Dataset Generation:** Successfully automated conversion from VLM logs to CASAS format\n")
            f.write("- **Comparison Framework:** Established metrics for VLM vs human behavior analysis\n\n")
            
            # Next Steps
            f.write("## Next Research Steps\n\n")
            f.write("1. **Model Improvement:** Use similarity analysis to refine VLM navigation algorithms\n")
            f.write("2. **Feature Enhancement:** Incorporate additional behavioral features for comparison\n")
            f.write("3. **Dataset Expansion:** Generate larger VLM datasets for more robust analysis\n")
            f.write("4. **Temporal Analysis:** Examine time-series patterns in navigation behavior\n")
            f.write("5. **Multi-Modal Integration:** Combine visual and sensor data for enhanced modeling\n\n")
            
            # File Locations
            f.write("## Generated Files\n\n")
            f.write(f"- **VLM Datasets:** `{self.vesper_generated_dir}`\n")
            f.write(f"- **Comparison Results:** `{self.comparison_results_dir}`\n")
            f.write(f"- **CASAS Ground Truth:** `{self.casas_ground_truth_dir}`\n")
        
        return str(summary_file)
    
    def run_complete_pipeline(self) -> dict:
        """Run the complete VESPER dataset generation and comparison pipeline"""
        print("🚀 Starting VESPER Dataset Generation and CASAS Comparison Pipeline\n")
        
        # Step 1: Convert VLM logs
        conversion_stats = self.convert_vlm_logs()
        print()
        
        # Step 2: Run comparison analysis
        analysis_stats = self.run_comparison_analysis()
        print()
        
        # Step 3: Generate research summary
        print("📋 Generating research summary...")
        summary_file = self.generate_research_summary(conversion_stats, analysis_stats)
        print(f"✅ Research summary generated: {os.path.basename(summary_file)}")
        
        # Compile final results
        pipeline_results = {
            'conversion_stats': conversion_stats,
            'analysis_stats': analysis_stats,
            'summary_file': summary_file,
            'status': 'completed',
            'timestamp': datetime.now().isoformat()
        }
        
        # Save pipeline results
        results_file = self.comparison_results_dir / "pipeline_results.json"
        with open(results_file, 'w') as f:
            json.dump(pipeline_results, f, indent=2)
        
        print(f"\n🎉 Pipeline completed successfully!")
        print(f"📁 Results saved to: {self.comparison_results_dir}")
        
        return pipeline_results


def main():
    """Main execution function with command line interface"""
    parser = argparse.ArgumentParser(description="VESPER Dataset Generation and CASAS Comparison Pipeline")
    parser.add_argument("--base-dir", help="Base directory for VESPER project", default=None)
    parser.add_argument("--convert-only", action="store_true", help="Only convert VLM logs to CASAS format")
    parser.add_argument("--compare-only", action="store_true", help="Only run comparison analysis")
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = VESPERDatasetPipeline(args.base_dir)
    
    try:
        if args.convert_only:
            pipeline.convert_vlm_logs()
        elif args.compare_only:
            pipeline.run_comparison_analysis()
        else:
            pipeline.run_complete_pipeline()
            
    except Exception as e:
        print(f"❌ Pipeline failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
