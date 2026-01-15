"""Unit tests for data validation module with comprehensive negative tests."""
import pytest
import numpy as np
import nibabel as nib
from pathlib import Path
import tempfile

from src.pipeline.loader import load_nifti_image
from src.pipeline.validator import validate_image_data, validate_or_raise
from src.pipeline.errors import (
    ValidationError,
    DataQualityError,
    DimensionalityError,
    MetadataError
)


def create_test_image(
    data: np.ndarray,
    affine: np.ndarray = None
) -> object:
    """Create test image data from numpy array."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.nii.gz"
        if affine is None:
            affine = np.eye(4)
        img = nib.Nifti1Image(data.astype(np.float32), affine)
        nib.save(img, str(test_file))
        return load_nifti_image(test_file)


# Positive test cases

def test_validate_normal_image() -> None:
    """Test validation passes for normal image."""
    data = np.random.randn(64, 64, 64).astype(np.float32)
    image_data = create_test_image(data)
    
    report = validate_image_data(image_data)
    
    assert report.is_valid()
    assert len(report.checks_passed) > 0
    assert len(report.errors) == 0


def test_validate_or_raise_success() -> None:
    """Test validate_or_raise succeeds for valid data."""
    data = np.random.randn(64, 64, 64).astype(np.float32)
    image_data = create_test_image(data)
    
    # Should not raise
    validate_or_raise(image_data)


# Negative test cases: Data quality

def test_validate_rejects_nan() -> None:
    """Test validation rejects images with NaN values."""
    data = np.random.randn(64, 64, 64).astype(np.float32)
    data[10, 10, 10] = np.nan
    image_data = create_test_image(data)
    
    report = validate_image_data(image_data)
    
    assert not report.is_valid()
    assert any('NaN' in error for error in report.errors)


def test_validate_rejects_multiple_nan() -> None:
    """Test validation reports multiple NaN locations."""
    data = np.random.randn(64, 64, 64).astype(np.float32)
    data[10:20, 10:20, 10:20] = np.nan  # 1000 NaN values
    image_data = create_test_image(data)
    
    report = validate_image_data(image_data)
    
    assert not report.is_valid()
    assert any('1000' in error for error in report.errors)


def test_validate_rejects_inf() -> None:
    """Test validation rejects images with positive infinite values."""
    data = np.random.randn(64, 64, 64).astype(np.float32)
    data[10, 10, 10] = np.inf
    image_data = create_test_image(data)
    
    report = validate_image_data(image_data)
    
    assert not report.is_valid()
    assert any('infinite' in error for error in report.errors)


def test_validate_rejects_negative_inf() -> None:
    """Test validation rejects images with negative infinite values."""
    data = np.random.randn(64, 64, 64).astype(np.float32)
    data[10, 10, 10] = -np.inf
    image_data = create_test_image(data)
    
    report = validate_image_data(image_data)
    
    assert not report.is_valid()
    assert any('infinite' in error for error in report.errors)


def test_validate_rejects_constant_data() -> None:
    """Test validation rejects constant (zero variance) data."""
    data = np.ones((64, 64, 64), dtype=np.float32) * 42.0
    image_data = create_test_image(data)
    
    report = validate_image_data(image_data)
    
    assert not report.is_valid()
    assert any('variance' in error.lower() for error in report.errors)


def test_validate_rejects_all_zeros() -> None:
    """Test validation rejects all-zero data."""
    data = np.zeros((64, 64, 64), dtype=np.float32)
    image_data = create_test_image(data)
    
    report = validate_image_data(image_data)
    
    assert not report.is_valid()


# Negative test cases: Dimensionality

def test_validate_rejects_2d_image() -> None:
    """Test validation rejects 2D images."""
    data = np.random.randn(64, 64).astype(np.float32)
    # NIfTI format requires at least 3D, so add singleton dimension
    data_3d = data[:, :, np.newaxis]
    affine = np.eye(4)
    affine[2, 2] = 0  # Invalid spacing in Z
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.nii.gz"
        img = nib.Nifti1Image(data_3d.astype(np.float32), np.eye(4))
        nib.save(img, str(test_file))
        
        # Manually create ImageData with 2D shape to test validation
        image_data = load_nifti_image(test_file)
        # Squeeze to simulate 2D data
        image_data.data = data
        
        report = validate_image_data(image_data)
        
        assert not report.is_valid()
        assert any('3D' in error for error in report.errors)


def test_validate_dimension_sizes() -> None:
    """Test validation checks dimension sizes."""
    # Too small
    data = np.random.randn(5, 5, 5).astype(np.float32)
    image_data = create_test_image(data)
    
    report = validate_image_data(image_data, min_dimension_size=10)
    
    assert not report.is_valid()
    assert len(report.errors) >= 3  # All three dimensions too small


def test_validate_rejects_oversized_dimensions() -> None:
    """Test validation rejects unrealistically large dimensions."""
    # Simulate metadata for huge image (don't actually create it)
    data = np.random.randn(50, 50, 50).astype(np.float32)
    image_data = create_test_image(data)
    
    # Override shape in validation call
    report = validate_image_data(image_data, max_dimension_size=40)
    
    assert not report.is_valid()


# Negative test cases: Affine matrix

def test_validate_rejects_wrong_affine_shape() -> None:
    """Test validation rejects non-4x4 affine matrices."""
    data = np.random.randn(64, 64, 64).astype(np.float32)
    # Create malformed affine (3x3 instead of 4x4)
    affine = np.eye(3)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.nii.gz"
        # NIfTI format requires 4x4, so we'll use eye(4) for saving
        # but then manually override for testing
        img = nib.Nifti1Image(data, np.eye(4))
        nib.save(img, str(test_file))
        
        image_data = load_nifti_image(test_file)
        image_data.affine = affine  # Override with malformed matrix
        
        report = validate_image_data(image_data)
        
        assert not report.is_valid()
        assert any('4x4' in error for error in report.errors)


def test_validate_rejects_nan_in_affine() -> None:
    """Test validation rejects affine matrices with NaN values."""
    data = np.random.randn(64, 64, 64).astype(np.float32)
    affine = np.eye(4)
    affine[0, 0] = np.nan
    
    image_data = create_test_image(data, affine)
    
    report = validate_image_data(image_data)
    
    assert not report.is_valid()
    assert any('non-finite' in error or 'NaN' in error 
               for error in report.errors)


def test_validate_rejects_inf_in_affine() -> None:
    """Test validation rejects affine matrices with infinite values."""
    data = np.random.randn(64, 64, 64).astype(np.float32)
    affine = np.eye(4)
    affine[1, 3] = np.inf
    
    image_data = create_test_image(data, affine)
    
    report = validate_image_data(image_data)
    
    assert not report.is_valid()
    assert any('non-finite' in error or 'Inf' in error 
               for error in report.errors)


def test_validate_rejects_singular_affine() -> None:
    """Test validation rejects singular affine matrices."""
    data = np.random.randn(64, 64, 64).astype(np.float32)
    affine = np.eye(4)
    # Make rotation/scale submatrix singular by zeroing a row
    affine[0, 0:3] = 0
    
    image_data = create_test_image(data, affine)
    
    report = validate_image_data(image_data)
    
    assert not report.is_valid()
    assert any('singular' in error.lower() for error in report.errors)


def test_validate_rejects_wrong_affine_bottom_row() -> None:
    """Test validation rejects affine with incorrect bottom row."""
    data = np.random.randn(64, 64, 64).astype(np.float32)
    affine = np.eye(4)
    affine[3, :] = [1, 0, 0, 1]  # Should be [0, 0, 0, 1]
    
    image_data = create_test_image(data, affine)
    
    report = validate_image_data(image_data)
    
    assert not report.is_valid()
    assert any('bottom row' in error for error in report.errors)


def test_validate_warns_reflection_matrix() -> None:
    """Test validation warns about reflection in affine matrix."""
    data = np.random.randn(64, 64, 64).astype(np.float32)
    affine = np.eye(4)
    affine[0, 0] = -1  # Reflection in x-axis
    
    image_data = create_test_image(data, affine)
    
    report = validate_image_data(image_data)
    
    # Should pass but with warning
    assert report.is_valid() or len(report.errors) == 0
    assert any('negative determinant' in warning.lower() 
               for warning in report.warnings)


# Negative test cases: Voxel spacing

def test_validate_rejects_zero_spacing() -> None:
    """Test validation rejects zero voxel spacing."""
    data = np.random.randn(64, 64, 64).astype(np.float32)
    affine = np.eye(4)
    affine[0, 0] = 0  # Zero spacing in x
    
    image_data = create_test_image(data, affine)
    
    report = validate_image_data(image_data)
    
    assert not report.is_valid()
    assert any('positive' in error for error in report.errors)


def test_validate_rejects_negative_spacing() -> None:
    """Test validation rejects negative voxel spacing."""
    data = np.random.randn(64, 64, 64).astype(np.float32)
    affine = np.eye(4)
    affine[1, 1] = -1  # Negative spacing in y
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.nii.gz"
        img = nib.Nifti1Image(data, affine)
        nib.save(img, str(test_file))
        
        image_data = load_nifti_image(test_file)
        
        # The loader takes absolute value, so manually override
        spacing_list = list(image_data.voxel_spacing)
        spacing_list[1] = -1.0
        image_data.voxel_spacing = tuple(spacing_list)
        
        report = validate_image_data(image_data)
        
        assert not report.is_valid()


def test_validate_rejects_extreme_spacing() -> None:
    """Test validation rejects physically unrealistic voxel spacing."""
    data = np.random.randn(64, 64, 64).astype(np.float32)
    affine = np.eye(4)
    affine[2, 2] = 1000  # 1000mm = 1m voxel spacing is unrealistic
    
    image_data = create_test_image(data, affine)
    
    report = validate_image_data(image_data)
    
    assert not report.is_valid()
    assert any('exceeds maximum' in error or 'threshold' in error 
               for error in report.errors)


def test_validate_rejects_microscopic_spacing() -> None:
    """Test validation rejects unrealistically small voxel spacing."""
    data = np.random.randn(64, 64, 64).astype(np.float32)
    affine = np.eye(4)
    affine[0, 0] = 0.001  # 1 micrometer is too small for medical imaging
    
    image_data = create_test_image(data, affine)
    
    report = validate_image_data(image_data)
    
    assert not report.is_valid()
    assert any('below minimum' in error for error in report.errors)


# Exception type tests

def test_validate_or_raise_raises_data_quality_error() -> None:
    """Test validate_or_raise raises DataQualityError for NaN."""
    data = np.random.randn(64, 64, 64).astype(np.float32)
    data[10, 10, 10] = np.nan
    image_data = create_test_image(data)
    
    with pytest.raises(DataQualityError):
        validate_or_raise(image_data)


def test_validate_or_raise_raises_metadata_error() -> None:
    """Test validate_or_raise raises MetadataError for invalid affine."""
    data = np.random.randn(64, 64, 64).astype(np.float32)
    affine = np.eye(4)
    affine[0, 0:3] = 0  # Singular matrix
    image_data = create_test_image(data, affine)
    
    with pytest.raises(MetadataError):
        validate_or_raise(image_data)


def test_validate_or_raise_raises_dimensionality_error() -> None:
    """Test validate_or_raise raises DimensionalityError for wrong dims."""
    data = np.random.randn(64, 64).astype(np.float32)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.nii.gz"
        img = nib.Nifti1Image(data[:, :, np.newaxis], np.eye(4))
        nib.save(img, str(test_file))
        
        image_data = load_nifti_image(test_file)
        image_data.data = data  # Force 2D
        
        with pytest.raises(DimensionalityError):
            validate_or_raise(image_data)
