"""
Enhanced CASAS Generator for Exact VESPER-CASAS Dataset Alignment
Maps VESPER Blender navigation to exact CASAS ADL task patterns
"""

import os
import csv
import time
from datetime import datetime
from typing import List, Dict, Tuple, Optional

class VESPERCASASDatasetGenerator:
    """Generate CASAS datasets that exactly match VESPER navigation with CASAS task patterns"""
    
    def __init__(self, output_dir: str = None):
        """Initialize with exact CASAS sensor and task mappings"""
        if output_dir is None:
            vesper_root = r"C:\Users\hbui11\Desktop\vesper_llm"
            output_dir = os.path.join(vesper_root, "casas_testbed", "data", "vesper_generated")
        
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Current session tracking
        self.session_id = None
        self.events = []
        self.start_time = None
        self.current_task = None
        self.participant_id = "p01"
        self.task_id = "t1"
        
        # Exact CASAS sensor mapping (based on Zenodo description)
        self.casas_sensors = {
            # Motion sensors (PIR detectors)
            'motion': {
                'living_room': ['M01', 'M02'],
                'dining_room': ['M03', 'M04', 'M05'], 
                'kitchen': ['M13', 'M14', 'M15'],
                'bedroom': ['M07', 'M08'],
                'bathroom': ['M09', 'M10'],
                'hallway': ['M11', 'M12']
            },
            
            # Item sensors (PRESENT/ABSENT)
            'items': {
                'oatmeal': 'I01',
                'raisins': 'I02', 
                'brown_sugar': 'I03',
                'bowl': 'I04',
                'measuring_spoon': 'I05',
                'medicine': 'I06',
                'pot': 'I07',
                'phone_book': 'I08'
            },
            
            # Infrastructure sensors
            'infrastructure': {
                'kitchen_cabinet': 'D01',  # Door sensor
                'kitchen_sink_A': 'AD1-A',  # Water level
                'kitchen_sink_B': 'AD1-B',  # Water level  
                'burner': 'AD1-C',  # Burner level
                'phone': '*'  # Phone use
            }
        }
        
        # CASAS ADL Task Patterns (from Zenodo description)
        self.casas_task_patterns = {
            't1_phone_call': {
                'sequence': [
                    ('move_to_dining_room', ['M03', 'M04'], 'ON'),
                    ('pick_up_phone_book', ['I08'], 'PRESENT'),
                    ('use_phone', ['*'], 'PHONE_PICKUP'),
                    ('listen_to_message', ['*'], 'PHONE_ACTIVE'),
                    ('hang_up_phone', ['*'], 'PHONE_HANGUP'),
                    ('put_down_phone_book', ['I08'], 'ABSENT'),
                    ('leave_dining_room', ['M03', 'M04'], 'OFF')
                ],
                'duration': 120  # 2 minutes average
            },
            
            't2_wash_hands': {
                'sequence': [
                    ('move_to_kitchen', ['M13', 'M14'], 'ON'),
                    ('turn_on_water', ['AD1-A'], '50'),  # Water level
                    ('wash_hands', ['AD1-A', 'AD1-B'], '75'),
                    ('turn_off_water', ['AD1-A'], '0'),
                    ('dry_hands', [], ''),  # Towel use (no sensor)
                    ('leave_kitchen', ['M13', 'M14'], 'OFF')
                ],
                'duration': 90  # 1.5 minutes
            },
            
            't3_cook': {
                'sequence': [
                    ('move_to_kitchen', ['M13', 'M14'], 'ON'),
                    ('get_pot', ['I07'], 'PRESENT'),
                    ('fill_water', ['AD1-A'], '100'),
                    ('put_pot_on_stove', ['AD1-C'], '80'),  # Burner on
                    ('get_oatmeal', ['I01'], 'PRESENT'),
                    ('add_oats', ['I01'], 'ABSENT'),
                    ('turn_off_burner', ['AD1-C'], '0'),
                    ('get_bowl', ['I04'], 'PRESENT'),
                    ('serve_oatmeal', ['I04'], 'PRESENT'),
                    ('add_raisins', ['I02'], 'PRESENT'),
                    ('add_brown_sugar', ['I03'], 'PRESENT'),
                    ('cooking_complete', ['M13'], 'OFF')
                ],
                'duration': 300  # 5 minutes
            },
            
            't4_eat': {
                'sequence': [
                    ('get_medicine', ['I06'], 'PRESENT'),
                    ('move_to_dining_room', ['M03', 'M04'], 'ON'),
                    ('eat_meal', ['I04'], 'PRESENT'),  # Bowl present
                    ('take_medicine', ['I06'], 'ABSENT'),
                    ('finish_eating', ['I04'], 'ABSENT'),
                    ('leave_dining_room', ['M03', 'M04'], 'OFF')
                ],
                'duration': 180  # 3 minutes
            },
            
            't5_clean': {
                'sequence': [
                    ('collect_dishes', ['I04', 'I07'], 'PRESENT'),
                    ('move_to_kitchen', ['M13'], 'ON'),
                    ('turn_on_water', ['AD1-A'], '60'),
                    ('wash_dishes', ['I04', 'I07'], 'ABSENT'),  # Dishes cleaned
                    ('turn_off_water', ['AD1-A'], '0'),
                    ('put_away_dishes', ['D01'], 'OPEN'),
                    ('close_cabinet', ['D01'], 'CLOSE'),
                    ('cleaning_complete', ['M13'], 'OFF')
                ],
                'duration': 150  # 2.5 minutes
            }
        }
        
        print(f"🏠 VESPER-CASAS: Dataset generator initialized")
        print(f"📁 Output: {output_dir}")
        print(f"📋 Tasks: {list(self.casas_task_patterns.keys())}")
    
    def start_vesper_session(self, participant_id: str = "p01", task_id: str = "t1"):
        """Start a VESPER session aligned with CASAS format"""
        self.participant_id = participant_id
        self.task_id = task_id
        self.current_task = f"{task_id}_{self._get_task_name(task_id)}"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_id = f"vesper_{participant_id}_{task_id}_{timestamp}"
        
        self.events = []
        self.start_time = time.time()
        
        print(f"📋 VESPER-CASAS: Session started")
        print(f"   👤 Participant: {participant_id}")
        print(f"   🎯 Task: {task_id} ({self._get_task_description(task_id)})")
        print(f"   🆔 Session: {self.session_id}")
        
        return self.session_id
    
    def execute_casas_task(self, task_id: str, blender_actor_position: Tuple[float, float, float] = None):
        """Execute a complete CASAS task with realistic sensor patterns"""
        if not self.session_id:
            print("⚠️ No active session - call start_vesper_session() first")
            return []
        
        task_key = f"{task_id}_{self._get_task_name(task_id)}"
        if task_key not in self.casas_task_patterns:
            print(f"❌ Unknown task: {task_key}")
            return []
        
        pattern = self.casas_task_patterns[task_key]
        print(f"🎯 Executing CASAS task: {task_key}")
        print(f"📊 Pattern: {len(pattern['sequence'])} steps, ~{pattern['duration']}s duration")
        
        # Execute the task sequence
        step_duration = pattern['duration'] / len(pattern['sequence'])
        
        for i, (action, sensors, message) in enumerate(pattern['sequence']):
            print(f"   {i+1}. {action}")
            
            # Generate events for all sensors in this step
            for sensor in sensors:
                self._add_casas_event(sensor, message, action)
            
            # Realistic timing between steps
            if i < len(pattern['sequence']) - 1:
                time.sleep(0.1)  # Quick for testing, use step_duration for real timing
        
        print(f"✅ Task {task_key} completed: {len(self.events)} total events")
        return self.events.copy()
    
    def execute_blender_navigation_task(self, vesper_task: str, actor_positions: List[Tuple[float, float, float]] = None):
        """Execute VESPER Blender navigation and map to CASAS events"""
        # Map VESPER task to CASAS task
        casas_task_map = {
            'Make phone call': 't1',
            'Cook in kitchen': 't3', 
            'Wash hands': 't2',
            'Rest in bedroom': 't4',  # Map to eating (rest after meal)
            'Clean': 't5'
        }
        
        vesper_task = vesper_task.strip()
        if vesper_task in casas_task_map:
            casas_task = casas_task_map[vesper_task]
            print(f"🔗 Mapping VESPER '{vesper_task}' → CASAS '{casas_task}'")
            return self.execute_casas_task(casas_task, actor_positions)
        else:
            print(f"⚠️ No CASAS mapping for VESPER task: '{vesper_task}'")
            return []
    
    def save_vesper_casas_dataset(self) -> str:
        """Save dataset in exact CASAS format with VESPER session info"""
        if not self.events:
            print("⚠️ No events to save")
            return None
        
        # Use CASAS naming convention: vesper_p{participant}.t{task}.csv
        filename = f"vesper_{self.participant_id}.{self.task_id}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        # Save in exact CASAS CSV format
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'time', 'sensor', 'message'])  # CASAS header
            
            for event in self.events:
                writer.writerow([event['date'], event['time'], event['sensor'], event['message']])
        
        # Generate metadata file
        metadata_file = f"vesper_{self.participant_id}.{self.task_id}_metadata.json"
        metadata_path = os.path.join(self.output_dir, metadata_file)
        
        import json
        metadata = {
            'session_id': self.session_id,
            'participant_id': self.participant_id,
            'task_id': self.task_id,
            'task_description': self._get_task_description(self.task_id),
            'event_count': len(self.events),
            'duration_seconds': time.time() - self.start_time if self.start_time else 0,
            'generated_by': 'VESPER-Blender-Navigation',
            'casas_format': True,
            'compatible_with': 'CASAS Smart Home dataset (Zenodo 15712834)'
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"💾 VESPER-CASAS dataset saved:")
        print(f"   📊 Events: {filepath} ({len(self.events)} events)")
        print(f"   📋 Metadata: {metadata_path}")
        
        return filepath
    
    def end_session(self):
        """End session and save dataset"""
        if not self.session_id:
            return None
        
        dataset_file = self.save_vesper_casas_dataset()
        
        # Reset session
        self.session_id = None
        self.events = []
        self.current_task = None
        
        return dataset_file
    
    def _add_casas_event(self, sensor: str, message: str, action: str = ""):
        """Add event in exact CASAS format"""
        now = datetime.now()
        event = {
            'date': now.strftime('%Y-%m-%d'),
            'time': now.strftime('%H:%M:%S.%f')[:-3],  # Milliseconds like CASAS
            'sensor': sensor,
            'message': message
        }
        self.events.append(event)
        
        action_display = f" ({action})" if action else ""
        print(f"   📊 {event['time']} {sensor} {message}{action_display}")
    
    def _get_task_name(self, task_id: str) -> str:
        """Get task name from task ID"""
        task_names = {
            't1': 'phone_call',
            't2': 'wash_hands', 
            't3': 'cook',
            't4': 'eat',
            't5': 'clean'
        }
        return task_names.get(task_id, 'unknown')
    
    def _get_task_description(self, task_id: str) -> str:
        """Get full task description"""
        descriptions = {
            't1': 'Make a phone call (phone book lookup, dial, listen, notes)',
            't2': 'Wash hands (kitchen sink, soap, towel)',
            't3': 'Cook oatmeal (measure, boil, serve with raisins and brown sugar)',
            't4': 'Eat meal (dining room, food and medicine)',
            't5': 'Clean dishes (sink, soap, water, put away)'
        }
        return descriptions.get(task_id, 'Unknown CASAS task')


# ==========================================
# Blender Integration Functions
# ==========================================

_vesper_casas_generator = None

def init_vesper_casas_session(participant_id: str = "p01", task_id: str = "t1"):
    """Initialize VESPER-CASAS generation for Blender"""
    global _vesper_casas_generator
    _vesper_casas_generator = VESPERCASASDatasetGenerator()
    return _vesper_casas_generator.start_vesper_session(participant_id, task_id)

def execute_vesper_task(vesper_task_name: str):
    """Execute VESPER task and generate CASAS events"""
    if _vesper_casas_generator:
        return _vesper_casas_generator.execute_blender_navigation_task(vesper_task_name)
    return []

def finalize_vesper_casas_session():
    """End session and save VESPER-CASAS dataset"""
    global _vesper_casas_generator
    if _vesper_casas_generator:
        dataset_file = _vesper_casas_generator.end_session()
        _vesper_casas_generator = None
        return dataset_file
    return None


# ==========================================
# Test Complete VESPER-CASAS Integration
# ==========================================

if __name__ == "__main__":
    print("🧪 Testing VESPER-CASAS Dataset Generation")
    print("=" * 60)
    
    generator = VESPERCASASDatasetGenerator()
    
    # Test all 5 CASAS tasks
    for task_id in ['t1', 't2', 't3', 't4', 't5']:
        print(f"\n🎯 Testing {task_id}...")
        
        generator.start_vesper_session("p01", task_id)
        generator.execute_casas_task(task_id)
        dataset_file = generator.end_session()
        
        print(f"✅ {task_id} completed: {dataset_file}")
    
    print(f"\n🎉 All CASAS tasks tested!")
    print(f"📁 Check: casas_testbed/vesper_datasets/")
    print(f"📊 Ready for VESPER-Blender integration")
