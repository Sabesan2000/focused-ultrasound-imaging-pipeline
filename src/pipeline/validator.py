"""
Data validation module for medical imaging pipeline.

Implements comprehensive validation to ensure data quality and catch
malformed inputs before processing.
"""
import numpy as np
from typing import Optional

from .loader import ImageData
from .errors import ValidationError, DataQualityError, DimensionalityError


class ValidationReport:
    """Container for validation results."""
    
    def __init__(self):
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
            f"Validation Summary:",
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


def validate_image_data(
    image_data: ImageData,
    min_dimension_size: int = 10,
    max_dimension_size: int = 1024,
    expected_value_range: Optional[tuple[float, float]] = None
) -> ValidationReport:
    """
    Perform comprehensive validation of loaded image data.
    
    Args:
        image_data: Loaded image data to validate
        min_dimension_size: Minimum acceptable dimension size
        max_dimension_size: Maximum acceptable dimension size
        expected_value_range: Optional expected (min, max) intensity range
        
    Returns:
        ValidationReport with results of all checks
    """
    report = ValidationReport()
    data = image_data.data
    
    # Check 1: Verify 3D dimensionality
    if data.ndim != 3:
        report.add_error(f"Expected 3D data, got {data.ndim}D")
    else:
        report.add_pass("Dimensionality check (3D)")
    
    # Check 2: Verify dimension sizes are reasonable
    for i, dim_size in enumerate(data.shape):
        if dim_size < min_dimension_size:
            report.add_error(
                f"Dimension {i} too small: {dim_size} < {min_dimension_size}"
            )
        elif dim_size > max_dimension_size:
            report.add_error(
                f"Dimension {i} too large: {dim_size} > {max_dimension_size}"
            )
        else:
            report.add_pass(f"Dimension {i} size valid ({dim_size})")
    
    # Check 3: Verify no NaN values
    nan_count = np.sum(np.isnan(data))
    if nan_count > 0:
        report.add_error(f"Data contains {nan_count} NaN values")
    else:
        report.add_pass("No NaN values")
    
    # Check 4: Verify no infinite values
    inf_count = np.sum(np.isinf(data))
    if inf_count > 0:
        report.add_error(f"Data contains {inf_count} infinite values")
    else:
        report.add_pass("No infinite values")
    
    # Check 5: Verify data is not constant
    if np.std(data) < 1e-10:
        report.add_error("Data is constant (zero variance)")
    else:
        report.add_pass("Data has non-zero variance")
    
    # Check 6: Verify value range if expected range provided
    data_min, data_max = float(np.min(data)), float(np.max(data))
    if expected_value_range is not None:
        expected_min, expected_max = expected_value_range
        if data_min < expected_min or data_max > expected_max:
            report.add_warning(
                f"Data range [{data_min:.2f}, {data_max:.2f}] outside "
                f"expected range [{expected_min:.2f}, {expected_max:.2f}]"
            )
        else:
            report.add_pass("Value range within expected bounds")
    else:
        report.add_pass(f"Value range: [{data_min:.2f}, {data_max:.2f}]")
    
    # Check 7: Verify voxel spacing is reasonable
    voxel_spacing = image_data.voxel_spacing
    for i, spacing in enumerate(voxel_spacing):
        if spacing <= 0:
            report.add_error(f"Invalid voxel spacing in dimension {i}: {spacing} <= 0")
        elif spacing < 0.1 or spacing > 10.0:
            report.add_warning(
                f"Unusual voxel spacing in dimension {i}: {spacing} mm "
                f"(expected 0.1-10.0 mm)"
            )
        else:
            report.add_pass(f"Voxel spacing dimension {i}: {spacing:.3f} mm")
    
    # Check 8: Verify affine matrix is well-formed
    affine = image_data.affine
    if not np.allclose(affine[3, :], [0, 0, 0, 1]):
        report.add_warning("Affine matrix bottom row is not [0, 0, 0, 1]")
    else:
        report.add_pass("Affine matrix well-formed")
    
    return report


def validate_or_raise(image_data: ImageData) -> None:
    """
    Validate image data and raise exception if validation fails.
    
    Args:
        image_data: Loaded image data to validate
        
    Raises:
        ValidationError: If any validation checks fail
    """
    report = validate_image_data(image_data)
    
    if not report.is_valid():
        raise ValidationError(
            f"Image validation failed:\n{report.get_summary()}"
        )
