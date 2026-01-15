"""Unit tests for image loading module."""
import pytest
import numpy as np
import nibabel as nib
from pathlib import Path
import tempfile

from src.pipeline.loader import load_nifti_image, compute_file_checksum
from src.pipeline.errors import ImageLoadError, MetadataError


def create_test_nifti(filepath: Path, shape: tuple = (64, 64, 64)) -> None:
    """Create a synthetic NIfTI file for testing."""
    data = np.random.randn(*shape).astype(np.float32)
    affine = np.eye(4)
    img = nib.Nifti1Image(data, affine)
    nib.save(img, str(filepath))


def test_load_valid_nifti():
    """Test loading a valid NIfTI file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.nii.gz"
        create_test_nifti(test_file)
        
        image_data = load_nifti_image(test_file)
        
        assert image_data.data.shape == (64, 64, 64)
        assert image_data.affine.shape == (4, 4)
        assert len(image_data.voxel_spacing) == 3
        assert image_data.checksum is not None


def test_load_nonexistent_file():
    """Test loading a nonexistent file raises error."""
    with pytest.raises(ImageLoadError, match="File does not exist"):
        load_nifti_image(Path("/nonexistent/file.nii"))


def test_load_invalid_extension():
    """Test loading file with invalid extension raises error."""
    with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
        with pytest.raises(ImageLoadError, match="Invalid file extension"):
            load_nifti_image(Path(tmp.name))


def test_load_2d_image_raises_error():
    """Test that 2D images are rejected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test_2d.nii.gz"
        data = np.random.randn(64, 64).astype(np.float32)
        affine = np.eye(4)
        img = nib.Nifti1Image(data, affine)
        nib.save(img, str(test_file))
        
        with pytest.raises(MetadataError, match="Expected 3D volumetric data"):
            load_nifti_image(test_file)


def test_compute_file_checksum():
    """Test checksum computation."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp.write("test content")
        tmp_path = Path(tmp.name)
    
    try:
        checksum1 = compute_file_checksum(tmp_path)
        checksum2 = compute_file_checksum(tmp_path)
        
        assert checksum1 == checksum2
        assert len(checksum1) == 64  # SHA256 hex digest length
    finally:
        tmp_path.unlink()


def test_voxel_spacing_extraction():
    """Test voxel spacing is correctly extracted."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.nii.gz"
        data = np.random.randn(32, 32, 32).astype(np.float32)
        affine = np.diag([2.0, 2.0, 3.0, 1.0])
        img = nib.Nifti1Image(data, affine)
        nib.save(img, str(test_file))
        
        image_data = load_nifti_image(test_file)
        
        assert image_data.voxel_spacing[0] == 2.0
        assert image_data.voxel_spacing[1] == 2.0
        assert image_data.voxel_spacing[2] == 3.0
