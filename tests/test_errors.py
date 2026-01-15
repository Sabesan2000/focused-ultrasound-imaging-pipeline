"""Tests for custom exception hierarchy."""
import pytest
from src.pipeline.errors import (
    PipelineError,
    ImageLoadError,
    ValidationError,
    DimensionalityError,
    DataQualityError,
    MetadataError,
    ProcessingError,
    ConfigurationError
)


def test_exception_hierarchy() -> None:
    """Test that all custom exceptions inherit from PipelineError."""
    exceptions = [
        ImageLoadError,
        ValidationError,
        DimensionalityError,
        DataQualityError,
        MetadataError,
        ProcessingError,
        ConfigurationError
    ]
    
    for exc_class in exceptions:
        assert issubclass(exc_class, PipelineError)


def test_validation_error_hierarchy() -> None:
    """Test validation error subclasses."""
    validation_exceptions = [
        DimensionalityError,
        DataQualityError,
        MetadataError
    ]
    
    for exc_class in validation_exceptions:
        assert issubclass(exc_class, ValidationError)


def test_exceptions_can_be_raised() -> None:
    """Test that exceptions can be raised with messages."""
    with pytest.raises(DataQualityError) as exc_info:
        raise DataQualityError("Test error message")
    
    assert "Test error message" in str(exc_info.value)
