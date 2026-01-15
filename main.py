"""
Main entry point for focused ultrasound imaging pipeline.

This is the primary executable for running the complete pipeline.
"""
import sys
import json
from pathlib import Path
from typing import Optional

from src.pipeline.config import PipelineConfig, ProcessingConfig, VisualizationConfig
from src.pipeline.loader import load_nifti_image
from src.pipeline.validator import validate_or_raise
from src.pipeline.processor import process_image_for_target_identification
from src.pipeline.metrics import compute_target_metrics, format_metrics_report
from src.pipeline.visualizer import create_slice_visualization
from src.utils.logging import create_pipeline_logger
from src.utils.reproducibility import set_seeds, get_environment_info, ensure_deterministic_execution
from src.pipeline.errors import PipelineError


def run_pipeline(config: PipelineConfig) -> int:
    """
    Execute the complete imaging pipeline.
    
    Args:
        config: Pipeline configuration
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Initialize logging
    logger = create_pipeline_logger(
        'FUS_Pipeline',
        config.log_level,
        config.output_directory
    )
    
    try:
        # Log environment and configuration
        logger.log_configuration(config.model_dump())
        env_info = get_environment_info()
        logger.logger.info(f"Environment info: {env_info}")
        
        # Ensure reproducibility
        ensure_deterministic_execution()
        set_seeds(config.processing.random_seed)
        
        # Stage 1: Load image
        logger.log_stage_start('load', input_path=str(config.input_path))
        image_data = load_nifti_image(config.input_path)
        logger.log_file_io('read', image_data.filepath, image_data.checksum)
        logger.log_stage_complete('load', **image_data.get_metadata_dict())
        
        # Stage 2: Validate image
        logger.log_stage_start('validate')
        validate_or_raise(image_data)
        logger.log_stage_complete('validate', validation_passed=True)
        
        # Stage 3: Process image
        logger.log_stage_start('process')
        target_region = process_image_for_target_identification(
            image_data,
            config.processing
        )
        logger.log_stage_complete(
            'process',
            target_voxel_count=target_region.voxel_count,
            target_volume_mm3=target_region.volume_mm3
        )
        
        # Stage 4: Compute metrics
        logger.log_stage_start('metrics')
        metrics = compute_target_metrics(target_region)
        logger.log_metrics(metrics)
        
        # Save metrics to JSON
        metrics_file = config.output_directory / 'metrics.json'
        with open(metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        logger.log_file_io('write', metrics_file)
        
        # Print metrics report
        report = format_metrics_report(metrics)
        print("\n" + report + "\n")
        
        # Save metrics report to text file
        report_file = config.output_directory / 'metrics_report.txt'
        with open(report_file, 'w') as f:
            f.write(report)
        logger.log_file_io('write', report_file)
        
        logger.log_stage_complete('metrics')
        
        # Stage 5: Visualization
        if config.visualization.generate_slice_views:
            logger.log_stage_start('visualization')
            
            viz_file = config.output_directory / 'target_visualization.png'
            create_slice_visualization(
                image_data,
                target_region,
                viz_file,
                config.visualization
            )
            logger.log_file_io('write', viz_file)
            logger.log_stage_complete('visualization')
        
        logger.logger.info("Pipeline completed successfully")
        return 0
        
    except PipelineError as e:
        logger.logger.error(f"Pipeline error: {e}", exc_info=True)
        return 1
    except Exception as e:
        logger.logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


def main() -> int:
    """Main entry point with argument parsing."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_nifti_file> [output_directory]")
        print("\nExample:")
        print("  python main.py data/brain_mri.nii.gz output/")
        return 1
    
    input_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("output")
    
    # Create configuration
    config = PipelineConfig(
        input_path=input_path,
        output_directory=output_dir,
        processing=ProcessingConfig(),
        visualization=VisualizationConfig()
    )
    
    return run_pipeline(config)


if __name__ == '__main__':
    sys.exit(main())
