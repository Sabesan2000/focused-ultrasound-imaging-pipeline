"""
Data validation module for medical imaging pipeline.

Implements comprehensive validation to ensure data quality and catch
malformed inputs before processing.
"""
import numpy as np
from typing import Optional

from .loader import ImageData
from .errors import (
    ValidationError,
    DataQualityError,
    DimensionalityError,
    MetadataError
)


class ValidationReport:
    """Container for validation results."""
    
    def __init__(self) -> None:
        """Initialize empty validation report."""
        self.checks_passed: list[str] = []
        self.warnings: list[str] = []
        self.errors: list[str] = []
    
    def add_pass(self, check_name: str) -> None:
        """Record successful validation check."""
        self.checks_passed.append(check_name)
    
    def add_warning(self, message: str) -> None:
        """Record validation warning."""
        self.warnings.append(message)
    
    def add_error(self, message: str) -> None:
        """Record validation error."""
        self.errors.append(message)
    
    def is_valid(self) -> bool:
        """Return True if no errors were recorded."""
        return len(self.errors) == 0
    
    def get_summary(self) -> str:
        """Return human-readable summary of validation."""
        lines = [
            "Validation Summary:",
            f"  Checks passed: {len(self.checks_passed)}",
            f"  Warnings: {len(self.warnings)}",
            f"  Errors: {len(self.errors)}"
        ]
        
        if self.warnings:
            lines.append("\nWarnings:")
            for warning in self.warnings:
                lines.append(f"  - {warning}")
        
        if self.errors:
            lines.append("\nErrors:")
            for error in self.errors:
                lines.append(f"  - {error}")
        
        return "\n".join(lines)


# Physical spacing constraints for medical imaging (mm)
MIN_VOXEL_SPACING_MM = 0.01  # 10 micrometers
MAX_VOXEL_SPACING_MM = 50.0  # 5 cm

# Dimension size constraints
ABSOLUTE_MIN_DIMENSION = 8
ABSOLUTE_MAX_DIMENSION = 2048


def _validate_affine_matrix(affine: np.ndarray, report: ValidationReport) -> None:
    """
    Validate affine transformation matrix.
    
    Args:
        affine: 4x4 affine transformation matrix
        report: ValidationReport to populate
    """
    # Check 1: Must be 4x4
    if affine.shape != (4, 4):
        report.add_error(
            f"Affine matrix must be 4x4, got shape {affine.shape}"
        )
        return  # Cannot continue validation
    else:
        report.add_pass("Affine matrix is 4x4")
    
    # Check 2: Must contain only finite values
    if not np.all(np.isfinite(affine)):
        report.add_error("Affine matrix contains non-finite values (NaN or Inf)")
        return
    else:
        report.add_pass("Affine matrix contains only finite values")
    
    # Check 3: Bottom row should be [0, 0, 0, 1]
    expected_bottom = np.array([0, 0, 0, 1])
    if not np.allclose(affine[3, :], expected_bottom, atol=1e-6):
        report.add_error(
            f"Affine matrix bottom row must be [0, 0, 0, 1], "
            f"got {affine[3, :]}"
        )
    else:
        report.add_pass("Affine matrix bottom row is [0, 0, 0, 1]")
    
    # Check 4: Rotation/scale submatrix must be non-singular
    rotation_scale = affine[:3, :3]
    det = np.linalg.det(rotation_scale)
    if np.abs(det) < 1e-10:
        report.add_error(
            f"Affine rotation/scale submatrix is singular (det={det:.2e})"
        )
    else:
        report.add_pass(
            f"Affine rotation/scale submatrix is non-singular (det={det:.4f})"
        )
    
    # Check 5: Warn if determinant is negative (indicates reflection)
    if det < 0:
        report.add_warning(
            f"Affine matrix has negative determinant ({det:.4f}), "
            "indicating coordinate system reflection"
        )


def _validate_voxel_spacing(
    spacing: tuple[float, float, float],
    report: ValidationReport
) -> None:
    """
    Validate voxel spacing with strict physical constraints.
    
    Args:
        spacing: Voxel spacing in (x, y, z) dimensions (mm)
        report: ValidationReport to populate
    """
    for i, sp in enumerate(spacing):
        # Check for non-positive spacing
        if sp <= 0:
            report.add_error(
                f"Voxel spacing dimension {i} must be positive, got {sp} mm"
            )
            continue
        
        # Check for non-finite spacing
        if not np.isfinite(sp):
            report.add_error(
                f"Voxel spacing dimension {i} must be finite, got {sp}"
            )
            continue
        
        # Check physical constraints
        if sp < MIN_VOXEL_SPACING_MM:
            report.add_error(
                f"Voxel spacing dimension {i} ({sp} mm) below minimum "
                f"threshold ({MIN_VOXEL_SPACING_MM} mm)"
            )
        elif sp > MAX_VOXEL_SPACING_MM:
            report.add_error(
                f"Voxel spacing dimension {i} ({sp} mm) exceeds maximum "
                f"threshold ({MAX_VOXEL_SPACING_MM} mm)"
            )
        elif sp < 0.1 or sp > 10.0:
            report.add_warning(
                f"Unusual voxel spacing dimension {i}: {sp:.3f} mm "
                "(typical range: 0.1-10.0 mm)"
            )
        else:
            report.add_pass(f"Voxel spacing dimension {i}: {sp:.3f} mm")


def validate_image_data(
    image_data: ImageData,
    min_dimension_size: int = ABSOLUTE_MIN_DIMENSION,
    max_dimension_size: int = ABSOLUTE_MAX_DIMENSION,
    expected_value_range: Optional[tuple[float, float]] = None
) -> ValidationReport:
    """
    Perform comprehensive validation of loaded image data.
    
    This function implements medical-grade validation suitable for
    safety-critical imaging pipelines. All checks are explicit and
    designed to catch malformed data before processing.
    
    Args:
        image_data: Loaded image data to validate
        min_dimension_size: Minimum acceptable dimension size (voxels)
        max_dimension_size: Maximum acceptable dimension size (voxels)
        expected_value_range: Optional expected (min, max) intensity range
        
    Returns:
        ValidationReport with results of all checks
        
    Note:
        This validation is designed for research use but follows
        principles appropriate for regulated medical device software.
    """
    report = ValidationReport()
    data = image_data.data
    
    # Check 1: Verify 3D dimensionality (MANDATORY for this pipeline)
    if data.ndim != 3:
        report.add_error(
            f"Pipeline requires 3D volumetric data, got {data.ndim}D array. "
            f"Shape: {data.shape}"
        )
        # This is fatal - cannot continue validation
        return report
    else:
        report.add_pass(f"Dimensionality check: 3D (shape: {data.shape})")
    
    # Check 2: Verify dimension sizes are physically reasonable
    for i, dim_size in enumerate(data.shape):
        if dim_size < min_dimension_size:
            report.add_error(
                f"Dimension {i} size ({dim_size}) below minimum "
                f"threshold ({min_dimension_size} voxels)"
            )
        elif dim_size > max_dimension_size:
            report.add_error(
                f"Dimension {i} size ({dim_size}) exceeds maximum "
                f"threshold ({max_dimension_size} voxels)"
            )
        else:
            report.add_pass(f"Dimension {i} size valid: {dim_size} voxels")
    
    # Check 3: Verify no NaN values (DATA QUALITY CRITICAL)
    nan_count = np.sum(np.isnan(data))
    if nan_count > 0:
        nan_fraction = nan_count / data.size
        report.add_error(
            f"Data contains {nan_count} NaN values "
            f"({nan_fraction*100:.4f}% of total voxels)"
        )
    else:
        report.add_pass("No NaN values detected")
    
    # Check 4: Verify no infinite values (DATA QUALITY CRITICAL)
    inf_count = np.sum(np.isinf(data))
    if inf_count > 0:
        inf_fraction = inf_count / data.size
        report.add_error(
            f"Data contains {inf_count} infinite values "
            f"({inf_fraction*100:.4f}% of total voxels)"
        )
    else:
        report.add_pass("No infinite values detected")
    
    # Check 5: Verify data is not constant (zero variance indicates corruption)
    data_std = float(np.std(data))
    if data_std < 1e-10:
        report.add_error(
            f"Data has zero variance (std={data_std:.2e}), indicating "
            "constant values or numerical precision issues"
        )
    else:
        report.add_pass(f"Data has non-zero variance (std={data_std:.4f})")
    
    # Check 6: Verify value range
    data_min, data_max = float(np.min(data)), float(np.max(data))
    if expected_value_range is not None:
        expected_min, expected_max = expected_value_range
        if data_min < expected_min or data_max > expected_max:
            report.add_warning(
                f"Data range [{data_min:.2f}, {data_max:.2f}] outside "
                f"expected range [{expected_min:.2f}, {expected_max:.2f}]"
            )
        else:
            report.add_pass(
                f"Value range [{data_min:.2f}, {data_max:.2f}] "
                "within expected bounds"
            )
    else:
        report.add_pass(f"Value range: [{data_min:.2f}, {data_max:.2f}]")
    
    # Check 7: Validate voxel spacing (CRITICAL for physical measurements)
    _validate_voxel_spacing(image_data.voxel_spacing, report)
    
    # Check 8: Validate affine matrix (CRITICAL for coordinate transforms)
    _validate_affine_matrix(image_data.affine, report)
    
    return report


def validate_or_raise(image_data: ImageData) -> None:
    """
    Validate image data and raise exception if validation fails.
    
    This is the primary validation entry point for the pipeline.
    It performs comprehensive checks and raises typed exceptions
    for traceability.
    
    Args:
        image_data: Loaded image data to validate
        
    Raises:
        DimensionalityError: If data is not 3D
        DataQualityError: If data contains NaN/Inf or is constant
        MetadataError: If voxel spacing or affine matrix is invalid
        ValidationError: For other validation failures
    """
    report = validate_image_data(image_data)
    
    if not report.is_valid():
        # Classify the type of failure for specific exception
        error_text = report.get_summary()
        
        # Check for dimensionality errors
        if any('3D' in err or 'dimension' in err.lower() 
               for err in report.errors):
            raise DimensionalityError(
                f"Image dimensionality validation failed:\n{error_text}"
            )
        
        # Check for data quality errors (NaN, Inf, constant)
        if any(term in err.lower() for err in report.errors 
               for term in ['nan', 'infinite', 'constant', 'variance']):
            raise DataQualityError(
                f"Image data quality validation failed:\n{error_text}"
            )
        
        # Check for metadata errors (spacing, affine)
        if any(term in err.lower() for err in report.errors 
               for term in ['spacing', 'affine', 'matrix']):
            raise MetadataError(
                f"Image metadata validation failed:\n{error_text}"
            )
        
        # Generic validation error
        raise ValidationError(
            f"Image validation failed:\n{error_text}"
        )
