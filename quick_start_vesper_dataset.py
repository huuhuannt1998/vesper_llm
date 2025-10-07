#!/usr/bin/env python3
"""
VESPER Dataset Quick Start Script
Demonstrates the complete workflow from generation to comparison
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Color codes for terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}\n")

def print_step(num, text):
    print(f"{Colors.BLUE}{Colors.BOLD}Step {num}: {text}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def main():
    print_header("VESPER DATASET GENERATION & CASAS COMPARISON")
    
    base_dir = Path(__file__).parent
    
    # ========================================================================
    # PART 1: SETUP VERIFICATION
    # ========================================================================
    print_header("PART 1: SETUP VERIFICATION")
    
    print_step(1, "Checking CASAS Integration")
    
    # Check casas_motion_logger.py exists
    casas_logger_file = base_dir / "blender" / "casas_motion_logger.py"
    if casas_logger_file.exists():
        print_success(f"CASAS logger exists: {casas_logger_file}")
    else:
        print_error(f"Missing CASAS logger: {casas_logger_file}")
        print("   Run: Check CASAS_INTEGRATION_COMPLETE.md for setup")
        return
    
    # Check navigation file
    nav_file = base_dir / "blender" / "llm_bge_navigation.py"
    if nav_file.exists():
        with open(nav_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "CASASMotionSensorLogger" in content:
                print_success("Navigation system has CASAS integration")
                
                if "bge.logic.casas_motion_logger = CASASMotionSensorLogger()" in content:
                    print_success("CASAS logger initialization: FOUND")
                else:
                    print_warning("CASAS logger initialization: NOT FOUND")
                    print("   Action needed: Add initialization code (see VESPER_DATASET_GENERATION_GUIDE.md)")
            else:
                print_error("Navigation system missing CASAS integration")
                return
    
    # Check ground truth data
    print_step(2, "Checking CASAS Ground Truth Data")
    
    casas_gt_dir = base_dir / "casas_testbed" / "data" / "casas_ground_truth"
    if casas_gt_dir.exists():
        # Count CSV and TXT files
        csv_files = list(casas_gt_dir.glob("**/*.csv"))
        txt_files = list(casas_gt_dir.glob("**/*.txt"))
        total_files = len(csv_files) + len(txt_files)
        
        print_success(f"Found {total_files} CASAS ground truth files")
        print(f"   Location: {casas_gt_dir}")
        if csv_files:
            print(f"   CSV format: {len(csv_files)} files")
            subdirs = set(f.parent.name for f in csv_files if f.parent != casas_gt_dir)
            if subdirs:
                print(f"   Subdirectories: {', '.join(sorted(subdirs))}")
        if txt_files:
            print(f"   TXT format: {len(txt_files)} files")
    else:
        print_warning("CASAS ground truth directory not found")
        print(f"   Expected: {casas_gt_dir}")
    
    # ========================================================================
    # PART 2: DATASET GENERATION
    # ========================================================================
    print_header("PART 2: DATASET GENERATION")
    
    print_step(3, "Running BGE Navigation (Dataset Generation)")
    print(f"{Colors.BOLD}To generate VESPER dataset:{Colors.END}")
    print(f"   {Colors.BLUE}python blender/llm_bge_navigation.py{Colors.END}")
    print()
    print("Expected output files (in casas_testbed/vesper_datasets/):")
    print("   1. vesper_casas_p01_YYYYMMDD_HHMMSS.txt     (CASAS format)")
    print("   2. vesper_metrics_p01_YYYYMMDD_HHMMSS.json  (VLM navigation logs)")
    print()
    
    # Check if data already exists
    dataset_dir = base_dir / "casas_testbed" / "vesper_datasets"
    if dataset_dir.exists():
        casas_files = list(dataset_dir.glob("vesper_casas_*.txt"))
        metrics_files = list(dataset_dir.glob("vesper_metrics_*.json"))
        
        if casas_files or metrics_files:
            print_success(f"Found existing datasets in {dataset_dir.name}/")
            if casas_files:
                latest_casas = sorted(casas_files)[-1]
                print(f"   Latest CASAS: {latest_casas.name}")
            if metrics_files:
                latest_metrics = sorted(metrics_files)[-1]
                print(f"   Latest metrics: {latest_metrics.name}")
        else:
            print_warning("No datasets found yet")
            print("   Generate by running: python blender/llm_bge_navigation.py")
    else:
        print_warning("Dataset directory will be created on first run")
    
    # ========================================================================
    # PART 3: DATA VALIDATION
    # ========================================================================
    print_header("PART 3: DATA VALIDATION")
    
    print_step(4, "Validating CASAS Format")
    
    dataset_dir = base_dir / "casas_testbed" / "vesper_datasets"
    if dataset_dir.exists():
        casas_files = list(dataset_dir.glob("vesper_casas_*.txt"))
        
        if casas_files:
            latest_casas = sorted(casas_files)[-1]
            
            try:
                # Basic validation
                with open(latest_casas, 'r') as f:
                    lines = [l.strip() for l in f if l.strip()]
                
                valid = True
                errors = []
                sensors = set()
                
                for i, line in enumerate(lines[:10]):
                    parts = line.split()
                    if len(parts) < 4:
                        valid = False
                        errors.append(f"Line {i+1}: Invalid format")
                        continue
                    
                    sensor_id = parts[2]
                    sensors.add(sensor_id)
                
                if valid and not errors:
                    print_success("CASAS format validation: PASSED")
                    print(f"   File: {latest_casas.name}")
                    print(f"   Total events: {len(lines)}")
                    print(f"   Unique sensors: {sorted(sensors)}")
                else:
                    print_warning("CASAS format has issues:")
                    for err in errors[:5]:
                        print(f"     {err}")
            
            except Exception as e:
                print_error(f"Validation failed: {e}")
        else:
            print_warning("No CASAS files to validate yet")
    else:
        print_warning("Dataset directory not created yet")
    
    # ========================================================================
    # PART 4: COMPARISON WITH GROUND TRUTH
    # ========================================================================
    print_header("PART 4: COMPARISON WITH GROUND TRUTH")
    
    print_step(5, "Running Comparison Pipeline")
    print(f"{Colors.BOLD}To compare with ground truth:{Colors.END}")
    print(f"   {Colors.BLUE}python evaluation/vesper_dataset_pipeline.py{Colors.END}")
    print()
    print("This will:")
    print("   1. Detect all CASAS files (ground truth + generated)")
    print("   2. Validate format of each file")
    print("   3. Convert VLM JSON logs to CASAS format")
    print("   4. Compare generated data with ground truth")
    print("   5. Calculate accuracy metrics:")
    print("      - Temporal accuracy (timing)")
    print("      - Spatial accuracy (location)")
    print("      - Event correlation (pattern matching)")
    
    # ========================================================================
    # PART 5: ANALYSIS & VISUALIZATION
    # ========================================================================
    print_header("PART 5: ANALYSIS & VISUALIZATION")
    
    print_step(6, "Analyzing Results")
    
    dataset_dir = base_dir / "casas_testbed" / "vesper_datasets"
    if dataset_dir.exists():
        casas_files = list(dataset_dir.glob("vesper_casas_*.txt"))
        metrics_files = list(dataset_dir.glob("vesper_metrics_*.json"))
        
        if casas_files or metrics_files:
            print(f"{Colors.BOLD}Quick analysis commands:{Colors.END}")
            print()
            
            if casas_files:
                latest_casas = sorted(casas_files)[-1]
                print(f"{Colors.BLUE}1. View CASAS data:{Colors.END}")
                print(f"   cat {latest_casas}")
                print()
            
            if metrics_files:
                latest_metrics = sorted(metrics_files)[-1]
                print(f"{Colors.BLUE}2. Analyze VLM metrics:{Colors.END}")
                print(f"""   python -c "
import json
with open('{latest_metrics}', 'r') as f:
    data = json.load(f)
print(f'Session: {{data[\"session_id\"]}}')
print(f'Tasks: {{len(data[\"tasks\"])}}')
"   """)
                print()
        else:
            print_warning("No datasets to analyze yet")
    else:
        print_warning("Dataset directory not created yet")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print_header("WORKFLOW SUMMARY")
    
    print(f"{Colors.BOLD}Complete VESPER Dataset Workflow:{Colors.END}\n")
    
    print(f"{Colors.GREEN}Phase 1: Setup (One-time){Colors.END}")
    print("   ✓ Install CASAS integration components")
    print("   ✓ Configure motion sensors in Blender")
    print("   ✓ Prepare ground truth data")
    print()
    
    print(f"{Colors.GREEN}Phase 2: Generation{Colors.END}")
    print("   1. Run: python blender/llm_bge_navigation.py")
    print("   2. Wait for tasks to complete")
    print("   3. Check: blender/vesper_motion_sensors.txt")
    print()
    
    print(f"{Colors.GREEN}Phase 3: Validation{Colors.END}")
    print("   1. Verify CASAS format")
    print("   2. Check sensor activations")
    print("   3. Review VLM metrics")
    print()
    
    print(f"{Colors.GREEN}Phase 4: Comparison{Colors.END}")
    print("   1. Run: python evaluation/vesper_dataset_pipeline.py")
    print("   2. Review accuracy metrics")
    print("   3. Analyze discrepancies")
    print()
    
    print(f"{Colors.GREEN}Phase 5: Analysis{Colors.END}")
    print("   1. Generate reports")
    print("   2. Create visualizations")
    print("   3. Iterate and improve")
    print()
    
    # ========================================================================
    # NEXT STEPS
    # ========================================================================
    print_header("NEXT STEPS")
    
    dataset_dir = base_dir / "casas_testbed" / "vesper_datasets"
    if dataset_dir.exists():
        casas_files = list(dataset_dir.glob("vesper_casas_*.txt"))
        if not casas_files:
            print(f"{Colors.YELLOW}⏭️  NEXT: Generate your first dataset{Colors.END}")
            print(f"   Run: {Colors.BLUE}python blender/llm_bge_navigation.py{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⏭️  NEXT: Compare with ground truth{Colors.END}")
            print(f"   Run: {Colors.BLUE}python evaluation/vesper_dataset_pipeline.py{Colors.END}")
    else:
        print(f"{Colors.YELLOW}⏭️  NEXT: Generate your first dataset{Colors.END}")
        print(f"   Run: {Colors.BLUE}python blender/llm_bge_navigation.py{Colors.END}")
    
    print()
    print(f"{Colors.BOLD}📚 Documentation:{Colors.END}")
    print(f"   - Full guide: VESPER_DATASET_GENERATION_GUIDE.md")
    print(f"   - CASAS setup: CASAS_INTEGRATION_COMPLETE.md")
    print(f"   - Ground truth info: CASAS_GROUND_TRUTH_INFO.md")
    print(f"   - Quick verify: python complete_casas_setup.py")
    print()
    
    print_header("Ready to Generate VESPER Datasets! 🚀")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Interrupted by user{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
