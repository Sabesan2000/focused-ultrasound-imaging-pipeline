"""Pytest configuration and shared fixtures."""
import pytest
import numpy as np
import nibabel as nib
from pathlib import Path
import tempfile

from src.pipeline.loader import load_nifti_image


@pytest.fixture
def synthetic_brain_volume():
    """Create a synthetic brain-like volume for testing."""
    # Create volume with realistic intensity distribution
    shape = (64, 64, 64)
    
    # Background
    data = np.random.randn(*shape) * 10 + 50
    
    # Add a "target" region with higher intensity
    center = (32, 32, 32)
    radius = 8
    
    x, y, z = np.ogrid[:shape[0], :shape[1], :shape[2]]
    mask = ((x - center[0])**2 + (y - center[1])**2 + (z - center[2])**2) <= radius**2
    
    data[mask] += 100  # Bright target region
    
    return data.astype(np.float32)


@pytest.fixture
def test_nifti_file(synthetic_brain_volume, tmp_path):
    """Create a temporary NIfTI file with synthetic data."""
    filepath = tmp_path / "test_volume.nii.gz"
    
    affine = np.diag([1.0, 1.0, 1.0, 1.0])
    img = nib.Nifti1Image(synthetic_brain_volume, affine)
    nib.save(img, str(filepath))
    
    return filepath


@pytest.fixture
def loaded_test_image(test_nifti_file):
    """Load the test NIfTI file."""
    return load_nifti_image(test_nifti_file)
