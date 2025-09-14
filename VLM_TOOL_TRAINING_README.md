# VLM Tool Selection Training System

## Overview

This comprehensive training system teaches a Visual Language Model (VLM) to intelligently choose which microservice tools to call for task completion in the VESPER environment. The system implements the complete pipeline from data collection through deployment.

## 🏗️ Architecture

### System Components

1. **Training Data Collection** (`vlm_tool_selection_training.py`)
   - Expert demonstration capture
   - Rule-based expert system
   - Context gathering from microservices
   - Reward function calculation

2. **Supervised Fine-tuning** (`vlm_finetuning_system.py`)
   - Model fine-tuning with labeled examples
   - Custom dataset implementation
   - Training pipeline with evaluation

3. **Inference Engine** (`vlm_inference_engine.py`)
   - Production inference system
   - Autonomous task solving
   - Performance metrics calculation

4. **Training Pipeline** (`vlm_training_pipeline.py`)
   - Complete orchestration of training stages
   - Automated pipeline execution
   - Comprehensive reporting

## 🎯 Training Approach

### 1. Tool Metadata Exposure

The system exposes all available microservice tools in structured prompts:

```
AVAILABLE MICROSERVICE TOOLS:

PERCEPTION TOOLS:
  - camera_service.capture_first_person_view(actor_name: str): Capture first-person view screenshot
  - image_analysis_service.analyze_room_from_image(image_path: str): Analyze image for room type

INFORMATION TOOLS:
  - spatial_service.get_current_position(actor_name: str): Get actor's current position
  - spatial_service.detect_room(actor_name: str): Detect current room

ACTION TOOLS:
  - movement_service.move_to_room(target_room: str): Move to specific room
  - movement_service.rotate_actor(rotation_change: List[float]): Rotate actor
```

### 2. Expert Demonstration Collection

The system collects labeled examples using a rule-based expert:

- **Navigation Tasks**: Position → Navigation → Verification
- **Analysis Tasks**: Capture → Analysis → Results
- **Exploration Tasks**: Survey → Rotate → Document
- **Complex Tasks**: Orchestrated multi-step sequences

### 3. Supervised Fine-tuning

Fine-tunes language models (DialoGPT, GPT-2, etc.) on collected demonstrations:

- Input: Context + Available Tools + Task Description
- Output: Tool Selection + Parameters + Reasoning
- Training: Causal language modeling with tool prediction

### 4. Reinforcement Learning (Framework)

Implements RL framework for further optimization:

- **Reward Function**: Task completion, efficiency, tool relevance
- **Policy**: VLM tool selection policy
- **Environment**: VESPER microservices environment

## 📊 Training Tasks

### Basic Tasks
- Navigate to kitchen/bedroom/bathroom
- Analyze current room
- Identify furniture objects
- Get current position
- Explore environment

### Complex Tasks
- Prepare coffee in kitchen
- Find comfortable seating
- Turn on lights in living room
- Locate and analyze bathroom
- Multi-room exploration sequences

## 🚀 Quick Start

### Prerequisites

```bash
pip install torch transformers datasets accelerate
pip install asyncio aiohttp pathlib
```

### 1. Run Complete Training Pipeline

```bash
python vlm_training_pipeline.py
```

This executes all stages:
- Data collection (expert demonstrations)
- Supervised fine-tuning
- Model evaluation
- Inference testing

### 2. Individual Stage Execution

#### Collect Training Data Only
```bash
python vlm_tool_selection_training.py
```

#### Fine-tune Model Only
```bash
python vlm_finetuning_system.py
```

#### Test Inference Only
```bash
python vlm_inference_engine.py
```

## 📈 Expected Output

### Model Prediction Format

Given context, the trained model outputs:

```
TOOL: movement_service.move_to_room
PARAMETERS: {"target_room": "kitchen", "actor_name": "Actor", "position_in_room": "center"}
REASONING: Task requires navigation to kitchen, current position is unknown, so move to target room
```

### Performance Metrics

- **Accuracy**: Percentage of correct tool predictions
- **Success Rate**: Task completion rate
- **Efficiency**: Steps per task completion
- **Confidence**: Average prediction confidence

## 🔧 Configuration

### Training Configuration

```python
FineTuningConfig(
    model_name="microsoft/DialoGPT-medium",
    max_length=1024,
    batch_size=4,
    learning_rate=5e-5,
    num_epochs=3
)
```

### Inference Configuration

```python
InferenceConfig(
    model_path="vlm_tool_model",
    temperature=0.7,
    confidence_threshold=0.7,
    max_steps=20
)
```

## 📁 Directory Structure

```
vesper_llm/
├── vlm_tool_selection_training.py    # Data collection & expert system
├── vlm_finetuning_system.py          # Supervised fine-tuning
├── vlm_inference_engine.py           # Production inference
├── vlm_training_pipeline.py          # Complete pipeline orchestration
├── vlm_training_data/                # Training data storage
│   ├── vlm_tool_training_data_*.pkl  # Collected training examples
│   └── pipeline_results_*.json       # Pipeline execution results
└── vlm_tool_model/                   # Fine-tuned model storage
    ├── pytorch_model.bin              # Model weights
    ├── config.json                    # Model configuration
    └── tokenizer.json                 # Tokenizer
```

## 🧪 Evaluation Tasks

The system evaluates on tasks not seen during training:

- Navigate to office
- Find the refrigerator  
- Analyze the dining area
- Explore upstairs rooms
- Check what's in the pantry

## 🎛️ Advanced Features

### Context-Aware Tool Selection

The VLM considers:
- Current room and position
- Available objects and devices
- Recent action history
- Task requirements and constraints
- Visual information from cameras

### Multi-Step Task Planning

Handles complex tasks requiring multiple tool calls:
1. **Information Gathering**: Position, room, visual context
2. **Planning**: Navigation paths, action sequences
3. **Execution**: Movement, interaction, verification
4. **Monitoring**: Progress tracking, error handling

### Error Recovery

Implements fallback strategies:
- Low confidence predictions → Conservative actions
- Failed tool calls → Alternative approaches
- Context mismatches → Information gathering
- Task stalling → Exploration and re-assessment

## 📊 Performance Benchmarks

### Training Metrics (Expected)
- **Data Collection**: ~200-500 examples per hour
- **Fine-tuning**: 2-4 hours on GPU for 1000 examples
- **Inference Speed**: <1 second per prediction
- **Model Accuracy**: 70-85% on held-out test set

### Task Performance (Target)
- **Simple Navigation**: 90%+ success rate
- **Room Analysis**: 85%+ accuracy
- **Complex Tasks**: 70%+ completion rate
- **Multi-step Tasks**: 60%+ success rate

## 🔄 Continuous Improvement

### Iterative Training Loop

1. **Deploy Model**: Use in VESPER environment
2. **Collect Data**: Log successful/failed interactions
3. **Augment Dataset**: Add new examples to training set
4. **Retrain Model**: Fine-tune on expanded dataset
5. **Evaluate**: Test on diverse task scenarios
6. **Deploy**: Update production model

### Active Learning

- Identify uncertain predictions (low confidence)
- Request expert demonstrations for challenging cases
- Focus training on error-prone scenarios
- Expand task coverage based on real usage

## 🚨 Troubleshooting

### Common Issues

1. **CUDA Out of Memory**
   - Reduce batch_size in FineTuningConfig
   - Use smaller model (DialoGPT-small)
   - Enable gradient accumulation

2. **Low Training Accuracy**
   - Increase training epochs
   - Check expert system logic
   - Verify data quality and diversity
   - Adjust learning rate

3. **Poor Inference Performance**
   - Lower confidence_threshold
   - Increase max_steps for complex tasks
   - Check microservice availability
   - Verify context gathering

4. **Service Connection Errors**
   - Ensure microservices are running
   - Check port configurations
   - Verify network connectivity
   - Review service health status

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🎯 Future Enhancements

1. **Multi-Modal Training**: Include image features in training
2. **Reinforcement Learning**: Implement full RL pipeline
3. **Active Learning**: Intelligent example selection
4. **Distributed Training**: Multi-GPU and multi-node support
5. **Real-time Adaptation**: Online learning from interactions
6. **Explainable AI**: Interpretable decision explanations

## 📚 References

- Microservices Architecture: `vesper_mcp/services/README.md`
- VESPER Environment: `README.md`
- CASAS Dataset Integration: `SMART_HOME_TESTING_GUIDE.md`

---

**Note**: This training system is designed to work with the VESPER microservices architecture. Ensure all services are deployed and healthy before training.
