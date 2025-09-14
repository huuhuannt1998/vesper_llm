"""
ASCII-only VLM Demo - Windows-compatible demonstration of VLM tool selection
"""

import json
from typing import Dict, Any, List

class WindowsVLMDemo:
    """Windows-compatible VLM tool selection demonstration"""
    
    def __init__(self):
        self.tool_metadata = {
            "navigate_to_location": {
                "description": "Navigate to a specific location",
                "parameters": ["target_location"],
                "context_requirements": ["current_position"]
            },
            "analyze_room": {
                "description": "Analyze the current room",
                "parameters": ["analysis_type"],
                "context_requirements": ["current_view"]
            },
            "control_device": {
                "description": "Control smart home devices",
                "parameters": ["device_id", "action"],
                "context_requirements": ["device_status"]
            }
        }
    
    def run_demo(self):
        """Run the complete demo"""
        
        print("VLM Tool Selection Training Demo")
        print("=" * 40)
        print()
        
        scenarios = [
            {
                "task": "Navigate to kitchen",
                "context": {"current_location": "living_room"},
                "expected_tool": "navigate_to_location"
            },
            {
                "task": "Analyze current room",
                "context": {"current_location": "bedroom"},
                "expected_tool": "analyze_room"
            },
            {
                "task": "Turn on lights",
                "context": {"device_available": "light_switch"},
                "expected_tool": "control_device"
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"Scenario {i}: {scenario['task']}")
            print("-" * 30)
            
            # Show context
            print("Context:")
            for key, value in scenario['context'].items():
                print(f"  {key}: {value}")
            
            # Show available tools
            print("\nAvailable Tools:")
            for tool_name, tool_info in self.tool_metadata.items():
                print(f"  - {tool_name}: {tool_info['description']}")
            
            # Show expected result
            print(f"\nExpected Tool Selection: {scenario['expected_tool']}")
            
            # Show training format
            training_example = self.generate_training_example(scenario)
            print("\nTraining Example Format:")
            print(json.dumps(training_example, indent=2))
            
            print("\n" + "=" * 50)
        
        print("\nDemo Complete!")
        print("\nKey Training Components:")
        print("1. Context gathering from environment")
        print("2. Tool metadata and capabilities")
        print("3. Expert demonstrations for labeling")
        print("4. Structured training data format")
        print("5. VLM fine-tuning on tool selection")
        
        return True
    
    def generate_training_example(self, scenario):
        """Generate training example in the correct format"""
        
        # Create VLM prompt
        prompt_parts = ["Task: " + scenario['task']]
        prompt_parts.append("Context:")
        for key, value in scenario['context'].items():
            prompt_parts.append(f"  {key}: {value}")
        
        prompt_parts.append("Available Tools:")
        for tool_name, tool_info in self.tool_metadata.items():
            prompt_parts.append(f"  - {tool_name}: {tool_info['description']}")
        
        prompt_parts.append("Select the most appropriate tool:")
        
        return {
            "input": "\n".join(prompt_parts),
            "output": scenario['expected_tool'],
            "metadata": {
                "task_type": "tool_selection",
                "context": scenario['context'],
                "available_tools": list(self.tool_metadata.keys())
            }
        }

def main():
    """Run the Windows-compatible demo"""
    demo = WindowsVLMDemo()
    success = demo.run_demo()
    
    if success:
        print("\nSystem ready for full training pipeline!")
        return 0
    else:
        print("\nDemo failed!")
        return 1

if __name__ == "__main__":
    exit(main())
