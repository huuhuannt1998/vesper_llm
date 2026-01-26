# VESPER LLM Technical Report

## 1. Executive Summary
VESPER LLM is a production-ready research platform that combines Vision Language Models (VLMs), a 3D smart home simulation, and activity-pattern analysis to evaluate embodied AI behavior in realistic environments. The system integrates Blender/UPBGE navigation, a FastAPI backend, microservices for perception and orchestration, and CASAS-compatible sensor logging to support reproducible experimentation.

## 2. Purpose and Goals
- **Embodied AI evaluation**: Measure VLM-driven navigation and task execution in a simulated smart home.
- **Smart home automation research**: Model device state changes and sensor events for ADL (Activities of Daily Living).
- **Safety-aware behavior**: Enforce and log safety constraints during agent action execution.
- **CASAS dataset generation**: Produce sensor logs compatible with CASAS testbed workflows.

## 3. System Architecture Overview
VESPER LLM is organized around the following major subsystems:

1. **3D Simulation & Navigation (Blender/UPBGE)**
   - Primary navigation and interaction runtime.
   - Coordinates with the VLM decision engine and safety enforcement.
2. **Backend API (FastAPI)**
   - Exposes REST/WebSocket endpoints for tasks, devices, simulation control, and LLM decisions.
3. **VLM Decision Engine**
   - Selects tools/actions based on visual inputs and task context.
4. **MCP Microservices**
   - Modular services for image analysis, movement, spatial reasoning, orchestration, and deployment.
5. **Smart Home & Sensor Simulation**
   - Simulated devices, motion sensors, and CASAS-formatted logging.
6. **Evaluation & Analysis**
   - Experiment runners, metrics collection, and statistical analysis utilities.

High-level directory layout (see `README.md` for the full list):
```
vesper_llm/
├── blender/                    # 3D Navigation & VLM Engine
├── backend/                   # LLM Integration & API
├── vesper_mcp/                # MCP services
├── motion_sensors/            # CASAS-compatible sensor simulation
├── evaluation/                # Evaluation framework
├── analysis/                  # Analysis utilities
├── configs/                   # Simulation/device configuration
└── virtual-interaction/       # Smart home testbed services
```

## 4. Technical Approach
### 4.1 VLM-Driven Navigation
- The Blender runtime captures visual context (first-person view and optional floorplan views).
- VLM prompts are structured to reason over the environment and propose navigation/actions.
- `blender/llm_bge_navigation.py` orchestrates action execution and environment updates.

### 4.2 Safety Enforcement Layer
- `blender/safety_enforcement.py` applies 31 safety rules spanning appliance safety, entry security, sensor integrity, spatial-temporal constraints, and task semantics.
- Two modes are supported:
  - **Baseline**: violations logged only.
  - **Enforced**: unsafe actions are blocked or modified.

### 4.3 Microservices & Orchestration
- `vesper_mcp/services/` defines MCP-compatible services (vision, movement, orchestration).
- Centralized configuration in `vlm_config.py` provides URLs, timeouts, and retry policies.

### 4.4 Smart Home & Sensor Integration
- Device definitions: `configs/devices.yaml`
- Room definitions: `configs/rooms.yaml`
- Navigation defaults: `configs/sim.yaml`
- Motion sensors generate CASAS-compatible events for evaluation and dataset generation.

### 4.5 Evaluation Workflow
- `run_eval.py`, `batch_experiment_runner.py`, and `evaluation/` scripts run trials.
- Metrics and statistical analyses are produced in `analysis/`.

## 5. Key Parameters and Configuration
### 5.1 Environment Variables (`.env.example`)
```
LLM_API_URL=http://cci-siscluster1.charlotte.edu:8080/api/chat/completions
LLM_API_KEY=<key>
LLM_MODEL=gpt-oss:120b
LLM_REQUEST_TIMEOUT=30

BACKEND_URL=http://127.0.0.1:8000
BACKEND_WS_URL=ws://127.0.0.1:8000/sim/ws
```

### 5.2 Simulation Configuration (`configs/`)
- **Devices**: `configs/devices.yaml`
  - Maps device IDs to room locations and device types.
- **Rooms**: `configs/rooms.yaml`
  - Defines room centers used for navigation.
- **Navigation**: `configs/sim.yaml`
  - `nav.default_speed`: 0.05
  - `nav.arrival_threshold`: 0.05
  - `ws.url`: WebSocket endpoint for simulation control.

### 5.3 VLM Training & Services (`vlm_config.py`)
Representative parameters (see full file for details):
- **Model**: `microsoft/DialoGPT-medium`, `max_length=512`
- **Training**: `learning_rate=5e-5`, `batch_size=8`, `num_epochs=3`
- **Services**: orchestration, navigation, vision, smart_home, task_planning
- **Rules/Rewards**: tool selection metadata and reward shaping

## 6. Primary Entry Points
| Script | Purpose |
| --- | --- |
| `backend/app/main.py` | Start FastAPI backend |
| `blender/llm_bge_navigation.py` | VLM-driven navigation in UPBGE |
| `run_eval.py` | Execute evaluation runs |
| `batch_experiment_runner.py` | Multi-trial experiment runner |
| `quick_start_vesper_dataset.py` | Dataset generation |

## 7. Development, Testing, and Tooling
Development guidance is documented in `development/README.md`. Key commands include:
```bash
pip install -r development/requirements-dev.txt
pytest tests/
black .
flake8 .
```

## 8. Outputs and Artifacts
- **Safety Logs**: `vesper_logs/safety/safety_trial_{mode}_{timestamp}.json`
- **Metrics & Analysis**: `analysis/` outputs and evaluation summaries
- **CASAS Sensor Logs**: output files generated by motion sensors and CASAS utilities

## 9. Summary
VESPER LLM delivers a cohesive research stack for testing VLM-driven embodied AI in a smart home context. It integrates simulation, API orchestration, safety enforcement, and reproducible evaluation, enabling researchers to compare navigation intelligence, safety compliance, and sensor-aligned activity patterns at scale.
