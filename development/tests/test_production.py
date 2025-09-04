#!/usr/bin/env python3
"""Quick test of the production system"""

from casas_testbed.integration import run_phone_call_evaluation

print("Testing clean production system...")
results = run_phone_call_evaluation()

if results["success"]:
    print(f"✅ Success!")
    print(f"📊 Similarity: {results['metrics'].overall_similarity:.1%}")
    print(f"📁 Dataset: {results['dataset_file']}")
    print(f"📋 Report: {results['report_file']}")
else:
    print("❌ Failed")
    print(f"Error: {results.get('error', 'Unknown error')}")
