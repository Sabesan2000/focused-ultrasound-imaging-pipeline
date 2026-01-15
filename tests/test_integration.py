"""Integration tests for complete pipeline execution."""
import pytest
import numpy as np
import nibabel as nib
from pathlib import Path
import tempfile

from src.pipeline.config import PipelineConfig, ProcessingConfig
from main import run_pipeline


def test_full_pipeline_execution() -> None:
    """Test complete pipeline executes successfully."""
    # Create synthetic test data
    data = np.random.randn(64, 64, 64).astype(np.float32) * 100 + 500
    affine = np.diag([1.0, 1.0, 1.0, 1.0])
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save test image
        input_file = Path(tmpdir) / "test_input.nii.gz"
        img = nib.Nifti1Image(data, affine)
        nib.save(img, str(input_file))
        
        # Create output directory
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()
        
        # Run pipeline
        config = PipelineConfig(
            input_path=input_file,
            output_directory=output_dir,
            processing=ProcessingConfig(random_seed=42)
        )
        
        exit_code = run_pipeline(config)
        
        # Verify success
        assert exit_code == 0
        
        # Verify outputs exist
        assert (output_dir / "metrics.json").exists()
        assert (output_dir / "metrics_report.txt").exists()
        assert (output_dir / "target_visualization.png").exists()


def test_pipeline_fails_on_invalid_input() -> None:
    """Test pipeline fails gracefully on invalid input."""
    # Create invalid test data (constant)
    data = np.ones((64, 64, 64), dtype=np.float32)
    affine = np.eye(4)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        input_file = Path(tmpdir) / "test_input.nii.gz"
        img = nib.Nifti1Image(data, affine)
        nib.save(img, str(input_file))
        
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()
        
        config = PipelineConfig(
            input_path=input_file,
            output_directory=output_dir
        )
        
        exit_code = run_pipeline(config)
        
        # Should fail
        assert exit_code == 1
