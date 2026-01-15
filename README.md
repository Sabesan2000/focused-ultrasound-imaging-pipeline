# Focused Ultrasound Imaging Pipeline

![CI Pipeline](https://github.com/YOUR_ORG/focused-ultrasound-imaging-pipeline/actions/workflows/ci.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-≥85%25-brightgreen)
![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue)

**Version 0.2.0**  
**Status: Research Use Only - NOT FOR CLINICAL USE**

## ⚠️ Important Disclaimer

This software is a **research prototype** for pre-clinical focused ultrasound (FUS) treatment planning. It is **NOT approved for clinical use**, **NOT a medical device**, and **NOT validated for patient care**.

This software is intended for:
- Research and development
- Algorithm validation studies
- Educational purposes
- Pre-clinical workflow simulation

## Overview

This pipeline implements a deterministic, safety-critical approach to medical image processing for focused ultrasound treatment planning. It demonstrates production-quality software engineering practices suitable for regulated medical research environments, following principles from FDA guidance and IEC 62304 standards.

### Key Features

- ✅ **Medical-grade validation** - Comprehensive input validation with explicit failure modes
- ✅ **Affine matrix validation** - Checks for singularity, finiteness, and proper structure
- ✅ **Physical constraints** - Voxel spacing validated against realistic medical imaging ranges
- ✅ **Deterministic processing** - Reproducible results with fixed seeds and checksums
- ✅ **Quantitative metrics** - Physical measurements with explicit units (mm, mm³)
- ✅ **Structured audit logging** - JSON-formatted logs suitable for regulatory review
- ✅ **Traceability** - SHA-256 checksums and full configuration tracking
- ✅ **Comprehensive testing** - >85% coverage with explicit negative tests
- ✅ **CI/CD pipeline** - Automated quality gates with linting, type checking, and coverage enforcement
- ✅ **Clean architecture** - Modular design with typed exceptions and separation of concerns

## Architecture

```
focused-ultrasound-imaging-pipeline/
├── .github/
│   └── workflows/
│       └── ci.yml            # CI/CD pipeline configuration
├── src/
│   ├── pipeline/
│   │   ├── loader.py         # NIfTI image loading with checksum
│   │   ├── validator.py      # Medical-grade validation with typed errors
│   │   ├── processor.py      # Deterministic target identification
│   │   ├── metrics.py        # Physical metric computation
│   │   ├── visualizer.py     # Publication-quality visualization
│   │   ├── config.py         # Type-safe configuration (Pydantic)
│   │   └── errors.py         # Custom exception hierarchy
│   └── utils/
│       ├── logging.py        # Structured JSON logging
│       └── reproducibility.py # Determinism and environment tracking
├── tests/
│   ├── conftest.py           # Shared test fixtures
│   ├── test_loader.py        # Loader tests
│   ├── test_validator.py     # Comprehensive validation tests
│   ├── test_processor.py     # Processing tests
│   ├── test_metrics.py       # Metrics tests
│   ├── test_reproducibility.py # Reproducibility tests
│   ├── test_errors.py        # Exception hierarchy tests
│   └── test_integration.py   # End-to-end pipeline tests
├── docs/
│   ├── architecture.md       # System design documentation
│   ├── safety_considerations.md # Safety analysis
│   ├── validation_strategy.md   # Testing philosophy
│   ├── DEVELOPMENT.md        # Development guidelines
│   └── CHANGELOG.md          # Version history
├── config/
│   └── example_config.yaml   # Example configuration
├── main.py                   # Pipeline entry point
├── requirements.txt          # Python dependencies
├── pyproject.toml            # Project configuration
└── .flake8                   # Linting configuration
```

See [docs/architecture.md](docs/architecture.md) for detailed design documentation.

## Installation

### Requirements

- Python 3.10 or higher
- Linux operating system (recommended; tested on Ubuntu 22.04)
- 4GB+ RAM for typical volumes

### Setup

```bash
# Clone repository
git clone <repository-url>
cd focused-ultrasound-imaging-pipeline

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Verify Installation

```bash
# Run test suite
pytest

# Check coverage
pytest --cov=src --cov-report=term

# Run linting
flake8 src tests

# Run type checking
mypy src --ignore-missing-imports
```

## Usage

### Basic Execution

```bash
python main.py <input_nifti_file> [output_directory]
```

### Example

```bash
# Process a brain MRI volume
python main.py data/brain_t1.nii.gz output/

# Use custom output directory
python main.py data/scan_001.nii.gz results/scan_001/
```

### Configuration File (Optional)

```bash
# Copy example configuration
cp config/example_config.yaml my_config.yaml

# Edit configuration as needed
# Then use programmatically in your scripts
```

### Output

The pipeline generates:

- `metrics.json` - Quantitative measurements in JSON format
- `metrics_report.txt` - Human-readable metrics report
- `target_visualization.png` - Orthogonal slice views with target overlay
- `pipeline_<timestamp>.log` - Structured execution log (JSON format)

### Example Output

```
==============================================================
TARGET REGION METRICS REPORT
==============================================================

VOLUME:
  Total volume: 2145.67 mm³
  Voxel count: 2146

CENTROID (Voxel Coordinates):
  X: 32.45
  Y: 31.89
  Z: 33.12

CENTROID (Physical Coordinates):
  X: 32.45 mm
  Y: 31.89 mm
  Z: 33.12 mm

BOUNDING BOX (Voxel Space):
  X: [25, 40]
  Y: [24, 39]
  Z: [26, 41]

... (additional metrics)
==============================================================
```

## Testing

### Run Full Test Suite

```bash
pytest
```

### Run with Coverage Report

```bash
pytest --cov=src --cov-report=html --cov-report=term
```

Open `htmlcov/index.html` to view detailed coverage report.

### Run with Coverage Enforcement

```bash
# Fail if coverage drops below 85%
pytest --cov=src --cov-fail-under=85
```

### Run Specific Test Categories

```bash
# Validation tests only
pytest tests/test_validator.py -v

# Integration tests
pytest tests/test_integration.py -v

# Fast unit tests (skip slow integration tests)
pytest -m "not slow"
```

### Run Negative Tests

All validation functions have corresponding negative tests that verify proper failure handling:

```bash
# See all tests that verify error conditions
pytest tests/test_validator.py -k "reject" -v
```

## Configuration

The pipeline uses strongly-typed configuration via Pydantic. Key parameters:

```python
ProcessingConfig:
  - intensity_percentile_threshold: 95.0  # Target intensity threshold
  - smoothing_sigma: 1.0                   # Gaussian smoothing (voxels)
  - random_seed: 42                        # For reproducibility

VisualizationConfig:
  - generate_slice_views: True
  - slice_selection: "mid"  # or "max_intensity"
  - dpi: 150
  - colormap: "gray"
```

See `config/example_config.yaml` for a complete configuration example.

## Validation Strategy

All input data undergoes comprehensive validation following medical device software principles:

### 1. Dimensionality Validation
- Must be 3D volumetric data (not 2D or 4D)
- Dimensions must be within realistic bounds (8-2048 voxels)

### 2. Data Quality Validation
- No NaN (Not-a-Number) values
- No infinite values
- Non-zero variance (detects constant/corrupted data)

### 3. Metadata Validation
- **Voxel spacing**: Must be positive, finite, within 0.01-50mm range
- **Affine matrix**: Must be 4×4, finite values, non-singular rotation/scale submatrix

### 4. Physical Constraints
- Value ranges checked against expected medical imaging intensities
- Physical units validated for all measurements

**Failure Handling**: All validation failures raise typed exceptions (DimensionalityError, DataQualityError, MetadataError) with detailed context.

See [docs/validation_strategy.md](docs/validation_strategy.md) for complete details.

## Safety Considerations

While this is research software, it follows safety-critical development principles appropriate for medical imaging:

- **Fail-fast philosophy**: Invalid data is rejected immediately with clear errors
- **Explicit error messages**: Every failure mode has a descriptive, actionable error
- **Typed exceptions**: Precise error classification for traceability
- **Comprehensive logging**: All operations logged with timestamps, checksums, and metadata
- **Determinism**: Fixed seeds and deterministic algorithms ensure reproducibility
- **Input validation**: Multiple layers of validation catch corrupted or malformed data
- **Unit testing**: >85% coverage with explicit negative tests for all failure modes
- **Continuous integration**: Automated quality gates prevent regression

See [docs/safety_considerations.md](docs/safety_considerations.md) for full discussion.

## Continuous Integration

This project uses GitHub Actions for automated quality assurance:

### CI Pipeline Checks

- ✅ **Multi-version testing**: Python 3.10 and 3.11
- ✅ **Linting**: flake8 with complexity checks
- ✅ **Type checking**: mypy static analysis
- ✅ **Test execution**: Full test suite on every push/PR
- ✅ **Coverage enforcement**: Fails if coverage drops below 85%
- ✅ **Artifact generation**: HTML coverage reports uploaded

### Running CI Checks Locally

```bash
# Run all CI checks before pushing
flake8 src tests --max-complexity=10 --max-line-length=100
mypy src --ignore-missing-imports
pytest --cov=src --cov-fail-under=85
```

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for full development guidelines.

## Limitations

- **Not validated for clinical use**
- **No regulatory approval** (FDA, CE, Health Canada, etc.)
- **Limited to NIfTI format** (DICOM support not implemented)
- **Single-target identification** (does not handle multiple targets)
- **No real-time processing** (batch processing only)
- **No user authentication** (single-user research tool)

## Contributing

This is a demonstration project showing medical research software engineering practices. For production medical software, additional requirements include:

1. **DICOM support** with conformance testing
2. **Multi-target identification** and tracking
3. **Formal validation protocols** (IQ/OQ/PQ)
4. **User authentication** and role-based access control
5. **Regulatory documentation** (design history file, risk management)
6. **Clinical validation** with ground truth data
7. **Formal risk management** (ISO 14971, FMEA)
8. **Change control** and version management

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for development guidelines.

## Documentation

- [Architecture Overview](docs/architecture.md) - System design and module responsibilities
- [Safety Considerations](docs/safety_considerations.md) - Failure modes and safety analysis
- [Validation Strategy](docs/validation_strategy.md) - Testing philosophy and coverage goals
- [Development Guidelines](docs/DEVELOPMENT.md) - Coding standards and workflow
- [Changelog](docs/CHANGELOG.md) - Version history

## License

MIT License - See LICENSE file

## Regulatory Intent Statement

**This software is a research prototype demonstrating medical device software engineering principles. It is NOT intended for clinical use and has NOT undergone regulatory review or approval.**

If this software were to be developed for clinical use, it would require:
- FDA 510(k) clearance or PMA approval (US)
- CE Mark under MDR (Europe)
- Health Canada MDEL license (Canada)
- ISO 13485 quality management system
- IEC 62304 software lifecycle compliance
- ISO 14971 risk management documentation
- Clinical validation studies
- Post-market surveillance

## Contact

For questions about this software engineering demonstration:
- Repository: <repository-url>
- Documentation: docs/
- Issues: <repository-url>/issues

---

**Remember: This is research software. Never use for clinical decision-making.**
