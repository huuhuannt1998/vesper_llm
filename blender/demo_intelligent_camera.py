"""
Intelligent Camera Selection Demo
================================

This demo script shows how the VLM intelligently chooses between
bird-eye view and first-person view based on navigation context.

Run this in BGE to see the intelligent camera selection in action.
"""

import bge
import time

def demo_intelligent_camera_selection():
    """Demonstrate intelligent camera selection with different scenarios"""
    
    print("🎬 INTELLIGENT CAMERA SELECTION DEMO")
    print("=" * 50)
    
    try:
        from intelligent_camera_selection import select_camera_intelligently
        
        # Get current actor position
        scene = bge.logic.getCurrentScene()
        actor = scene.objects.get("Actor")
        
        if not actor:
            print("❌ Actor not found in scene")
            return
        
        actor_pos = (actor.worldPosition.x, actor.worldPosition.y, actor.worldPosition.z)
        print(f"📍 Actor position: [{actor_pos[0]:.2f}, {actor_pos[1]:.2f}, {actor_pos[2]:.2f}]")
        
        # Demo Scenario 1: Stuck movement pattern
        print("\n🧪 SCENARIO 1: Actor appears stuck")
        print("-" * 30)
        
        stuck_movements = [actor_pos, actor_pos, actor_pos, actor_pos, actor_pos]
        decision1 = select_camera_intelligently(
            actor_pos,
            current_task="Go to kitchen",
            recent_movements=stuck_movements
        )
        
        print(f"📊 Decision: {decision1['camera_choice']}")
        print(f"💭 Reasoning: {decision1['reasoning']}")
        print(f"🎯 Expected benefit: {decision1['expected_benefit']}")
        print(f"📈 Confidence: {decision1['confidence']:.2f}")
        
        # Demo Scenario 2: Interaction task
        print("\n🧪 SCENARIO 2: Interaction task (cook in kitchen)")
        print("-" * 45)
        
        progressing_movements = [
            (actor_pos[0]-1, actor_pos[1], actor_pos[2]),
            (actor_pos[0]-0.5, actor_pos[1], actor_pos[2]),
            actor_pos
        ]
        decision2 = select_camera_intelligently(
            actor_pos,
            current_task="Cook in kitchen",
            recent_movements=progressing_movements
        )
        
        print(f"📊 Decision: {decision2['camera_choice']}")
        print(f"💭 Reasoning: {decision2['reasoning']}")
        print(f"🎯 Expected benefit: {decision2['expected_benefit']}")
        print(f"📈 Confidence: {decision2['confidence']:.2f}")
        
        # Demo Scenario 3: Exploration (navigation)
        print("\n🧪 SCENARIO 3: Room exploration")
        print("-" * 30)
        
        exploring_movements = [
            (actor_pos[0]-2, actor_pos[1]+1, actor_pos[2]),
            (actor_pos[0]-1, actor_pos[1]+0.5, actor_pos[2]),
            (actor_pos[0]-0.5, actor_pos[1], actor_pos[2]),
            actor_pos
        ]
        decision3 = select_camera_intelligently(
            actor_pos,
            current_task="Relax in living room",
            recent_movements=exploring_movements
        )
        
        print(f"📊 Decision: {decision3['camera_choice']}")
        print(f"💭 Reasoning: {decision3['reasoning']}")
        print(f"🎯 Expected benefit: {decision3['expected_benefit']}")
        print(f"📈 Confidence: {decision3['confidence']:.2f}")
        
        # Demo Scenario 4: Let VLM decide without strong heuristics
        print("\n🧪 SCENARIO 4: VLM decision (no strong heuristics)")
        print("-" * 48)
        
        decision4 = select_camera_intelligently(
            actor_pos,
            current_task="Prepare in bathroom",
            recent_movements=None
        )
        
        print(f"📊 Decision: {decision4['camera_choice']}")
        print(f"💭 Reasoning: {decision4['reasoning']}")
        print(f"🎯 Expected benefit: {decision4['expected_benefit']}")
        print(f"📈 Confidence: {decision4['confidence']:.2f}")
        print(f"🔧 Source: {decision4.get('source', 'unknown')}")
        
        # Summary
        print("\n📊 DEMO SUMMARY")
        print("-" * 20)
        decisions = [decision1, decision2, decision3, decision4]
        bird_eye_count = sum(1 for d in decisions if d['camera_choice'] == 'bird_eye')
        first_person_count = sum(1 for d in decisions if d['camera_choice'] == 'first_person')
        
        print(f"🐦 Bird-eye selections: {bird_eye_count}")
        print(f"👁️ First-person selections: {first_person_count}")
        
        avg_confidence = sum(d['confidence'] for d in decisions) / len(decisions)
        print(f"📈 Average confidence: {avg_confidence:.2f}")
        
        # Show camera selection performance if available
        try:
            from intelligent_camera_selection import get_camera_selection_stats
            stats = get_camera_selection_stats()
            
            if any(stats[cam]['total_decisions'] > 0 for cam in stats):
                print("\n📈 HISTORICAL PERFORMANCE:")
                for camera, perf in stats.items():
                    if perf['total_decisions'] > 0:
                        print(f"   {camera}: {perf['success_rate']:.1%} success rate ({perf['successful_decisions']}/{perf['total_decisions']})")
            else:
                print("\n📈 No historical performance data yet")
                
        except Exception as e:
            print(f"\n⚠️ Could not get performance stats: {e}")
        
        print("\n✅ Demo completed successfully!")
        
    except ImportError as e:
        print(f"❌ Intelligent camera selection not available: {e}")
        print("💡 Make sure intelligent_camera_selection.py is properly loaded")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

def demo_live_camera_capture():
    """Demo live camera capture with intelligent selection"""
    
    print("\n🎬 LIVE CAMERA CAPTURE DEMO")
    print("=" * 35)
    
    try:
        from intelligent_camera_selection import capture_with_intelligent_camera
        
        # Get current actor state
        scene = bge.logic.getCurrentScene()
        actor = scene.objects.get("Actor")
        
        if not actor:
            print("❌ Actor not found")
            return
        
        actor_pos = (actor.worldPosition.x, actor.worldPosition.y, actor.worldPosition.z)
        actor_orient = (0, 0, 0)  # Simplified for demo
        
        print(f"📍 Capturing from position: [{actor_pos[0]:.2f}, {actor_pos[1]:.2f}, {actor_pos[2]:.2f}]")
        
        # Capture with intelligent selection
        result = capture_with_intelligent_camera(
            actor_pos,
            actor_orient,
            current_task="Demo task",
            recent_movements=None
        )
        
        if result["success"]:
            print(f"✅ Capture successful!")
            print(f"📷 Camera used: {result['camera_used']}")
            print(f"📁 Image saved: {result['image_path']}")
            print(f"💭 Selection reasoning: {result['selection_reasoning']}")
            print(f"📈 Confidence: {result.get('confidence', 'N/A')}")
            
            # Verify file exists
            import os
            if os.path.exists(result['image_path']):
                size = os.path.getsize(result['image_path'])
                print(f"📐 File size: {size} bytes")
            else:
                print("⚠️ Image file not found")
                
        else:
            print(f"❌ Capture failed: {result.get('error', 'Unknown')}")
            
    except ImportError as e:
        print(f"❌ Intelligent camera capture not available: {e}")
    except Exception as e:
        print(f"❌ Live capture demo failed: {e}")
        import traceback
        traceback.print_exc()

def run_complete_demo():
    """Run complete intelligent camera selection demo"""
    
    print("🚀 COMPLETE INTELLIGENT CAMERA DEMO")
    print("=" * 50)
    
    # Test camera selection logic
    demo_intelligent_camera_selection()
    
    # Test live capture
    demo_live_camera_capture()
    
    print("\n🎉 All demos completed!")

# Auto-run if executed directly
if __name__ == "__main__":
    run_complete_demo()

print("✅ Intelligent camera demo loaded - call run_complete_demo() to execute")
