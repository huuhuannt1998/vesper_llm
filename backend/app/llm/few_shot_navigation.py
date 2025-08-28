"""
VESPER Few-Shot Navigation Prompting System
This module implements few-shot prompting to improve navigation accuracy
"""

import os
import json

class VESPERFewShotPrompts:
    """
    Few-shot prompting system for VESPER navigation
    """
    
    def __init__(self, captures_dir):
        self.captures_dir = captures_dir
        
        # Dedicated folder for few-shot training images
        self.few_shot_images_dir = os.path.join(
            os.path.dirname(__file__), 
            "few_shot_images"
        )
        
        # System prompt with clear rules for multi-step navigation
        self.system_prompt = """You are VESPER's navigation VLM. Return STRICT JSON only (no markdown).

JSON Fields: current_room, furniture_visible, task_complete, movement_sequence, reasoning.

RULES:
- movement_sequence: List of moves to reach destination. Each move: ["UP","DOWN","LEFT","RIGHT","STAY"].
- Plan complete path to target room - don't just make one move.
- Use STAY only when already at destination or blocked.
- If the image is ambiguous, choose the most plausible path based on corridors/doorways.
- current_room must be one of: KITCHEN, BATHROOM, BEDROOM, LIVING_ROOM, UNKNOWN.
- Keep reasoning ≤ 50 words to explain the path.
- Plan efficient routes - avoid unnecessary detours.

SAFETY:
- Only move through areas with visible floors and furniture
- NEVER move toward dark/black void areas outside the house
- If unclear, choose the safest path toward visible furniture/rooms"""

        # Few-shot examples using dedicated training images
        # Images should be manually copied to backend/app/llm/few_shot_images/ folder
        self.few_shot_examples = [
            {
                "task": "Go to kitchen",
                "image_path": "living_room_to_kitchen.png",  # Copy your best example here
                "gold_response": {
                    "current_room": "LIVING_ROOM",
                    "furniture_visible": ["SOFA", "COFFEE_TABLE"],
                    "task_complete": False,
                    "movement_sequence": ["UP", "UP", "UP", "UP", "RIGHT", "RIGHT", "RIGHT", "RIGHT", "RIGHT", "DOWN", "DOWN", "DOWN"],
                    "reasoning": "In living room, need to go through hallway north, then east corridor, then south into kitchen."
                }
            },
            {
                "task": "Go to bathroom",
                "image_path": "hallway_to_bathroom.png",  # Copy appropriate example
                "gold_response": {
                    "current_room": "HALLWAY",
                    "furniture_visible": [],
                    "task_complete": False,
                    "movement_sequence": ["LEFT", "LEFT", "DOWN", "DOWN", "DOWN"],
                    "reasoning": "From hallway, go right toward bathroom area, then go down to enter bathroom."
                }
            },
            {
                "task": "Rest in bedroom",
                "image_path": "inside_bedroom.png",  # Copy example where actor is already in bedroom
                "gold_response": {
                    "current_room": "BEDROOM",
                    "furniture_visible": ["BED", "NIGHTSTAND"],
                    "task_complete": True,
                    "movement_sequence": ["STAY"],
                    "reasoning": "Already in bedroom with bed visible; task complete, no movement needed."
                }
            },
            {
                "task": "Go to living room",
                "image_path": "hallway_to_living_room.png",  # Copy appropriate example
                "gold_response": {
                    "current_room": "HALLWAY",
                    "furniture_visible": [],
                    "task_complete": False,
                    "movement_sequence": ["LEFT", "LEFT", "LEFT", "LEFT", "LEFT", "LEFT", "DOWN", "DOWN", "DOWN", "DOWN", "DOWN", "DOWN", "DOWN", "LEFT", "LEFT", "LEFT"],
                    "reasoning": "From hallway, go south then west to reach living room with furniture."
                }
            },
            {
                "task": "Cook in kitchen",
                "image_path": "near_kitchen_entrance.png",  # Copy example near kitchen
                "gold_response": {
                    "current_room": "HALLWAY",
                    "furniture_visible": [],
                    "task_complete": False,
                    "movement_sequence": ["LEFT", "LEFT", "LEFT", "DOWN", "DOWN", "DOWN", "DOWN"],
                    "reasoning": "Near kitchen area, go east into kitchen corridor then south to reach cooking area."
                }
            }
        ]
        
        # Anti-pattern example (what NOT to do) - using dedicated training image
        self.negative_example = {
            "task": "Go to bathroom",
            "image_path": "ambiguous_corridor.png",  # Copy an ambiguous corridor image
            "bad_response": {
                "current_room": "UNKNOWN",
                "furniture_visible": [],
                "task_complete": False,
                "movement_sequence": ["STAY"],
                "reasoning": "Uncertain."
            },
            "explanation": "INCORRECT: When uncertain in corridor, prefer single step toward likely goal rather than STAY."
        }

    def build_few_shot_prompt(self, current_task, current_image_path):
        """
        Build the complete few-shot prompt with examples and current query
        """
        prompt_parts = [self.system_prompt]
        
        # Add few-shot examples
        prompt_parts.append("\n=== EXAMPLES ===")
        
        for i, example in enumerate(self.few_shot_examples, 1):
            prompt_parts.append(f"\nExample {i}:")
            prompt_parts.append(f"Task: {example['task']}")
            prompt_parts.append(f"Image: {example['image_path']}")
            prompt_parts.append("Response:")
            prompt_parts.append(json.dumps(example['gold_response'], indent=2))
        
        # Add negative example
        prompt_parts.append(f"\nAnti-pattern (DO NOT DO THIS):")
        prompt_parts.append(f"Task: {self.negative_example['task']}")
        prompt_parts.append("BAD Response:")
        prompt_parts.append(json.dumps(self.negative_example['bad_response'], indent=2))
        prompt_parts.append(f"Why bad: {self.negative_example['explanation']}")
        
        # Add current query
        prompt_parts.append(f"\n=== CURRENT QUERY ===")
        prompt_parts.append(f"Task: {current_task}")
        prompt_parts.append(f"Image: {current_image_path}")
        prompt_parts.append("Return STRICT JSON only. One action in movement_sequence.")
        
        return "\n".join(prompt_parts)

    def get_messages_format(self, current_task, current_image_path):
        """
        Build messages in the format expected by vision models
        For multi-modal APIs like OpenAI GPT-4V or similar
        """
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add few-shot examples as conversation history
        for example in self.few_shot_examples:
            # User message with task
            messages.append({
                "role": "user", 
                "content": [
                    {"type": "text", "text": f"Task: {example['task']}\nReturn STRICT JSON."},
                    {"type": "image_url", "image_url": {"url": f"file://{os.path.join(self.few_shot_images_dir, example['image_path'])}"}}
                ]
            })
            
            # Assistant response with gold JSON
            messages.append({
                "role": "assistant",
                "content": json.dumps(example['gold_response'])
            })
        
        # Add current query
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": f"Task: {current_task}\nReturn STRICT JSON."},
                {"type": "image_url", "image_url": {"url": f"file://{current_image_path}"}}
            ]
        })
        
        return messages

    def customize_examples_from_logs(self, log_data):
        """
        Helper to create few-shot examples from your actual game logs
        Call this with successful navigation sequences to build real examples
        """
        # You would implement this to parse your logs and extract good examples
        # For now, this is a placeholder for the manual process
        pass

def validate_json_response(response_text):
    """
    Validate that the response is proper JSON with required fields
    Now supports multi-step movement sequences
    """
    try:
        data = json.loads(response_text.strip())
        required_fields = ["current_room", "furniture_visible", "task_complete", "movement_sequence", "reasoning"]
        
        for field in required_fields:
            if field not in data:
                return False, f"Missing field: {field}"
        
        # Validate movement_sequence (now allows multiple moves)
        valid_moves = ["UP", "DOWN", "LEFT", "RIGHT", "STAY"]
        if not isinstance(data["movement_sequence"], list) or len(data["movement_sequence"]) == 0:
            return False, "movement_sequence must be a non-empty list"
        
        # Check each move in the sequence
        for i, move in enumerate(data["movement_sequence"]):
            if move not in valid_moves:
                return False, f"Invalid movement at position {i}: {move}"
        
        # Limit sequence length to prevent overly long paths
        if len(data["movement_sequence"]) > 15:
            return False, f"Movement sequence too long: {len(data['movement_sequence'])} moves (max 15)"
        
        # STAY should only appear alone or at the end
        if "STAY" in data["movement_sequence"]:
            stay_indices = [i for i, move in enumerate(data["movement_sequence"]) if move == "STAY"]
            if len(stay_indices) > 1 or (len(stay_indices) == 1 and stay_indices[0] != len(data["movement_sequence"]) - 1):
                return False, "STAY can only appear once and must be the last move"
        
        # Validate current_room
        valid_rooms = ["KITCHEN", "BATHROOM", "BEDROOM", "LIVING_ROOM", "UNKNOWN"]
        if data["current_room"] not in valid_rooms:
            return False, f"Invalid room: {data['current_room']}"
        
        return True, data
        
    except json.JSONDecodeError as e:
        return False, f"JSON decode error: {e}"

# Usage example for your navigation system with multi-step sequences:
"""
# In your navigation function:
few_shot = VESPERFewShotPrompts(captures_dir)
prompt = few_shot.build_few_shot_prompt(current_task, screenshot_path)
response = chat_completion_with_vision(prompt, image_path=screenshot_path)

# Validate response
is_valid, result = validate_json_response(response)
if not is_valid:
    # Retry with stricter prompt or fallback
    print(f"Invalid response: {result}")
else:
    # Execute the movement sequence
    movement_queue = result["movement_sequence"]
    print(f"Planned path: {' -> '.join(movement_queue)}")
    
    # Execute moves one by one in your game loop
    for move in movement_queue:
        execute_movement(move)
        if move == "STAY":
            break  # Task complete
"""
