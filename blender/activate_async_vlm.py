"""
Quick Async VLM Activation Patch
This adds a simple async VLM wrapper to maximize CPU/GPU usage
"""

def add_async_vlm_usage():
    filepath = "llm_bge_navigation.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the VLM call location and add async wrapper
    # We'll add a helper function that uses the async manager when available
    
    async_wrapper = '''
def call_vlm_with_async(fp_image_path, house_layout_path, current_task, current_position, step):
    """
    Smart VLM caller that uses async manager if available, falls back to sync
    """
    # Try async VLM first (non-blocking, much faster)
    if hasattr(bge.logic, 'vlm_manager') and bge.logic.vlm_manager:
        try:
            # Submit async query
            bge.logic.vlm_manager.submit_query(
                fp_image=fp_image_path,
                map_image=house_layout_path,
                task=current_task,
                step=step
            )
            
            # Wait up to 100ms for result (non-blocking)
            result = bge.logic.vlm_manager.get_result(timeout=0.1)
            
            if result and 'movement_decision' in result:
                print("⚡ Using ASYNC VLM (fast!)")
                return result
            else:
                print("⏳ Async VLM pending, using last known action...")
                return bge.logic.vlm_manager.last_result
                
        except Exception as e:
            print(f"⚠️ Async VLM error: {e}, falling back to sync")
    
    # Fallback to synchronous VLM (slower but reliable)
    print("🐌 Using SYNC VLM (slower)")
    if ENHANCED_VLM_AVAILABLE:
        return enhanced_analyze_dual_image_navigation(
            fp_image_path, house_layout_path, current_task, 
            current_position, step
        )
    else:
        return analyze_dual_image_navigation(
            fp_image_path, house_layout_path, current_task, 
            current_position, step
        )

'''
    
    # Find where to insert (before run_continuous_navigation)
    insert_marker = "def run_continuous_navigation():"
    if insert_marker in content:
        insert_pos = content.find(insert_marker)
        content = content[:insert_pos] + async_wrapper + "\n" + content[insert_pos:]
        print("✅ Added async VLM wrapper function")
    else:
        print("⚠️ Could not find insertion point")
        return
    
    # Now replace the actual VLM calls
    # Find: enhanced_analyze_dual_image_navigation(
    # Replace with: call_vlm_with_async(
    
    old_call = "enhanced_analyze_dual_image_navigation("
    new_call = "call_vlm_with_async("
    
    replacements = content.count(old_call)
    content = content.replace(old_call, new_call)
    
    print(f"✅ Replaced {replacements} VLM calls with async wrapper")
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ Async VLM activation complete!")
    print(f"   This should increase CPU usage to 40-60%")
    print(f"   GPU usage will also increase during rendering")

if __name__ == "__main__":
    add_async_vlm_usage()
