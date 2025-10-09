#!/usr/bin/env python3
"""
MCP Integration for VLM Position Estimation

Provides Model Context Protocol interface for position estimation service.
Can be called from Blender BGE navigation or run as standalone service.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from map.vlm_position_estimator import VLMPositionEstimator


class VLMPositionMCP:
    """MCP service for VLM-based position estimation and map generation"""
    
    def __init__(self, house_layout_path=None):
        """
        Initialize MCP service
        
        Args:
            house_layout_path: Path to house layout reference image
        """
        self.estimator = VLMPositionEstimator(house_layout_path)
        self.last_position = None
        self.session_start = None
        
        print("🚀 VLM Position MCP Service initialized")
    
    def estimate_and_generate_map(self, fp_view_path, task, vlm_func, 
                                 actor_coordinates=None, actor_orientation=None):
        """
        Main MCP service function: estimate position and generate map
        
        Args:
            fp_view_path: Path to first-person screenshot
            task: Current navigation task
            vlm_func: VLM completion function
            actor_coordinates: BGE coordinates dict (optional hint)
            actor_orientation: BGE orientation dict (optional hint)
            
        Returns:
            dict: {
                'success': bool,
                'map_path': str or None,
                'position_data': dict or None,
                'error': str or None
            }
        """
        
        try:
            # Estimate position using VLM (with coordinate hints if available)
            position_data = self.estimator.estimate_position(
                fp_view_path,
                task,
                vlm_func,
                previous_position=self.last_position,
                actor_coordinates=actor_coordinates,
                actor_orientation=actor_orientation
            )
            
            if not position_data:
                return {
                    'success': False,
                    'map_path': None,
                    'position_data': None,
                    'error': 'VLM position estimation failed'
                }
            
            # Generate map with estimated position
            map_path = self.estimator.generate_position_map(position_data)
            
            if not map_path:
                return {
                    'success': False,
                    'map_path': None,
                    'position_data': position_data,
                    'error': 'Map generation failed'
                }
            
            # Update last position for continuity
            self.last_position = position_data
            
            return {
                'success': True,
                'map_path': map_path,
                'position_data': position_data,
                'error': None
            }
            
        except Exception as e:
            print(f"❌ MCP service error: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'map_path': None,
                'position_data': None,
                'error': str(e)
            }
    
    def get_position_only(self, fp_view_path, task, vlm_func):
        """
        Get position estimation without generating map
        
        Args:
            fp_view_path: Path to first-person screenshot
            task: Current navigation task
            vlm_func: VLM completion function
            
        Returns:
            dict or None: Position data
        """
        
        position_data = self.estimator.estimate_position(
            fp_view_path,
            task,
            vlm_func,
            previous_position=self.last_position
        )
        
        if position_data:
            self.last_position = position_data
        
        return position_data
    
    def generate_map_from_position(self, position_data, output_path=None):
        """
        Generate map from existing position data
        
        Args:
            position_data: Position dict from estimate_position
            output_path: Custom output path (optional)
            
        Returns:
            str or None: Path to generated map
        """
        
        return self.estimator.generate_position_map(position_data, output_path)
    
    def reset_session(self):
        """Reset position history and start new session"""
        
        self.last_position = None
        self.estimator.position_history = []
        print("🔄 VLM Position MCP session reset")


# Global MCP instance for reuse
_mcp_instance = None

def get_mcp_instance(house_layout_path=None):
    """
    Get or create global MCP instance
    
    Args:
        house_layout_path: Path to house layout (only used on first call)
        
    Returns:
        VLMPositionMCP: Global MCP instance
    """
    global _mcp_instance
    
    if _mcp_instance is None:
        _mcp_instance = VLMPositionMCP(house_layout_path)
    
    return _mcp_instance


def get_vlm_position_map(fp_view_path, task, vlm_func, house_layout_path=None, 
                        actor_coordinates=None, actor_orientation=None):
    """
    Convenience function for Blender integration
    
    Get VLM-estimated position map in one call.
    Maintains state across calls for position continuity.
    
    Args:
        fp_view_path: Path to first-person screenshot
        task: Current navigation task
        vlm_func: VLM completion function
        house_layout_path: Path to house layout (optional, uses default)
        actor_coordinates: BGE coordinates dict {'x': float, 'y': float, 'z': float} (optional hint)
        actor_orientation: BGE orientation dict {'x': float, 'y': float, 'z': float} (optional hint)
        
    Returns:
        str or None: Path to generated map with VLM-estimated position
    """
    
    # Get MCP instance (creates if doesn't exist)
    mcp = get_mcp_instance(house_layout_path)
    
    # Estimate position and generate map with coordinate hints
    result = mcp.estimate_and_generate_map(
        fp_view_path, 
        task, 
        vlm_func,
        actor_coordinates=actor_coordinates,
        actor_orientation=actor_orientation
    )
    
    if result['success']:
        print(f"✅ VLM position map generated: {Path(result['map_path']).name}")
        return result['map_path']
    else:
        print(f"❌ VLM position map generation failed: {result['error']}")
        return None


# Test function
def test_mcp_service():
    """Test MCP service with mock data"""
    
    print("🧪 Testing VLM Position MCP Service\n")
    
    # Mock VLM function
    def mock_vlm(prompt, images):
        return '''{
            "room": "LIVING_ROOM",
            "estimated_x_normalized": 0.35,
            "estimated_y_normalized": 0.55,
            "estimated_angle": 90.0,
            "confidence": 0.90,
            "landmarks_visible": ["sofa", "tv", "coffee table"],
            "reasoning": "Mock test position"
        }'''
    
    # Initialize MCP
    mcp = VLMPositionMCP()
    
    # Find test screenshot
    captures_dir = Path(__file__).parent.parent / 'blender' / 'captures'
    if captures_dir.exists():
        screenshots = sorted(captures_dir.glob('fp_view_*.png'))
        if screenshots:
            test_screenshot = screenshots[-1]
            print(f"📸 Using: {test_screenshot}")
            
            # Test service
            result = mcp.estimate_and_generate_map(
                str(test_screenshot),
                "Test navigation",
                mock_vlm
            )
            
            if result['success']:
                print(f"\n✅ MCP Service Test Successful!")
                print(f"   Map: {result['map_path']}")
                print(f"   Room: {result['position_data']['room']}")
                print(f"   Position: ({result['position_data']['estimated_x_normalized']:.2f}, {result['position_data']['estimated_y_normalized']:.2f})")
            else:
                print(f"\n❌ MCP Service Test Failed: {result['error']}")
        else:
            print("❌ No screenshots found")
    else:
        print("❌ Captures directory not found")


if __name__ == '__main__':
    test_mcp_service()
