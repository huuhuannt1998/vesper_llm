
# VESPER ADL Quick Test - Run in Blender
import sys
sys.path.append(r"C:\Users\hbui11\Desktop\vesper_llm\blender")

try:
    from vesper_adl_game_engine_integration import initialize_vesper_adl_for_game_engine
    success = initialize_vesper_adl_for_game_engine()
    print(f"VESPER ADL Ready: {success}")
except Exception as e:
    print(f"Error: {e}")
