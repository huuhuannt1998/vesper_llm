"""
Comprehensive Task Dataset for VESPER LLM Testing
================================================

This file contains an extensive collection of tasks organized by categories
for comprehensive LLM navigation testing and evaluation.

Usage:
    from comprehensive_task_dataset import get_all_tasks, get_tasks_by_category
    
    # Get all tasks
    all_tasks = get_all_tasks()
    
    # Get specific category
    morning_tasks = get_tasks_by_category("morning")
"""

import random
from typing import Dict, List, Tuple, Any

# =============================================================================
# BASIC DAILY TASKS
# =============================================================================

BASIC_KITCHEN_TASKS = [
    "Make coffee",
    "Brew tea", 
    "Get water",
    "Make breakfast",
    "Cook dinner",
    "Prepare lunch",
    "Heat up food",
    "Get a snack",
    "Wash dishes",
    "Clean the counter",
    "Check the refrigerator",
    "Make toast",
    "Boil water",
    "Use the microwave",
    "Get cooking utensils",
    "Prepare ingredients",
    "Set the table",
    "Put away groceries",
    "Make smoothie",
    "Bake something",
    "Get ice from freezer",
    "Clean the sink",
    "Check expiration dates",
    "Make salad",
    "Get plates and cups"
]

BASIC_LIVING_ROOM_TASKS = [
    "Watch TV",
    "Turn on television",
    "Change TV channel", 
    "Turn off TV",
    "Dim living room lights",
    "Turn on lights",
    "Turn off lights",
    "Sit on sofa",
    "Read a book",
    "Listen to music",
    "Check the news",
    "Relax on couch",
    "Adjust thermostat",
    "Close the curtains",
    "Open the curtains", 
    "Clean living room",
    "Vacuum the carpet",
    "Dust furniture",
    "Arrange pillows",
    "Get remote control",
    "Turn on stereo",
    "Watch a movie",
    "Play video games",
    "Tidy up living area",
    "Get comfortable blanket"
]

BASIC_BEDROOM_TASKS = [
    "Go to bed",
    "Go to sleep",
    "Wake up",
    "Get dressed",
    "Change clothes",
    "Put on pajamas",
    "Make the bed",
    "Get out of bed",
    "Open bedroom window",
    "Close bedroom window",
    "Turn on bedroom lights",
    "Turn off bedroom lights",
    "Get clothes from closet",
    "Put clothes away",
    "Set alarm clock",
    "Check the time",
    "Get shoes",
    "Put on shoes",
    "Take off shoes",
    "Organize closet",
    "Find clean clothes",
    "Get jacket",
    "Rest for a while",
    "Take a nap",
    "Read before sleep"
]

BASIC_BATHROOM_TASKS = [
    "Brush teeth",
    "Take a shower",
    "Wash hands",
    "Use the toilet",
    "Wash face",
    "Comb hair",
    "Brush hair",
    "Apply makeup",
    "Remove makeup",
    "Shave",
    "Use mouthwash",
    "Take medicine",
    "Get ready for work",
    "Get ready for bed",
    "Clean the mirror",
    "Wash towels",
    "Get clean towel",
    "Apply lotion",
    "Check appearance",
    "Use deodorant",
    "Floss teeth",
    "Take a bath",
    "Dry hair",
    "Get toiletries",
    "Clean bathroom"
]

BASIC_OFFICE_TASKS = [
    "Work on computer",
    "Check emails",
    "Make phone calls",
    "Do paperwork",
    "Study",
    "Read documents",
    "Write reports",
    "Use the printer",
    "Video conference",
    "Take work break",
    "Organize desk",
    "Get office supplies",
    "File documents",
    "Review schedules",
    "Plan meetings",
    "Research online",
    "Update calendar",
    "Backup files",
    "Clean workspace",
    "Get reference books",
    "Charge devices",
    "Set up equipment",
    "Return to work",
    "Focus on tasks",
    "Finish project"
]

BASIC_DINING_ROOM_TASKS = [
    "Eat breakfast",
    "Eat lunch", 
    "Eat dinner",
    "Have a meal",
    "Set dining table",
    "Clear the table",
    "Serve food",
    "Have family dinner",
    "Entertain guests",
    "Have coffee with friends",
    "Celebrate occasion",
    "Clean dining table",
    "Arrange chairs",
    "Get dining utensils",
    "Put away dishes",
    "Light candles",
    "Set placemats",
    "Serve drinks",
    "Have formal meal",
    "Host dinner party",
    "Prepare dining area",
    "Get tablecloth",
    "Arrange flowers",
    "Have business lunch",
    "Family gathering"
]

# =============================================================================
# ROUTINE-BASED TASK SEQUENCES
# =============================================================================

MORNING_ROUTINES = [
    # Basic morning routines
    ["Wake up", "Brush teeth", "Make coffee"],
    ["Get out of bed", "Take shower", "Get dressed", "Eat breakfast"],
    ["Wake up", "Wash face", "Make coffee", "Check emails"],
    ["Get up", "Use bathroom", "Make breakfast", "Get ready for work"],
    ["Wake up", "Brush teeth", "Get dressed", "Have coffee"],
    
    # Extended morning routines  
    ["Wake up", "Make bed", "Brush teeth", "Take shower", "Get dressed", "Make breakfast"],
    ["Get out of bed", "Open curtains", "Use bathroom", "Make coffee", "Check news"],
    ["Wake up", "Wash face", "Brush teeth", "Get dressed", "Make toast", "Read news"],
    ["Get up", "Turn on lights", "Use bathroom", "Make coffee", "Check phone", "Get ready"],
    ["Wake up", "Stretch", "Use bathroom", "Make breakfast", "Get work clothes"],
    
    # Weekend morning routines
    ["Sleep in", "Make coffee", "Read newspaper", "Have leisurely breakfast"],
    ["Wake up late", "Take long shower", "Make big breakfast", "Watch morning TV"],
    ["Get up slowly", "Make coffee", "Sit in living room", "Plan the day"],
    ["Wake up", "Make coffee", "Check weather", "Decide on activities"],
    ["Get out of bed", "Open windows", "Make breakfast", "Relax with coffee"]
]

EVENING_ROUTINES = [
    # Basic evening routines
    ["Turn on TV", "Dim living room lights", "Go to bedroom"],
    ["Have dinner", "Watch TV", "Brush teeth", "Go to bed"],
    ["Finish work", "Have dinner", "Relax", "Go to sleep"],
    ["Turn off work computer", "Have dinner", "Watch news", "Go to bedroom"],
    ["Cook dinner", "Eat dinner", "Clean up", "Watch TV", "Go to bed"],
    
    # Extended evening routines
    ["Finish work", "Cook dinner", "Eat in dining room", "Clean dishes", "Watch TV", "Go to bed"],
    ["Turn off office lights", "Have dinner", "Relax in living room", "Take shower", "Go to sleep"],
    ["Close work laptop", "Prepare dinner", "Eat dinner", "Clean kitchen", "Watch movie", "Go to bedroom"],
    ["End work day", "Have dinner", "Tidy living room", "Watch TV", "Get ready for bed"],
    ["Cook meal", "Have dinner", "Do dishes", "Relax on couch", "Brush teeth", "Go to sleep"],
    
    # Weekend evening routines
    ["Have late dinner", "Watch movie", "Have snack", "Go to bed late"],
    ["Cook special dinner", "Have wine", "Watch entertainment", "Relax", "Go to sleep"],
    ["Order takeout", "Watch TV shows", "Have dessert", "Go to bedroom"],
    ["Make fancy dinner", "Eat slowly", "Watch documentary", "Go to bed"],
    ["Have casual dinner", "Play games", "Watch late night TV", "Go to sleep"]
]

WORK_ROUTINES = [
    # Work break routines
    ["Get coffee", "Check TV news", "Return to work area"],
    ["Take break", "Get water", "Check phone", "Go back to office"],
    ["Leave office", "Get coffee", "Stretch in living room", "Return to work"],
    ["Save work", "Get snack", "Use bathroom", "Continue working"],
    ["Stop working", "Get tea", "Relax briefly", "Resume work"],
    
    # Work day routines
    ["Start work day", "Check emails", "Have coffee", "Begin tasks"],
    ["Turn on computer", "Review schedule", "Get coffee", "Start working"],
    ["Open office", "Set up workspace", "Get water", "Begin work"],
    ["Check calendar", "Prepare materials", "Get coffee", "Start meetings"],
    ["Review yesterday's work", "Plan today", "Get tea", "Begin tasks"],
    
    # End of work day
    ["Finish tasks", "Save work", "Turn off computer", "Leave office"],
    ["Complete project", "Back up files", "Organize desk", "End work day"],
    ["Send final emails", "Close programs", "Clean workspace", "Finish work"],
    ["Review completed work", "Plan tomorrow", "Turn off lights", "Leave office"],
    ["Wrap up tasks", "Update calendar", "Organize papers", "End work"]
]

CLEANING_ROUTINES = [
    # Basic cleaning
    ["Check kitchen", "Tidy living room", "Make bed"],
    ["Clean bathroom", "Vacuum living room", "Organize bedroom"],
    ["Wash dishes", "Clean counters", "Sweep floor"],
    ["Tidy bedroom", "Clean bathroom", "Vacuum carpet"],
    ["Make bed", "Clean kitchen", "Organize living room"],
    
    # Deep cleaning
    ["Clean entire kitchen", "Scrub bathroom", "Vacuum all rooms", "Dust furniture"],
    ["Wash dishes", "Clean appliances", "Scrub sink", "Mop floors"],
    ["Organize closet", "Clean mirrors", "Vacuum bedroom", "Dust surfaces"],
    ["Deep clean bathroom", "Organize kitchen", "Vacuum living room", "Clean windows"],
    ["Wash laundry", "Clean bedroom", "Organize office", "Tidy dining room"],
    
    # Quick cleanup
    ["Quick kitchen tidy", "Make bed", "Straighten living room"],
    ["Put away dishes", "Organize clothes", "Tidy bathroom"],
    ["Clear dining table", "Fluff sofa pillows", "Quick bedroom pickup"],
    ["Wipe counters", "Make bed", "Put away items"],
    ["Quick vacuum", "Tidy bedroom", "Clean bathroom sink"]
]

ENTERTAINMENT_ROUTINES = [
    # TV and media
    ["Turn on TV", "Get comfortable", "Watch show"],
    ["Choose movie", "Make popcorn", "Watch in living room"],
    ["Check TV guide", "Select program", "Relax and watch"],
    ["Turn on streaming", "Get blanket", "Watch series"],
    ["Find documentary", "Get comfortable", "Learn something new"],
    
    # Reading and relaxation
    ["Get book", "Find comfortable spot", "Read quietly"],
    ["Choose magazine", "Sit in living room", "Read articles"],
    ["Get newspaper", "Make coffee", "Read news"],
    ["Find novel", "Get cozy", "Read chapter"],
    ["Select audiobook", "Relax in bedroom", "Listen to story"],
    
    # Music and audio
    ["Turn on stereo", "Choose playlist", "Relax with music"],
    ["Get headphones", "Select music", "Listen in bedroom"],
    ["Play radio", "Listen to news", "Stay informed"],
    ["Choose podcast", "Get comfortable", "Listen and learn"],
    ["Turn on music", "Dance in living room", "Have fun"]
]

GUEST_PREPARATION = [
    # Basic guest prep
    ["Clean living room", "Prepare coffee", "Check bedroom"],
    ["Tidy house", "Prepare snacks", "Set up seating"],
    ["Clean bathroom", "Prepare guest room", "Get refreshments"],
    ["Vacuum living room", "Set dining table", "Prepare drinks"],
    ["Organize space", "Prepare food", "Check everything"],
    
    # Formal guest prep
    ["Deep clean house", "Prepare formal dinner", "Set elegant table", "Prepare guest room"],
    ["Clean all rooms", "Cook special meal", "Set up entertainment", "Prepare beverages"],
    ["Organize entire house", "Prepare multiple courses", "Decorate dining room", "Set mood"],
    ["Clean and vacuum", "Prepare appetizers", "Set up living room", "Prepare guest area"],
    ["Thorough cleaning", "Cook elaborate meal", "Set formal dining", "Prepare hospitality"],
    
    # Casual guest prep
    ["Quick tidy up", "Make coffee", "Set out snacks"],
    ["Straighten living room", "Prepare drinks", "Get comfortable seating"],
    ["Light cleaning", "Prepare casual meal", "Set relaxed atmosphere"],
    ["Basic tidying", "Get beverages ready", "Prepare casual space"],
    ["Quick organization", "Simple refreshments", "Comfortable setup"]
]

# =============================================================================
# SPECIALIZED TASK CATEGORIES
# =============================================================================

COOKING_TASKS = [
    "Prepare breakfast",
    "Cook elaborate dinner", 
    "Make quick lunch",
    "Bake bread",
    "Make soup",
    "Grill food",
    "Make salad",
    "Prepare appetizers",
    "Cook pasta",
    "Make stir-fry",
    "Bake cookies",
    "Make sandwich",
    "Prepare smoothie",
    "Cook rice",
    "Make omelet",
    "Prepare fruit salad",
    "Cook vegetables",
    "Make pancakes",
    "Prepare marinade",
    "Cook meat",
    "Make dessert",
    "Prepare snacks",
    "Cook ethnic food",
    "Make healthy meal",
    "Prepare party food"
]

MAINTENANCE_TASKS = [
    "Check smoke detectors",
    "Test electrical outlets",
    "Check plumbing",
    "Inspect windows",
    "Check heating system",
    "Test air conditioning",
    "Check door locks",
    "Inspect bathroom fixtures",
    "Check kitchen appliances",
    "Test light switches",
    "Check for leaks",
    "Inspect flooring",
    "Check ventilation",
    "Test security system",
    "Check insulation",
    "Inspect roof area",
    "Check weather sealing",
    "Test emergency systems",
    "Check storage areas",
    "Inspect outdoor areas",
    "Check utility connections",
    "Test backup systems",
    "Check safety equipment",
    "Inspect structural elements",
    "Check maintenance schedule"
]

HEALTH_WELLNESS_TASKS = [
    "Take vitamins",
    "Do morning exercises",
    "Practice yoga",
    "Take medication",
    "Stretch muscles",
    "Do breathing exercises",
    "Meditate quietly",
    "Take health measurements",
    "Do physical therapy",
    "Practice relaxation",
    "Take breaks from work",
    "Drink water regularly",
    "Eat healthy snacks",
    "Check blood pressure",
    "Do eye exercises",
    "Practice mindfulness",
    "Take supplements",
    "Do light cardio",
    "Practice balance",
    "Do strength exercises",
    "Take mental breaks",
    "Practice good posture",
    "Do flexibility work",
    "Take deep breaths",
    "Practice stress relief"
]

TECHNOLOGY_TASKS = [
    "Check computer updates",
    "Backup important files",
    "Charge electronic devices",
    "Test internet connection",
    "Update software",
    "Check email security",
    "Clean computer screen",
    "Organize digital files",
    "Check device batteries",
    "Update passwords",
    "Test video calls",
    "Check printer supplies",
    "Sync devices",
    "Update apps",
    "Check cloud storage",
    "Test smart home devices",
    "Configure settings",
    "Check security cameras",
    "Update entertainment systems",
    "Test audio equipment",
    "Check network settings",
    "Update streaming services",
    "Test remote controls",
    "Check device connections",
    "Update system preferences"
]

SEASONAL_TASKS = [
    # Spring tasks
    "Open windows for fresh air",
    "Change to lighter clothes",
    "Clean winter items",
    "Prepare for warmer weather",
    "Check air conditioning",
    
    # Summer tasks  
    "Keep house cool",
    "Prepare cold drinks",
    "Use fans for cooling",
    "Wear summer clothes",
    "Take cool showers",
    
    # Fall tasks
    "Prepare for cooler weather",
    "Get warmer clothes ready",
    "Check heating system",
    "Prepare for shorter days",
    "Organize seasonal items",
    
    # Winter tasks
    "Keep house warm",
    "Wear warm clothes",
    "Make hot drinks",
    "Use heating efficiently",
    "Prepare for cold weather"
]

# =============================================================================
# COMPLEX MULTI-ROOM TASK SEQUENCES
# =============================================================================

COMPLEX_ROUTINES = [
    # Long morning routine
    ["Wake up in bedroom", "Use bathroom", "Take shower", "Get dressed", "Go to kitchen", 
     "Make coffee", "Prepare breakfast", "Eat in dining room", "Clean dishes", 
     "Go to office", "Start work day"],
     
    # Comprehensive evening routine
    ["Finish work in office", "Turn off computer", "Go to kitchen", "Prepare dinner", 
     "Set dining table", "Eat dinner", "Clean kitchen", "Go to living room", 
     "Watch TV", "Relax", "Go to bathroom", "Brush teeth", "Go to bedroom", "Sleep"],
     
    # Weekend cleaning routine
    ["Start in bedroom", "Make bed", "Organize closet", "Go to bathroom", "Deep clean", 
     "Go to kitchen", "Clean appliances", "Go to living room", "Vacuum and dust", 
     "Go to dining room", "Clean and organize", "Go to office", "Organize workspace"],
     
    # Hosting guests routine
    ["Clean bedroom for guests", "Prepare guest bathroom", "Go to kitchen", "Prepare appetizers",
     "Set up dining room", "Go to living room", "Arrange seating", "Prepare entertainment", 
     "Go to kitchen", "Finish cooking", "Serve guests", "Clean up"],
     
    # Work from home routine
    ["Wake up in bedroom", "Quick bathroom visit", "Go to kitchen", "Make coffee", 
     "Quick breakfast", "Go to office", "Set up workspace", "Work morning session", 
     "Go to kitchen", "Make lunch", "Eat in dining room", "Return to office", 
     "Work afternoon", "End work day", "Relax in living room"],
     
    # Sick day routine
    ["Stay in bedroom", "Rest", "Go to bathroom as needed", "Go to kitchen", 
     "Make tea", "Get light snacks", "Return to bedroom", "Rest more", 
     "Take medication", "Stay comfortable", "Monitor health"]
]

# =============================================================================
# AMBIGUOUS AND CHALLENGING TASKS
# =============================================================================

AMBIGUOUS_TASKS = [
    # Tasks that could be done in multiple rooms
    "Make a phone call",  # Office, Living room, Bedroom
    "Read a book",        # Living room, Bedroom, Office
    "Listen to music",    # Any room
    "Check the weather",  # Any room with device
    "Take a break",       # Living room, Bedroom
    "Have a snack",       # Kitchen, Dining room, Living room
    "Write something",    # Office, Dining room, Bedroom
    "Plan activities",    # Office, Living room, Dining room
    "Organize items",     # Any room
    "Take medicine",      # Bathroom, Kitchen, Bedroom
    "Check messages",     # Office, Living room, Bedroom
    "Do stretching",      # Living room, Bedroom, Office
    "Practice hobby",     # Office, Living room, Bedroom
    "Video chat",         # Office, Living room, Bedroom
    "Take photos",        # Any room
    
    # Vague or unclear tasks
    "Do something productive",
    "Get comfortable",
    "Prepare for later",
    "Handle important stuff",
    "Take care of things",
    "Get organized",
    "Make improvements",
    "Deal with issues",
    "Get things done",
    "Make progress",
    "Handle priorities",
    "Take care of business",
    "Address concerns",
    "Make arrangements",
    "Handle responsibilities"
]

CONTEXTUAL_TASKS = [
    # Time-based contexts
    ("It's 6 AM", "I need to start my day"),
    ("It's noon", "I need lunch"),
    ("It's 8 PM", "I want to relax"),
    ("It's bedtime", "I need to wind down"),
    ("It's morning", "I need caffeine"),
    
    # Situation-based contexts  
    ("I just woke up", "I need to get ready"),
    ("I finished work", "I want to unwind"),
    ("I'm hungry", "I need food"),
    ("I'm tired", "I need rest"),
    ("I'm cold", "I need warmth"),
    
    # Activity-based contexts
    ("After cooking", "I should clean up"),
    ("Before bed", "I need to prepare"),
    ("Before guests arrive", "I should prepare"),
    ("After eating", "I should clean"),
    ("Before work", "I need to get ready"),
    
    # Mood-based contexts
    ("I'm stressed", "I need relaxation"),
    ("I'm excited", "I want to celebrate"),
    ("I'm bored", "I need entertainment"), 
    ("I'm focused", "I want to be productive"),
    ("I'm social", "I want to connect with others")
]

ERROR_INDUCING_TASKS = [
    # Non-existent rooms
    "Go to the garage",
    "Visit the basement", 
    "Check the attic",
    "Go to the balcony",
    "Visit the shed",
    
    # Impossible tasks
    "Fly to another room",
    "Teleport to kitchen",
    "Walk through walls",
    "Go outside the house",
    "Visit another building",
    
    # Empty or nonsense input
    "",
    "asdf qwerty",
    "123 456 789",
    "Lorem ipsum dolor",
    "Random gibberish text",
    
    # Overly vague tasks
    "Do something",
    "Go somewhere",
    "Handle it",
    "Take care of that",
    "Do the thing"
]

# =============================================================================
# TASK ORGANIZATION AND ACCESS FUNCTIONS
# =============================================================================

ALL_TASK_CATEGORIES = {
    "basic_kitchen": BASIC_KITCHEN_TASKS,
    "basic_living_room": BASIC_LIVING_ROOM_TASKS,
    "basic_bedroom": BASIC_BEDROOM_TASKS,
    "basic_bathroom": BASIC_BATHROOM_TASKS,
    "basic_office": BASIC_OFFICE_TASKS,
    "basic_dining_room": BASIC_DINING_ROOM_TASKS,
    
    "morning_routines": MORNING_ROUTINES,
    "evening_routines": EVENING_ROUTINES,
    "work_routines": WORK_ROUTINES,
    "cleaning_routines": CLEANING_ROUTINES,
    "entertainment_routines": ENTERTAINMENT_ROUTINES,
    "guest_preparation": GUEST_PREPARATION,
    
    "cooking_tasks": COOKING_TASKS,
    "maintenance_tasks": MAINTENANCE_TASKS,
    "health_wellness_tasks": HEALTH_WELLNESS_TASKS,
    "technology_tasks": TECHNOLOGY_TASKS,
    "seasonal_tasks": SEASONAL_TASKS,
    
    "complex_routines": COMPLEX_ROUTINES,
    "ambiguous_tasks": AMBIGUOUS_TASKS,
    "contextual_tasks": CONTEXTUAL_TASKS,
    "error_inducing_tasks": ERROR_INDUCING_TASKS
}

def get_all_tasks() -> Dict[str, List]:
    """Get all task categories and their tasks"""
    return ALL_TASK_CATEGORIES

def get_tasks_by_category(category: str) -> List:
    """Get tasks from a specific category"""
    return ALL_TASK_CATEGORIES.get(category, [])

def get_random_tasks(count: int = 3, category: str = None) -> List:
    """Get random tasks from all categories or a specific category"""
    if category:
        if category in ALL_TASK_CATEGORIES:
            tasks = ALL_TASK_CATEGORIES[category]
            if isinstance(tasks[0], list):  # For routine categories
                return random.choices(tasks, k=min(count, len(tasks)))
            else:  # For individual task categories
                return random.choices(tasks, k=min(count, len(tasks)))
        else:
            print(f"⚠️ Category '{category}' not found")
            return []
    else:
        # Get random tasks from all individual task categories (not routines)
        individual_task_categories = [
            "basic_kitchen", "basic_living_room", "basic_bedroom", 
            "basic_bathroom", "basic_office", "basic_dining_room",
            "cooking_tasks", "maintenance_tasks", "health_wellness_tasks",
            "technology_tasks", "seasonal_tasks", "ambiguous_tasks"
        ]
        
        all_individual_tasks = []
        for cat in individual_task_categories:
            all_individual_tasks.extend(ALL_TASK_CATEGORIES[cat])
        
        return random.choices(all_individual_tasks, k=count)

def get_routine_by_type(routine_type: str) -> List:
    """Get a random routine of a specific type"""
    routine_categories = {
        "morning": "morning_routines",
        "evening": "evening_routines", 
        "work": "work_routines",
        "cleaning": "cleaning_routines",
        "entertainment": "entertainment_routines",
        "guest": "guest_preparation",
        "complex": "complex_routines"
    }
    
    if routine_type in routine_categories:
        category = routine_categories[routine_type]
        routines = ALL_TASK_CATEGORIES[category]
        return random.choice(routines)
    else:
        print(f"⚠️ Routine type '{routine_type}' not found")
        return []

def get_challenging_tasks(count: int = 5) -> List:
    """Get challenging tasks for advanced testing"""
    challenging_categories = ["ambiguous_tasks", "contextual_tasks", "error_inducing_tasks"]
    challenging_tasks = []
    
    for category in challenging_categories:
        challenging_tasks.extend(ALL_TASK_CATEGORIES[category])
    
    return random.choices(challenging_tasks, k=count)

def print_task_statistics():
    """Print statistics about the task dataset"""
    print("📊 COMPREHENSIVE TASK DATASET STATISTICS")
    print("=" * 50)
    
    total_individual_tasks = 0
    total_routines = 0
    
    for category, tasks in ALL_TASK_CATEGORIES.items():
        if "routines" in category:
            total_routines += len(tasks)
            print(f"📋 {category}: {len(tasks)} routines")
        else:
            total_individual_tasks += len(tasks)
            print(f"🎯 {category}: {len(tasks)} tasks")
    
    print(f"\n📊 SUMMARY:")
    print(f"   Individual Tasks: {total_individual_tasks}")
    print(f"   Task Routines: {total_routines}")
    print(f"   Total Categories: {len(ALL_TASK_CATEGORIES)}")
    print(f"   Total Dataset Size: {total_individual_tasks + total_routines}")

def create_test_suite(size: str = "medium") -> Dict[str, List]:
    """Create a comprehensive test suite for evaluation"""
    test_suites = {
        "small": {
            "individual_tasks": 20,
            "routines": 5,
            "challenging": 3
        },
        "medium": {
            "individual_tasks": 50,
            "routines": 10,
            "challenging": 8
        },
        "large": {
            "individual_tasks": 100,
            "routines": 20,
            "challenging": 15
        },
        "comprehensive": {
            "individual_tasks": 200,
            "routines": 35,
            "challenging": 25
        }
    }
    
    if size not in test_suites:
        size = "medium"
    
    config = test_suites[size]
    
    # Create test suite
    test_suite = {
        "basic_tasks": get_random_tasks(config["individual_tasks"]),
        "routine_tasks": [],
        "challenging_tasks": get_challenging_tasks(config["challenging"])
    }
    
    # Add random routines from different categories
    routine_types = ["morning", "evening", "work", "cleaning", "entertainment"]
    for _ in range(config["routines"]):
        routine_type = random.choice(routine_types)
        routine = get_routine_by_type(routine_type)
        test_suite["routine_tasks"].append({
            "type": routine_type,
            "tasks": routine
        })
    
    return test_suite

# =============================================================================
# MAIN EXECUTION AND TESTING
# =============================================================================

def main():
    """Main function to demonstrate the task dataset"""
    print("🎯 VESPER LLM COMPREHENSIVE TASK DATASET")
    print("=" * 45)
    
    # Print statistics
    print_task_statistics()
    
    print(f"\n🔍 SAMPLE TASKS BY CATEGORY:")
    print("-" * 30)
    
    # Show samples from each category
    sample_categories = [
        "basic_kitchen", "basic_living_room", "morning_routines", 
        "evening_routines", "ambiguous_tasks"
    ]
    
    for category in sample_categories:
        tasks = get_tasks_by_category(category)
        if tasks:
            if isinstance(tasks[0], list):  # Routines
                sample = random.choice(tasks)
                print(f"📋 {category}: {sample}")
            else:  # Individual tasks
                samples = random.choices(tasks, k=3)
                print(f"🎯 {category}: {samples}")
    
    print(f"\n🧪 SAMPLE TEST SUITE (MEDIUM):")
    print("-" * 25)
    
    # Create and display a sample test suite
    test_suite = create_test_suite("medium")
    print(f"📊 Basic Tasks: {len(test_suite['basic_tasks'])} tasks")
    print(f"📊 Routine Tasks: {len(test_suite['routine_tasks'])} routines")
    print(f"📊 Challenging Tasks: {len(test_suite['challenging_tasks'])} tasks")
    
    # Show some samples
    print(f"\n📝 Sample Basic Tasks:")
    for task in test_suite['basic_tasks'][:5]:
        print(f"   • {task}")
    
    print(f"\n📝 Sample Routine:")
    if test_suite['routine_tasks']:
        sample_routine = test_suite['routine_tasks'][0]
        print(f"   Type: {sample_routine['type']}")
        print(f"   Tasks: {sample_routine['tasks']}")
    
    print(f"\n📝 Sample Challenging Tasks:")
    for task in test_suite['challenging_tasks'][:3]:
        if isinstance(task, tuple):
            print(f"   • Context: {task[0]} → Task: {task[1]}")
        else:
            print(f"   • {task}")

if __name__ == "__main__":
    main()
