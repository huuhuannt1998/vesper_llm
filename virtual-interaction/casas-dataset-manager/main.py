from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import redis
import json
import os
import pandas as pd
import numpy as np
import asyncio
import logging
import requests
import csv
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CASAS Dataset Manager")

# Redis connection
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

# Cloud server URL
cloud_server_url = os.getenv("CLOUD_SERVER_URL", "http://cloud-server:8080")

class CASASEvent(BaseModel):
    date: str
    time: str
    sensor: str
    message: str
    timestamp: Optional[str] = None

class TaskExecution(BaseModel):
    participant_id: str
    task_id: int
    task_name: str
    error_type: str = "none"
    start_time: str
    duration: Optional[float] = None
    success: Optional[bool] = None

class ComparisonRequest(BaseModel):
    vesper_session_id: str
    casas_reference_file: str
    task_id: int
    participant_id: str

class DatasetExportRequest(BaseModel):
    session_ids: List[str]
    format: str = "casas_csv"  # casas_csv, json, smartthings
    include_comparison: bool = True

class CASASDatasetManager:
    def __init__(self):
        self.initialized = False
        self.casas_ground_truth_dir = os.getenv("CASAS_GROUND_TRUTH_DIR", "/app/data/casas_ground_truth")
        self.vesper_output_dir = os.getenv("VESPER_OUTPUT_DIR", "/app/data/vesper_generated")
        self.comparison_output_dir = os.getenv("COMPARISON_OUTPUT_DIR", "/app/data/comparisons")
        
        # Ensure directories exist
        Path(self.casas_ground_truth_dir).mkdir(parents=True, exist_ok=True)
        Path(self.vesper_output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.comparison_output_dir).mkdir(parents=True, exist_ok=True)
        
        # CASAS task mapping
        self.casas_tasks = {
            1: "Make phone call",
            2: "Wash hands", 
            3: "Cook oatmeal",
            4: "Eat meal",
            5: "Clean dishes"
        }
        
        # Sensor mapping
        self.sensor_types = {
            "M": "motion",
            "I": "item",
            "D": "door",
            "AD1-A": "water_hot",
            "AD1-B": "water_cold", 
            "AD1-C": "burner",
            "*": "phone"
        }
        
    async def initialize(self):
        """Initialize dataset manager"""
        if self.initialized:
            return
            
        # Load any existing CASAS ground truth data
        await self.load_casas_ground_truth()
        
        # Start data collection loop
        asyncio.create_task(self.data_collection_loop())
        
        self.initialized = True
        logger.info("CASAS Dataset Manager initialized")
    
    async def load_casas_ground_truth(self):
        """Load CASAS ground truth CSV files"""
        casas_data = {}
        
        if os.path.exists(self.casas_ground_truth_dir):
            for filename in os.listdir(self.casas_ground_truth_dir):
                if filename.endswith('.csv'):
                    filepath = os.path.join(self.casas_ground_truth_dir, filename)
                    try:
                        df = pd.read_csv(filepath, names=['date', 'time', 'sensor', 'message'])
                        casas_data[filename] = df
                        logger.info(f"Loaded CASAS ground truth: {filename} ({len(df)} events)")
                    except Exception as e:
                        logger.error(f"Failed to load {filename}: {e}")
        
        # Store in Redis for quick access
        redis_client.set("casas:ground_truth", json.dumps({
            k: v.to_dict('records') for k, v in casas_data.items()
        }))
        
        return casas_data
    
    async def data_collection_loop(self):
        """Continuous loop to collect VESPER sensor events"""
        while True:
            try:
                # Collect events from Redis
                await self.collect_sensor_events()
                
                # Process any pending comparison requests
                await self.process_comparison_queue()
                
                await asyncio.sleep(1)  # 1Hz data collection
                
            except Exception as e:
                logger.error(f"Error in data collection loop: {e}")
                await asyncio.sleep(5)
    
    async def collect_sensor_events(self):
        """Collect sensor events from Redis and organize by session"""
        # Get all CASAS events from Redis
        events_raw = redis_client.lrange("casas:events", 0, -1)
        
        if not events_raw:
            return
        
        # Group events by session/time window
        current_time = datetime.now().timestamp()
        session_window = 1800  # 30 minutes
        
        for event_str in events_raw:
            try:
                event = json.loads(event_str)
                event_time = datetime.fromisoformat(event.get('timestamp', datetime.now().isoformat())).timestamp()
                
                # Determine session ID based on time window
                session_id = f"session_{int(event_time // session_window)}"
                
                # Store event in session-specific key
                redis_client.lpush(f"vesper:session:{session_id}", event_str)
                
                # Mark session as active
                redis_client.setex(f"vesper:session:{session_id}:active", 3600, "1")
                
            except Exception as e:
                logger.error(f"Error processing event: {e}")
        
        # Clear processed events
        redis_client.delete("casas:events")
    
    async def process_comparison_queue(self):
        """Process any pending comparison requests"""
        comparison_requests = redis_client.lrange("casas:comparison_queue", 0, -1)
        
        for request_str in comparison_requests:
            try:
                request = json.loads(request_str)
                await self.perform_comparison(request)
                
                # Remove from queue
                redis_client.lrem("casas:comparison_queue", 1, request_str)
                
            except Exception as e:
                logger.error(f"Error processing comparison request: {e}")
    
    async def perform_comparison(self, request: Dict):
        """Perform comparison between VESPER data and CASAS ground truth"""
        session_id = request.get("vesper_session_id")
        casas_file = request.get("casas_reference_file")
        task_id = request.get("task_id")
        participant_id = request.get("participant_id")
        
        # Get VESPER session data
        vesper_events_raw = redis_client.lrange(f"vesper:session:{session_id}", 0, -1)
        vesper_events = [json.loads(e) for e in vesper_events_raw]
        
        if not vesper_events:
            logger.warning(f"No VESPER events found for session {session_id}")
            return
        
        # Get CASAS ground truth
        casas_data_str = redis_client.get("casas:ground_truth")
        if not casas_data_str:
            logger.warning("No CASAS ground truth data available")
            return
        
        casas_data = json.loads(casas_data_str)
        if casas_file not in casas_data:
            logger.warning(f"CASAS file {casas_file} not found in ground truth")
            return
        
        casas_events = casas_data[casas_file]
        
        # Perform comparison analysis
        comparison_result = await self.analyze_event_sequences(vesper_events, casas_events)
        
        # Add metadata
        comparison_result.update({
            "vesper_session_id": session_id,
            "casas_reference_file": casas_file,
            "task_id": task_id,
            "participant_id": participant_id,
            "comparison_timestamp": datetime.now().isoformat(),
            "vesper_event_count": len(vesper_events),
            "casas_event_count": len(casas_events)
        })
        
        # Save comparison result
        output_file = os.path.join(
            self.comparison_output_dir,
            f"comparison_{participant_id}_t{task_id}_{session_id}.json"
        )
        
        with open(output_file, 'w') as f:
            json.dump(comparison_result, f, indent=2)
        
        # Store in Redis
        redis_client.setex(f"comparison:{session_id}", 86400, json.dumps(comparison_result))
        
        logger.info(f"Comparison completed for session {session_id}")
    
    async def analyze_event_sequences(self, vesper_events: List[Dict], casas_events: List[Dict]) -> Dict:
        """Analyze and compare event sequences"""
        
        # Convert to comparable formats
        vesper_sequence = [(e['sensor'], e['message']) for e in vesper_events]
        casas_sequence = [(e['sensor'], e['message']) for e in casas_events]
        
        # Calculate sequence similarity
        sequence_similarity = self.calculate_sequence_similarity(vesper_sequence, casas_sequence)
        
        # Analyze sensor coverage
        sensor_coverage = self.analyze_sensor_coverage(vesper_events, casas_events)
        
        # Analyze timing patterns
        timing_analysis = self.analyze_timing_patterns(vesper_events, casas_events)
        
        # Analyze task completion patterns
        task_completion = self.analyze_task_completion(vesper_events, casas_events)
        
        return {
            "sequence_similarity": sequence_similarity,
            "sensor_coverage": sensor_coverage,
            "timing_analysis": timing_analysis,
            "task_completion": task_completion,
            "overall_score": (
                sequence_similarity.get("similarity_score", 0) * 0.4 +
                sensor_coverage.get("coverage_score", 0) * 0.3 +
                timing_analysis.get("timing_score", 0) * 0.3
            )
        }
    
    def calculate_sequence_similarity(self, vesper_seq: List, casas_seq: List) -> Dict:
        """Calculate sequence similarity using edit distance"""
        
        # Simple edit distance calculation
        def edit_distance(seq1, seq2):
            m, n = len(seq1), len(seq2)
            dp = [[0] * (n + 1) for _ in range(m + 1)]
            
            for i in range(m + 1):
                dp[i][0] = i
            for j in range(n + 1):
                dp[0][j] = j
            
            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    if seq1[i-1] == seq2[j-1]:
                        dp[i][j] = dp[i-1][j-1]
                    else:
                        dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
            
            return dp[m][n]
        
        edit_dist = edit_distance(vesper_seq, casas_seq)
        max_len = max(len(vesper_seq), len(casas_seq))
        similarity_score = 1.0 - (edit_dist / max_len) if max_len > 0 else 1.0
        
        return {
            "edit_distance": edit_dist,
            "similarity_score": similarity_score,
            "vesper_length": len(vesper_seq),
            "casas_length": len(casas_seq)
        }
    
    def analyze_sensor_coverage(self, vesper_events: List[Dict], casas_events: List[Dict]) -> Dict:
        """Analyze which sensors were activated in each dataset"""
        
        vesper_sensors = set(e['sensor'] for e in vesper_events)
        casas_sensors = set(e['sensor'] for e in casas_events)
        
        intersection = vesper_sensors & casas_sensors
        union = vesper_sensors | casas_sensors
        
        coverage_score = len(intersection) / len(union) if union else 1.0
        
        return {
            "vesper_sensors": list(vesper_sensors),
            "casas_sensors": list(casas_sensors),
            "common_sensors": list(intersection),
            "vesper_only": list(vesper_sensors - casas_sensors),
            "casas_only": list(casas_sensors - vesper_sensors),
            "coverage_score": coverage_score
        }
    
    def analyze_timing_patterns(self, vesper_events: List[Dict], casas_events: List[Dict]) -> Dict:
        """Analyze timing patterns between datasets"""
        
        if not vesper_events or not casas_events:
            return {"timing_score": 0.0, "error": "Insufficient events"}
        
        # Calculate duration
        vesper_duration = self.calculate_event_duration(vesper_events)
        casas_duration = self.calculate_event_duration(casas_events)
        
        # Duration similarity
        if max(vesper_duration, casas_duration) > 0:
            duration_similarity = 1.0 - abs(vesper_duration - casas_duration) / max(vesper_duration, casas_duration)
        else:
            duration_similarity = 1.0
        
        return {
            "vesper_duration": vesper_duration,
            "casas_duration": casas_duration,
            "duration_similarity": duration_similarity,
            "timing_score": duration_similarity
        }
    
    def calculate_event_duration(self, events: List[Dict]) -> float:
        """Calculate total duration of event sequence"""
        if len(events) < 2:
            return 0.0
        
        try:
            first_time = datetime.fromisoformat(events[0].get('timestamp', ''))
            last_time = datetime.fromisoformat(events[-1].get('timestamp', ''))
            return (last_time - first_time).total_seconds()
        except:
            return 0.0
    
    def analyze_task_completion(self, vesper_events: List[Dict], casas_events: List[Dict]) -> Dict:
        """Analyze task completion patterns"""
        
        # Count events by sensor type
        vesper_sensor_counts = {}
        casas_sensor_counts = {}
        
        for event in vesper_events:
            sensor = event['sensor']
            sensor_type = self.get_sensor_type(sensor)
            vesper_sensor_counts[sensor_type] = vesper_sensor_counts.get(sensor_type, 0) + 1
        
        for event in casas_events:
            sensor = event['sensor']
            sensor_type = self.get_sensor_type(sensor)
            casas_sensor_counts[sensor_type] = casas_sensor_counts.get(sensor_type, 0) + 1
        
        # Calculate completion fidelity
        completion_scores = []
        all_sensor_types = set(vesper_sensor_counts.keys()) | set(casas_sensor_counts.keys())
        
        for sensor_type in all_sensor_types:
            vesper_count = vesper_sensor_counts.get(sensor_type, 0)
            casas_count = casas_sensor_counts.get(sensor_type, 0)
            
            if casas_count > 0:
                score = 1.0 - abs(vesper_count - casas_count) / casas_count
                completion_scores.append(max(0.0, score))
            elif vesper_count == 0:
                completion_scores.append(1.0)
            else:
                completion_scores.append(0.0)
        
        completion_fidelity = np.mean(completion_scores) if completion_scores else 0.0
        
        return {
            "vesper_sensor_counts": vesper_sensor_counts,
            "casas_sensor_counts": casas_sensor_counts,
            "completion_fidelity": completion_fidelity
        }
    
    def get_sensor_type(self, sensor_id: str) -> str:
        """Get sensor type from sensor ID"""
        for prefix, sensor_type in self.sensor_types.items():
            if sensor_id.startswith(prefix):
                return sensor_type
        return "unknown"
    
    async def export_vesper_dataset(self, session_ids: List[str], format: str = "casas_csv") -> str:
        """Export VESPER data in specified format"""
        
        all_events = []
        
        # Collect events from all sessions
        for session_id in session_ids:
            events_raw = redis_client.lrange(f"vesper:session:{session_id}", 0, -1)
            session_events = [json.loads(e) for e in events_raw]
            
            # Add session metadata
            for event in session_events:
                event['session_id'] = session_id
            
            all_events.extend(session_events)
        
        # Sort by timestamp
        all_events.sort(key=lambda x: x.get('timestamp', ''))
        
        # Export in specified format
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "casas_csv":
            filename = f"vesper_dataset_{timestamp}.csv"
            filepath = os.path.join(self.vesper_output_dir, filename)
            
            with open(filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                for event in all_events:
                    writer.writerow([
                        event.get('date', ''),
                        event.get('time', ''),
                        event.get('sensor', ''),
                        event.get('message', '')
                    ])
        
        elif format == "json":
            filename = f"vesper_dataset_{timestamp}.json"
            filepath = os.path.join(self.vesper_output_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(all_events, f, indent=2)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        return filepath

# Initialize global dataset manager
dataset_manager = CASASDatasetManager()

@app.on_event("startup")
async def startup_event():
    await dataset_manager.initialize()

@app.get("/")
async def root():
    return {"service": "CASAS Dataset Manager", "status": "active"}

@app.post("/task_execution")
async def log_task_execution(execution: TaskExecution):
    """Log a task execution for dataset tracking"""
    
    # Store task execution metadata
    execution_data = execution.dict()
    execution_data['logged_at'] = datetime.now().isoformat()
    
    redis_client.setex(
        f"task_execution:{execution.participant_id}:t{execution.task_id}",
        86400,  # 24 hours
        json.dumps(execution_data)
    )
    
    return {"status": "logged", "execution_id": f"{execution.participant_id}_t{execution.task_id}"}

@app.post("/compare")
async def request_comparison(comparison: ComparisonRequest):
    """Request comparison between VESPER data and CASAS ground truth"""
    
    # Add to comparison queue
    redis_client.lpush("casas:comparison_queue", json.dumps(comparison.dict()))
    
    return {"status": "comparison_queued", "session_id": comparison.vesper_session_id}

@app.get("/comparison/{session_id}")
async def get_comparison_result(session_id: str):
    """Get comparison result for a session"""
    
    result_str = redis_client.get(f"comparison:{session_id}")
    if not result_str:
        raise HTTPException(status_code=404, detail="Comparison result not found")
    
    return json.loads(result_str)

@app.post("/export")
async def export_dataset(export_request: DatasetExportRequest):
    """Export VESPER dataset in specified format"""
    
    try:
        filepath = await dataset_manager.export_vesper_dataset(
            export_request.session_ids,
            export_request.format
        )
        
        return {"status": "exported", "filepath": filepath, "filename": os.path.basename(filepath)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download exported dataset file"""
    
    filepath = os.path.join(dataset_manager.vesper_output_dir, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(filepath, filename=filename)

@app.get("/sessions")
async def list_active_sessions():
    """List all active VESPER sessions"""
    
    # Find all active session keys
    session_keys = redis_client.keys("vesper:session:*:active")
    sessions = []
    
    for key in session_keys:
        session_id = key.split(':')[2]
        event_count = redis_client.llen(f"vesper:session:{session_id}")
        
        sessions.append({
            "session_id": session_id,
            "event_count": event_count,
            "last_active": redis_client.ttl(key)
        })
    
    return {"active_sessions": sessions}

@app.get("/ground_truth")
async def list_ground_truth_files():
    """List available CASAS ground truth files"""
    
    casas_data_str = redis_client.get("casas:ground_truth")
    if not casas_data_str:
        return {"ground_truth_files": []}
    
    casas_data = json.loads(casas_data_str)
    
    files = []
    for filename, events in casas_data.items():
        files.append({
            "filename": filename,
            "event_count": len(events),
            "sensors": list(set(e['sensor'] for e in events))
        })
    
    return {"ground_truth_files": files}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "initialized": dataset_manager.initialized,
        "casas_ground_truth_dir": dataset_manager.casas_ground_truth_dir,
        "vesper_output_dir": dataset_manager.vesper_output_dir
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
