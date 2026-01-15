"""Unit tests for data validation module."""
import pytest
import numpy as np
import nibabel as nib
from pathlib import Path
import tempfile

from src.pipeline.loader import load_nifti_image
from src.pipeline.validator import validate_image_data, validate_or_raise
from src.pipeline.errors import ValidationError


def create_test_image(data: np.ndarray) -> object:
    """Create test image data from numpy array."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.nii.gz"
        affine = np.eye(4)
        img = nib.Nifti1Image(data.astype(np.float32), affine)
        nib.save(img, str(test_file))
        return load_nifti_image(test_file)


def test_validate_normal_image():
    """Test validation passes for normal image."""
    data = np.random.randn(64, 64, 64).astype(np.float32)
    image_data = create_test_image(data)
    
    report = validate_image_data(image_data)
    
    assert report.is_valid()
    assert len(report.checks_passed) > 0
    assert len(report.errors) == 0


def test_validate_rejects_nan():
    """Test validation rejects images with NaN values."""
    data = np.random.randn(64, 64, 64).astype(np.float32)
    data[10, 10, 10] = np.nan
    image_data = create_test_image(data)
    
    report = validate_image_data(image_data)
    
    assert not report.is_valid()
    assert any('NaN' in error for error in report.errors)


def test_validate_rejects_inf():
    """Test validation rejects images with infinite values."""
    data = np.random.randn(64, 64, 64).astype(np.float32)
    data[10, 10, 10] = np.inf
    image_data = create_test_image(data)
    
    report = validate_image_data(image_data)
    
    assert not report.is_valid()
    assert any('infinite' in error for error in report.errors)


def test_validate_rejects_constant_data():
    """Test validation rejects constant (zero variance) data."""
    data = np.ones((64, 64, 64), dtype=np.float32)
    image_data = create_test_image(data)
    
    report = validate_image_data(image_data)
    
    assert not report.is_valid()
    assert any('constant' in error for error in report.errors)


def test_validate_or_raise_success():
    """Test validate_or_raise succeeds for valid data."""
    data = np.random.randn(64, 64, 64).astype(np.float32)
    image_data = create_test_image(data)
    
    # Should not raise
    validate_or_raise(image_data)


def test_validate_or_raise_failure():
    """Test validate_or_raise raises for invalid data."""
    data = np.ones((64, 64, 64), dtype=np.float32)
    image_data = create_test_image(data)
    
    with pytest.raises(ValidationError):
        validate_or_raise(image_data)


def test_validate_dimension_sizes():
    """Test validation checks dimension sizes."""
    # Too small
    data = np.random.randn(5, 5, 5).astype(np.float32)
    image_data = create_test_image(data)
    
    report = validate_image_data(image_data, min_dimension_size=10)
    
    assert not report.is_valid()
    assert len(report.errors) >= 3  # All three dimensions too small
