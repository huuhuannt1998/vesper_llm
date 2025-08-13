"""
Quick test of LLM task planning
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.app.llm.client import chat_completion

def test_simple_planning():
    """Test simple LLM task planning"""
    print("🧠 Testing Simple LLM Planning")
    
    try:
        response = chat_completion(
            "You help plan room visits for tasks.",
            "For tasks: Wake up, Brush teeth, Make coffee - which rooms should I visit? Just say: Bedroom, Kitchen",
            max_tokens=20
        )
        print(f"✅ LLM Plan: {response}")
        return True
    except Exception as e:
        print(f"❌ Planning failed: {e}")
        return False

if __name__ == "__main__":
    test_simple_planning()
