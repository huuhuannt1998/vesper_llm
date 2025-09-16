"""
Intelligent Camera Selection System for VLM Navigation
====================================================

This system allows the VLM to intelligently choose between bird-eye view
and first-person view based on the current navigation context, task type,
and specific situational needs.

Integration with MCP Server Tools:
- Uses MCP spatial analysis for context assessment
- Leverages MCP task planning for camera recommendations
- Provides dynamic camera selection based on navigation state
"""

import bge
import json
import time
from typing import Dict, Optional, Tuple, List, Any

class IntelligentCameraSelector:
    """Manages intelligent camera selection for VLM navigation"""
    
    def __init__(self):
        self.selection_history = []
        self.max_history = 10
        self.camera_performance = {
            "bird_eye": {"success_count": 0, "total_count": 0},
            "first_person": {"success_count": 0, "total_count": 0}
        }
        
    def analyze_navigation_context(self, actor_position: Tuple[float, float, float],
                                 current_task: Optional[str] = None,
                                 recent_movements: Optional[List] = None) -> Dict[str, Any]:
        """Analyze current navigation context to inform camera selection"""
        
        context = {
            "actor_position": actor_position,
            "current_task": current_task,
            "movement_pattern": "unknown",
            "spatial_complexity": "medium",
            "obstacle_density": "unknown",
            "room_transition": False,
            "task_phase": "navigation"
        }
        
        # Analyze movement patterns
        if recent_movements and len(recent_movements) >= 3:
            # Check for stuck/repeated positions
            unique_positions = len(set(str(pos) for pos in recent_movements[-6:]))
            if unique_positions <= 2:
                context["movement_pattern"] = "stuck"
            elif unique_positions <= 4:
                context["movement_pattern"] = "exploring"
            else:
                context["movement_pattern"] = "progressing"
        
        # Determine task phase
        if current_task:
            task_lower = current_task.lower()
            if any(word in task_lower for word in ["find", "go to", "navigate", "move"]):
                context["task_phase"] = "navigation"
            elif any(word in task_lower for word in ["cook", "prepare", "use", "operate"]):
                context["task_phase"] = "interaction"
            elif any(word in task_lower for word in ["relax", "sit", "watch", "rest"]):
                context["task_phase"] = "positioning"
        
        # Basic room detection (can be enhanced with MCP spatial tools)
        x, y, z = actor_position
        if x < -2.0 and y > 1.0:
            context["current_room"] = "kitchen"
        elif x > -1.0 and y > 1.0:
            context["current_room"] = "dining_room"
        elif x < 0 and y < 1.0:
            context["current_room"] = "living_room"
        elif x > 0 and y < 1.0:
            context["current_room"] = "bedroom"
        else:
            context["current_room"] = "hallway"
        
        return context
    
    def query_vlm_for_camera_preference(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Ask VLM which camera view would be most helpful for current situation"""
        
        # Create a focused prompt for camera selection
        prompt_parts = [
            "🎥 CAMERA SELECTION DECISION",
            "=" * 35,
            "",
            "📍 CURRENT SITUATION:",
            f"   Actor Position: {context['actor_position']}",
            f"   Current Task: {context.get('current_task', 'Unknown')}",
            f"   Room: {context.get('current_room', 'Unknown')}",
            f"   Movement Pattern: {context.get('movement_pattern', 'Unknown')}",
            f"   Task Phase: {context.get('task_phase', 'Unknown')}",
            "",
            "🎯 CAMERA OPTIONS:",
            "",
            "📐 BIRD-EYE VIEW - Best for:",
            "   • Room layout understanding",
            "   • Path planning and obstacle avoidance", 
            "   • Furniture identification and spatial relationships",
            "   • Getting unstuck from repeated positions",
            "   • Understanding overall room structure",
            "",
            "👁️ FIRST-PERSON VIEW - Best for:",
            "   • Detailed object interaction",
            "   • Precise positioning near furniture",
            "   • Reading labels or small details",
            "   • Understanding what's directly accessible",
            "   • Fine-tuned navigation adjustments",
            "",
            "💡 DECISION CRITERIA:",
            "   • If stuck/repeating positions → Bird-eye (for path planning)",
            "   • If exploring new room → Bird-eye (for layout understanding)",
            "   • If near target furniture → First-person (for interaction)",
            "   • If task requires precision → First-person (for details)",
            "   • If need room overview → Bird-eye (for spatial context)",
            "",
            "🎯 RESPOND WITH JSON DECISION:",
            '{',
            '  "camera_choice": "bird_eye" | "first_person",',
            '  "reasoning": "Why this camera view is best for current situation",',
            '  "confidence": 0.0-1.0,',
            '  "expected_benefit": "What this view will help accomplish"',
            '}'
        ]
        
        prompt = "\n".join(prompt_parts)
        
        try:
            # Use MCP LLM integration if available
            if hasattr(self, '_query_mcp_llm'):
                response = self._query_mcp_llm(prompt)
            else:
                # Fallback to direct LLM query
                response = self._query_llm_direct(prompt)
            
            # Parse response
            return self._parse_camera_decision(response)
            
        except Exception as e:
            print(f"❌ VLM camera selection query failed: {e}")
            return self._fallback_camera_decision(context)
    
    def _query_llm_direct(self, prompt: str) -> str:
        """Direct LLM query for camera selection"""
        
        try:
            # Use existing LLM infrastructure from backend
            from backend.app.llm.client import client, HOST, MODEL
            
            if not client:
                raise Exception("No LLM client available")
            
            # Use Ollama chat format
            response = client.chat(
                model=MODEL,
                messages=[{
                    "role": "user", 
                    "content": prompt
                }],
                options={
                    'temperature': 0.1,
                    'num_predict': 300
                }
            )
            
            return response['message']['content']
            
        except Exception as e:
            print(f"⚠️ Direct LLM query failed: {e}")
            raise
    
    def _parse_camera_decision(self, response: str) -> Dict[str, Any]:
        """Parse VLM response for camera decision"""
        
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{[^}]*\}', response, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(0)
                decision = json.loads(json_str)
                
                # Validate required fields
                camera_choice = decision.get("camera_choice", "").lower()
                if camera_choice not in ["bird_eye", "first_person"]:
                    raise ValueError(f"Invalid camera choice: {camera_choice}")
                
                return {
                    "camera_choice": camera_choice,
                    "reasoning": decision.get("reasoning", "No reasoning provided"),
                    "confidence": float(decision.get("confidence", 0.5)),
                    "expected_benefit": decision.get("expected_benefit", ""),
                    "source": "vlm_decision"
                }
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            print(f"⚠️ Failed to parse camera decision: {e}")
            print(f"🔍 Raw response: {response[:200]}...")
            
            # Try to extract camera choice from text
            response_lower = response.lower()
            if "bird" in response_lower and "eye" in response_lower:
                return {
                    "camera_choice": "bird_eye",
                    "reasoning": "Extracted from text analysis",
                    "confidence": 0.3,
                    "expected_benefit": "Layout understanding",
                    "source": "text_extraction"
                }
            elif "first" in response_lower and "person" in response_lower:
                return {
                    "camera_choice": "first_person", 
                    "reasoning": "Extracted from text analysis",
                    "confidence": 0.3,
                    "expected_benefit": "Detail interaction",
                    "source": "text_extraction"
                }
            else:
                raise ValueError("Could not extract camera choice")
    
    def _fallback_camera_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback camera decision based on heuristics"""
        
        # Rule-based fallback decisions
        movement_pattern = context.get("movement_pattern", "unknown")
        task_phase = context.get("task_phase", "navigation")
        
        # If stuck, use bird-eye for path planning
        if movement_pattern == "stuck":
            return {
                "camera_choice": "bird_eye",
                "reasoning": "Actor appears stuck, need room overview for path planning",
                "confidence": 0.8,
                "expected_benefit": "Find alternative path",
                "source": "fallback_heuristic"
            }
        
        # If in interaction phase, use first-person
        if task_phase == "interaction":
            return {
                "camera_choice": "first_person",
                "reasoning": "Task requires interaction, need detailed view",
                "confidence": 0.7,
                "expected_benefit": "Precise positioning for interaction",
                "source": "fallback_heuristic"
            }
        
        # Default to bird-eye for navigation
        return {
            "camera_choice": "bird_eye",
            "reasoning": "Default choice for navigation tasks",
            "confidence": 0.5,
            "expected_benefit": "Room layout understanding",
            "source": "fallback_default"
        }
    
    def select_optimal_camera(self, actor_position: Tuple[float, float, float],
                            current_task: Optional[str] = None,
                            recent_movements: Optional[List] = None,
                            force_decision: bool = False) -> Dict[str, Any]:
        """
        Main function to select optimal camera view
        
        Args:
            actor_position: Current actor position
            current_task: Current navigation task
            recent_movements: Recent movement history
            force_decision: Force VLM decision even if heuristics are confident
        
        Returns:
            Camera selection decision with reasoning
        """
        
        print("🎥 Analyzing optimal camera view...")
        
        # Analyze context
        context = self.analyze_navigation_context(
            actor_position, current_task, recent_movements
        )
        
        print(f"📊 Context: {context['movement_pattern']} movement, {context['task_phase']} phase")
        
        # Check if we should use quick heuristics or ask VLM
        if not force_decision:
            heuristic_decision = self._try_quick_heuristics(context)
            if heuristic_decision and heuristic_decision.get("confidence", 0) > 0.7:
                print(f"🚀 Quick decision: {heuristic_decision['camera_choice']} (confidence: {heuristic_decision['confidence']:.2f})")
                return heuristic_decision
        
        # Query VLM for intelligent decision
        print("🧠 Querying VLM for camera selection...")
        decision = self.query_vlm_for_camera_preference(context)
        
        # Record decision in history
        self._record_decision(decision, context)
        
        print(f"✅ VLM Decision: {decision['camera_choice']}")
        print(f"💭 Reasoning: {decision['reasoning']}")
        print(f"🎯 Expected: {decision['expected_benefit']}")
        
        return decision
    
    def _try_quick_heuristics(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Try quick heuristic-based decisions for common scenarios"""
        
        movement_pattern = context.get("movement_pattern")
        task_phase = context.get("task_phase")
        
        # High-confidence heuristics
        if movement_pattern == "stuck":
            return {
                "camera_choice": "bird_eye",
                "reasoning": "Actor stuck - need overview for new path",
                "confidence": 0.9,
                "expected_benefit": "Find way around obstacle",
                "source": "heuristic_stuck"
            }
        
        if task_phase == "interaction" and movement_pattern == "progressing":
            return {
                "camera_choice": "first_person",
                "reasoning": "Interaction task with good movement - need detail view",
                "confidence": 0.8,
                "expected_benefit": "Precise object interaction",
                "source": "heuristic_interaction"
            }
        
        return None
    
    def _record_decision(self, decision: Dict[str, Any], context: Dict[str, Any]):
        """Record decision for learning and performance tracking"""
        
        record = {
            "timestamp": time.time(),
            "decision": decision,
            "context": context,
            "success": None  # Will be updated later based on results
        }
        
        self.selection_history.append(record)
        
        # Trim history
        if len(self.selection_history) > self.max_history:
            self.selection_history.pop(0)
    
    def update_decision_success(self, success: bool):
        """Update the success status of the most recent decision"""
        
        if self.selection_history:
            self.selection_history[-1]["success"] = success
            
            # Update performance metrics
            camera_choice = self.selection_history[-1]["decision"]["camera_choice"]
            self.camera_performance[camera_choice]["total_count"] += 1
            if success:
                self.camera_performance[camera_choice]["success_count"] += 1
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get camera selection performance statistics"""
        
        stats = {}
        for camera, perf in self.camera_performance.items():
            total = perf["total_count"]
            success = perf["success_count"]
            stats[camera] = {
                "total_decisions": total,
                "successful_decisions": success,
                "success_rate": success / total if total > 0 else 0.0
            }
        
        return stats

# Global instance
intelligent_camera_selector = IntelligentCameraSelector()

def select_camera_intelligently(actor_position: Tuple[float, float, float],
                               current_task: Optional[str] = None,
                               recent_movements: Optional[List] = None) -> Dict[str, Any]:
    """
    Select optimal camera view using intelligent analysis
    
    Returns:
        {
            "camera_choice": "bird_eye" | "first_person",
            "reasoning": "Why this choice was made",
            "confidence": 0.0-1.0,
            "expected_benefit": "What this will help accomplish"
        }
    """
    return intelligent_camera_selector.select_optimal_camera(
        actor_position, current_task, recent_movements
    )

def capture_with_intelligent_camera(actor_position: Tuple[float, float, float],
                                  actor_orientation: Tuple[float, float, float],
                                  current_task: Optional[str] = None,
                                  recent_movements: Optional[List] = None) -> Dict[str, Any]:
    """
    Capture screenshot using intelligently selected camera
    
    Returns:
        {
            "success": bool,
            "camera_used": "bird_eye" | "first_person", 
            "image_path": "path/to/screenshot.png",
            "selection_reasoning": "Why this camera was chosen"
        }
    """
    
    print("🎬 Starting intelligent camera capture...")
    
    # Select optimal camera
    selection = select_camera_intelligently(actor_position, current_task, recent_movements)
    
    camera_choice = selection["camera_choice"]
    
    try:
        if camera_choice == "bird_eye":
            # Capture bird-eye view
            from llm_bge_navigation import request_bird_eye_screenshot, poll_screenshot_ready
            
            shot_path = request_bird_eye_screenshot()
            if not shot_path:
                raise Exception("Bird-eye screenshot request failed")
            
            # Poll for completion
            start_time = time.time()
            while time.time() - start_time < 10.0:
                result = poll_screenshot_ready()
                if result and result != "TIMEOUT":
                    return {
                        "success": True,
                        "camera_used": "bird_eye",
                        "image_path": result,
                        "selection_reasoning": selection["reasoning"],
                        "confidence": selection["confidence"]
                    }
                time.sleep(0.2)
            
            raise Exception("Bird-eye screenshot timeout")
            
        else:  # first_person
            # Capture first-person view
            from first_person_camera import capture_immediate_first_person_view
            
            result = capture_immediate_first_person_view(actor_position, actor_orientation)
            
            if result["success"]:
                return {
                    "success": True,
                    "camera_used": "first_person",
                    "image_path": result["path"],
                    "selection_reasoning": selection["reasoning"],
                    "confidence": selection["confidence"]
                }
            else:
                raise Exception(f"First-person capture failed: {result.get('error', 'Unknown')}")
                
    except Exception as e:
        print(f"❌ Intelligent camera capture failed: {e}")
        
        # Update decision as failed
        intelligent_camera_selector.update_decision_success(False)
        
        return {
            "success": False,
            "error": str(e),
            "camera_used": camera_choice,
            "selection_reasoning": selection["reasoning"]
        }

def get_camera_selection_stats() -> Dict[str, Any]:
    """Get camera selection performance statistics"""
    return intelligent_camera_selector.get_performance_stats()

print("✅ Intelligent Camera Selection System loaded")
