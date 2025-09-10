#!/usr/bin/env python3
"""
VLM to CASAS Dataset Converter

Converts VLM evaluation logs to CASAS format for ground truth comparison.
Extracts sensor events from movement data and room transitions.
"""

import json
import csv
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import logging


class VLMToCASASConverter:
    """Converts VLM evaluation logs to CASAS CSV format"""
    
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.room_sensors = {
            'LIVING_ROOM': 'M01',
            'KITCHEN': 'M02', 
            'BEDROOM': 'M03',
            'BATHROOM': 'M04',
            'DINING_ROOM': 'M05',
            'OFFICE': 'M06',
            'HALLWAY': 'M07',
            'ENTRANCE': 'M08'
        }
        self.motion_threshold = 0.5  # Movement distance to trigger motion sensor
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def convert_timestamp(self, unix_timestamp: float) -> Tuple[str, str]:
        """Convert Unix timestamp to CASAS date/time format"""
        dt = datetime.fromtimestamp(unix_timestamp)
        date = dt.strftime('%Y-%m-%d')
        time = dt.strftime('%H:%M:%S.%f')
        return date, time
    
    def calculate_distance(self, pos1: List[float], pos2: List[float]) -> float:
        """Calculate Euclidean distance between two positions"""
        return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5
    
    def extract_sensor_events(self, log_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract sensor events from VLM log data"""
        events = []
        current_room = None
        last_position = None
        
        for task in log_data.get('task_details', []):
            movement_path = task.get('movement_path', [])
            
            for step in movement_path:
                timestamp = step['timestamp']
                room = step['room_detected']
                from_pos = step['from_position']
                to_pos = step['to_position']
                
                date, time = self.convert_timestamp(timestamp)
                
                # Room transition sensor event
                if room != current_room and room in self.room_sensors:
                    # Turn off previous room sensor
                    if current_room and current_room in self.room_sensors:
                        events.append({
                            'date': date,
                            'time': time,
                            'sensor': self.room_sensors[current_room],
                            'message': 'OFF'
                        })
                    
                    # Turn on new room sensor
                    events.append({
                        'date': date,
                        'time': time,
                        'sensor': self.room_sensors[room],
                        'message': 'ON'
                    })
                    current_room = room
                
                # Motion sensor event based on movement distance
                if last_position and from_pos:
                    distance = self.calculate_distance(last_position, from_pos)
                    if distance > self.motion_threshold:
                        # Motion detected
                        motion_sensor = f"M{room[-2:]}" if len(room) >= 2 else "M99"
                        events.append({
                            'date': date,
                            'time': time,
                            'sensor': motion_sensor,
                            'message': 'ON'
                        })
                
                last_position = to_pos
        
        return events
    
    def process_log_file(self, log_file: str) -> str:
        """Process a single VLM log file and convert to CASAS format"""
        try:
            with open(log_file, 'r') as f:
                log_data = json.load(f)
            
            # Extract sensor events
            events = self.extract_sensor_events(log_data)
            
            if not events:
                self.logger.warning(f"No events extracted from {log_file}")
                return None
            
            # Generate output filename
            session_id = log_data.get('session_id', 'unknown')
            output_file = os.path.join(self.output_dir, f"vlm_{session_id}.csv")
            
            # Write CASAS CSV format
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['date', 'time', 'sensor', 'message'])
                
                for event in events:
                    writer.writerow([
                        event['date'],
                        event['time'], 
                        event['sensor'],
                        event['message']
                    ])
            
            self.logger.info(f"Converted {log_file} -> {output_file} ({len(events)} events)")
            return output_file
            
        except Exception as e:
            self.logger.error(f"Error processing {log_file}: {e}")
            return None
    
    def convert_all_logs(self) -> List[str]:
        """Convert all VLM logs in input directory to CASAS format"""
        converted_files = []
        
        for filename in os.listdir(self.input_dir):
            if filename.endswith('.json') and 'vesper_navigation_log' in filename:
                log_file = os.path.join(self.input_dir, filename)
                output_file = self.process_log_file(log_file)
                if output_file:
                    converted_files.append(output_file)
        
        self.logger.info(f"Converted {len(converted_files)} log files")
        return converted_files
    
    def generate_summary_report(self, converted_files: List[str]) -> str:
        """Generate summary report of conversion"""
        report_file = os.path.join(self.output_dir, "conversion_summary.txt")
        
        with open(report_file, 'w') as f:
            f.write("VLM to CASAS Conversion Summary\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Input Directory: {self.input_dir}\n")
            f.write(f"Output Directory: {self.output_dir}\n")
            f.write(f"Files Converted: {len(converted_files)}\n\n")
            
            f.write("Converted Files:\n")
            for file in converted_files:
                f.write(f"  - {os.path.basename(file)}\n")
            
            f.write(f"\nRoom Sensor Mapping:\n")
            for room, sensor in self.room_sensors.items():
                f.write(f"  {room}: {sensor}\n")
        
        return report_file


def main():
    """Main execution function"""
    # Set up paths
    base_dir = r"c:\Users\hbui11\Desktop\vesper_llm"
    input_dir = os.path.join(base_dir, "blender", "evaluation_logs")
    output_dir = os.path.join(base_dir, "casas_testbed", "data", "vesper_generated")
    
    # Create converter and process logs
    converter = VLMToCASASConverter(input_dir, output_dir)
    
    print("Converting VLM evaluation logs to CASAS format...")
    converted_files = converter.convert_all_logs()
    
    # Generate summary report
    report_file = converter.generate_summary_report(converted_files)
    print(f"\nConversion complete!")
    print(f"Output directory: {output_dir}")
    print(f"Summary report: {report_file}")
    print(f"Converted {len(converted_files)} files")


if __name__ == "__main__":
    main()
