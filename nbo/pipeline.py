"""
Workflow orchestration system for the NBO pipeline.

This module provides the main pipeline orchestrator that manages the execution
of all NBO components in the correct order with proper dependency management.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging
import pandas as pd

from .configuration import NBOConfig, get_config
from .data_loader import DataLoader
from .validation import assess_data_quality, validate_business_rules

logger = logging.getLogger(__name__)


@dataclass
class PipelineStep:
    """Represents a single step in the NBO pipeline."""
    name: str
    script_path: str
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    description: str = ""
    validation_only: bool = False  # For steps like contract_checks that only validate
    dependencies: List[str] = field(default_factory=list)  # Other steps this depends on
    
    def __post_init__(self):
        """Validate step configuration."""
        if not self.script_path:
            raise ValueError(f"Step {self.name}: script_path is required")
        
        if not self.inputs and not self.validation_only:
            logger.warning(f"Step {self.name}: No inputs specified")


@dataclass 
class PipelineRun:
    """Represents a pipeline execution run."""
    run_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"  # running, completed, failed, cancelled
    steps_completed: List[str] = field(default_factory=list)
    steps_failed: List[str] = field(default_factory=list)
    error_messages: List[str] = field(default_factory=list)
    outputs_generated: Dict[str, str] = field(default_factory=dict)  # filename -> path


class NBOPipeline:
    """Main workflow orchestrator for the NBO pipeline."""
    
    def __init__(self, 
                 data_path: Union[str, Path] = "data",
                 output_path: Union[str, Path] = "output", 
                 config: Optional[NBOConfig] = None,
                 scripts_path: Union[str, Path] = "nbo"):
        """
        Initialize the NBO pipeline.
        
        Args:
            data_path: Path to input data directory
            output_path: Path to output directory
            config: Configuration instance
            scripts_path: Path to directory containing Python scripts
        """
        self.data_path = Path(data_path)
        self.output_path = Path(output_path)
        self.scripts_path = Path(scripts_path)
        self.config = config or get_config()
        
        # Create output directory if it doesn't exist
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize data loader
        self.data_loader = DataLoader(self.data_path, self.config)
        
        # Define pipeline steps
        self.steps = self._define_pipeline_steps()
        
        # Current run information
        self.current_run: Optional[PipelineRun] = None
        
        # Validate pipeline configuration
        self._validate_pipeline()
    
    def _define_pipeline_steps(self) -> Dict[str, PipelineStep]:
        """Define all pipeline steps and their dependencies."""
        steps = {
            "catalog_guardrails": PipelineStep(
                name="catalog_guardrails",
                script_path="catalog_guardrails.py",
                inputs=["offer_master.csv"],
                outputs=["offer_catalog_v1.csv"],
                description="Process offer master data and apply catalog guardrails",
                dependencies=[]
            ),
            
            "contract_checks": PipelineStep(
                name="contract_checks", 
                script_path="contract_checks.py",
                inputs=["offer_catalog_v1.csv"],
                outputs=["offer_catalog_v1.csv"],  # Same file, validated
                description="Validate offer catalog data and filter valid records",
                validation_only=True,
                dependencies=["catalog_guardrails"]
            ),
            
            "fatigue_candidates": PipelineStep(
                name="fatigue_candidates",
                script_path="fatigue_candidates.py", 
                inputs=["feature_mart.csv", "touch_history.csv", "offer_catalog_v1.csv"],
                outputs=["scored_candidates.csv"],
                description="Generate candidate offers while respecting fatigue rules",
                dependencies=["contract_checks"]
            ),
            
            "model_training": PipelineStep(
                name="model_training",
                script_path="model_training.py",
                inputs=["offer_master.csv", "scored_candidates.csv", "offer_catalog_v1.csv"],
                outputs=["model_scores_output.csv"],
                description="Train uplift models and score candidate offers",
                dependencies=["fatigue_candidates"]
            ),
            
            "guardrails_winners": PipelineStep(
                name="guardrails_winners",
                script_path="guardrails_winners.py",
                inputs=["model_scores_output.csv"],
                outputs=["decision_log_output.csv"],
                description="Apply guardrails and select winning offers",
                dependencies=["model_training"]
            ),
            
            "test_marketing_view": PipelineStep(
                name="test_marketing_view",
                script_path="test_marketing_view.py",
                inputs=["offer_catalog_v1.csv", "decision_log_output.csv"],  # From contract_checks and guardrails_winners
                outputs=["test_marketing_view_output.csv"],
                description="Generate test marketing view combining validated offers and decisions",
                dependencies=["contract_checks", "guardrails_winners"]
            ),
            
            "shap": PipelineStep(
                name="shap",
                script_path="shap.py",
                inputs=["decision_log_output.csv"],  # From guardrails_winners
                outputs=["decision_log_output.csv"],  # Enhanced with SHAP values
                description="Add SHAP explanations to decision log",
                dependencies=["guardrails_winners"]
            )
        }
        
        return steps
    
    def _validate_pipeline(self):
        """Validate pipeline configuration and dependencies."""
        # Check that all script files exist
        missing_scripts = []
        for step in self.steps.values():
            script_file = self.scripts_path / step.script_path
            if not script_file.exists():
                missing_scripts.append(str(script_file))
        
        if missing_scripts:
            logger.warning(f"Missing script files: {missing_scripts}")
        
        # Check for circular dependencies
        self._check_circular_dependencies()
        
        # Validate input files exist
        self._validate_input_files()
    
    def _check_circular_dependencies(self):
        """Check for circular dependencies in the pipeline."""
        def has_cycle(step_name: str, visited: set, rec_stack: set) -> bool:
            visited.add(step_name)
            rec_stack.add(step_name)
            
            step = self.steps.get(step_name)
            if step:
                for dep in step.dependencies:
                    if dep not in visited:
                        if has_cycle(dep, visited, rec_stack):
                            return True
                    elif dep in rec_stack:
                        return True
            
            rec_stack.remove(step_name)
            return False
        
        visited = set()
        for step_name in self.steps:
            if step_name not in visited:
                if has_cycle(step_name, visited, set()):
                    raise ValueError(f"Circular dependency detected in pipeline starting from {step_name}")
    
    def _validate_input_files(self):
        """Validate that required input files exist."""
        # Get all unique input files across all steps
        all_inputs = set()
        for step in self.steps.values():
            all_inputs.update(step.inputs)
        
        # Check which files exist
        missing_files = []
        available_files = self.data_loader.get_available_tables()
        
        for input_file in all_inputs:
            # Remove .csv extension for table lookup
            table_name = input_file.replace('.csv', '')
            if table_name not in available_files:
                missing_files.append(input_file)
        
        if missing_files:
            logger.warning(f"Missing input files: {missing_files}")
            logger.info(f"Available files: {available_files}")
    
    def get_execution_order(self) -> List[str]:
        """Get the correct execution order based on dependencies."""
        # Topological sort
        in_degree = {step_name: 0 for step_name in self.steps}
        
        # Calculate in-degrees
        for step in self.steps.values():
            for dep in step.dependencies:
                if dep in in_degree:
                    in_degree[step.name] += 1
        
        # Queue for steps with no dependencies
        queue = [step_name for step_name, degree in in_degree.items() if degree == 0]
        execution_order = []
        
        while queue:
            current = queue.pop(0)
            execution_order.append(current)
            
            # Reduce in-degree for dependent steps
            for step in self.steps.values():
                if current in step.dependencies:
                    in_degree[step.name] -= 1
                    if in_degree[step.name] == 0:
                        queue.append(step.name)
        
        if len(execution_order) != len(self.steps):
            raise ValueError("Cannot determine execution order - possible circular dependencies")
        
        return execution_order
    
    def run_step(self, step_name: str, **kwargs) -> bool:
        """
        Run a single pipeline step.
        
        Args:
            step_name: Name of the step to run
            **kwargs: Additional arguments for script execution
            
        Returns:
            True if step succeeded, False otherwise
        """
        if step_name not in self.steps:
            raise ValueError(f"Unknown step: {step_name}")
        
        step = self.steps[step_name]
        script_file = self.scripts_path / step.script_path
        
        logger.info(f"Running step: {step.name}")
        logger.info(f"Description: {step.description}")
        logger.info(f"Script: {script_file}")
        logger.info(f"Inputs: {step.inputs}")
        logger.info(f"Outputs: {step.outputs}")
        
        # Check dependencies
        if self.current_run:
            missing_deps = [dep for dep in step.dependencies 
                          if dep not in self.current_run.steps_completed]
            if missing_deps:
                error_msg = f"Step {step_name} missing dependencies: {missing_deps}"
                logger.error(error_msg)
                if self.current_run:
                    self.current_run.error_messages.append(error_msg)
                return False
        
        # Validate inputs exist
        for input_file in step.inputs:
            table_name = input_file.replace('.csv', '')
            if table_name not in self.data_loader.get_available_tables():
                # Check if it's an output from a previous step
                input_path = self.output_path / input_file
                data_path = self.data_path / input_file
                
                if not input_path.exists() and not data_path.exists():
                    error_msg = f"Input file not found: {input_file}"
                    logger.error(error_msg)
                    if self.current_run:
                        self.current_run.error_messages.append(error_msg)
                    return False
        
        try:
            # Change to the scripts directory for execution
            original_cwd = os.getcwd()
            os.chdir(self.scripts_path)
            
            # Set up environment
            env = os.environ.copy()
            env['PYTHONPATH'] = str(Path(original_cwd))
            
            # Run the script
            result = subprocess.run(
                [sys.executable, step.script_path],
                capture_output=True,
                text=True,
                env=env,
                cwd=self.scripts_path
            )
            
            # Change back to original directory
            os.chdir(original_cwd)
            
            if result.returncode == 0:
                logger.info(f"Step {step_name} completed successfully")
                if result.stdout:
                    logger.debug(f"Step output: {result.stdout}")
                
                # Record outputs
                if self.current_run:
                    self.current_run.steps_completed.append(step_name)
                    for output_file in step.outputs:
                        output_path = self.output_path / output_file
                        if output_path.exists():
                            self.current_run.outputs_generated[output_file] = str(output_path)
                
                return True
            else:
                error_msg = f"Step {step_name} failed with return code {result.returncode}"
                if result.stderr:
                    error_msg += f"\nError: {result.stderr}"
                if result.stdout:
                    error_msg += f"\nOutput: {result.stdout}"
                
                logger.error(error_msg)
                if self.current_run:
                    self.current_run.steps_failed.append(step_name)
                    self.current_run.error_messages.append(error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Exception running step {step_name}: {str(e)}"
            logger.error(error_msg)
            if self.current_run:
                self.current_run.steps_failed.append(step_name)
                self.current_run.error_messages.append(error_msg)
            return False
    
    def run_pipeline(self, 
                    steps: Optional[List[str]] = None,
                    stop_on_error: bool = True,
                    validate_outputs: bool = True) -> PipelineRun:
        """
        Run the complete pipeline or specified steps.
        
        Args:
            steps: List of step names to run (default: all steps in order)
            stop_on_error: Whether to stop on first error
            validate_outputs: Whether to validate outputs after each step
            
        Returns:
            PipelineRun object with execution results
        """
        # Create new run
        run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_run = PipelineRun(
            run_id=run_id,
            start_time=datetime.now()
        )
        
        logger.info(f"Starting pipeline run: {run_id}")
        
        try:
            # Determine steps to run
            if steps is None:
                steps_to_run = self.get_execution_order()
            else:
                # Validate requested steps exist
                invalid_steps = [s for s in steps if s not in self.steps]
                if invalid_steps:
                    raise ValueError(f"Invalid steps requested: {invalid_steps}")
                steps_to_run = steps
            
            logger.info(f"Steps to run: {steps_to_run}")
            
            # Run each step
            for step_name in steps_to_run:
                success = self.run_step(step_name)
                
                if not success:
                    if stop_on_error:
                        logger.error(f"Pipeline stopped due to failure in step: {step_name}")
                        self.current_run.status = "failed"
                        break
                    else:
                        logger.warning(f"Step {step_name} failed, continuing with next steps")
                
                # Validate outputs if requested
                if success and validate_outputs:
                    self._validate_step_outputs(step_name)
            
            # Update final status
            if self.current_run.status == "running":
                if self.current_run.steps_failed:
                    self.current_run.status = "completed_with_errors"
                else:
                    self.current_run.status = "completed"
            
            self.current_run.end_time = datetime.now()
            duration = self.current_run.end_time - self.current_run.start_time
            
            logger.info(f"Pipeline run {run_id} completed in {duration}")
            logger.info(f"Status: {self.current_run.status}")
            logger.info(f"Steps completed: {len(self.current_run.steps_completed)}")
            logger.info(f"Steps failed: {len(self.current_run.steps_failed)}")
            
            return self.current_run
            
        except Exception as e:
            logger.error(f"Pipeline run failed with exception: {str(e)}")
            if self.current_run:
                self.current_run.status = "failed"
                self.current_run.end_time = datetime.now()
                self.current_run.error_messages.append(str(e))
            raise
    
    def _validate_step_outputs(self, step_name: str):
        """Validate that step outputs were created and are valid."""
        step = self.steps[step_name]
        
        for output_file in step.outputs:
            output_path = self.output_path / output_file
            
            if not output_path.exists():
                logger.warning(f"Expected output file not found: {output_path}")
                continue
            
            # Basic validation - check if file is not empty
            if output_path.stat().st_size == 0:
                logger.warning(f"Output file is empty: {output_path}")
                continue
            
            # If it's a CSV, try to load and validate
            if output_file.endswith('.csv'):
                try:
                    df = pd.read_csv(output_path)
                    if len(df) == 0:
                        logger.warning(f"Output CSV is empty: {output_path}")
                    else:
                        logger.info(f"Output validated: {output_file} ({len(df)} rows, {len(df.columns)} columns)")
                except Exception as e:
                    logger.warning(f"Could not validate output CSV {output_file}: {e}")
    
    def get_step_info(self, step_name: str) -> Dict[str, Any]:
        """Get detailed information about a pipeline step."""
        if step_name not in self.steps:
            raise ValueError(f"Unknown step: {step_name}")
        
        step = self.steps[step_name]
        script_file = self.scripts_path / step.script_path
        
        return {
            'name': step.name,
            'description': step.description,
            'script_path': str(script_file),
            'script_exists': script_file.exists(),
            'inputs': step.inputs,
            'outputs': step.outputs,
            'dependencies': step.dependencies,
            'validation_only': step.validation_only
        }
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status and configuration."""
        return {
            'data_path': str(self.data_path),
            'output_path': str(self.output_path), 
            'scripts_path': str(self.scripts_path),
            'total_steps': len(self.steps),
            'execution_order': self.get_execution_order(),
            'current_run': {
                'run_id': self.current_run.run_id if self.current_run else None,
                'status': self.current_run.status if self.current_run else None,
                'steps_completed': len(self.current_run.steps_completed) if self.current_run else 0,
                'steps_failed': len(self.current_run.steps_failed) if self.current_run else 0
            } if self.current_run else None
        }


# Convenience function
def run_nbo_pipeline(data_path: str = "data", 
                    output_path: str = "output",
                    config_path: Optional[str] = None,
                    steps: Optional[List[str]] = None) -> PipelineRun:
    """
    Convenience function to run the NBO pipeline.
    
    Args:
        data_path: Path to input data directory
        output_path: Path to output directory  
        config_path: Path to configuration file/directory
        steps: Specific steps to run (default: all)
        
    Returns:
        PipelineRun object with results
    """
    config = NBOConfig(config_path) if config_path else None
    pipeline = NBOPipeline(data_path, output_path, config)
    return pipeline.run_pipeline(steps)
