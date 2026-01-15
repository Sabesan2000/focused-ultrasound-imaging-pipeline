# Development Guidelines

This document outlines development practices for the focused ultrasound imaging pipeline, following medical device software engineering principles.

## Code Quality Standards

### Type Annotations

All functions MUST include complete type annotations:

```python
def process_image(data: np.ndarray, threshold: float) -> np.ndarray:
    """Process image with threshold."""
    return data > threshold
```

### Docstrings

All public functions MUST include NumPy-style docstrings:

```python
def compute_volume(voxel_count: int, spacing: tuple[float, float, float]) -> float:
    """
    Compute physical volume from voxel count.
    
    Args:
        voxel_count: Number of voxels in region
        spacing: Voxel spacing in (x, y, z) dimensions (mm)
        
    Returns:
        Volume in cubic millimeters (mm³)
        
    Raises:
        ValueError: If voxel_count is negative
    """
    if voxel_count < 0:
        raise ValueError("Voxel count must be non-negative")
    
    voxel_volume_mm3 = spacing[0] * spacing[1] * spacing[2]
    return voxel_count * voxel_volume_mm3
```

### Physical Units

All physical quantities MUST include units:

- Use variable suffixes: `volume_mm3`, `spacing_mm`, `distance_cm`
- Document units in docstrings
- Include units in log messages and error messages

### Constants

Define all magic numbers as named constants:

```python
# Good
MIN_VOXEL_SPACING_MM = 0.01
MAX_DIMENSION_SIZE = 2048

# Bad
if spacing < 0.01:  # What is 0.01?
    raise ValueError("Spacing too small")
```

## Testing Requirements

### Coverage

Minimum code coverage: **85%**

Run coverage check:

```bash
pytest --cov=src --cov-fail-under=85
```

### Test Structure

Organize tests by module:

```
tests/
├── conftest.py           # Shared fixtures
├── test_loader.py        # Tests for loader module
├── test_validator.py     # Tests for validator module
├── test_processor.py     # Tests for processor module
└── test_integration.py   # End-to-end tests
```

### Negative Tests

Every validation check MUST have explicit negative tests:

```python
def test_validate_rejects_nan() -> None:
    """Test validation rejects images with NaN values."""
    data = np.random.randn(64, 64, 64)
    data[10, 10, 10] = np.nan
    
    with pytest.raises(DataQualityError):
        validate_or_raise(create_image_data(data))
```

### Test Determinism

All tests MUST be deterministic:

```python
def test_processing_is_reproducible() -> None:
    """Test that processing produces identical results."""
    set_seeds(42)
    result1 = process_image(data)
    
    set_seeds(42)
    result2 = process_image(data)
    
    np.testing.assert_array_equal(result1, result2)
```

## Error Handling

### Custom Exceptions

Use specific exception types for traceability:

```python
# Good
raise DataQualityError(f"Image contains {nan_count} NaN values")

# Bad
raise Exception("Invalid data")
```

### Exception Messages

Provide context in exception messages:

```python
# Good
raise DimensionalityError(
    f"Expected 3D data, got {data.ndim}D. Shape: {data.shape}"
)

# Bad
raise DimensionalityError("Wrong dimensions")
```

## Logging

### Structured Logging

Use structured logging with context:

```python
logger.log_stage_start('process', input_shape=data.shape)
logger.log_metrics({'volume_mm3': volume, 'voxel_count': count})
```

### Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: Pipeline stages, configuration, metrics
- **WARNING**: Unusual but acceptable conditions
- **ERROR**: Validation failures, processing errors

## Git Workflow

### Branch Naming

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `refactor/description` - Code refactoring

### Commit Messages

Follow conventional commits:

```
type(scope): Short description

Longer explanation if needed.

- Bullet points for details
```

**Types**: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`

### Pull Requests

All PRs must:

1. Pass CI checks (linting, type checking, tests)
2. Maintain ≥85% coverage
3. Include tests for new functionality
4. Update documentation if needed

## Pre-Commit Checklist

Before committing code:

- [ ] Run `flake8 src tests` - No linting errors
- [ ] Run `mypy src` - No type errors
- [ ] Run `pytest --cov=src --cov-fail-under=85` - All tests pass, coverage ≥85%
- [ ] Run `black src tests` - Code formatted (optional)
- [ ] Update docstrings for new/modified functions
- [ ] Add tests for new functionality

## Code Review Guidelines

Reviewers should verify:

1. **Safety**: Input validation, error handling, edge cases
2. **Testability**: Code is testable, tests are comprehensive
3. **Documentation**: Docstrings, comments, type hints
4. **Maintainability**: Clear logic, no magic numbers, good naming
5. **Standards**: Follows project conventions

## Performance Considerations

While safety and correctness are paramount:

- Profile before optimizing
- Document performance trade-offs
- Avoid premature optimization
- Prefer clarity over cleverness

## Documentation

Update documentation for:

- New features → README.md
- Architecture changes → docs/architecture.md
- New failure modes → docs/safety_considerations.md
- Testing strategy → docs/validation_strategy.md
