"""
Simple VLM Demo - Standalone demonstration of VLM tool selection
"""

import json
import sys
import os
from typing import Dict, Any, List

# Configure console encoding for Windows
if sys.platform == "win32":
    try:
        # Try to set UTF-8 encoding
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        # Fallback to safe ASCII
        pass

class SimpleVLMDemo:
    """Simplified VLM tool selection demonstration"""
    
    def __init__(self):
        # Define available tools
        self.available_tools = {
            "camera_service.capture_first_person_view": {
                "description": "Capture first-person view screenshot from actor's perspective",
                "parameters": ["actor_name"],
                "category": "perception"
            },
            "spatial_service.get_current_position": {
                "description": "Get the current 3D position of the specified actor",
                "parameters": ["actor_name"],
                "category": "information"
            },
            "movement_service.move_to_room": {
                "description": "Move actor to a specific room",
                "parameters": ["target_room", "actor_name"],
                "category": "action"
            },
            "image_analysis_service.analyze_room_from_image": {
                "description": "Analyze an image to determine room type and identify objects",
                "parameters": ["image_path", "detailed_analysis"],
                "category": "perception"
            },
            "spatial_service.get_navigation_context": {
                "description": "Get comprehensive navigation context for the actor",
                "parameters": ["actor_name", "target_room"],
                "category": "planning"
            }
        }
    
    def generate_tool_prompt(self) -> str:
        """Generate tool list for VLM prompt"""
        
        # Group tools by category
        categories = {
            "PERCEPTION TOOLS": [],
            "INFORMATION TOOLS": [],
            "PLANNING TOOLS": [],
            "ACTION TOOLS": []
        }
        
        for tool_name, tool_info in self.available_tools.items():
            category_name = f"{tool_info['category'].upper()} TOOLS"
            if category_name not in categories:
                categories[category_name] = []
            
            params = ", ".join(tool_info['parameters'])
            tool_line = f"  - {tool_name}({params}): {tool_info['description']}"
            categories[category_name].append(tool_line)
        
        # Build prompt
        prompt_parts = ["AVAILABLE MICROSERVICE TOOLS:", ""]
        for category, tools in categories.items():
            if tools:
                prompt_parts.append(f"{category}:")
                prompt_parts.extend(tools)
                prompt_parts.append("")
        
        return "\n".join(prompt_parts)
    
    def generate_context_prompt(self, task: str, context: Dict[str, Any]) -> str:
        """Generate complete context prompt for VLM"""
        
        tool_prompt = self.generate_tool_prompt()
        
        context_prompt = f"""
{tool_prompt}
{"=" * 80}

CURRENT CONTEXT:
Task: {task}
Current Room: {context.get('room', 'unknown')}
Actor Position: {context.get('position', [0.0, 0.0, 0.0])}
Visible Objects: {', '.join(context.get('objects', [])) or '[none detected]'}
Images Available: {'Yes' if context.get('has_image') else 'No'}

INSTRUCTION:
Based on the current context and available tools, select the most appropriate tool to call next.
Provide your response in the following format:
TOOL: service_name.tool_name
PARAMETERS: {{parameter_dict}}
REASONING: Brief explanation of why this tool is appropriate
"""
        return context_prompt.strip()
    
    def expert_action(self, task: str, context: Dict[str, Any], step: int) -> Dict[str, Any]:
        """Rule-based expert action selection"""
        
        task_lower = task.lower()
        
        # Navigation tasks
        if "navigate to" in task_lower or "go to" in task_lower:
            if step == 0:
                return {
                    "tool": "spatial_service.get_current_position",
                    "parameters": {"actor_name": "Actor"},
                    "reasoning": "Need to know current position before navigation"
                }
            elif step == 1:
                # Extract target room
                target_room = "kitchen"  # Default
                for room in ["kitchen", "bedroom", "bathroom", "living_room"]:
                    if room in task_lower:
                        target_room = room
                        break
                
                return {
                    "tool": "movement_service.move_to_room",
                    "parameters": {"target_room": target_room, "actor_name": "Actor"},
                    "reasoning": f"Move to the target room: {target_room}"
                }
        
        # Analysis tasks
        elif "analyze" in task_lower or "identify" in task_lower:
            if step == 0:
                return {
                    "tool": "camera_service.capture_first_person_view",
                    "parameters": {"actor_name": "Actor"},
                    "reasoning": "Need current view to analyze room content"
                }
            elif step == 1:
                return {
                    "tool": "image_analysis_service.analyze_room_from_image",
                    "parameters": {"image_path": "/path/to/image.png", "detailed_analysis": True},
                    "reasoning": "Analyze captured image to identify room type and objects"
                }
        
        # Default action
        return {
            "tool": "spatial_service.get_current_position",
            "parameters": {"actor_name": "Actor"},
            "reasoning": "Get current state as starting point"
        }
    
    def demonstrate_vlm_training(self):
        """Demonstrate VLM training data generation"""
        
        print(">>> VLM Tool Selection Demo")
        print("=" * 50)
        
        # Define test scenarios
        scenarios = [
            {
                "task": "Navigate to the kitchen",
                "context": {"room": "living_room", "position": [0, 0, 0], "objects": ["sofa", "tv"], "has_image": False}
            },
            {
                "task": "Analyze the current room",
                "context": {"room": "unknown", "position": [2, 1, 0], "objects": [], "has_image": False}
            },
            {
                "task": "Navigate to the bedroom",
                "context": {"room": "hallway", "position": [-1, 0, 0], "objects": ["door"], "has_image": True}
            }
        ]
        
        for i, scenario in enumerate(scenarios):
            print(f"\n📋 Scenario {i+1}: {scenario['task']}")
            print("-" * 40)
            
            # Generate training prompt
            prompt = self.generate_context_prompt(scenario['task'], scenario['context'])
            
            # Get expert action for first step
            expert_action = self.expert_action(scenario['task'], scenario['context'], 0)
            
            print("🔍 VLM Training Input:")
            print(prompt)
            
            print(f"\n🎯 Expected VLM Output:")
            print(f"TOOL: {expert_action['tool']}")
            print(f"PARAMETERS: {json.dumps(expert_action['parameters'])}")
            print(f"REASONING: {expert_action['reasoning']}")
            
            print("\n" + "=" * 60)
        
        print("\n[OK] VLM Training Demo Complete!")
        print("\nThis demonstrates how the VLM training system works:")
        print("1. [DATA] Context gathering from microservices")
        print("2. [PROMPT] Prompt generation with available tools")
        print("3. [EXPERT] Expert action selection for training")
        print("4. [TRAIN] Labeled examples for model fine-tuning")

def main():
    """Run the VLM demo"""
    demo = SimpleVLMDemo()
    demo.demonstrate_vlm_training()

if __name__ == "__main__":
    main()
