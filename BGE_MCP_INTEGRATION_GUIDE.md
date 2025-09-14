"""
Integration Guide for llm_bge_navigation.py with MCP Services
============================================================

This file shows how to modify the existing llm_bge_navigation.py to use MCP microservices
instead of direct function calls.

STEP 1: Add MCP imports at the top of llm_bge_navigation.py
"""

# Add these imports after the existing imports in llm_bge_navigation.py:

"""
# MCP Integration - Add after existing imports
try:
    from bge_mcp_integration import (
        initialize_mcp_for_bge,
        get_enhanced_context_for_navigation,
        capture_scene_images,
        get_navigation_context,
        execute_navigation_action,
        create_llm_prompt_for_task,
        execute_llm_tool_suggestion,
        check_mcp_services_status,
        get_mcp_integration_info
    )
    MCP_INTEGRATION_AVAILABLE = True
    print("✅ MCP integration loaded for BGE")
except ImportError as e:
    MCP_INTEGRATION_AVAILABLE = False
    print(f"⚠️ MCP integration not available: {e}")
"""

"""
STEP 2: Initialize MCP in the main BGE setup function
"""

# Modify the setup function (usually around line 50-100):

"""
def setup_llm_navigation():
    # Existing setup code...
    
    # Add MCP initialization
    if MCP_INTEGRATION_AVAILABLE:
        mcp_ready = initialize_mcp_for_bge()
        if mcp_ready:
            print("✅ MCP services ready for BGE navigation")
            
            # Check service status
            services_status = check_mcp_services_status()
            healthy_services = sum(1 for status in services_status.values() if status)
            total_services = len(services_status)
            print(f"🔍 MCP Services: {healthy_services}/{total_services} healthy")
        else:
            print("⚠️ MCP services not ready - using fallback mode")
    
    # Continue with existing setup...
"""

"""
STEP 3: Replace direct function calls with MCP calls
"""

# Example replacements throughout llm_bge_navigation.py:

"""
# OLD: Direct function call
# context_data = get_current_scene_context()

# NEW: MCP service call
context_data = get_enhanced_context_for_navigation(
    current_task=current_navigation_task,
    scene_data=scene_object_data
)
"""

"""
# OLD: Direct image capture
# images = capture_overhead_and_fp_images(scene_name)

# NEW: MCP camera service
images = capture_scene_images(scene_name, analysis_focus="navigation")
"""

"""
# OLD: Direct spatial query
# spatial_info = analyze_current_position()

# NEW: MCP spatial service
spatial_info = get_navigation_context()
"""

"""
# OLD: Direct movement execution
# result = execute_movement(action, parameters)

# NEW: MCP movement service
result = execute_navigation_action(action, parameters)
"""

"""
STEP 4: Update LLM prompt generation
"""

# Replace LLM prompt creation:

"""
# OLD: Manual prompt creation
# prompt = f"Task: {task}\nContext: {context}\nPlease navigate..."

# NEW: MCP orchestrated prompt
prompt = create_llm_prompt_for_task(task, context)
"""

"""
STEP 5: Update tool execution based on LLM responses
"""

# Replace tool execution logic:

"""
# OLD: Manual tool dispatch
# if llm_response.get('action') == 'navigate':
#     result = execute_navigation(llm_response['parameters'])

# NEW: MCP tool execution
if 'tool_name' in llm_response and 'parameters' in llm_response:
    result = execute_llm_tool_suggestion(
        llm_response['tool_name'], 
        llm_response['parameters']
    )
"""

"""
STEP 6: Add error handling and fallback
"""

# Add error handling for MCP failures:

"""
def safe_mcp_call(mcp_function, *args, **kwargs):
    '''Safe wrapper for MCP calls with fallback'''
    
    try:
        if MCP_INTEGRATION_AVAILABLE:
            return mcp_function(*args, **kwargs)
        else:
            return None
    except Exception as e:
        print(f"⚠️ MCP call failed: {str(e)}")
        return None

# Example usage:
context = safe_mcp_call(get_enhanced_context_for_navigation, current_task) or fallback_context
"""

"""
STEP 7: Complete example of modified navigation loop
"""

EXAMPLE_MODIFIED_NAVIGATION_LOOP = '''
def enhanced_navigation_loop():
    """Enhanced navigation loop using MCP services"""
    
    # Initialize MCP if available
    if MCP_INTEGRATION_AVAILABLE:
        initialize_mcp_for_bge()
    
    while navigation_active:
        try:
            # Get enhanced context via MCP
            context = get_enhanced_context_for_navigation(
                current_task=current_navigation_task,
                scene_data=get_scene_data()
            )
            
            # Capture images if needed
            if context.get('needs_visual_analysis'):
                images = capture_scene_images(
                    scene_name=current_scene_name,
                    focus="navigation_planning"
                )
                context['images'] = images
            
            # Get spatial context
            spatial_context = get_navigation_context()
            context['spatial'] = spatial_context
            
            # Create LLM prompt via MCP orchestration
            llm_prompt = create_llm_prompt_for_task(
                current_navigation_task, 
                context
            )
            
            # Call LLM (existing code)
            llm_response = call_llm_with_prompt(llm_prompt)
            
            # Execute suggested action via MCP
            if llm_response and 'tool_name' in llm_response:
                action_result = execute_llm_tool_suggestion(
                    llm_response['tool_name'],
                    llm_response.get('parameters', {})
                )
                
                # Process result (existing code)
                process_action_result(action_result)
            
            # Small delay
            time.sleep(0.1)
            
        except Exception as e:
            print(f"❌ Navigation loop error: {str(e)}")
            # Fallback behavior
            continue
'''

"""
STEP 8: Configuration and monitoring
"""

MONITORING_EXAMPLE = '''
def monitor_mcp_integration():
    """Monitor MCP integration status"""
    
    integration_info = get_mcp_integration_info()
    
    print("🔍 MCP Integration Status:")
    print(f"  Available: {integration_info['mcp_available']}")
    print(f"  Initialized: {integration_info['initialized']}")
    print(f"  Fallback Mode: {integration_info['fallback_mode']}")
    
    print("📊 Services Status:")
    for service, status in integration_info['services_status'].items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {service}")
    
    return integration_info
'''

"""
IMPLEMENTATION CHECKLIST:
========================

□ 1. Start MCP services using launch_mcp_services.py
□ 2. Add MCP imports to llm_bge_navigation.py
□ 3. Initialize MCP in BGE setup function
□ 4. Replace direct function calls with MCP adapter calls
□ 5. Update LLM prompt generation to use MCP orchestration
□ 6. Update tool execution to use MCP services
□ 7. Add error handling and fallback mechanisms
□ 8. Test integration with Blender/UPBGE
□ 9. Monitor service health and performance
□ 10. Iterate and optimize based on results

TESTING PROCEDURE:
=================

1. Terminal 1: Run MCP services
   python launch_mcp_services.py

2. Terminal 2: Start Blender with modified navigation
   blender house.blend --python llm_bge_navigation.py

3. Monitor logs for:
   - MCP service connections
   - Successful tool executions
   - Fallback activations
   - Performance metrics

4. Test scenarios:
   - Normal navigation with all services
   - Service failure simulation
   - Fallback mode operation
   - Performance under load
"""
