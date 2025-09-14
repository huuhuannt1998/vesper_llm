"""
VLM Tool Selection Training System
=================================

Comprehensive training framework for teaching a Visual Language Model to choose
the correct microservice tools for task completion in the VESPER environment.

This system implements:
1. Tool metadata exposure in prompts
2. Labeled example collection
3. Supervised fine-tuning
4. Reinforcement learning with reward functions
5. Orchestration service integration
"""

import asyncio
import json
import os
import time
import logging
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
import pickle
import random
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import VESPER services
try:
    from vesper_mcp.services import SERVICES, get_service_url
    from vesper_mcp.services.orchestration_service import ServiceManager
    SERVICES_AVAILABLE = True
except ImportError:
    SERVICES_AVAILABLE = False
    logger.warning("VESPER microservices not available")

@dataclass
class ToolMetadata:
    """Metadata for a microservice tool"""
    service_name: str
    tool_name: str
    description: str
    parameters: Dict[str, Any]
    return_type: str
    category: str
    complexity: int  # 1-5, higher = more complex
    prerequisites: List[str]  # Other tools that should be called first

@dataclass
class ContextState:
    """Current state context for VLM decision making"""
    task_description: str
    current_room: str
    actor_position: List[float]
    actor_rotation: List[float]
    visible_objects: List[str]
    recent_actions: List[str]
    first_person_image_path: Optional[str]
    bird_eye_image_path: Optional[str]
    spatial_context: Dict[str, Any]
    device_states: Dict[str, Any]
    task_progress: Dict[str, Any]
    timestamp: float

@dataclass
class ToolInvocation:
    """A tool call with parameters"""
    service_name: str
    tool_name: str
    parameters: Dict[str, Any]
    expected_outcome: str
    reasoning: str

@dataclass
class TrainingExample:
    """A single training example for VLM tool selection"""
    context_state: ContextState
    correct_tool_invocation: ToolInvocation
    alternative_tools: List[ToolInvocation]  # Wrong choices for negative examples
    reward_score: float
    completion_step: int  # Step number in task sequence
    example_id: str

class VLMToolTrainingSystem:
    """Main training system for VLM tool selection"""
    
    def __init__(self, data_dir: str = "vlm_training_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Training data storage
        self.training_examples = []
        self.tool_metadata = {}
        self.task_sequences = {}
        
        # Service manager for orchestration
        self.service_manager = ServiceManager() if SERVICES_AVAILABLE else None
        
        # Initialize tool metadata
        self._initialize_tool_metadata()
        
        # Reward function parameters
        self.reward_config = {
            "task_completion": 10.0,
            "efficient_action": 1.0,
            "irrelevant_tool": -1.0,
            "redundant_action": -0.5,
            "step_penalty": -0.01,
            "context_mismatch": -2.0
        }
    
    def _initialize_tool_metadata(self):
        """Initialize metadata for all available microservice tools"""
        
        # Camera Service Tools
        self.tool_metadata.update({
            "camera_service.setup_first_person_camera": ToolMetadata(
                service_name="camera",
                tool_name="setup_first_person_camera",
                description="Initialize first-person camera for the actor",
                parameters={"actor_name": "str"},
                return_type="Dict[str, Any]",
                category="setup",
                complexity=1,
                prerequisites=[]
            ),
            "camera_service.capture_first_person_view": ToolMetadata(
                service_name="camera",
                tool_name="capture_first_person_view",
                description="Capture first-person view screenshot from actor's perspective",
                parameters={"actor_name": "str", "filename": "Optional[str]", "resolution_x": "int", "resolution_y": "int"},
                return_type="Dict[str, Any]",
                category="perception",
                complexity=2,
                prerequisites=["camera_service.setup_first_person_camera"]
            ),
            "camera_service.get_camera_info": ToolMetadata(
                service_name="camera",
                tool_name="get_camera_info",
                description="Get current first-person camera information and status",
                parameters={"actor_name": "str"},
                return_type="Dict[str, Any]",
                category="information",
                complexity=1,
                prerequisites=[]
            )
        })
        
        # Image Analysis Service Tools
        self.tool_metadata.update({
            "image_analysis_service.analyze_room_from_image": ToolMetadata(
                service_name="image_analysis",
                tool_name="analyze_room_from_image",
                description="Analyze an image to determine room type and identify objects",
                parameters={"image_path": "str", "detailed_analysis": "bool"},
                return_type="Dict[str, Any]",
                category="perception",
                complexity=3,
                prerequisites=["camera_service.capture_first_person_view"]
            ),
            "image_analysis_service.identify_furniture_objects": ToolMetadata(
                service_name="image_analysis",
                tool_name="identify_furniture_objects",
                description="Identify specific furniture objects in an image",
                parameters={"image_path": "str", "target_objects": "Optional[List[str]]"},
                return_type="Dict[str, Any]",
                category="perception",
                complexity=3,
                prerequisites=["camera_service.capture_first_person_view"]
            )
        })
        
        # Spatial Service Tools
        self.tool_metadata.update({
            "spatial_service.get_current_position": ToolMetadata(
                service_name="spatial",
                tool_name="get_current_position",
                description="Get the current 3D position of the specified actor",
                parameters={"actor_name": "str"},
                return_type="Dict[str, Any]",
                category="information",
                complexity=1,
                prerequisites=[]
            ),
            "spatial_service.detect_room": ToolMetadata(
                service_name="spatial",
                tool_name="detect_room",
                description="Detect which room a position is in",
                parameters={"position": "Optional[List[float]]", "actor_name": "str"},
                return_type="Dict[str, Any]",
                category="information",
                complexity=2,
                prerequisites=[]
            ),
            "spatial_service.get_navigation_context": ToolMetadata(
                service_name="spatial",
                tool_name="get_navigation_context",
                description="Get comprehensive navigation context for the actor",
                parameters={"actor_name": "str", "target_room": "Optional[str]"},
                return_type="Dict[str, Any]",
                category="planning",
                complexity=3,
                prerequisites=[]
            )
        })
        
        # Movement Service Tools
        self.tool_metadata.update({
            "movement_service.move_actor_to_position": ToolMetadata(
                service_name="movement",
                tool_name="move_actor_to_position",
                description="Move actor to a specific 3D position",
                parameters={"target_position": "List[float]", "actor_name": "str", "movement_speed": "Optional[float]", "check_collisions": "bool"},
                return_type="Dict[str, Any]",
                category="action",
                complexity=3,
                prerequisites=["spatial_service.get_current_position"]
            ),
            "movement_service.move_to_room": ToolMetadata(
                service_name="movement",
                tool_name="move_to_room",
                description="Move actor to a specific room",
                parameters={"target_room": "str", "actor_name": "str", "position_in_room": "str"},
                return_type="Dict[str, Any]",
                category="action",
                complexity=4,
                prerequisites=["spatial_service.detect_room"]
            ),
            "movement_service.rotate_actor": ToolMetadata(
                service_name="movement",
                tool_name="rotate_actor",
                description="Rotate actor by specified angles",
                parameters={"rotation_change": "List[float]", "actor_name": "str", "absolute_rotation": "bool"},
                return_type="Dict[str, Any]",
                category="action",
                complexity=2,
                prerequisites=[]
            )
        })
        
        # Orchestration Service Tools
        self.tool_metadata.update({
            "orchestration_service.vlm_navigation_guidance": ToolMetadata(
                service_name="orchestration",
                tool_name="vlm_navigation_guidance",
                description="Get comprehensive VLM navigation guidance for a task",
                parameters={"task_description": "str", "actor_name": "str", "include_visual_analysis": "bool"},
                return_type="Dict[str, Any]",
                category="guidance",
                complexity=5,
                prerequisites=["spatial_service.get_current_position", "camera_service.capture_first_person_view"]
            ),
            "orchestration_service.execute_coordinated_action": ToolMetadata(
                service_name="orchestration",
                tool_name="execute_coordinated_action",
                description="Execute a coordinated action across multiple services",
                parameters={"action_type": "str", "action_params": "Dict[str, Any]", "actor_name": "str"},
                return_type="Dict[str, Any]",
                category="action",
                complexity=5,
                prerequisites=[]
            )
        })
    
    def generate_tool_list_prompt(self) -> str:
        """Generate a prompt section listing all available tools"""
        
        tool_sections = {
            "PERCEPTION TOOLS": [],
            "INFORMATION TOOLS": [],
            "PLANNING TOOLS": [],
            "ACTION TOOLS": [],
            "SETUP TOOLS": [],
            "GUIDANCE TOOLS": []
        }
        
        # Categorize tools
        for tool_id, metadata in self.tool_metadata.items():
            category_map = {
                "perception": "PERCEPTION TOOLS",
                "information": "INFORMATION TOOLS", 
                "planning": "PLANNING TOOLS",
                "action": "ACTION TOOLS",
                "setup": "SETUP TOOLS",
                "guidance": "GUIDANCE TOOLS"
            }
            
            category_key = category_map.get(metadata.category, "INFORMATION TOOLS")
            
            # Format parameters
            params_str = ", ".join([f"{k}: {v}" for k, v in metadata.parameters.items()])
            
            tool_desc = f"  - {tool_id}({params_str}): {metadata.description}"
            if metadata.prerequisites:
                tool_desc += f" [Requires: {', '.join(metadata.prerequisites)}]"
            
            tool_sections[category_key].append(tool_desc)
        
        # Build prompt
        prompt_parts = ["AVAILABLE MICROSERVICE TOOLS:\n"]
        
        for section_name, tools in tool_sections.items():
            if tools:
                prompt_parts.append(f"\n{section_name}:")
                prompt_parts.extend(tools)
        
        return "\n".join(prompt_parts)
    
    async def collect_expert_demonstration(self, task_description: str, actor_name: str = "Actor") -> List[TrainingExample]:
        """Collect expert demonstration for a task"""
        
        logger.info(f"Collecting expert demonstration for task: {task_description}")
        
        examples = []
        step_count = 0
        task_completed = False
        
        while not task_completed and step_count < 20:  # Maximum 20 steps
            # Gather current context
            context = await self._gather_current_context(task_description, actor_name)
            
            # Get expert action for this context
            expert_action = await self._get_expert_action(context, task_description, step_count)
            
            if expert_action is None:
                logger.warning("Expert action not available, stopping demonstration")
                break
            
            # Create training example
            example = TrainingExample(
                context_state=context,
                correct_tool_invocation=expert_action,
                alternative_tools=await self._generate_alternative_actions(context, expert_action),
                reward_score=await self._calculate_reward(context, expert_action, task_description),
                completion_step=step_count,
                example_id=f"{task_description}_{step_count}_{int(time.time())}"
            )
            
            examples.append(example)
            
            # Execute the expert action (if services available)
            if self.service_manager:
                result = await self._execute_tool_invocation(expert_action)
                logger.info(f"Step {step_count}: {expert_action.tool_name} -> {result.get('success', False)}")
            
            step_count += 1
            
            # Check if task is completed (simplified check)
            if "complete" in expert_action.expected_outcome.lower() or step_count >= 15:
                task_completed = True
        
        logger.info(f"Collected {len(examples)} training examples for task: {task_description}")
        return examples
    
    async def _gather_current_context(self, task_description: str, actor_name: str) -> ContextState:
        """Gather current context state from all services"""
        
        context = ContextState(
            task_description=task_description,
            current_room="unknown",
            actor_position=[0.0, 0.0, 0.0],
            actor_rotation=[0.0, 0.0, 0.0],
            visible_objects=[],
            recent_actions=[],
            first_person_image_path=None,
            bird_eye_image_path=None,
            spatial_context={},
            device_states={},
            task_progress={},
            timestamp=time.time()
        )
        
        if not self.service_manager:
            return context
        
        try:
            # Get spatial context
            spatial_result = await self.service_manager.call_service(
                "spatial", "get_current_position", actor_name=actor_name
            )
            
            if spatial_result.get("success"):
                context.actor_position = [
                    spatial_result["position"]["x"],
                    spatial_result["position"]["y"], 
                    spatial_result["position"]["z"]
                ]
                context.actor_rotation = [
                    spatial_result["rotation"]["x"],
                    spatial_result["rotation"]["y"],
                    spatial_result["rotation"]["z"]
                ]
                context.current_room = spatial_result["spatial_context"].get("current_room", "unknown")
                context.spatial_context = spatial_result["spatial_context"]
            
            # Capture current view
            camera_result = await self.service_manager.call_service(
                "camera", "capture_first_person_view", actor_name=actor_name
            )
            
            if camera_result.get("success"):
                context.first_person_image_path = camera_result.get("filepath")
                
                # Analyze the image
                if context.first_person_image_path:
                    analysis_result = await self.service_manager.call_service(
                        "image_analysis", "analyze_room_from_image",
                        image_path=context.first_person_image_path
                    )
                    
                    if analysis_result.get("success"):
                        detected_objects = analysis_result["analysis"].get("detected_objects", [])
                        context.visible_objects = [obj["object"] for obj in detected_objects]
        
        except Exception as e:
            logger.warning(f"Error gathering context: {str(e)}")
        
        return context
    
    async def _get_expert_action(self, context: ContextState, task_description: str, step: int) -> Optional[ToolInvocation]:
        """Get expert action based on context and task - implements rule-based expert"""
        
        # Rule-based expert system for different tasks
        task_lower = task_description.lower()
        
        # Navigation tasks
        if "navigate to" in task_lower or "go to" in task_lower:
            target_room = None
            for room in ["kitchen", "bedroom", "bathroom", "living_room", "dining_room"]:
                if room in task_lower:
                    target_room = room
                    break
            
            if target_room:
                if step == 0:
                    # First, get current position
                    return ToolInvocation(
                        service_name="spatial",
                        tool_name="get_current_position",
                        parameters={"actor_name": "Actor"},
                        expected_outcome="Get current position and spatial context",
                        reasoning="Need to know current location before navigation"
                    )
                elif step == 1:
                    # Then move to target room
                    return ToolInvocation(
                        service_name="movement",
                        tool_name="move_to_room",
                        parameters={"target_room": target_room, "actor_name": "Actor", "position_in_room": "center"},
                        expected_outcome=f"Move to {target_room}",
                        reasoning=f"Navigate to the target room: {target_room}"
                    )
                elif step == 2:
                    # Capture view to verify arrival
                    return ToolInvocation(
                        service_name="camera",
                        tool_name="capture_first_person_view",
                        parameters={"actor_name": "Actor"},
                        expected_outcome="Capture current view for verification",
                        reasoning="Verify successful navigation to target room"
                    )
        
        # Room analysis tasks
        elif "analyze" in task_lower or "identify" in task_lower:
            if step == 0:
                return ToolInvocation(
                    service_name="camera",
                    tool_name="capture_first_person_view",
                    parameters={"actor_name": "Actor"},
                    expected_outcome="Capture current view for analysis",
                    reasoning="Need current view to analyze room content"
                )
            elif step == 1 and context.first_person_image_path:
                return ToolInvocation(
                    service_name="image_analysis",
                    tool_name="analyze_room_from_image",
                    parameters={"image_path": context.first_person_image_path, "detailed_analysis": True},
                    expected_outcome="Complete room analysis with object detection",
                    reasoning="Analyze captured image to identify room type and objects"
                )
        
        # Exploration tasks
        elif "explore" in task_lower or "look around" in task_lower:
            if step == 0:
                return ToolInvocation(
                    service_name="spatial",
                    tool_name="get_navigation_context",
                    parameters={"actor_name": "Actor"},
                    expected_outcome="Get exploration options",
                    reasoning="Get available navigation options for exploration"
                )
            elif step == 1:
                return ToolInvocation(
                    service_name="camera",
                    tool_name="capture_first_person_view",
                    parameters={"actor_name": "Actor"},
                    expected_outcome="Capture current view",
                    reasoning="Document current location during exploration"
                )
            elif step >= 2 and step % 2 == 0:
                # Rotate to look around
                rotation_angle = (step - 2) * 1.57  # 90 degrees in radians
                return ToolInvocation(
                    service_name="movement",
                    tool_name="rotate_actor",
                    parameters={"rotation_change": [0, 0, rotation_angle], "actor_name": "Actor", "absolute_rotation": False},
                    expected_outcome="Rotate to explore different directions",
                    reasoning="Look around to explore the environment"
                )
        
        # Complex tasks requiring orchestration
        elif any(keyword in task_lower for keyword in ["prepare", "cook", "clean", "turn on", "interact"]):
            if step == 0:
                return ToolInvocation(
                    service_name="orchestration",
                    tool_name="vlm_navigation_guidance",
                    parameters={"task_description": task_description, "actor_name": "Actor", "include_visual_analysis": True},
                    expected_outcome="Get comprehensive guidance for complex task",
                    reasoning="Complex task requires orchestrated guidance from multiple services"
                )
        
        # Default fallback
        if step == 0:
            return ToolInvocation(
                service_name="spatial",
                tool_name="get_current_position",
                parameters={"actor_name": "Actor"},
                expected_outcome="Get current position as starting point",
                reasoning="Default action to understand current state"
            )
        
        return None  # Task completion
    
    async def _generate_alternative_actions(self, context: ContextState, correct_action: ToolInvocation) -> List[ToolInvocation]:
        """Generate alternative (incorrect) actions for negative examples"""
        
        alternatives = []
        
        # Get all tools except the correct one
        other_tools = [tool_id for tool_id in self.tool_metadata.keys() 
                      if tool_id != f"{correct_action.service_name}_service.{correct_action.tool_name}"]
        
        # Select 3-5 random alternatives
        num_alternatives = min(5, len(other_tools))
        selected_tools = random.sample(other_tools, num_alternatives)
        
        for tool_id in selected_tools:
            service_name, tool_name = tool_id.split(".", 1)
            service_name = service_name.replace("_service", "")
            metadata = self.tool_metadata[tool_id]
            
            # Generate plausible but wrong parameters
            alt_params = {}
            for param_name, param_type in metadata.parameters.items():
                if param_name == "actor_name":
                    alt_params[param_name] = "Actor"
                elif "position" in param_name:
                    alt_params[param_name] = [random.uniform(-5, 5), random.uniform(-5, 5), 0.0]
                elif "room" in param_name:
                    alt_params[param_name] = random.choice(["kitchen", "bedroom", "bathroom", "living_room"])
                elif param_type == "bool":
                    alt_params[param_name] = random.choice([True, False])
                elif param_type == "str":
                    alt_params[param_name] = "default_value"
            
            alternatives.append(ToolInvocation(
                service_name=service_name,
                tool_name=tool_name.replace(f"{service_name}_service.", ""),
                parameters=alt_params,
                expected_outcome="Incorrect action",
                reasoning="Alternative action for negative training example"
            ))
        
        return alternatives
    
    async def _calculate_reward(self, context: ContextState, action: ToolInvocation, task_description: str) -> float:
        """Calculate reward for an action in given context"""
        
        reward = 0.0
        
        # Base step penalty
        reward += self.reward_config["step_penalty"]
        
        # Reward for relevant actions
        task_lower = task_description.lower()
        
        # Navigation task rewards
        if "navigate" in task_lower or "go to" in task_lower:
            if action.service_name == "spatial" and "position" in action.tool_name:
                reward += self.reward_config["efficient_action"]
            elif action.service_name == "movement":
                reward += self.reward_config["efficient_action"] * 2
            else:
                reward += self.reward_config["irrelevant_tool"]
        
        # Analysis task rewards
        elif "analyze" in task_lower:
            if action.service_name == "camera" or action.service_name == "image_analysis":
                reward += self.reward_config["efficient_action"]
            else:
                reward += self.reward_config["irrelevant_tool"]
        
        # Context-specific rewards
        if context.current_room == "unknown" and action.tool_name == "detect_room":
            reward += self.reward_config["efficient_action"]
        
        if not context.first_person_image_path and action.tool_name == "capture_first_person_view":
            reward += self.reward_config["efficient_action"]
        
        # Penalty for context mismatch
        if action.prerequisites:
            for prereq in action.prerequisites:
                if prereq not in context.recent_actions:
                    reward += self.reward_config["context_mismatch"]
        
        return reward
    
    async def _execute_tool_invocation(self, invocation: ToolInvocation) -> Dict[str, Any]:
        """Execute a tool invocation via service manager"""
        
        if not self.service_manager:
            return {"success": False, "error": "Service manager not available"}
        
        try:
            result = await self.service_manager.call_service(
                invocation.service_name,
                invocation.tool_name,
                **invocation.parameters
            )
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def save_training_data(self, filename: str = None):
        """Save collected training data to file"""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vlm_tool_training_data_{timestamp}.pkl"
        
        filepath = self.data_dir / filename
        
        training_data = {
            "examples": [asdict(example) for example in self.training_examples],
            "tool_metadata": {k: asdict(v) for k, v in self.tool_metadata.items()},
            "reward_config": self.reward_config,
            "task_sequences": self.task_sequences
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(training_data, f)
        
        logger.info(f"Training data saved to {filepath}")
        return str(filepath)
    
    def load_training_data(self, filepath: str):
        """Load training data from file"""
        
        with open(filepath, 'rb') as f:
            training_data = pickle.load(f)
        
        # Convert back to dataclasses
        self.training_examples = [
            TrainingExample(**example) for example in training_data["examples"]
        ]
        
        self.tool_metadata = {
            k: ToolMetadata(**v) for k, v in training_data["tool_metadata"].items()
        }
        
        self.reward_config = training_data["reward_config"]
        self.task_sequences = training_data["task_sequences"]
        
        logger.info(f"Loaded {len(self.training_examples)} training examples")
    
    def generate_training_prompt(self, context: ContextState, include_tools: bool = True) -> str:
        """Generate a training prompt for the VLM"""
        
        prompt_parts = []
        
        if include_tools:
            prompt_parts.append(self.generate_tool_list_prompt())
            prompt_parts.append("\n" + "="*80 + "\n")
        
        prompt_parts.append("CURRENT CONTEXT:")
        prompt_parts.append(f"Task: {context.task_description}")
        prompt_parts.append(f"Current Room: {context.current_room}")
        prompt_parts.append(f"Actor Position: ({context.actor_position[0]:.1f}, {context.actor_position[1]:.1f}, {context.actor_position[2]:.1f})")
        prompt_parts.append(f"Actor Rotation: ({context.actor_rotation[0]:.2f}, {context.actor_rotation[1]:.2f}, {context.actor_rotation[2]:.2f})")
        
        if context.visible_objects:
            prompt_parts.append(f"Visible Objects: {', '.join(context.visible_objects)}")
        else:
            prompt_parts.append("Visible Objects: [none detected]")
        
        if context.recent_actions:
            prompt_parts.append(f"Recent Actions: {', '.join(context.recent_actions[-3:])}")
        
        if context.spatial_context:
            prompt_parts.append(f"Navigation Options: {len(context.spatial_context.get('navigation_options', []))} available")
        
        prompt_parts.append(f"Images Available: {'Yes' if context.first_person_image_path else 'No'}")
        
        prompt_parts.append("\nINSTRUCTION:")
        prompt_parts.append("Based on the current context and available tools, select the most appropriate tool to call next.")
        prompt_parts.append("Provide your response in the following format:")
        prompt_parts.append("TOOL: service_name.tool_name")
        prompt_parts.append("PARAMETERS: {parameter_dict}")
        prompt_parts.append("REASONING: Brief explanation of why this tool is appropriate")
        
        return "\n".join(prompt_parts)
    
    async def generate_comprehensive_training_dataset(self, tasks: List[str]) -> str:
        """Generate comprehensive training dataset for multiple tasks"""
        
        logger.info(f"Generating training dataset for {len(tasks)} tasks")
        
        all_examples = []
        
        for task in tasks:
            logger.info(f"Processing task: {task}")
            
            try:
                # Collect expert demonstrations
                examples = await self.collect_expert_demonstration(task)
                all_examples.extend(examples)
                
                # Store task sequence
                self.task_sequences[task] = [asdict(ex.correct_tool_invocation) for ex in examples]
                
                logger.info(f"Collected {len(examples)} examples for task: {task}")
                
            except Exception as e:
                logger.error(f"Error processing task {task}: {str(e)}")
        
        # Store all examples
        self.training_examples.extend(all_examples)
        
        # Save training data
        filepath = self.save_training_data()
        
        logger.info(f"Generated {len(all_examples)} total training examples")
        logger.info(f"Training data saved to: {filepath}")
        
        return filepath

# Example usage and testing
async def main():
    """Main function for testing the training system"""
    
    # Initialize training system
    training_system = VLMToolTrainingSystem()
    
    # Define example tasks for training
    training_tasks = [
        "Navigate to the kitchen",
        "Navigate to the bedroom", 
        "Navigate to the bathroom",
        "Analyze the current room",
        "Identify furniture in the room",
        "Explore the environment",
        "Look around the current area",
        "Get current position and room information",
        "Prepare coffee in the kitchen",
        "Turn on the lights in the living room"
    ]
    
    # Generate training dataset
    print("🚀 Starting VLM Tool Selection Training Dataset Generation")
    print(f"📋 Tasks to process: {len(training_tasks)}")
    
    # Show available tools
    print("\n📊 Available Tools:")
    print(training_system.generate_tool_list_prompt())
    
    # Generate dataset
    dataset_path = await training_system.generate_comprehensive_training_dataset(training_tasks)
    
    print(f"\n✅ Training dataset generated successfully!")
    print(f"📁 Dataset saved to: {dataset_path}")
    print(f"📈 Total examples: {len(training_system.training_examples)}")
    
    # Show example prompt
    if training_system.training_examples:
        example = training_system.training_examples[0]
        print("\n📝 Example Training Prompt:")
        print("=" * 80)
        prompt = training_system.generate_training_prompt(example.context_state)
        print(prompt)
        print("=" * 80)
        print(f"\n🎯 Correct Answer:")
        print(f"TOOL: {example.correct_tool_invocation.service_name}.{example.correct_tool_invocation.tool_name}")
        print(f"PARAMETERS: {example.correct_tool_invocation.parameters}")
        print(f"REASONING: {example.correct_tool_invocation.reasoning}")

if __name__ == "__main__":
    asyncio.run(main())
