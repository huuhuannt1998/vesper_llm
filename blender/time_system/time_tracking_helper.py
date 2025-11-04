"""
Virtual Time Integration Helper for VLM Navigation
===================================================

Fixes the time tracking issue where virtual time continues during VLM calls.
Properly pauses virtual time when waiting for VLM and resumes after.

Key Features:
1. Pause virtual time before VLM call
2. Resume after VLM response
3. Track real VLM call duration separately
4. Maintain accurate task duration in virtual time

Usage:
    from time_tracking_helper import pause_for_vlm, resume_after_vlm
"""

import time


class VLMTimeTracker:
    """Tracks time spent in VLM calls separately from virtual time"""
    
    def __init__(self, virtual_time_manager=None):
        self.virtual_time_manager = virtual_time_manager
        self.vlm_call_count = 0
        self.total_vlm_real_time = 0.0
        self.current_vlm_start = None
        self.paused = False
        
    def pause_for_vlm(self, reason="VLM analysis"):
        """
        Pause virtual time before VLM call.
        
        Args:
            reason: Description of why pausing
        
        Returns:
            float: Real time when paused
        """
        if self.paused:
            print("⚠️  Already paused, skipping pause")
            return self.current_vlm_start
        
        self.current_vlm_start = time.time()
        self.paused = True
        
        # Pause virtual time manager if available
        if self.virtual_time_manager:
            # Save current time scale
            self.saved_time_scale = self.virtual_time_manager.time_scale
            
            # Set time scale to 0 (pause)
            self.virtual_time_manager.set_time_scale(0.0, reason=f"Paused for {reason}")
            
            print(f"⏸️  Virtual time PAUSED for {reason}")
        else:
            print(f"⏸️  Time tracking paused (no virtual time manager)")
        
        return self.current_vlm_start
    
    def resume_after_vlm(self):
        """
        Resume virtual time after VLM call completes.
        
        Returns:
            dict: {
                'vlm_real_duration': float,  # Seconds in real time
                'total_vlm_time': float,     # Total VLM time this session
                'vlm_call_count': int        # Number of VLM calls
            }
        """
        if not self.paused:
            print("⚠️  Not paused, skipping resume")
            return None
        
        # Calculate VLM duration
        vlm_end = time.time()
        vlm_duration = vlm_end - self.current_vlm_start
        
        # Update tracking
        self.total_vlm_real_time += vlm_duration
        self.vlm_call_count += 1
        self.paused = False
        
        # Resume virtual time manager
        if self.virtual_time_manager:
            # Restore original time scale
            self.virtual_time_manager.set_time_scale(
                self.saved_time_scale,
                reason="Resumed after VLM call"
            )
            
            print(f"▶️  Virtual time RESUMED (VLM took {vlm_duration:.2f}s real time)")
        else:
            print(f"▶️  Time tracking resumed ({vlm_duration:.2f}s elapsed)")
        
        return {
            'vlm_real_duration': vlm_duration,
            'total_vlm_time': self.total_vlm_real_time,
            'vlm_call_count': self.vlm_call_count
        }
    
    def get_summary(self):
        """Get summary of VLM time tracking"""
        return {
            'total_vlm_calls': self.vlm_call_count,
            'total_vlm_real_time': self.total_vlm_real_time,
            'average_vlm_time': self.total_vlm_real_time / self.vlm_call_count if self.vlm_call_count > 0 else 0,
            'currently_paused': self.paused
        }


# Global instance
_vlm_time_tracker = None


def get_vlm_time_tracker(virtual_time_manager=None):
    """Get or create global VLM time tracker"""
    global _vlm_time_tracker
    if _vlm_time_tracker is None:
        _vlm_time_tracker = VLMTimeTracker(virtual_time_manager)
    return _vlm_time_tracker


def pause_for_vlm(virtual_time_manager=None, reason="VLM analysis"):
    """
    Convenience function: Pause virtual time before VLM call.
    
    Args:
        virtual_time_manager: Instance of VirtualTimeManager (optional)
        reason: Why we're pausing
    
    Returns:
        float: Real time when paused
    """
    tracker = get_vlm_time_tracker(virtual_time_manager)
    return tracker.pause_for_vlm(reason)


def resume_after_vlm():
    """
    Convenience function: Resume virtual time after VLM call.
    
    Returns:
        dict: VLM call statistics
    """
    tracker = get_vlm_time_tracker()
    return tracker.resume_after_vlm()


def get_vlm_time_summary():
    """Get summary of time spent in VLM calls"""
    tracker = get_vlm_time_tracker()
    return tracker.get_summary()


# Example usage in navigation loop:
"""
# At the start of navigation, initialize with virtual time manager:
from time_tracking_helper import get_vlm_time_tracker

vlm_tracker = get_vlm_time_tracker(metrics_logger.virtual_time_manager)


# Before VLM call:
from time_tracking_helper import pause_for_vlm

pause_for_vlm(metrics_logger.virtual_time_manager, reason="Analyzing navigation")


# Make VLM call here...
result = enhanced_analyze_dual_image_navigation(...)


# After VLM call:
from time_tracking_helper import resume_after_vlm

stats = resume_after_vlm()
print(f"VLM call took {stats['vlm_real_duration']:.2f}s (real time)")


# At end of session, get summary:
from time_tracking_helper import get_vlm_time_summary

summary = get_vlm_time_summary()
print(f"Total VLM calls: {summary['total_vlm_calls']}")
print(f"Total VLM time: {summary['total_vlm_real_time']:.1f}s")
print(f"Average VLM time: {summary['average_vlm_time']:.2f}s")
"""
