"""
VLM Tool Selection Inference Engine
==================================

Production inference system for the trained VLM to select appropriate microservice tools
for task completion in the VESPER environment.
"""

import asyncio
import json
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Dict, Any, List, Optional, Tuple
import logging
from pathlib import Path
import re
import time
from dataclasses import dataclass

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
class InferenceConfig:
    """Configuration for VLM inference"""
    model_path: str = "vlm_tool_model"
    max_length: int = 1024
    max_new_tokens: int = 200
    temperature: float = 0.7
    top_p: float = 0.9
    device: str = "auto"
    confidence_threshold: float = 0.7

@dataclass
class ToolPrediction:
    """Prediction result from VLM"""
    service_name: str
    tool_name: str
    parameters: Dict[str, Any]
    reasoning: str
    confidence: float
    raw_response: str

class VLMToolInferenceEngine:
    """Inference engine for VLM tool selection"""
    
    def __init__(self, config: InferenceConfig = None):
        self.config = config or InferenceConfig()
        
        # Model components
        self.tokenizer = None
        self.model = None
        
        # Service manager for execution
        self.service_manager = ServiceManager() if SERVICES_AVAILABLE else None
        
        # Execution history
        self.execution_history = []
        
        # Tool metadata for validation
        self.available_tools = self._get_available_tools()
        
        self._load_model()
    
    def _load_model(self):
        """Load the fine-tuned model and tokenizer"""
        
        model_path = Path(self.config.model_path)
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found at: {model_path}")
        
        logger.info(f"Loading fine-tuned model from: {model_path}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_path))
        
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            str(model_path),
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map=self.config.device if self.config.device != "auto" else "auto"
        )
        
        self.model.eval()
        logger.info("Model loaded successfully")
    
    def _get_available_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get available tools metadata"""
        
        tools = {
            # Camera Service
            "camera_service.setup_first_person_camera": {
                "service": "camera",
                "tool": "setup_first_person_camera",
                "parameters": {"actor_name": "str"}
            },
            "camera_service.capture_first_person_view": {
                "service": "camera", 
                "tool": "capture_first_person_view",
                "parameters": {"actor_name": "str", "filename": "Optional[str]", "resolution_x": "int", "resolution_y": "int"}
            },
            "camera_service.get_camera_info": {
                "service": "camera",
                "tool": "get_camera_info", 
                "parameters": {"actor_name": "str"}
            },
            
            # Image Analysis Service
            "image_analysis_service.analyze_room_from_image": {
                "service": "image_analysis",
                "tool": "analyze_room_from_image",
                "parameters": {"image_path": "str", "detailed_analysis": "bool"}
            },
            "image_analysis_service.identify_furniture_objects": {
                "service": "image_analysis",
                "tool": "identify_furniture_objects",
                "parameters": {"image_path": "str", "target_objects": "Optional[List[str]]"}
            },
            
            # Spatial Service
            "spatial_service.get_current_position": {
                "service": "spatial",
                "tool": "get_current_position",
                "parameters": {"actor_name": "str"}
            },
            "spatial_service.detect_room": {
                "service": "spatial",
                "tool": "detect_room",
                "parameters": {"position": "Optional[List[float]]", "actor_name": "str"}
            },
            "spatial_service.get_navigation_context": {
                "service": "spatial",
                "tool": "get_navigation_context",
                "parameters": {"actor_name": "str", "target_room": "Optional[str]"}
            },
            
            # Movement Service
            "movement_service.move_actor_to_position": {
                "service": "movement",
                "tool": "move_actor_to_position",
                "parameters": {"target_position": "List[float]", "actor_name": "str", "movement_speed": "Optional[float]", "check_collisions": "bool"}
            },
            "movement_service.move_to_room": {
                "service": "movement",
                "tool": "move_to_room",
                "parameters": {"target_room": "str", "actor_name": "str", "position_in_room": "str"}
            },
            "movement_service.rotate_actor": {
                "service": "movement",
                "tool": "rotate_actor",
                "parameters": {"rotation_change": "List[float]", "actor_name": "str", "absolute_rotation": "bool"}
            },
            
            # Orchestration Service
            "orchestration_service.vlm_navigation_guidance": {
                "service": "orchestration",
                "tool": "vlm_navigation_guidance",
                "parameters": {"task_description": "str", "actor_name": "str", "include_visual_analysis": "bool"}
            },
            "orchestration_service.execute_coordinated_action": {
                "service": "orchestration",
                "tool": "execute_coordinated_action",
                "parameters": {"action_type": "str", "action_params": "Dict[str, Any]", "actor_name": "str"}
            }
        }
        
        return tools
    
    def generate_context_prompt(self, 
                              task_description: str,
                              current_context: Dict[str, Any],
                              execution_history: List[str] = None) -> str:
        """Generate context prompt for VLM inference"""
        
        prompt_parts = [
            "AVAILABLE MICROSERVICE TOOLS:",
            "",
            "PERCEPTION TOOLS:",
            "  - camera_service.capture_first_person_view(actor_name: str): Capture first-person view screenshot",
            "  - image_analysis_service.analyze_room_from_image(image_path: str, detailed_analysis: bool): Analyze image for room type",
            "  - image_analysis_service.identify_furniture_objects(image_path: str): Identify furniture objects",
            "",
            "INFORMATION TOOLS:",
            "  - spatial_service.get_current_position(actor_name: str): Get actor's current position",
            "  - spatial_service.detect_room(actor_name: str): Detect current room",
            "  - spatial_service.get_navigation_context(actor_name: str, target_room: str): Get navigation options",
            "  - camera_service.get_camera_info(actor_name: str): Get camera information",
            "",
            "PLANNING TOOLS:",
            "  - spatial_service.get_navigation_context(actor_name: str): Get navigation options",
            "",
            "ACTION TOOLS:",
            "  - movement_service.move_actor_to_position(target_position: List[float], actor_name: str): Move to position",
            "  - movement_service.move_to_room(target_room: str, actor_name: str): Move to specific room",
            "  - movement_service.rotate_actor(rotation_change: List[float], actor_name: str): Rotate actor",
            "",
            "SETUP TOOLS:",
            "  - camera_service.setup_first_person_camera(actor_name: str): Initialize first-person camera",
            "",
            "GUIDANCE TOOLS:",
            "  - orchestration_service.vlm_navigation_guidance(task_description: str, actor_name: str): Get comprehensive guidance",
            "  - orchestration_service.execute_coordinated_action(action_type: str, action_params: Dict): Execute coordinated action",
            "",
            "=" * 80,
            "",
            "CURRENT CONTEXT:",
            f"Task: {task_description}",
            f"Current Room: {current_context.get('current_room', 'unknown')}",
            f"Actor Position: {current_context.get('actor_position', [0.0, 0.0, 0.0])}",
            f"Actor Rotation: {current_context.get('actor_rotation', [0.0, 0.0, 0.0])}",
            f"Visible Objects: {', '.join(current_context.get('visible_objects', [])) or '[none detected]'}",
            f"Images Available: {'Yes' if current_context.get('first_person_image_path') else 'No'}",
            f"Navigation Options: {len(current_context.get('navigation_options', []))} available"
        ]
        
        if execution_history:
            prompt_parts.extend([
                f"Recent Actions: {', '.join(execution_history[-3:])}"
            ])
        
        prompt_parts.extend([
            "",
            "INSTRUCTION:",
            "Based on the current context and available tools, select the most appropriate tool to call next.",
            "Consider the task requirements, current state, and available information.",
            "Provide your response in the following format:",
            "TOOL: service_name.tool_name",
            "PARAMETERS: {parameter_dict}",
            "REASONING: Brief explanation of why this tool is appropriate"
        ])
        
        return "\n".join(prompt_parts)
    
    def predict_tool(self, context_prompt: str) -> ToolPrediction:
        """Generate tool prediction from context prompt"""
        
        # Tokenize input
        inputs = self.tokenizer(
            context_prompt + "\n\nRESPONSE:\n",
            return_tensors="pt",
            truncation=True,
            max_length=self.config.max_length - self.config.max_new_tokens
        )
        
        # Move to device if needed
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        # Generate response
        with torch.no_grad():
            outputs = self.model.generate(
                inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_new_tokens=self.config.max_new_tokens,
                do_sample=True,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                pad_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.1
            )
        
        # Decode response
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract generated part
        response_start = full_response.find("RESPONSE:\n")
        if response_start != -1:
            generated_response = full_response[response_start + len("RESPONSE:\n"):].strip()
        else:
            generated_response = full_response.split(context_prompt)[-1].strip()
        
        # Parse the response
        return self._parse_tool_response(generated_response)
    
    def _parse_tool_response(self, response: str) -> ToolPrediction:
        """Parse the model's tool response"""
        
        lines = response.split('\n')
        
        tool_name = ""
        parameters = {}
        reasoning = ""
        confidence = 0.5  # Default confidence
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("TOOL:"):
                tool_name = line.replace("TOOL:", "").strip()
            elif line.startswith("PARAMETERS:"):
                param_str = line.replace("PARAMETERS:", "").strip()
                try:
                    parameters = json.loads(param_str)
                except json.JSONDecodeError:
                    # Try to extract parameters manually
                    parameters = self._extract_parameters_manually(param_str)
            elif line.startswith("REASONING:"):
                reasoning = line.replace("REASONING:", "").strip()
        
        # Extract service and tool names
        if "." in tool_name:
            service_name = tool_name.split(".")[0].replace("_service", "")
            tool_name_only = tool_name.split(".", 1)[1]
        else:
            service_name = "unknown"
            tool_name_only = tool_name
        
        # Calculate confidence based on tool validity
        if tool_name in self.available_tools:
            confidence = 0.8
        elif any(tool_name_only in tool for tool in self.available_tools.keys()):
            confidence = 0.6
        else:
            confidence = 0.3
        
        return ToolPrediction(
            service_name=service_name,
            tool_name=tool_name_only,
            parameters=parameters,
            reasoning=reasoning,
            confidence=confidence,
            raw_response=response
        )
    
    def _extract_parameters_manually(self, param_str: str) -> Dict[str, Any]:
        """Manually extract parameters if JSON parsing fails"""
        
        parameters = {}
        
        # Try to find key-value pairs
        patterns = [
            r'"(\w+)"\s*:\s*"([^"]+)"',  # "key": "value"
            r'"(\w+)"\s*:\s*(\[.*?\])',   # "key": [list]
            r'"(\w+)"\s*:\s*(\w+)',      # "key": value
            r'(\w+)\s*:\s*"([^"]+)"',    # key: "value"
            r'(\w+)\s*:\s*(\[.*?\])',    # key: [list]
            r'(\w+)\s*:\s*(\w+)'         # key: value
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, param_str)
            for key, value in matches:
                # Try to parse value
                try:
                    if value.startswith('[') and value.endswith(']'):
                        parameters[key] = json.loads(value)
                    elif value.lower() in ['true', 'false']:
                        parameters[key] = value.lower() == 'true'
                    elif value.isdigit():
                        parameters[key] = int(value)
                    else:
                        parameters[key] = value.strip('"')
                except:
                    parameters[key] = value.strip('"')
        
        return parameters
    
    async def execute_predicted_tool(self, prediction: ToolPrediction) -> Dict[str, Any]:
        """Execute the predicted tool using service manager"""
        
        if not self.service_manager:
            return {
                "success": False,
                "error": "Service manager not available"
            }
        
        if prediction.confidence < self.config.confidence_threshold:
            return {
                "success": False,
                "error": f"Prediction confidence {prediction.confidence:.2f} below threshold {self.config.confidence_threshold}"
            }
        
        try:
            # Execute the tool
            result = await self.service_manager.call_service(
                prediction.service_name,
                prediction.tool_name,
                **prediction.parameters
            )
            
            # Log execution
            self.execution_history.append(f"{prediction.service_name}.{prediction.tool_name}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing tool: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def solve_task_autonomously(self, 
                                    task_description: str,
                                    max_steps: int = 20,
                                    actor_name: str = "Actor") -> Dict[str, Any]:
        """Autonomously solve a task using VLM tool selection"""
        
        logger.info(f"Starting autonomous task solving: {task_description}")
        
        execution_log = []
        step_count = 0
        task_completed = False
        
        while not task_completed and step_count < max_steps:
            logger.info(f"Step {step_count + 1}: Gathering context...")
            
            # Gather current context
            current_context = await self._gather_current_context(actor_name)
            
            # Generate context prompt
            context_prompt = self.generate_context_prompt(
                task_description,
                current_context,
                [entry["tool"] for entry in execution_log[-3:]]  # Last 3 actions
            )
            
            # Predict next tool
            logger.info(f"Step {step_count + 1}: Predicting next tool...")
            prediction = self.predict_tool(context_prompt)
            
            logger.info(f"Step {step_count + 1}: Predicted {prediction.service_name}.{prediction.tool_name} (confidence: {prediction.confidence:.2f})")
            logger.info(f"Reasoning: {prediction.reasoning}")
            
            # Execute predicted tool
            execution_result = await self.execute_predicted_tool(prediction)
            
            # Log execution step
            step_log = {
                "step": step_count + 1,
                "tool": f"{prediction.service_name}.{prediction.tool_name}",
                "parameters": prediction.parameters,
                "reasoning": prediction.reasoning,
                "confidence": prediction.confidence,
                "result": execution_result,
                "success": execution_result.get("success", False)
            }
            
            execution_log.append(step_log)
            
            logger.info(f"Step {step_count + 1}: {'✓' if execution_result.get('success') else '✗'} {execution_result.get('error', 'Success')}")
            
            # Check for task completion (simplified)
            if self._check_task_completion(task_description, execution_log):
                task_completed = True
                logger.info("Task completed successfully!")
            
            step_count += 1
            
            # Brief pause between steps
            await asyncio.sleep(0.5)
        
        return {
            "task_description": task_description,
            "completed": task_completed,
            "total_steps": step_count,
            "execution_log": execution_log,
            "final_context": current_context
        }
    
    async def _gather_current_context(self, actor_name: str) -> Dict[str, Any]:
        """Gather current context from services"""
        
        context = {
            "current_room": "unknown",
            "actor_position": [0.0, 0.0, 0.0],
            "actor_rotation": [0.0, 0.0, 0.0],
            "visible_objects": [],
            "first_person_image_path": None,
            "navigation_options": []
        }
        
        if not self.service_manager:
            return context
        
        try:
            # Get spatial context
            spatial_result = await self.service_manager.call_service(
                "spatial", "get_current_position", actor_name=actor_name
            )
            
            if spatial_result.get("success"):
                context["actor_position"] = [
                    spatial_result["position"]["x"],
                    spatial_result["position"]["y"],
                    spatial_result["position"]["z"]
                ]
                context["actor_rotation"] = [
                    spatial_result["rotation"]["x"],
                    spatial_result["rotation"]["y"], 
                    spatial_result["rotation"]["z"]
                ]
                context["current_room"] = spatial_result["spatial_context"].get("current_room", "unknown")
            
            # Get navigation context
            nav_result = await self.service_manager.call_service(
                "spatial", "get_navigation_context", actor_name=actor_name
            )
            
            if nav_result.get("success"):
                context["navigation_options"] = nav_result.get("navigation_options", [])
        
        except Exception as e:
            logger.warning(f"Error gathering context: {str(e)}")
        
        return context
    
    def _check_task_completion(self, task_description: str, execution_log: List[Dict]) -> bool:
        """Check if task is completed based on execution log"""
        
        if not execution_log:
            return False
        
        # Simple completion checks
        task_lower = task_description.lower()
        
        # Navigation tasks
        if "navigate to" in task_lower or "go to" in task_lower:
            # Check if we've moved to target room
            for entry in execution_log[-3:]:  # Check last 3 steps
                if "move_to_room" in entry["tool"] and entry["success"]:
                    return True
        
        # Analysis tasks
        elif "analyze" in task_lower or "identify" in task_lower:
            # Check if we've analyzed an image
            for entry in execution_log[-3:]:
                if "analyze_room_from_image" in entry["tool"] and entry["success"]:
                    return True
        
        # Exploration tasks
        elif "explore" in task_lower:
            # Check if we've captured multiple views
            capture_count = sum(1 for entry in execution_log if "capture" in entry["tool"] and entry["success"])
            if capture_count >= 2:
                return True
        
        # Default: task completes after 10 successful steps
        successful_steps = sum(1 for entry in execution_log if entry["success"])
        return successful_steps >= 5
    
    def get_performance_metrics(self, execution_log: List[Dict]) -> Dict[str, Any]:
        """Calculate performance metrics from execution log"""
        
        if not execution_log:
            return {}
        
        total_steps = len(execution_log)
        successful_steps = sum(1 for entry in execution_log if entry["success"])
        average_confidence = sum(entry["confidence"] for entry in execution_log) / total_steps
        
        # Tool usage distribution
        tool_usage = {}
        for entry in execution_log:
            tool = entry["tool"]
            tool_usage[tool] = tool_usage.get(tool, 0) + 1
        
        return {
            "total_steps": total_steps,
            "successful_steps": successful_steps,
            "success_rate": successful_steps / total_steps if total_steps > 0 else 0,
            "average_confidence": average_confidence,
            "tool_usage_distribution": tool_usage,
            "efficiency_score": successful_steps / total_steps if total_steps > 0 else 0
        }

# Example usage and testing
async def main():
    """Main function for testing inference engine"""
    
    print("🚀 Starting VLM Tool Selection Inference Engine")
    
    # Check if fine-tuned model exists
    model_path = Path("vlm_tool_model")
    if not model_path.exists():
        print("❌ Fine-tuned model not found. Please run vlm_finetuning_system.py first.")
        return
    
    # Initialize inference engine
    config = InferenceConfig(model_path=str(model_path))
    inference_engine = VLMToolInferenceEngine(config)
    
    # Test tasks
    test_tasks = [
        "Navigate to the kitchen",
        "Analyze the current room",
        "Explore the environment",
        "Get current position information"
    ]
    
    print(f"🧪 Testing {len(test_tasks)} tasks")
    
    for i, task in enumerate(test_tasks):
        print(f"\n{'='*60}")
        print(f"Test {i+1}: {task}")
        print(f"{'='*60}")
        
        # Solve task autonomously
        result = await inference_engine.solve_task_autonomously(task, max_steps=5)
        
        # Show results
        print(f"✅ Task completed: {result['completed']}")
        print(f"📊 Total steps: {result['total_steps']}")
        
        # Show execution log
        for step in result["execution_log"]:
            status = "✓" if step["success"] else "✗"
            print(f"  {status} Step {step['step']}: {step['tool']} (confidence: {step['confidence']:.2f})")
            print(f"    Reasoning: {step['reasoning']}")
        
        # Performance metrics
        metrics = inference_engine.get_performance_metrics(result["execution_log"])
        print(f"📈 Success rate: {metrics.get('success_rate', 0):.2%}")
        print(f"🎯 Average confidence: {metrics.get('average_confidence', 0):.2f}")
    
    print(f"\n✅ Inference testing complete!")

if __name__ == "__main__":
    asyncio.run(main())
