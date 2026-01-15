"""
Custom exception types for the medical imaging pipeline.

All exceptions are explicit and traceable to support safety-critical workflows.
"""


class PipelineError(Exception):
    """Base exception for all pipeline errors."""
    pass


class ImageLoadError(PipelineError):
    """Raised when image loading fails."""
    pass


class ValidationError(PipelineError):
    """Raised when input validation fails."""
    pass


class DimensionalityError(ValidationError):
    """Raised when image dimensions are incorrect."""
    pass


class DataQualityError(ValidationError):
    """Raised when data contains invalid values (NaN, Inf, out of range)."""
    pass


class MetadataError(ValidationError):
    """Raised when required metadata is missing or invalid."""
    pass


class ProcessingError(PipelineError):
    """Raised when image processing fails."""
    pass


class ConfigurationError(PipelineError):
    """Raised when configuration is invalid."""
    pass
