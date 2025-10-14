"""
VESPER Virtual Time System
Manages simulation time with time acceleration for long-duration tasks
Compatible with CASAS dataset timestamp requirements
"""

import time
from datetime import datetime, timedelta
import json
import os


class VirtualTimeManager:
    """
    Manages virtual time that can run faster or slower than real time
    Essential for tasks like sleeping, cooking, etc.
    """
    
    def __init__(self, start_time=None, time_scale=1.0):
        """
        Initialize virtual time manager
        
        Args:
            start_time: Virtual start time (datetime object) or None for now
            time_scale: Time acceleration factor (1.0 = real-time, 10.0 = 10x faster)
        """
        # Real-world tracking
        self.real_start_time = time.time()
        
        # Virtual time tracking
        if start_time is None:
            self.virtual_start_time = datetime.now()
        else:
            self.virtual_start_time = start_time
        
        self.current_virtual_time = self.virtual_start_time
        self.last_update_real_time = self.real_start_time
        
        # Time scale (how fast virtual time passes)
        self.time_scale = time_scale
        self.default_time_scale = time_scale
        
        # Time acceleration events
        self.time_events = []
        
        # Scheduled events
        self.scheduled_callbacks = []
        
        print(f"✅ Virtual Time System initialized")
        print(f"   Virtual start: {self.virtual_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Time scale: {time_scale}x")
    
    def update(self):
        """Update virtual time based on real time elapsed"""
        current_real_time = time.time()
        real_delta = current_real_time - self.last_update_real_time
        
        # Apply time scale
        virtual_delta = real_delta * self.time_scale
        
        # Update virtual time
        self.current_virtual_time += timedelta(seconds=virtual_delta)
        self.last_update_real_time = current_real_time
        
        # Check scheduled callbacks
        self._check_scheduled_events()
        
        return self.current_virtual_time
    
    def get_current_time(self):
        """Get current virtual time"""
        self.update()
        return self.current_virtual_time
    
    def get_timestamp(self):
        """Get current virtual time as Unix timestamp"""
        return self.current_virtual_time.timestamp()
    
    def get_formatted_time(self, format_str="%Y-%m-%d %H:%M:%S.%f"):
        """Get formatted virtual time string"""
        self.update()
        time_str = self.current_virtual_time.strftime(format_str)
        # Trim microseconds to milliseconds for CASAS compatibility
        if ".%f" in format_str:
            time_str = time_str[:-3]
        return time_str
    
    def set_time_scale(self, scale, duration_real_seconds=None, reason=""):
        """
        Change time acceleration
        
        Args:
            scale: New time scale (1.0 = real-time)
            duration_real_seconds: How long to keep this scale (real seconds)
            reason: Why time is being accelerated (for logging)
        """
        self.update()  # Update before changing scale
        
        old_scale = self.time_scale
        self.time_scale = scale
        
        event = {
            "real_time": time.time(),
            "virtual_time": self.current_virtual_time,
            "old_scale": old_scale,
            "new_scale": scale,
            "reason": reason
        }
        self.time_events.append(event)
        
        print(f"⏱️  Time scale changed: {old_scale}x → {scale}x")
        if reason:
            print(f"   Reason: {reason}")
        
        # Schedule return to normal if duration specified
        if duration_real_seconds:
            self.schedule_callback(
                duration_real_seconds,
                lambda: self.set_time_scale(self.default_time_scale, reason="End of time acceleration")
            )
    
    def accelerate_for_task(self, task_name, virtual_duration_seconds, max_real_seconds=10.0):
        """
        Accelerate time for a specific task
        
        Args:
            task_name: Name of task (e.g., "sleeping", "cooking")
            virtual_duration_seconds: How long the task takes in virtual time
            max_real_seconds: Maximum real-world time to spend
        
        Returns:
            Required time scale to complete task in max_real_seconds
        """
        required_scale = virtual_duration_seconds / max_real_seconds
        
        print(f"🚀 Accelerating time for task: {task_name}")
        print(f"   Virtual duration: {virtual_duration_seconds}s ({virtual_duration_seconds/60:.1f} min)")
        print(f"   Real duration: {max_real_seconds}s")
        print(f"   Time scale: {required_scale:.1f}x")
        
        self.set_time_scale(
            required_scale,
            max_real_seconds,
            f"Task: {task_name}"
        )
        
        return required_scale
    
    def schedule_callback(self, delay_real_seconds, callback):
        """
        Schedule a callback after a real-time delay
        
        Args:
            delay_real_seconds: Delay in real seconds
            callback: Function to call
        """
        execute_time = time.time() + delay_real_seconds
        self.scheduled_callbacks.append({
            "execute_time": execute_time,
            "callback": callback
        })
    
    def _check_scheduled_events(self):
        """Check and execute scheduled callbacks"""
        current_time = time.time()
        
        # Find callbacks to execute
        to_execute = [
            cb for cb in self.scheduled_callbacks
            if cb["execute_time"] <= current_time
        ]
        
        # Execute and remove
        for cb in to_execute:
            try:
                cb["callback"]()
            except Exception as e:
                print(f"⚠️ Scheduled callback error: {e}")
            
            self.scheduled_callbacks.remove(cb)
    
    def fast_forward(self, virtual_seconds, real_seconds=1.0):
        """
        Fast forward virtual time
        
        Args:
            virtual_seconds: How much virtual time to skip
            real_seconds: How long to take in real time
        """
        scale = virtual_seconds / real_seconds
        
        print(f"⏩ Fast forwarding {virtual_seconds}s ({virtual_seconds/60:.1f} min) in {real_seconds}s")
        
        self.set_time_scale(scale, real_seconds, "Fast forward")
    
    def get_time_summary(self):
        """Get summary of time system state"""
        self.update()
        
        real_elapsed = time.time() - self.real_start_time
        virtual_elapsed = (self.current_virtual_time - self.virtual_start_time).total_seconds()
        
        return {
            "current_virtual_time": self.get_formatted_time(),
            "current_time_scale": self.time_scale,
            "real_elapsed": real_elapsed,
            "virtual_elapsed": virtual_elapsed,
            "time_ratio": virtual_elapsed / real_elapsed if real_elapsed > 0 else 1.0,
            "time_events_count": len(self.time_events)
        }
    
    def print_summary(self):
        """Print time system summary"""
        summary = self.get_time_summary()
        
        print("\n" + "="*60)
        print("VIRTUAL TIME SYSTEM SUMMARY")
        print("="*60)
        print(f"🕐 Current Virtual Time: {summary['current_virtual_time']}")
        print(f"⚡ Current Time Scale: {summary['current_time_scale']:.1f}x")
        print(f"⏱️  Real Time Elapsed: {summary['real_elapsed']:.1f}s")
        print(f"🕰️  Virtual Time Elapsed: {summary['virtual_elapsed']:.1f}s ({summary['virtual_elapsed']/60:.1f} min)")
        print(f"📊 Average Time Ratio: {summary['time_ratio']:.1f}x")
        print(f"📅 Time Events: {summary['time_events_count']}")
        print("="*60 + "\n")
    
    def export_time_log(self, output_dir):
        """Export time events log"""
        try:
            output_file = os.path.join(output_dir, "virtual_time_log.json")
            
            data = {
                "virtual_start_time": self.virtual_start_time.isoformat(),
                "real_start_time": self.real_start_time,
                "current_virtual_time": self.current_virtual_time.isoformat(),
                "time_scale": self.time_scale,
                "time_events": self.time_events,
                "summary": self.get_time_summary()
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"💾 Time log exported: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"❌ Time log export failed: {e}")
            return None


class TaskTimer:
    """Helper class for timing specific tasks"""
    
    def __init__(self, virtual_time_manager):
        self.time_manager = virtual_time_manager
        self.active_timers = {}
        self.completed_timers = []
    
    def start_task_timer(self, task_name, expected_virtual_duration=None):
        """Start timing a task"""
        if task_name in self.active_timers:
            print(f"⚠️ Timer already running for: {task_name}")
            return False
        
        self.active_timers[task_name] = {
            "start_time": self.time_manager.get_current_time(),
            "start_timestamp": self.time_manager.get_timestamp(),
            "expected_duration": expected_virtual_duration
        }
        
        print(f"⏱️  Started timer: {task_name}")
        if expected_virtual_duration:
            print(f"   Expected duration: {expected_virtual_duration}s ({expected_virtual_duration/60:.1f} min)")
        
        return True
    
    def end_task_timer(self, task_name):
        """End task timer and record duration"""
        if task_name not in self.active_timers:
            print(f"⚠️ No timer running for: {task_name}")
            return None
        
        timer_data = self.active_timers[task_name]
        end_time = self.time_manager.get_current_time()
        
        virtual_duration = (end_time - timer_data["start_time"]).total_seconds()
        
        completed = {
            "task_name": task_name,
            "start_time": timer_data["start_time"],
            "end_time": end_time,
            "virtual_duration": virtual_duration,
            "expected_duration": timer_data.get("expected_duration")
        }
        
        self.completed_timers.append(completed)
        del self.active_timers[task_name]
        
        print(f"✅ Task completed: {task_name}")
        print(f"   Duration: {virtual_duration:.1f}s ({virtual_duration/60:.1f} min)")
        
        return completed
    
    def get_task_duration(self, task_name):
        """Get current duration of running task"""
        if task_name not in self.active_timers:
            return None
        
        timer_data = self.active_timers[task_name]
        current_time = self.time_manager.get_current_time()
        duration = (current_time - timer_data["start_time"]).total_seconds()
        
        return duration


# Global instance
_virtual_time_manager = None
_task_timer = None

def get_virtual_time_manager():
    """Get or create global virtual time manager"""
    global _virtual_time_manager
    if _virtual_time_manager is None:
        _virtual_time_manager = VirtualTimeManager()
    return _virtual_time_manager

def get_task_timer():
    """Get or create global task timer"""
    global _task_timer
    if _task_timer is None:
        _task_timer = TaskTimer(get_virtual_time_manager())
    return _task_timer


# Common task time profiles (virtual seconds)
TASK_TIME_PROFILES = {
    "sleep": 28800,  # 8 hours
    "nap": 1800,     # 30 minutes
    "shower": 600,   # 10 minutes
    "cook_simple": 900,   # 15 minutes
    "cook_complex": 2700, # 45 minutes
    "eat": 1200,     # 20 minutes
    "phone_call": 300,    # 5 minutes
    "wash_hands": 60,     # 1 minute
    "brush_teeth": 120,   # 2 minutes
    "watch_tv": 3600,     # 1 hour
    "read": 1800,    # 30 minutes
}


if __name__ == "__main__":
    print("🧪 Testing Virtual Time System\n")
    
    # Create time manager
    tm = VirtualTimeManager(time_scale=1.0)
    
    print(f"Initial time: {tm.get_formatted_time()}\n")
    
    # Simulate normal operation
    print("⏸️  Waiting 2 real seconds (1x speed)...")
    time.sleep(2)
    print(f"Time after 2s: {tm.get_formatted_time()}\n")
    
    # Test time acceleration for sleeping
    print("😴 Simulating 8-hour sleep in 5 real seconds...")
    tm.accelerate_for_task("sleeping", 8*3600, max_real_seconds=5.0)
    
    time.sleep(5.5)  # Wait for acceleration to complete
    
    print(f"Time after sleep: {tm.get_formatted_time()}\n")
    
    # Print summary
    tm.print_summary()
