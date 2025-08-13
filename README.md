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

### Technical Features
- **Real-time LLM Integration**: OpenAI-compatible API support
- **Blender Addon System**: Seamless P-key activation in 3D viewport
- **Visual Feedback Loop**: Screenshot → LLM Analysis → Movement Commands
- **Fallback System**: Works offline with rule-based navigation
- **Game Engine Integration**: Smooth transition to Blender Game Engine

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
