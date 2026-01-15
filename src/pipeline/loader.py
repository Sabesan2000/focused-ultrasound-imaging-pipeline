"""
Medical image loading module.

Handles loading of volumetric imaging data with explicit validation
of all metadata and data integrity.
"""
import hashlib
from pathlib import Path
from typing import Tuple, Dict, Any
import numpy as np
import nibabel as nib
from nibabel.nifti1 import Nifti1Image

from .errors import ImageLoadError, MetadataError


class ImageData:
    """Container for loaded image data with validated metadata."""
    
    def __init__(
        self,
        data: np.ndarray,
        affine: np.ndarray,
        header: nib.Nifti1Header,
        filepath: Path,
        checksum: str
    ):
        """
        Initialize ImageData container.
        
        Args:
            data: 3D volumetric data array
            affine: 4x4 affine transformation matrix
            header: NIfTI header with metadata
            filepath: Source file path
            checksum: SHA256 checksum of source file
        """
        self.data = data
        self.affine = affine
        self.header = header
        self.filepath = filepath
        self.checksum = checksum
        
        # Extract critical metadata
        self.voxel_spacing = self._extract_voxel_spacing()
        self.dimensions = data.shape
        self.data_type = data.dtype
    
    def _extract_voxel_spacing(self) -> Tuple[float, float, float]:
        """
        Extract voxel spacing from header.
        
        Returns:
            Tuple of (x, y, z) voxel dimensions in mm
        """
        pixdim = self.header.get_zooms()
        if len(pixdim) < 3:
            raise MetadataError(
                f"Invalid voxel spacing: expected 3D, got {len(pixdim)}D"
            )
        return (float(pixdim[0]), float(pixdim[1]), float(pixdim[2]))
    
    def get_metadata_dict(self) -> Dict[str, Any]:
        """Return metadata as dictionary for logging."""
        return {
            'filepath': str(self.filepath),
            'checksum': self.checksum,
            'dimensions': self.dimensions,
            'voxel_spacing_mm': self.voxel_spacing,
            'data_type': str(self.data_type),
            'value_range': (float(np.min(self.data)), float(np.max(self.data)))
        }


def compute_file_checksum(filepath: Path) -> str:
    """
    Compute SHA256 checksum of file for traceability.
    
    Args:
        filepath: Path to file
        
    Returns:
        Hex digest of SHA256 hash
    """
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def load_nifti_image(filepath: Path) -> ImageData:
    """
    Load NIfTI image with comprehensive validation.
    
    Args:
        filepath: Path to NIfTI file (.nii or .nii.gz)
        
    Returns:
        ImageData container with loaded data and metadata
        
    Raises:
        ImageLoadError: If file cannot be loaded
        MetadataError: If metadata is invalid or missing
    """
    if not filepath.exists():
        raise ImageLoadError(f"File does not exist: {filepath}")
    
    # Verify file extension
    valid_extensions = {'.nii', '.gz'}
    if not any(str(filepath).endswith(ext) for ext in ['.nii', '.nii.gz']):
        raise ImageLoadError(
            f"Invalid file extension: {filepath.suffix}. "
            f"Expected .nii or .nii.gz"
        )
    
    # Compute checksum for traceability
    try:
        checksum = compute_file_checksum(filepath)
    except Exception as e:
        raise ImageLoadError(f"Failed to compute checksum: {e}")
    
    # Load NIfTI file
    try:
        nifti_img: Nifti1Image = nib.load(str(filepath))
    except Exception as e:
        raise ImageLoadError(f"Failed to load NIfTI file: {e}")
    
    # Extract data and metadata
    try:
        data = np.asarray(nifti_img.dataobj, dtype=np.float64)
        affine = nifti_img.affine
        header = nifti_img.header
    except Exception as e:
        raise ImageLoadError(f"Failed to extract image data: {e}")
    
    # Verify dimensionality
    if data.ndim != 3:
        raise MetadataError(
            f"Expected 3D volumetric data, got {data.ndim}D array with shape {data.shape}"
        )
    
    # Verify affine matrix
    if affine.shape != (4, 4):
        raise MetadataError(
            f"Invalid affine matrix shape: {affine.shape}, expected (4, 4)"
        )
    
    return ImageData(
        data=data,
        affine=affine,
        header=header,
        filepath=filepath,
        checksum=checksum
    )
