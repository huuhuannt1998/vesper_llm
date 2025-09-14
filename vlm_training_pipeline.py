"""
VLM Tool Selection Training Runner
=================================

Complete training pipeline for VLM tool selection in VESPER environment.
Orchestrates data collection, supervised fine-tuning, and model evaluation.
"""

import asyncio
import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import training components
from vlm_tool_selection_training import VLMToolTrainingSystem
from vlm_finetuning_system import VLMToolFinetuner, FineTuningConfig
from vlm_inference_engine import VLMToolInferenceEngine, InferenceConfig

class VLMTrainingPipeline:
    """Complete training pipeline for VLM tool selection"""
    
    def __init__(self, 
                 data_dir: str = "vlm_training_data",
                 model_dir: str = "vlm_tool_model",
                 base_model: str = "microsoft/DialoGPT-medium"):
        
        self.data_dir = Path(data_dir)
        self.model_dir = Path(model_dir)
        self.base_model = base_model
        
        # Create directories
        self.data_dir.mkdir(exist_ok=True)
        self.model_dir.mkdir(exist_ok=True)
        
        # Pipeline components
        self.training_system = None
        self.finetuner = None
        self.inference_engine = None
        
        # Training configuration
        self.training_config = FineTuningConfig(
            model_name=base_model,
            output_dir=str(self.model_dir),
            num_epochs=3,
            batch_size=4,
            learning_rate=5e-5,
            max_length=1024
        )
        
        # Training tasks
        self.training_tasks = [
            # Basic navigation tasks
            "Navigate to the kitchen",
            "Navigate to the bedroom",
            "Navigate to the bathroom", 
            "Navigate to the living room",
            "Navigate to the dining room",
            
            # Room analysis tasks
            "Analyze the current room",
            "Identify furniture in the room",
            "Detect objects in the current view",
            "Classify the room type",
            
            # Exploration tasks
            "Explore the environment",
            "Look around the current area",
            "Survey the available rooms",
            "Search for specific objects",
            
            # Information gathering tasks
            "Get current position information",
            "Check camera status",
            "Get navigation options",
            "Detect current room",
            
            # Complex tasks requiring multiple tools
            "Prepare coffee in the kitchen",
            "Turn on the lights in the living room",
            "Find a comfortable place to sit",
            "Locate the bathroom and analyze it",
            "Go to bedroom and identify furniture"
        ]
        
        # Evaluation tasks (different from training)
        self.evaluation_tasks = [
            "Navigate to office",
            "Find the refrigerator",
            "Analyze the dining area", 
            "Explore upstairs rooms",
            "Check what's in the pantry"
        ]
    
    async def run_complete_pipeline(self) -> Dict[str, Any]:
        """Run the complete training pipeline"""
        
        pipeline_start = datetime.now()
        logger.info("🚀 Starting VLM Tool Selection Training Pipeline")
        
        results = {
            "pipeline_start": pipeline_start.isoformat(),
            "stages": {}
        }
        
        try:
            # Stage 1: Data Collection
            logger.info("📊 Stage 1: Collecting training data...")
            data_results = await self._collect_training_data()
            results["stages"]["data_collection"] = data_results
            
            # Stage 2: Supervised Fine-tuning
            logger.info("🔥 Stage 2: Fine-tuning model...")
            finetuning_results = await self._run_supervised_finetuning(data_results["dataset_path"])
            results["stages"]["finetuning"] = finetuning_results
            
            # Stage 3: Model Evaluation
            logger.info("📈 Stage 3: Evaluating model...")
            evaluation_results = await self._evaluate_model()
            results["stages"]["evaluation"] = evaluation_results
            
            # Stage 4: Inference Testing
            logger.info("🧪 Stage 4: Testing inference...")
            inference_results = await self._test_inference()
            results["stages"]["inference"] = inference_results
            
            pipeline_end = datetime.now()
            pipeline_duration = (pipeline_end - pipeline_start).total_seconds()
            
            results.update({
                "pipeline_end": pipeline_end.isoformat(),
                "duration_seconds": pipeline_duration,
                "success": True
            })
            
            logger.info(f"✅ Pipeline completed successfully in {pipeline_duration:.2f} seconds")
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {str(e)}")
            results.update({
                "success": False,
                "error": str(e),
                "pipeline_end": datetime.now().isoformat()
            })
        
        # Save pipeline results
        results_file = self.data_dir / f"pipeline_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"📁 Pipeline results saved to: {results_file}")
        
        return results
    
    async def _collect_training_data(self) -> Dict[str, Any]:
        """Collect training data using expert demonstrations"""
        
        stage_start = datetime.now()
        
        # Initialize training system
        self.training_system = VLMToolTrainingSystem(str(self.data_dir))
        
        logger.info(f"📋 Collecting data for {len(self.training_tasks)} tasks")
        
        # Generate comprehensive training dataset
        dataset_path = await self.training_system.generate_comprehensive_training_dataset(self.training_tasks)
        
        stage_end = datetime.now()
        duration = (stage_end - stage_start).total_seconds()
        
        return {
            "dataset_path": dataset_path,
            "total_tasks": len(self.training_tasks),
            "total_examples": len(self.training_system.training_examples),
            "duration_seconds": duration,
            "tasks": self.training_tasks
        }
    
    async def _run_supervised_finetuning(self, dataset_path: str) -> Dict[str, Any]:
        """Run supervised fine-tuning"""
        
        stage_start = datetime.now()
        
        # Initialize fine-tuner
        self.finetuner = VLMToolFinetuner(self.training_config)
        
        # Load training data
        logger.info(f"📁 Loading training data from: {dataset_path}")
        self.finetuner.load_training_data(dataset_path)
        
        # Setup training
        logger.info("⚙️ Setting up training...")
        self.finetuner.setup_training()
        
        # Train the model
        logger.info("🔥 Starting fine-tuning...")
        self.finetuner.train()
        
        stage_end = datetime.now()
        duration = (stage_end - stage_start).total_seconds()
        
        return {
            "model_path": str(self.model_dir),
            "training_examples": len(self.finetuner.train_dataset),
            "eval_examples": len(self.finetuner.eval_dataset),
            "epochs": self.training_config.num_epochs,
            "duration_seconds": duration
        }
    
    async def _evaluate_model(self) -> Dict[str, Any]:
        """Evaluate the fine-tuned model"""
        
        stage_start = datetime.now()
        
        # Run evaluation on test set
        logger.info("📊 Running model evaluation...")
        eval_results = self.finetuner.evaluate_model()
        
        stage_end = datetime.now()
        duration = (stage_end - stage_start).total_seconds()
        
        return {
            "accuracy": eval_results["accuracy"],
            "correct_predictions": eval_results["correct_predictions"],
            "total_predictions": eval_results["total_predictions"],
            "duration_seconds": duration
        }
    
    async def _test_inference(self) -> Dict[str, Any]:
        """Test inference engine on evaluation tasks"""
        
        stage_start = datetime.now()
        
        # Initialize inference engine
        inference_config = InferenceConfig(model_path=str(self.model_dir))
        self.inference_engine = VLMToolInferenceEngine(inference_config)
        
        # Test on evaluation tasks
        logger.info(f"🧪 Testing inference on {len(self.evaluation_tasks)} tasks")
        
        task_results = []
        
        for i, task in enumerate(self.evaluation_tasks):
            logger.info(f"Testing task {i+1}/{len(self.evaluation_tasks)}: {task}")
            
            try:
                # Solve task autonomously
                result = await self.inference_engine.solve_task_autonomously(task, max_steps=5)
                
                # Calculate metrics
                metrics = self.inference_engine.get_performance_metrics(result["execution_log"])
                
                task_result = {
                    "task": task,
                    "completed": result["completed"],
                    "total_steps": result["total_steps"],
                    "success_rate": metrics.get("success_rate", 0),
                    "average_confidence": metrics.get("average_confidence", 0),
                    "tool_usage": metrics.get("tool_usage_distribution", {})
                }
                
                task_results.append(task_result)
                
                logger.info(f"  ✅ Completed: {result['completed']}, Steps: {result['total_steps']}, Success rate: {metrics.get('success_rate', 0):.2%}")
                
            except Exception as e:
                logger.error(f"  ❌ Task failed: {str(e)}")
                task_results.append({
                    "task": task,
                    "completed": False,
                    "error": str(e)
                })
        
        # Calculate overall metrics
        completed_tasks = sum(1 for r in task_results if r.get("completed", False))
        average_success_rate = sum(r.get("success_rate", 0) for r in task_results) / len(task_results)
        average_confidence = sum(r.get("average_confidence", 0) for r in task_results) / len(task_results)
        
        stage_end = datetime.now()
        duration = (stage_end - stage_start).total_seconds()
        
        return {
            "total_evaluation_tasks": len(self.evaluation_tasks),
            "completed_tasks": completed_tasks,
            "completion_rate": completed_tasks / len(self.evaluation_tasks),
            "average_success_rate": average_success_rate,
            "average_confidence": average_confidence,
            "task_results": task_results,
            "duration_seconds": duration
        }
    
    def generate_training_report(self, pipeline_results: Dict[str, Any]) -> str:
        """Generate a comprehensive training report"""
        
        report_lines = [
            "VLM Tool Selection Training Report",
            "=" * 50,
            "",
            f"Pipeline Duration: {pipeline_results.get('duration_seconds', 0):.2f} seconds",
            f"Success: {'✅' if pipeline_results.get('success') else '❌'}",
            ""
        ]
        
        # Data Collection Results
        if "data_collection" in pipeline_results["stages"]:
            data_results = pipeline_results["stages"]["data_collection"]
            report_lines.extend([
                "Data Collection Results:",
                f"  📊 Total Tasks: {data_results.get('total_tasks', 0)}",
                f"  📈 Total Examples: {data_results.get('total_examples', 0)}",
                f"  ⏱️ Duration: {data_results.get('duration_seconds', 0):.2f}s",
                ""
            ])
        
        # Fine-tuning Results
        if "finetuning" in pipeline_results["stages"]:
            ft_results = pipeline_results["stages"]["finetuning"]
            report_lines.extend([
                "Fine-tuning Results:",
                f"  🔥 Training Examples: {ft_results.get('training_examples', 0)}",
                f"  📊 Eval Examples: {ft_results.get('eval_examples', 0)}",
                f"  🔄 Epochs: {ft_results.get('epochs', 0)}",
                f"  ⏱️ Duration: {ft_results.get('duration_seconds', 0):.2f}s",
                ""
            ])
        
        # Evaluation Results
        if "evaluation" in pipeline_results["stages"]:
            eval_results = pipeline_results["stages"]["evaluation"]
            report_lines.extend([
                "Model Evaluation Results:",
                f"  🎯 Accuracy: {eval_results.get('accuracy', 0):.2%}",
                f"  ✅ Correct: {eval_results.get('correct_predictions', 0)}",
                f"  📊 Total: {eval_results.get('total_predictions', 0)}",
                ""
            ])
        
        # Inference Results
        if "inference" in pipeline_results["stages"]:
            inf_results = pipeline_results["stages"]["inference"]
            report_lines.extend([
                "Inference Testing Results:",
                f"  🧪 Evaluation Tasks: {inf_results.get('total_evaluation_tasks', 0)}",
                f"  ✅ Completed: {inf_results.get('completed_tasks', 0)}",
                f"  📈 Completion Rate: {inf_results.get('completion_rate', 0):.2%}",
                f"  🎯 Avg Success Rate: {inf_results.get('average_success_rate', 0):.2%}",
                f"  🔍 Avg Confidence: {inf_results.get('average_confidence', 0):.2f}",
                ""
            ])
        
        report_lines.extend([
            "Training Complete! 🎉",
            f"Model saved to: {self.model_dir}",
            f"Training data saved to: {self.data_dir}"
        ])
        
        return "\n".join(report_lines)

async def main():
    """Main function to run the complete training pipeline"""
    
    print("🚀 VLM Tool Selection Training Pipeline")
    print("=" * 50)
    
    # Initialize pipeline
    pipeline = VLMTrainingPipeline(
        base_model="microsoft/DialoGPT-small",  # Smaller model for testing
    )
    
    try:
        # Run complete pipeline
        results = await pipeline.run_complete_pipeline()
        
        # Generate and display report
        report = pipeline.generate_training_report(results)
        print("\n" + report)
        
        if results.get("success"):
            print("\n🎉 Training pipeline completed successfully!")
            print("You can now use the trained model for VLM tool selection in VESPER.")
        else:
            print("\n❌ Training pipeline failed. Check logs for details.")
            
    except KeyboardInterrupt:
        print("\n⚠️ Training interrupted by user")
    except Exception as e:
        print(f"\n❌ Training failed: {str(e)}")
        logger.exception("Pipeline error")

if __name__ == "__main__":
    asyncio.run(main())
