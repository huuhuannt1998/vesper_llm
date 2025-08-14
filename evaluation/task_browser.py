"""
VESPER LLM Task Browser
======================

Simple browser to explore and extract specific task lists for testing.

Usage:
    python task_browser.py --category basic_kitchen
    python task_browser.py --routine morning
    python task_browser.py --random 10
    python task_browser.py --all
"""

import argparse
import json
from datetime import datetime
from comprehensive_task_dataset import *

def browse_category(category_name: str):
    """Browse tasks in a specific category"""
    print(f"🎯 BROWSING CATEGORY: {category_name}")
    print("=" * 50)
    
    tasks = get_tasks_by_category(category_name)
    if not tasks:
        print(f"❌ Category '{category_name}' not found")
        return
    
    if isinstance(tasks[0], list):  # Routines
        print(f"📋 Found {len(tasks)} routines:")
        for i, routine in enumerate(tasks, 1):
            print(f"\\n  {i:2d}. {routine}")
    else:  # Individual tasks
        print(f"🎯 Found {len(tasks)} tasks:")
        for i, task in enumerate(tasks, 1):
            print(f"  {i:2d}. {task}")

def browse_routine_type(routine_type: str):
    """Browse routines of a specific type"""
    print(f"📋 BROWSING ROUTINE TYPE: {routine_type}")
    print("=" * 50)
    
    routine = get_routine_by_type(routine_type)
    if not routine:
        print(f"❌ Routine type '{routine_type}' not found")
        return
    
    print(f"🎯 Sample {routine_type} routine:")
    for i, task in enumerate(routine, 1):
        print(f"  {i}. {task}")

def browse_random_tasks(count: int):
    """Browse random tasks"""
    print(f"🎲 RANDOM TASKS: {count} tasks")
    print("=" * 30)
    
    tasks = get_random_tasks(count)
    for i, task in enumerate(tasks, 1):
        print(f"  {i:2d}. {task}")

def browse_all_categories():
    """Browse all available categories"""
    print("📚 ALL AVAILABLE CATEGORIES")
    print("=" * 40)
    
    all_tasks = get_all_tasks()
    
    print("\\n🎯 INDIVIDUAL TASK CATEGORIES:")
    for category, tasks in all_tasks.items():
        if "routines" not in category:
            print(f"  • {category}: {len(tasks)} tasks")
    
    print("\\n📋 ROUTINE CATEGORIES:")
    for category, routines in all_tasks.items():
        if "routines" in category:
            print(f"  • {category}: {len(routines)} routines")

def export_category(category_name: str, output_file: str):
    """Export category tasks to file"""
    tasks = get_tasks_by_category(category_name)
    if not tasks:
        print(f"❌ Category '{category_name}' not found")
        return
    
    export_data = {
        "category": category_name,
        "task_count": len(tasks),
        "tasks": tasks,
        "export_timestamp": datetime.now().isoformat()
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"✅ Exported {len(tasks)} tasks from '{category_name}' to {output_file}")

def show_task_examples():
    """Show examples from each category"""
    print("📝 TASK EXAMPLES BY CATEGORY")
    print("=" * 45)
    
    examples = {
        "basic_kitchen": "Make coffee, Get water, Cook dinner",
        "basic_living_room": "Watch TV, Turn on lights, Relax on couch", 
        "basic_bedroom": "Go to sleep, Get dressed, Make bed",
        "basic_bathroom": "Brush teeth, Take shower, Wash hands",
        "basic_office": "Work on computer, Check emails, Make phone calls",
        "basic_dining_room": "Eat dinner, Set table, Have family meal",
        "morning_routines": "Wake up → Brush teeth → Make coffee",
        "evening_routines": "Have dinner → Watch TV → Go to bed",
        "work_routines": "Get coffee → Check news → Return to work",
        "cleaning_routines": "Check kitchen → Tidy living room → Make bed",
        "cooking_tasks": "Prepare breakfast, Bake bread, Make soup",
        "maintenance_tasks": "Check smoke detectors, Test outlets, Inspect windows",
        "health_wellness_tasks": "Take vitamins, Do exercises, Meditate",
        "technology_tasks": "Check updates, Backup files, Charge devices",
        "ambiguous_tasks": "Make phone call, Read book, Take break",
        "contextual_tasks": "('It's morning', 'I need caffeine')",
        "error_inducing_tasks": "Go to garage, Fly to moon, Do something"
    }
    
    for category, example in examples.items():
        print(f"🎯 {category:20s}: {example}")

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="VESPER LLM Task Browser")
    parser.add_argument("--category", help="Browse specific category")
    parser.add_argument("--routine", help="Browse specific routine type (morning, evening, work, etc.)")
    parser.add_argument("--random", type=int, help="Show N random tasks")
    parser.add_argument("--all", action="store_true", help="Show all categories")
    parser.add_argument("--examples", action="store_true", help="Show task examples")
    parser.add_argument("--export", help="Export category to JSON file")
    parser.add_argument("--output", default="tasks_export.json", help="Output file for export")
    
    args = parser.parse_args()
    
    if args.examples:
        show_task_examples()
    elif args.all:
        browse_all_categories()
    elif args.category:
        if args.export:
            export_category(args.category, args.output)
        else:
            browse_category(args.category)
    elif args.routine:
        browse_routine_type(args.routine)
    elif args.random:
        browse_random_tasks(args.random)
    else:
        # Default: show overview
        print("🎯 VESPER LLM TASK BROWSER")
        print("=" * 30)
        print("Available commands:")
        print("  --category CATEGORY_NAME  : Browse specific category")
        print("  --routine ROUTINE_TYPE    : Browse routine type") 
        print("  --random N               : Show N random tasks")
        print("  --all                    : Show all categories")
        print("  --examples               : Show task examples")
        print("  --export --category NAME : Export category to JSON")
        print()
        print("Examples:")
        print("  python task_browser.py --category basic_kitchen")
        print("  python task_browser.py --routine morning")
        print("  python task_browser.py --random 15")
        print("  python task_browser.py --examples")

if __name__ == "__main__":
    main()
