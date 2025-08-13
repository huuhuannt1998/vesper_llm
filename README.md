# VESPER LLM - Smart House Navigation System

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Blender](https://img.shields.io/badge/blender-4.0+-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

VESPER LLM is an intelligent house navigation system that combines Large Language Models (LLM) with Blender's 3D environment to create realistic, AI-controlled actor movement through virtual house environments.

## 🚀 Features

### Core Functionality
- **🤖 LLM-Controlled Navigation**: AI determines optimal room visitation order based on tasks
- **📸 Bird's Eye View Analysis**: Real-time screenshot capture for visual feedback
- **🚶 Realistic Human Movement**: Step-by-step movement with human-like timing and pace
- **🎯 Task-Based Planning**: 6 different daily routine types (Morning, Evening, Cleaning, etc.)
- **🏠 Smart House Integration**: Pre-configured room layouts with navigation logic
- **📊 LLM Evaluation System**: Comprehensive correctness testing with 6 evaluation methods

### Technical Features
- **Real-time LLM Integration**: OpenAI-compatible API support
- **Blender Addon System**: Seamless P-key activation in 3D viewport
- **Visual Feedback Loop**: Screenshot → LLM Analysis → Movement Commands
- **Fallback System**: Works offline with rule-based navigation
- **Game Engine Integration**: Smooth transition to Blender Game Engine
- **Standalone Evaluation**: Independent LLM testing without Blender dependency

## 🏗️ Architecture

```
vesper_llm/
├── backend/                 # LLM integration and API handling
│   └── app/
│       └── llm/
│           ├── client.py    # LLM communication client
│           └── planner.py   # Task planning logic
├── blender/                 # Blender integration
│   └── addons/
│       └── vesper_tools/
│           └── __init__.py  # Main Blender addon
├── evaluation/              # LLM correctness evaluation system
│   ├── simple_evaluator.py # Standalone evaluation with 6 methods
│   ├── metrics.py          # Research metrics and statistics
│   └── quick_eval.py       # Quick evaluation runner
├── configs/                 # Configuration files
├── scripts/                 # Utility scripts
└── requirements.txt         # Python dependencies
```

## 🛠️ Installation

### Prerequisites
- **Blender 4.0+** (UPBGE recommended)
- **Python 3.8+**
- **LLM Server** (OpenAI-compatible API)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/huuhuannt1998/vesper_llm.git
   cd vesper_llm
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure LLM server**
   ```bash
   cp .env.example .env
   # Edit .env with your LLM server details
   ```

4. **Install Blender addon**
   - Open Blender
   - Go to `Edit > Preferences > Add-ons`
   - Click "Install..." and select `blender/addons/vesper_tools/__init__.py`
   - Enable "VESPER Tools" addon

## 🎮 Usage

### Basic Operation

1. **Load your house.blend file** in Blender
2. **Ensure you have an actor object** (named "Actor", "Human", or similar)
3. **Press P key** in the 3D Viewport
4. **Watch the AI-controlled navigation!**

### Expected Behavior

```
🎯 VESPER LLM NAVIGATION TRIGGERED!
📋 Selected 3 Random Tasks: ['Make coffee', 'Watch TV', 'Go to bed']
🧠 LLM Response: ["Kitchen", "LivingRoom", "Bedroom"]
🚶 Found actor: Actor at [-2.40, 1.10]

📸 Bird's eye screenshot captured
🚶 Starting realistic human movement to Kitchen
  Step 1: Actor at [-2.40, 1.10], Distance: 4.42
  📡 Movement: RIGHT (small human step)
  ...continues with realistic movement...
  🎯 Reached Kitchen in 18 steps!

🎮 Starting Game Engine...
✅ Game Engine started successfully!
```

### Room Configuration

The system supports these predefined rooms:
- **LivingRoom**: `[-2.0, 1.5]`
- **Kitchen**: `[2.0, 1.5]`
- **Bedroom**: `[-3.0, -2.0]`
- **Bathroom**: `[1.0, -2.0]`
- **DiningRoom**: `[0.0, 1.0]`
- **Office**: `[3.0, 3.0]`

## 🔧 Configuration

### LLM Server Setup

Configure your LLM server in the `.env` file:

```env
LLM_API_URL=http://your-llm-server:8080/api/chat/completions
LLM_API_KEY=your-api-key
LLM_MODEL=openai/gpt-oss-20b
LLM_REQUEST_TIMEOUT=30
LLM_MAX_TOKENS=256
```

### Movement Parameters

Adjust movement realism in the addon:
- **Step size**: `0.12` units (realistic human steps)
- **Step timing**: `0.4` seconds between steps
- **Max steps**: `25` steps per room
- **Tolerance**: `0.3` units accuracy

## 📊 Task Routines

The system includes 6 predefined daily routines:

1. **Morning Routine**: Wake up → Brush teeth → Make coffee
2. **Evening Routine**: Turn on TV → Dim lights → Go to bedroom
3. **Cleaning Routine**: Check kitchen → Tidy living room → Make bed
4. **Work Break**: Get coffee → Check TV news → Return to work area
5. **Guest Preparation**: Clean living room → Prepare coffee → Check bedroom
6. **Relaxation Time**: Turn off lights → Watch TV → Go to bed

## 🎯 API Reference

### Core Functions

#### `chat_completion(system: str, user: str) -> str`
Communicates with LLM server for task planning and navigation decisions.

#### `execute_self_contained_navigation()`
Main navigation loop with LLM integration and visual feedback.

#### `capture_birds_eye_view() -> str`
Captures top-down screenshot for visual analysis.

#### `move_actor_step_by_step(actor, target_room, target_pos)`
Executes realistic human-like movement between rooms.

## 🛡️ Error Handling

The system includes comprehensive fallback mechanisms:
- **LLM Unavailable**: Falls back to rule-based room selection
- **Screenshot Failure**: Continues with direct pathfinding
- **Movement Blocked**: Skips to next room after timeout
- **Game Engine Issues**: Continues in Edit mode

## 📊 LLM Correctness Evaluation

### Overview

VESPER includes a comprehensive **standalone evaluation system** that measures LLM correctness in navigation tasks through 6 different testing methods. This evaluation framework is perfect for research papers and system validation.

### 🔬 Evaluation Methods

The evaluation system assesses LLM performance across multiple dimensions:

1. **📍 Task-to-Room Mapping Accuracy** - Tests basic navigation understanding
2. **🗺️ Spatial Reasoning Assessment** - Evaluates logical spatial decision making
3. **📋 Multi-step Task Planning** - Measures complex sequence planning capability
4. **🧠 Context Understanding** - Tests implicit reasoning from situational context
5. **⚠️ Error Handling and Edge Cases** - Validates robustness with invalid inputs
6. **⏱️ Response Consistency and Reliability** - Ensures repeatable performance

### 🚀 Running the Evaluation

#### Quick Evaluation (Standalone)
```bash
# Navigate to evaluation directory
cd evaluation

# Run standalone evaluation (no external dependencies)
python simple_evaluator.py
```

#### Expected Output
```
🔬 VESPER LLM Navigation Evaluation
==================================================
📍 Method 1: Task-to-Room Mapping Accuracy
  Testing systematic task-to-room associations...
    ✅ 'make coffee' → Kitchen (confidence: 0.95)
    ✅ 'watch television' → LivingRoom (confidence: 0.92)
    📊 Task-Room Mapping Accuracy: 90.0%

🗺️ Method 2: Spatial Reasoning Assessment
  Testing spatial reasoning and navigation planning...
    ✅ Closest room to Kitchen for water → DiningRoom
    📊 Spatial Reasoning Accuracy: 100.0%

📋 Method 3: Multi-step Task Planning
  Testing multi-step task planning and sequencing...
    Task: Morning routine
      Predicted: ['Bedroom', 'Bathroom', 'Kitchen', 'Office']
      Expected:  ['Bedroom', 'Bathroom', 'Kitchen', 'Office']
      Similarity: 1.00
    📊 Multi-step Planning Accuracy: 84.4%

📊 LLM CORRECTNESS EVALUATION RESULTS
============================================================
🎯 Overall LLM Correctness Score: 85.0%
📍 Task Mapping Accuracy: 90.0%
🗺️ Spatial Reasoning: 100.0%
📋 Multi-step Planning: 84.4%
🧠 Context Understanding: 80.0%
⚠️ Error Handling: 83.3%
⏱️ Response Consistency: 93.3%

💡 Assessment: Good
📁 Full report saved: vesper_llm_evaluation_20250813_154305.json
```

### 📈 Research Integration

#### Generated Report Structure
```json
{
  "metadata": {
    "evaluation_type": "LLM Navigation Correctness Assessment",
    "evaluation_date": "2025-08-13T15:43:05.629462",
    "vesper_version": "2.3.0",
    "evaluation_methods": 6,
    "total_test_cases": 44
  },
  "llm_correctness_metrics": {
    "overall_correctness_score": 0.85,
    "task_mapping_accuracy": 0.90,
    "spatial_reasoning_accuracy": 1.00,
    "multi_step_planning_accuracy": 0.84,
    "context_understanding_accuracy": 0.80,
    "error_handling_rate": 0.83,
    "response_consistency": 0.93
  }
}
```

#### For Research Papers

The evaluation system provides:
- **✅ Quantitative Metrics** - Statistical validation with confidence scores
- **✅ Comprehensive Testing** - 44+ test cases across 6 different methods
- **✅ Research-Ready Data** - JSON reports with metadata and detailed results
- **✅ Reproducible Results** - Consistent evaluation framework
- **✅ Baseline Comparisons** - Performance benchmarking

### 🎯 Evaluation Test Cases

#### Task-to-Room Mapping Tests
```python
# Clear mappings
"make coffee" → Kitchen (95% confidence)
"brush teeth" → Bathroom (98% confidence)
"watch television" → LivingRoom (92% confidence)

# Ambiguous cases
"read a book" → [LivingRoom, Bedroom] (75% confidence)
"make a phone call" → [Office, LivingRoom] (72% confidence)
```

#### Spatial Reasoning Tests
- Proximity analysis: "Closest room to Kitchen for water"
- Path optimization: "Most efficient route planning"
- Activity sequences: "Morning routine spatial logic"

#### Multi-step Planning Tests
- **Morning Routine**: Bedroom → Bathroom → Kitchen → Office
- **Evening Routine**: Office → DiningRoom → LivingRoom → Bedroom
- **Work Break**: Office → Kitchen → Office
- **Guest Preparation**: Kitchen → DiningRoom → LivingRoom

### 📋 Evaluation Configuration

#### Custom Test Cases
You can extend the evaluation by modifying `simple_evaluator.py`:

```python
# Add custom task mappings
custom_tests = [
    {"task": "your_custom_task", "expected": "TargetRoom", "confidence": 0.85},
    # Add more test cases...
]
```

#### Performance Benchmarks
- **Excellent**: Overall score > 90%
- **Good**: Overall score 80-90%
- **Needs Improvement**: Overall score < 80%

### 🔧 Advanced Evaluation

#### With Real LLM Server
```python
# Configure LLM server in evaluator
LLM_SERVER = "http://cci-siscluster1.charlotte.edu:8080/api/chat/completions"
MODEL = "openai/gpt-oss-20b"

# Run evaluation with live LLM queries
python standalone_evaluator.py  # Full server integration
```

#### Batch Testing
```python
# Run multiple evaluation rounds for statistical analysis
for i in range(10):
    evaluator.run_evaluation_suite()
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Blender](https://www.blender.org/) 3D creation suite
- Powered by OpenAI-compatible LLM APIs
- Inspired by smart home automation and AI-driven navigation

---

**VESPER LLM v1.0.0** - Bringing AI intelligence to virtual house navigation 🏠🤖
