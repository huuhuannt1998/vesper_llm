# VESPER BGE Navigation Test Script
# Quick test to verify LLM navigation setup in UPBGE

import sys
import os

# Add VESPER path
vesper_path = r"c:\Users\hbui11\Desktop\vesper_llm"
if vesper_path not in sys.path:
    sys.path.insert(0, vesper_path)

def test_bge_setup():
    """Test BGE navigation setup"""
    print("🎮 Testing VESPER BGE Navigation Setup...")
    
    # Test 1: BGE availability
    try:
        import bge
        from bge import logic
        print("✅ Test 1: BGE module available - UPBGE detected!")
        bge_available = True
    except ImportError:
        print("❌ Test 1: BGE module not available - not in UPBGE")
        bge_available = False
        return False
    
    # Test 2: LLM client connection
    try:
        from backend.app.llm.client import chat_completion
        from scripts.visual_navigation import analyze_visual_scene_for_navigation
        print("✅ Test 2: LLM client available")
        llm_available = True
    except ImportError as e:
        print(f"❌ Test 2: LLM client not available - {e}")
        llm_available = False
    
    # Test 3: Scene setup
    try:
        scene = logic.getCurrentScene()
        actor = scene.objects.get("Actor")
        if actor:
            print(f"✅ Test 3: Actor found at {actor.worldPosition}")
        else:
            print("❌ Test 3: No Actor object in BGE scene")
            return False
    except Exception as e:
        print(f"❌ Test 3: Scene access failed - {e}")
        return False
    
    # Test 4: Camera setup
    try:
        camera_found = False
        for obj in scene.objects:
            if obj.name == "Camera" or "camera" in obj.name.lower():
                print(f"✅ Test 4: Camera found - {obj.name}")
                camera_found = True
                break
        if not camera_found:
            print("⚠️ Test 4: No camera found - screenshots may not work")
    except Exception as e:
        print(f"❌ Test 4: Camera check failed - {e}")
    
    print(f"\n📊 BGE Navigation Readiness:")
    print(f"   BGE Available: {bge_available}")
    print(f"   LLM Available: {llm_available}")
    print(f"   Actor Ready: {actor is not None}")
    
    if bge_available and actor:
        print("🚀 Ready to start LLM navigation in BGE!")
        return True
    else:
        print("⚠️ Setup incomplete - check failed tests above")
        return False

def demo_llm_navigation():
    """Demo LLM navigation in BGE"""
    try:
        import bge
        from bge import logic
        
        # Initialize navigation state
        if not hasattr(logic, 'demo_nav_state'):
            logic.demo_nav_state = {
                "step": 0,
                "max_steps": 5,
                "task": "Navigate to kitchen",
                "active": True
            }
            print("🧠 Demo: LLM Navigation initialized")
        
        state = logic.demo_nav_state
        if not state["active"] or state["step"] >= state["max_steps"]:
            return
        
        # Get scene and actor
        scene = logic.getCurrentScene()
        actor = scene.objects.get("Actor")
        
        if actor:
            # Simple demo movement
            directions = ["RIGHT", "UP", "LEFT", "DOWN", "STAY"]
            direction = directions[state["step"]]
            
            # Apply movement
            step_size = 0.2
            old_pos = [actor.worldPosition.x, actor.worldPosition.y, actor.worldPosition.z]
            
            if direction == "RIGHT":
                actor.worldPosition.x += step_size
            elif direction == "LEFT":
                actor.worldPosition.x -= step_size
            elif direction == "UP":
                actor.worldPosition.y += step_size
            elif direction == "DOWN":
                actor.worldPosition.y -= step_size
            
            new_pos = [actor.worldPosition.x, actor.worldPosition.y, actor.worldPosition.z]
            
            print(f"🎮 Demo Step {state['step'] + 1}: {direction}")
            print(f"   From: {[round(x, 2) for x in old_pos]}")
            print(f"   To:   {[round(x, 2) for x in new_pos]}")
            
            state["step"] += 1
            
            if state["step"] >= state["max_steps"]:
                print("✅ Demo navigation complete!")
                state["active"] = False
    
    except Exception as e:
        print(f"❌ Demo failed: {e}")

# Main function for BGE Logic Brick
def main(cont=None):
    """Main entry point for BGE navigation"""
    try:
        # Run setup test first
        if test_bge_setup():
            # Run demo navigation
            demo_llm_navigation()
    except Exception as e:
        print(f"❌ BGE Navigation error: {e}")

# For testing outside BGE
if __name__ == "__main__":
    main()
