#!/usr/bin/env python3
"""
VESPER ADL Enhancement - Phase 3: VLM Intelligence Enhancement

Advanced VLM capabilities for complex ADL task reasoning:
- Multi-step task planning and adaptation
- Context-aware decision making
- Error detection and recovery strategies
- Dynamic task modification based on environment state
- Human-like reasoning patterns for ADL activities

Builds on Phase 1 (Object Interaction) and Phase 2 (Task Execution).
"""

import bge
import mathutils
from typing import Dict, List, Tuple, Optional, Any, Callable
import json
import time
import base64
import requests
from dataclasses import dataclass
from enum import Enum
import cv2
import numpy as np

# Import previous phases
from object_interaction_system import CASASObjectManager, VLMObjectInteraction
from adl_task_execution_system import ADLTaskExecutor, ADLTask, TaskStep, TaskStatus, ADLCategory

class ReasoningContext(Enum):
    TASK_PLANNING = "task_planning"
    OBSTACLE_NAVIGATION = "obstacle_navigation"
    OBJECT_IDENTIFICATION = "object_identification"
    ERROR_RECOVERY = "error_recovery"
    SAFETY_ASSESSMENT = "safety_assessment"
    EFFICIENCY_OPTIMIZATION = "efficiency_optimization"

class VLMComplexity(Enum):
    SIMPLE = "simple"      # Single object, single action
    MODERATE = "moderate"  # Multiple objects, sequence of actions
    COMPLEX = "complex"    # Multi-step reasoning, conditional logic
    EXPERT = "expert"      # Human-level ADL reasoning

@dataclass
class VLMPromptTemplate:
    """Structured prompt template for VLM interactions"""
    template_id: str
    reasoning_context: ReasoningContext
    complexity_level: VLMComplexity
    prompt_structure: str
    expected_response_format: Dict[str, Any]
    validation_criteria: List[str]

class AdvancedVLMProcessor:
    """Enhanced VLM processing for complex ADL reasoning"""
    
    def __init__(self):
        self.prompt_templates = self._initialize_prompt_templates()
        self.reasoning_history: List[Dict[str, Any]] = []
        self.context_memory: Dict[str, Any] = {}
        self.error_patterns: Dict[str, int] = {}
        
        # VLM configuration
        self.vlm_endpoint = "http://localhost:11434/api/generate"  # Ollama default
        self.vlm_model = "llava:7b"
        self.max_context_length = 4096
        
    def _initialize_prompt_templates(self) -> Dict[str, VLMPromptTemplate]:
        """Initialize comprehensive VLM prompt templates"""
        
        templates = {}
        
        # Task Planning Template
        templates["adl_task_planning"] = VLMPromptTemplate(
            template_id="adl_task_planning",
            reasoning_context=ReasoningContext.TASK_PLANNING,
            complexity_level=VLMComplexity.COMPLEX,
            prompt_structure="""
You are an expert in Activities of Daily Living (ADL) in smart homes. 

CONTEXT:
- Current environment: {environment_description}
- Available objects: {available_objects}
- Actor position: {actor_position}
- Current task goal: {task_goal}
- Previous actions: {action_history}

TASK:
Plan the optimal sequence of actions to complete: "{task_description}"

Consider:
1. Object dependencies (what objects are needed for each step)
2. Spatial efficiency (minimize unnecessary movement)
3. Safety requirements (proper handling of items)
4. Human behavior patterns (natural ADL sequence)

RESPOND WITH:
{{
    "action_plan": [
        {{
            "step_number": 1,
            "action": "specific_action_description",
            "target_objects": ["object1", "object2"],
            "target_location": "location_name",
            "reasoning": "why_this_step_is_necessary",
            "safety_notes": "safety_considerations",
            "estimated_duration": 30.0
        }}
    ],
    "overall_strategy": "high_level_approach_description",
    "potential_obstacles": ["obstacle1", "obstacle2"],
    "success_indicators": ["indicator1", "indicator2"]
}}
""",
            expected_response_format={
                "action_plan": "list",
                "overall_strategy": "string",
                "potential_obstacles": "list",
                "success_indicators": "list"
            },
            validation_criteria=[
                "action_plan_has_steps",
                "steps_have_required_fields",
                "objects_exist_in_environment",
                "locations_are_valid"
            ]
        )
        
        # Error Recovery Template
        templates["error_recovery"] = VLMPromptTemplate(
            template_id="error_recovery",
            reasoning_context=ReasoningContext.ERROR_RECOVERY,
            complexity_level=VLMComplexity.EXPERT,
            prompt_structure="""
You are an expert at diagnosing and recovering from ADL task failures.

SITUATION:
- Failed action: {failed_action}
- Error description: {error_description}
- Current environment state: {environment_state}
- Available objects: {available_objects}
- Actor status: {actor_status}

PREVIOUS ATTEMPTS:
{previous_recovery_attempts}

TASK:
Diagnose the failure and provide a recovery strategy.

Consider:
1. Root cause analysis (why did this fail?)
2. Environment constraints (what's preventing success?)
3. Alternative approaches (different way to achieve goal?)
4. Resource availability (do we have what we need?)

RESPOND WITH:
{{
    "diagnosis": {{
        "primary_cause": "main_reason_for_failure",
        "contributing_factors": ["factor1", "factor2"],
        "severity": "low|medium|high",
        "recoverable": true/false
    }},
    "recovery_strategy": {{
        "approach": "description_of_recovery_approach",
        "alternative_actions": [
            {{
                "action": "alternative_action",
                "probability_of_success": 0.8,
                "required_changes": ["change1", "change2"]
            }}
        ],
        "preventive_measures": ["measure1", "measure2"]
    }},
    "success_probability": 0.75
}}
""",
            expected_response_format={
                "diagnosis": "dict",
                "recovery_strategy": "dict", 
                "success_probability": "float"
            },
            validation_criteria=[
                "diagnosis_has_cause",
                "recovery_strategy_provided",
                "success_probability_valid"
            ]
        )
        
        # Safety Assessment Template
        templates["safety_assessment"] = VLMPromptTemplate(
            template_id="safety_assessment",
            reasoning_context=ReasoningContext.SAFETY_ASSESSMENT,
            complexity_level=VLMComplexity.MODERATE,
            prompt_structure="""
You are a safety expert analyzing ADL activities in smart homes.

SCENARIO:
- Planned action: {planned_action}
- Environment: {environment_description}
- Objects involved: {objects_involved}
- Actor capabilities: {actor_capabilities}

TASK:
Assess safety risks and provide safety recommendations.

Consider:
1. Physical safety (falling, injury, burns)
2. Object safety (proper handling, storage)
3. Environmental hazards (obstacles, unsafe areas)
4. Task-specific risks (cooking, medication, etc.)

RESPOND WITH:
{{
    "safety_assessment": {{
        "overall_risk_level": "low|medium|high",
        "identified_risks": [
            {{
                "risk_type": "risk_category",
                "description": "detailed_description",
                "probability": "low|medium|high",
                "severity": "minor|moderate|severe"
            }}
        ],
        "safety_recommendations": [
            {{
                "recommendation": "safety_measure",
                "priority": "low|medium|high",
                "implementation": "how_to_implement"
            }}
        ],
        "proceed_with_action": true/false,
        "required_modifications": ["modification1", "modification2"]
    }}
}}
""",
            expected_response_format={
                "safety_assessment": "dict"
            },
            validation_criteria=[
                "risk_level_provided",
                "risks_identified",
                "recommendations_given"
            ]
        )
        
        return templates
    
    def process_vlm_request(self, template_id: str, context_data: Dict[str, Any], 
                           screenshot_path: Optional[str] = None) -> Dict[str, Any]:
        """Process a VLM request using structured templates"""
        
        template = self.prompt_templates.get(template_id)
        if not template:
            raise ValueError(f"Unknown template: {template_id}")
        
        # Build prompt from template
        prompt = self._build_prompt(template, context_data)
        
        # Add screenshot if available
        image_data = None
        if screenshot_path:
            image_data = self._encode_image(screenshot_path)
        
        # Send request to VLM
        response = self._send_vlm_request(prompt, image_data)
        
        # Validate and process response
        processed_response = self._process_vlm_response(response, template)
        
        # Log reasoning step
        self._log_reasoning_step(template_id, context_data, processed_response)
        
        return processed_response
    
    def _build_prompt(self, template: VLMPromptTemplate, context_data: Dict[str, Any]) -> str:
        """Build a prompt from template and context data"""
        try:
            return template.prompt_structure.format(**context_data)
        except KeyError as e:
            missing_key = str(e).strip("'")
            raise ValueError(f"Missing context data for template {template.template_id}: {missing_key}")
    
    def _encode_image(self, screenshot_path: str) -> Optional[str]:
        """Encode screenshot for VLM processing"""
        try:
            with open(screenshot_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"⚠️  Failed to encode image: {e}")
            return None
    
    def _send_vlm_request(self, prompt: str, image_data: Optional[str] = None) -> Dict[str, Any]:
        """Send request to VLM endpoint"""
        
        payload = {
            "model": self.vlm_model,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        
        if image_data:
            payload["images"] = [image_data]
        
        try:
            response = requests.post(
                self.vlm_endpoint,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result
            
        except requests.RequestException as e:
            print(f"❌ VLM request failed: {e}")
            return {"error": str(e)}
        except json.JSONDecodeError as e:
            print(f"❌ VLM response parsing failed: {e}")
            return {"error": "Invalid JSON response"}
    
    def _process_vlm_response(self, response: Dict[str, Any], template: VLMPromptTemplate) -> Dict[str, Any]:
        """Process and validate VLM response"""
        
        if "error" in response:
            return {"error": response["error"], "valid": False}
        
        # Extract response text
        response_text = response.get("response", "")
        
        try:
            # Parse JSON response
            parsed_response = json.loads(response_text)
            
            # Validate response format
            valid = self._validate_response_format(parsed_response, template)
            
            return {
                "data": parsed_response,
                "valid": valid,
                "template_id": template.template_id,
                "complexity": template.complexity_level.value
            }
            
        except json.JSONDecodeError:
            return {
                "error": "VLM response not valid JSON",
                "raw_response": response_text,
                "valid": False
            }
    
    def _validate_response_format(self, response_data: Dict[str, Any], template: VLMPromptTemplate) -> bool:
        """Validate VLM response against template expectations"""
        
        expected_format = template.expected_response_format
        
        # Check required fields exist
        for field, expected_type in expected_format.items():
            if field not in response_data:
                print(f"⚠️  Missing required field: {field}")
                return False
            
            # Basic type checking
            value = response_data[field]
            if expected_type == "list" and not isinstance(value, list):
                print(f"⚠️  Field {field} should be list, got {type(value)}")
                return False
            elif expected_type == "dict" and not isinstance(value, dict):
                print(f"⚠️  Field {field} should be dict, got {type(value)}")
                return False
            elif expected_type == "string" and not isinstance(value, str):
                print(f"⚠️  Field {field} should be string, got {type(value)}")
                return False
            elif expected_type == "float" and not isinstance(value, (int, float)):
                print(f"⚠️  Field {field} should be float, got {type(value)}")
                return False
        
        return True
    
    def _log_reasoning_step(self, template_id: str, context_data: Dict[str, Any], response: Dict[str, Any]):
        """Log VLM reasoning step for analysis and improvement"""
        
        reasoning_entry = {
            "timestamp": time.time(),
            "template_id": template_id,
            "context_size": len(str(context_data)),
            "response_valid": response.get("valid", False),
            "complexity": response.get("complexity", "unknown"),
            "has_error": "error" in response
        }
        
        self.reasoning_history.append(reasoning_entry)
        
        # Update error patterns if there's an error
        if "error" in response:
            error_type = type(response["error"]).__name__
            self.error_patterns[error_type] = self.error_patterns.get(error_type, 0) + 1
    
    def get_reasoning_analytics(self) -> Dict[str, Any]:
        """Get analytics on VLM reasoning performance"""
        
        if not self.reasoning_history:
            return {"status": "no_data"}
        
        total_requests = len(self.reasoning_history)
        valid_responses = sum(1 for entry in self.reasoning_history if entry["response_valid"])
        error_requests = sum(1 for entry in self.reasoning_history if entry["has_error"])
        
        complexity_distribution = {}
        for entry in self.reasoning_history:
            complexity = entry["complexity"]
            complexity_distribution[complexity] = complexity_distribution.get(complexity, 0) + 1
        
        return {
            "total_requests": total_requests,
            "success_rate": valid_responses / total_requests if total_requests > 0 else 0,
            "error_rate": error_requests / total_requests if total_requests > 0 else 0,
            "complexity_distribution": complexity_distribution,
            "error_patterns": self.error_patterns,
            "average_context_size": sum(entry["context_size"] for entry in self.reasoning_history) / total_requests
        }

class IntelligentTaskPlanner:
    """Advanced task planning using enhanced VLM reasoning"""
    
    def __init__(self):
        self.vlm_processor = AdvancedVLMProcessor()
        self.task_executor = ADLTaskExecutor()
        self.adaptation_history: List[Dict[str, Any]] = []
        
    def plan_adaptive_task(self, task_goal: str, environment_context: Dict[str, Any], 
                          screenshot_path: Optional[str] = None) -> Dict[str, Any]:
        """Plan a task with adaptive reasoning based on environment"""
        
        # Gather context for VLM planning
        context_data = {
            "environment_description": self._describe_environment(environment_context),
            "available_objects": self._list_available_objects(),
            "actor_position": environment_context.get("actor_position", "unknown"),
            "task_goal": task_goal,
            "task_description": task_goal,
            "action_history": self._get_recent_action_history()
        }
        
        # Use VLM for intelligent task planning
        planning_response = self.vlm_processor.process_vlm_request(
            "adl_task_planning", 
            context_data, 
            screenshot_path
        )
        
        if not planning_response.get("valid", False):
            print(f"❌ Task planning failed: {planning_response.get('error', 'Unknown error')}")
            return {"success": False, "error": planning_response.get("error")}
        
        plan_data = planning_response["data"]
        
        # Convert VLM plan to executable task format
        executable_task = self._convert_plan_to_task(plan_data, task_goal)
        
        return {
            "success": True,
            "task_plan": executable_task,
            "vlm_reasoning": plan_data,
            "adaptation_notes": self._identify_adaptations(plan_data)
        }
    
    def handle_task_failure_intelligently(self, failed_action: str, error_context: Dict[str, Any], 
                                        screenshot_path: Optional[str] = None) -> Dict[str, Any]:
        """Use VLM reasoning for intelligent error recovery"""
        
        context_data = {
            "failed_action": failed_action,
            "error_description": error_context.get("error_description", "Unknown error"),
            "environment_state": self._describe_current_environment(),
            "available_objects": self._list_available_objects(),
            "actor_status": error_context.get("actor_status", "unknown"),
            "previous_recovery_attempts": self._get_previous_recovery_attempts()
        }
        
        # Use VLM for error diagnosis and recovery
        recovery_response = self.vlm_processor.process_vlm_request(
            "error_recovery",
            context_data,
            screenshot_path
        )
        
        if not recovery_response.get("valid", False):
            print(f"❌ Error recovery planning failed: {recovery_response.get('error')}")
            return {"success": False, "fallback_to_default": True}
        
        recovery_data = recovery_response["data"]
        
        # Log adaptation for learning
        self._log_adaptation(failed_action, recovery_data)
        
        return {
            "success": True,
            "diagnosis": recovery_data["diagnosis"],
            "recovery_strategy": recovery_data["recovery_strategy"],
            "success_probability": recovery_data["success_probability"]
        }
    
    def assess_action_safety(self, planned_action: str, environment_context: Dict[str, Any],
                           screenshot_path: Optional[str] = None) -> Dict[str, Any]:
        """Use VLM for intelligent safety assessment"""
        
        context_data = {
            "planned_action": planned_action,
            "environment_description": self._describe_environment(environment_context),
            "objects_involved": self._extract_objects_from_action(planned_action),
            "actor_capabilities": environment_context.get("actor_capabilities", "standard")
        }
        
        safety_response = self.vlm_processor.process_vlm_request(
            "safety_assessment",
            context_data,
            screenshot_path
        )
        
        if not safety_response.get("valid", False):
            # Default to conservative safety approach
            return {
                "safe_to_proceed": False,
                "reason": "Safety assessment failed",
                "fallback": True
            }
        
        safety_data = safety_response["data"]["safety_assessment"]
        
        return {
            "safe_to_proceed": safety_data["proceed_with_action"],
            "risk_level": safety_data["overall_risk_level"],
            "identified_risks": safety_data["identified_risks"],
            "recommendations": safety_data["safety_recommendations"],
            "required_modifications": safety_data.get("required_modifications", [])
        }
    
    def _describe_environment(self, environment_context: Dict[str, Any]) -> str:
        """Generate natural language description of environment"""
        # Placeholder - would integrate with scene analysis
        return f"Smart home environment with actor at position {environment_context.get('actor_position', 'unknown')}"
    
    def _list_available_objects(self) -> List[str]:
        """List currently available objects in the environment"""
        obj_manager = CASASObjectManager()
        available = []
        
        for sensor_id, obj_data in obj_manager.casas_objects.items():
            if obj_data["state"] == "PRESENT":
                available.append(f"{obj_data['name']} ({sensor_id}) at {obj_data['location']}")
        
        return available
    
    def _get_recent_action_history(self) -> List[str]:
        """Get recent action history for context"""
        # Placeholder - would integrate with action logging
        return ["actor_moved_to_kitchen", "actor_opened_cabinet"]
    
    def _convert_plan_to_task(self, plan_data: Dict[str, Any], task_goal: str) -> ADLTask:
        """Convert VLM plan to executable ADL task format"""
        
        action_plan = plan_data.get("action_plan", [])
        
        # Convert plan steps to TaskStep objects
        task_steps = []
        for i, step in enumerate(action_plan):
            task_step = TaskStep(
                step_id=f"vlm_step_{i+1}",
                description=step.get("action", f"Step {i+1}"),
                required_objects=self._extract_object_sensors(step.get("target_objects", [])),
                required_location=step.get("target_location", "unknown"),
                validation_criteria={"vlm_generated": True},
                estimated_duration=step.get("estimated_duration", 30.0)
            )
            task_steps.append(task_step)
        
        # Create adaptive task
        adaptive_task = ADLTask(
            task_id=f"vlm_adaptive_{int(time.time())}",
            name=f"VLM Planned: {task_goal}",
            category=ADLCategory.COOKING,  # Default, could be inferred
            description=plan_data.get("overall_strategy", task_goal),
            steps=task_steps,
            total_estimated_duration=sum(step.estimated_duration for step in task_steps),
            success_criteria={"vlm_planned": True, "goal_achieved": True}
        )
        
        return adaptive_task
    
    def _extract_object_sensors(self, object_names: List[str]) -> List[str]:
        """Map object names to CASAS sensor IDs"""
        obj_manager = CASASObjectManager()
        sensor_ids = []
        
        for obj_name in object_names:
            for sensor_id, obj_data in obj_manager.casas_objects.items():
                if obj_data["name"].lower() in obj_name.lower():
                    sensor_ids.append(sensor_id)
                    break
        
        return sensor_ids
    
    def _identify_adaptations(self, plan_data: Dict[str, Any]) -> List[str]:
        """Identify what adaptations the VLM made"""
        adaptations = []
        
        if "potential_obstacles" in plan_data and plan_data["potential_obstacles"]:
            adaptations.append("Identified potential obstacles")
        
        if "overall_strategy" in plan_data:
            adaptations.append("Generated custom strategy")
        
        return adaptations
    
    def _describe_current_environment(self) -> str:
        """Describe current environment state"""
        # Placeholder - would integrate with scene analysis
        return "Kitchen environment with objects on counter"
    
    def _get_previous_recovery_attempts(self) -> List[str]:
        """Get history of previous recovery attempts"""
        return [entry["recovery_type"] for entry in self.adaptation_history[-3:]]
    
    def _extract_objects_from_action(self, action: str) -> List[str]:
        """Extract object names from action description"""
        # Simple keyword extraction - could be enhanced
        obj_manager = CASASObjectManager()
        found_objects = []
        
        for sensor_id, obj_data in obj_manager.casas_objects.items():
            if obj_data["name"].lower() in action.lower():
                found_objects.append(obj_data["name"])
        
        return found_objects
    
    def _log_adaptation(self, failed_action: str, recovery_data: Dict[str, Any]):
        """Log adaptation for learning and improvement"""
        adaptation_entry = {
            "timestamp": time.time(),
            "failed_action": failed_action,
            "recovery_type": recovery_data["recovery_strategy"]["approach"],
            "success_probability": recovery_data["success_probability"],
            "primary_cause": recovery_data["diagnosis"]["primary_cause"]
        }
        
        self.adaptation_history.append(adaptation_entry)

# Integration function for main system
def integrate_vlm_intelligence_with_system():
    """Integration point with existing VESPER system"""
    
    # Initialize intelligent planner
    if not hasattr(bge.logic, 'intelligent_planner'):
        bge.logic.intelligent_planner = IntelligentTaskPlanner()
    
    # Get current context
    scene = bge.logic.getCurrentScene()
    actor = scene.objects.get("Actor")
    
    if not actor:
        return
    
    # Prepare environment context
    environment_context = {
        "actor_position": tuple(actor.worldPosition),
        "actor_capabilities": "standard",
        "scene_objects": [obj.name for obj in scene.objects]
    }
    
    # Check if we need intelligent planning
    planner = bge.logic.intelligent_planner
    
    # Example: Automatically plan task if no task is active
    if not hasattr(bge.logic, 'task_executor') or bge.logic.task_executor.task_status == TaskStatus.NOT_STARTED:
        # Use VLM to suggest and plan next task
        task_plan = planner.plan_adaptive_task(
            "Prepare breakfast with available ingredients",
            environment_context,
            getattr(bge.logic, 'latest_screenshot', None)
        )
        
        if task_plan["success"]:
            print("🧠 VLM generated intelligent task plan")
            # Could automatically start the planned task
    
# Test function for Phase 3 development
def test_vlm_intelligence_system():
    """Test the VLM intelligence enhancement system"""
    print("🧪 Testing VESPER VLM Intelligence Enhancement...")
    
    # Initialize system
    planner = IntelligentTaskPlanner()
    
    # Test adaptive task planning
    print("\n--- Testing Adaptive Task Planning ---")
    environment_context = {
        "actor_position": (2.0, 1.0, 0.0),
        "actor_capabilities": "standard"
    }
    
    task_plan = planner.plan_adaptive_task(
        "Make oatmeal for breakfast",
        environment_context
    )
    
    if task_plan["success"]:
        print("✅ Adaptive task planning successful")
        print(f"📋 Generated {len(task_plan['task_plan'].steps)} steps")
        print(f"🎯 Strategy: {task_plan['task_plan'].description}")
    else:
        print("❌ Adaptive task planning failed")
    
    # Test error recovery
    print("\n--- Testing Intelligent Error Recovery ---")
    error_context = {
        "error_description": "Cannot reach object",
        "actor_status": "blocked by obstacle"
    }
    
    recovery = planner.handle_task_failure_intelligently(
        "pick_up_oatmeal",
        error_context
    )
    
    if recovery["success"]:
        print("✅ Intelligent error recovery successful")
        print(f"🔍 Diagnosis: {recovery['diagnosis']['primary_cause']}")
        print(f"🔄 Recovery approach: {recovery['recovery_strategy']['approach']}")
    else:
        print("❌ Intelligent error recovery failed")
    
    # Test safety assessment
    print("\n--- Testing Safety Assessment ---")
    safety = planner.assess_action_safety(
        "use stove to cook oatmeal",
        environment_context
    )
    
    print(f"🛡️  Safe to proceed: {safety['safe_to_proceed']}")
    print(f"⚠️  Risk level: {safety.get('risk_level', 'unknown')}")
    
    # Get VLM analytics
    print("\n--- VLM Performance Analytics ---")
    analytics = planner.vlm_processor.get_reasoning_analytics()
    if analytics.get("status") != "no_data":
        print(f"📊 Total VLM requests: {analytics['total_requests']}")
        print(f"✅ Success rate: {analytics['success_rate']:.2%}")
        print(f"❌ Error rate: {analytics['error_rate']:.2%}")
    else:
        print("📊 No VLM analytics data available yet")
    
    print("🧪 VLM intelligence system test complete!")

if __name__ == "__main__":
    # Run tests when executed directly
    test_vlm_intelligence_system()
