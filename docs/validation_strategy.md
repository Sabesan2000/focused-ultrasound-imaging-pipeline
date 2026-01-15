# Validation Strategy

## Overview

This document describes the comprehensive validation approach used throughout the focused ultrasound imaging pipeline. Validation occurs at multiple levels to ensure data quality, correctness, and safety.

## Validation Philosophy

### Core Principles

1. **Validate Early**: Catch errors as close to the source as possible
2. **Validate Often**: Multiple validation stages throughout pipeline
3. **Fail Explicitly**: Every validation failure has a clear, actionable error message
4. **Be Comprehensive**: Check everything that can go wrong
5. **Be Specific**: Generic checks are insufficient; validate domain-specific constraints

### Validation vs. Verification

- **Validation**: "Are we building the right thing?" (Requirements)
- **Verification**: "Are we building it right?" (Implementation)

This pipeline includes both:
- **Validation**: Input data meets medical imaging requirements
- **Verification**: Algorithms produce correct outputs (unit tests)

## Validation Layers

### Layer 1: File-Level Validation

**When**: Before attempting to load file  
**Purpose**: Ensure file exists and is accessible  
**Location**: `loader.py`

**Checks**:
- ✅ File exists on filesystem
- ✅ File extension is valid (`.nii` or `.nii.gz`)
- ✅ File is readable
- ✅ Checksum can be computed

**Failure Mode**:
```python
raise ImageLoadError("File does not exist: /path/to/file.nii")
```

### Layer 2: Format Validation

**When**: During file loading  
**Purpose**: Ensure file format is correct  
**Location**: `loader.py`

**Checks**:
- ✅ File can be parsed as NIfTI
- ✅ Header is well-formed
- ✅ Data array can be extracted
- ✅ Affine matrix is present

**Failure Mode**:
```python
raise ImageLoadError("Failed to load NIfTI file: <underlying error>")
```

### Layer 3: Dimensionality Validation

**When**: Immediately after loading  
**Purpose**: Ensure data has correct structure  
**Location**: `loader.py`, `validator.py`

**Checks**:
- ✅ Data is 3D (not 2D or 4D)
- ✅ Dimensions are within reasonable ranges (10-1024 voxels)
- ✅ Affine matrix is 4×4
- ✅ Voxel spacing is 3D

**Failure Mode**:
```python
raise DimensionalityError(
    "Expected 3D volumetric data, got 4D array with shape (64, 64, 64, 20)"
)
```

### Layer 4: Metadata Validation

**When**: After loading, before processing  
**Purpose**: Ensure metadata is physically plausible  
**Location**: `validator.py`

**Checks**:
- ✅ Voxel spacing > 0
- ✅ Voxel spacing in reasonable range (0.1-10mm)
- ✅ Affine matrix bottom row is [0, 0, 0, 1]
- ✅ Orientation information is consistent

**Failure Mode**:
```python
raise MetadataError("Invalid voxel spacing: -1.5 mm")
```

**Warning** (non-blocking):
```
Unusual voxel spacing: 15.0 mm (expected 0.1-10mm)
```

### Layer 5: Data Quality Validation

**When**: After loading, before processing  
**Purpose**: Ensure data values are valid  
**Location**: `validator.py`

**Checks**:
- ✅ No NaN (Not-a-Number) values
- ✅ No infinite values
- ✅ Data is not constant (variance > 0)
- ✅ Value range is reasonable (optional)

**Failure Mode**:
```python
raise DataQualityError("Data contains 42 NaN values")
```

### Layer 6: Configuration Validation

**When**: Before pipeline execution  
**Purpose**: Ensure parameters are valid  
**Location**: `config.py` (Pydantic models)

**Checks**:
- ✅ Required fields are present
- ✅ Types are correct (int, float, Path, etc.)
- ✅ Values are in valid ranges (e.g., percentile 0-100)
- ✅ Paths exist (for input files)
- ✅ Directories can be created (for output)

**Failure Mode**:
```python
pydantic.ValidationError: 
  intensity_threshold_percentile must be between 0 and 100, got 150
```

### Layer 7: Processing Validation

**When**: During image processing  
**Purpose**: Ensure algorithms produce valid outputs  
**Location**: `processor.py`

**Checks**:
- ✅ Thresholding produces non-empty mask
- ✅ Connected components exist
- ✅ Largest component meets minimum volume
- ✅ Target region has valid properties

**Failure Mode**:
```python
raise ProcessingError(
    "No connected components above minimum volume (100.0 mm³)"
)
```

## Validation Report

The `ValidationReport` class provides structured validation results:

```python
report = validate_image_data(image_data)

# Check if valid
if report.is_valid():
    print("All checks passed!")
else:
    print("Validation failed:")
    for error in report.errors:
        print(f"  - {error}")

# Print summary
print(report.get_summary())
```

**Example Output**:
```
Validation Summary:
  Checks passed: 12
  Warnings: 1
  Errors: 0

Warnings:
  - Unusual voxel spacing in dimension 2: 0.05 mm (expected 0.1-10.0 mm)
```

## Unit Test Validation

### Test Coverage Requirements

Each module must have tests covering:

1. **Happy Path**: Normal operation with valid inputs
2. **Error Cases**: Each validation check that can fail
3. **Boundary Cases**: Min/max values, edge conditions
4. **Integration**: Module interactions

### Test Data Strategy

- **Synthetic Data**: Programmatically generated test volumes
- **Controlled Properties**: Exact knowledge of ground truth
- **No Real Data**: Avoids privacy/compliance issues

### Example Test Structure

```python
def test_validate_rejects_nan():
    """Test validation rejects images with NaN values."""
    # Setup: Create data with known defect
    data = create_test_volume()
    data[10, 10, 10] = np.nan
    
    # Execute: Run validation
    report = validate_image_data(image_data)
    
    # Assert: Verify expected failure
    assert not report.is_valid()
    assert any('NaN' in error for error in report.errors)
```

## Validation vs. Performance

### Trade-offs

- **Comprehensive validation** takes time
- **Performance optimization** may reduce validation
- **Medical software** prioritizes correctness over speed

### Current Approach

✅ **Validate everything** - Safety first  
✅ **Single-threaded** - Determinism over speed  
✅ **Explicit checks** - Clarity over brevity  

### Future Optimization

If performance becomes critical:
1. **Profile first**: Identify actual bottlenecks
2. **Optimize algorithms**: Before reducing validation
3. **Parallel processing**: Without compromising determinism
4. **Caching**: Memoize expensive validations (with caution)

**Never**: Skip validation to improve performance in medical software.

## Failure Handling

### Error Response Strategy

When validation fails:

1. **Stop immediately**: Do not continue processing
2. **Log the error**: Structured log with full context
3. **Raise exception**: Appropriate `PipelineError` subclass
4. **Clear message**: Actionable information for user

### Example Error Flow

```
User provides file: corrupted_scan.nii.gz
    ↓
Layer 1: File exists ✅
Layer 2: Format validation ✅
Layer 3: Dimensionality ✅
Layer 4: Metadata ✅
Layer 5: Data quality ❌ → NaN detected
    ↓
Raise DataQualityError("Data contains 15 NaN values")
    ↓
Catch in main.py
    ↓
Log error + context
    ↓
Exit with code 1
```

## Test Coverage Goals

### Quantitative Goals

- **Line coverage**: >90%
- **Branch coverage**: >85%
- **Function coverage**: 100%

### Qualitative Goals

- Every validation check has explicit test
- Every error path is tested
- Integration tests cover full pipeline

### Running Coverage

```bash
# Generate coverage report
pytest --cov=src --cov-report=html

# View report
open htmlcov/index.html
```

## Validation Checklist

Before releasing any version, verify:

- [ ] All validation layers implemented
- [ ] Every check has unit test
- [ ] Error messages are clear and actionable
- [ ] Logs include sufficient context
- [ ] Documentation describes validation strategy
- [ ] Test coverage meets goals (>90% lines)

## Limitations

### What This Validation Does NOT Cover

- **Clinical appropriateness**: Is this the right scan for FUS?
- **Image quality**: Is this a good quality scan?
- **Patient safety**: Is treatment safe for this patient?
- **Expert review**: Should this plan be approved?

These require **clinical validation**, which is beyond the scope of research software.

## Conclusion

This validation strategy ensures:

✅ Bad data is rejected early  
✅ Errors are explicit and traceable  
✅ Tests cover all failure modes  
✅ Validation is comprehensive and thorough  

However, **validation ≠ clinical approval**. This software requires clinical validation and regulatory approval before patient use.
