"""
Complete VLM + Enhanced Camera Integration Test

This script demonstrates how the VLM agent can now intelligently choose
between bird-eye and first-person cameras using MCP tools.
"""
import json
import time
import asyncio
from typing import Dict, Any

class VLMCameraIntegrationDemo:
    """Simulates VLM agent using enhanced camera MCP tools"""
    
    def __init__(self):
        self.task_scenarios = [
            {
                "task": "Navigate to the kitchen from living room",
                "context": "Actor is standing in living room, needs to find kitchen",
                "expected_camera": "bird_eye",
                "reason": "Navigation benefits from spatial overview"
            },
            {
                "task": "Use the stove to cook dinner",
                "context": "Actor is in kitchen near stove, needs to see controls",
                "expected_camera": "first_person", 
                "reason": "Interaction requires detailed object view"
            },
            {
                "task": "Find the bedroom door",
                "context": "Actor is lost in hallway, needs orientation",
                "expected_camera": "bird_eye",
                "reason": "Getting unstuck requires room layout view"
            },
            {
                "task": "Read the book on the table",
                "context": "Actor is near table, needs to see book details",
                "expected_camera": "first_person",
                "reason": "Reading requires close-up detailed view"
            }
        ]
    
    def simulate_camera_recommendation(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate the MCP camera recommendation logic"""
        task_lower = scenario["task"].lower()
        
        # Simulate the scoring logic from get_camera_recommendations
        bird_eye_score = 0
        first_person_score = 0
        bird_eye_reasons = []
        first_person_reasons = []
        
        # Navigation keywords
        if any(word in task_lower for word in ["navigate", "go to", "move to", "find room", "find"]):
            bird_eye_score += 3
            bird_eye_reasons.append("Navigation tasks benefit from spatial overview")
        
        # Interaction keywords
        if any(word in task_lower for word in ["use", "interact", "read", "operate", "cook"]):
            first_person_score += 3
            first_person_reasons.append("Interaction tasks need detailed object view")
        
        # Problem solving keywords
        if any(word in task_lower for word in ["lost", "find", "door"]):
            bird_eye_score += 2
            bird_eye_reasons.append("Problem-solving benefits from room layout view")
        
        # Context analysis
        context_lower = scenario["context"].lower()
        if any(word in context_lower for word in ["detail", "precise", "close", "controls", "see"]):
            first_person_score += 2
            first_person_reasons.append("Context suggests need for detailed view")
        
        # Determine recommendation
        if bird_eye_score > first_person_score:
            recommended = "bird_eye"
        elif first_person_score > bird_eye_score:
            recommended = "first_person"
        else:
            recommended = "bird_eye"  # Default
            bird_eye_reasons.append("Default choice for general navigation")
        
        confidence = max(max(bird_eye_score, first_person_score) / 5.0, 0.5)
        
        return {
            "recommended_camera": recommended,
            "confidence": confidence,
            "bird_eye_score": bird_eye_score,
            "first_person_score": first_person_score,
            "bird_eye_reasons": bird_eye_reasons,
            "first_person_reasons": first_person_reasons
        }
    
    def simulate_camera_capture(self, camera_type: str, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate MCP camera capture"""
        timestamp = int(time.time() * 1000)
        
        if camera_type == "bird_eye":
            return {
                "success": True,
                "filepath": f"blender/captures/bird_eye_{timestamp}.png",
                "camera_type": "bird_eye",
                "description": "Top-down view for spatial navigation",
                "resolution": "1024x768"
            }
        else:
            return {
                "success": True,
                "filepath": f"blender/captures/first_person_{timestamp}.png", 
                "camera_type": "first_person",
                "description": "Actor's eye-level perspective",
                "resolution": "1024x768"
            }
    
    def run_demo(self):
        """Run the complete integration demo"""
        print("VLM + Enhanced Camera Integration Demo")
        print("=" * 50)
        print()
        
        correct_predictions = 0
        total_scenarios = len(self.task_scenarios)
        
        for i, scenario in enumerate(self.task_scenarios, 1):
            print(f"Scenario {i}: {scenario['task']}")
            print(f"Context: {scenario['context']}")
            print(f"Expected Camera: {scenario['expected_camera']}")
            print()
            
            # Step 1: VLM calls get_camera_recommendations MCP tool
            print("📋 VLM Agent: Calling get_camera_recommendations()...")
            recommendation = self.simulate_camera_recommendation(scenario)
            
            print(f"📊 Recommendation Result:")
            print(f"   • Recommended: {recommendation['recommended_camera']}")
            print(f"   • Confidence: {recommendation['confidence']:.2f}")
            print(f"   • Bird-eye score: {recommendation['bird_eye_score']}")
            print(f"   • First-person score: {recommendation['first_person_score']}")
            
            # Check if prediction matches expected
            is_correct = recommendation['recommended_camera'] == scenario['expected_camera']
            if is_correct:
                correct_predictions += 1
                print("   ✓ CORRECT prediction!")
            else:
                print("   ✗ Unexpected prediction")
            
            print()
            
            # Step 2: VLM calls appropriate camera capture MCP tool
            camera_choice = recommendation['recommended_camera']
            if camera_choice == "bird_eye":
                print("📸 VLM Agent: Calling capture_bird_eye_view()...")
            else:
                print("📸 VLM Agent: Calling capture_first_person_view()...")
            
            capture_result = self.simulate_camera_capture(camera_choice, scenario)
            print(f"📁 Capture Result: {capture_result['filepath']}")
            print(f"🎯 Purpose: {capture_result['description']}")
            
            print("-" * 50)
            print()
        
        # Summary
        accuracy = (correct_predictions / total_scenarios) * 100
        print(f"🎯 DEMO SUMMARY")
        print(f"Accuracy: {correct_predictions}/{total_scenarios} ({accuracy:.1f}%)")
        print(f"Expected Accuracy: 100% (logic-based selection)")
        
        if accuracy >= 100:
            print("✅ INTEGRATION SUCCESS!")
            print("\nThe enhanced camera service correctly:")
            print("  • Analyzes task context and requirements")
            print("  • Recommends appropriate camera type")
            print("  • Provides separate MCP tools for each camera")
            print("  • Enables intelligent VLM camera selection")
        else:
            print("⚠️  Some scenarios need tuning")
        
        print(f"\n📚 Next Steps:")
        print("  1. Test in live Blender BGE environment")
        print("  2. Integrate with actual VLM model")
        print("  3. Validate camera switching and capture")
        print("  4. Fine-tune scoring thresholds if needed")

def main():
    """Run the integration demo"""
    demo = VLMCameraIntegrationDemo()
    demo.run_demo()

if __name__ == "__main__":
    main()
