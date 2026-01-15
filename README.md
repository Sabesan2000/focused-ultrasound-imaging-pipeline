# Focused Ultrasound Imaging Pipeline

**Version 0.1.0**  
**Status: Research Use Only - NOT FOR CLINICAL USE**

## ⚠️ Important Disclaimer

This software is a **research prototype** for pre-clinical focused ultrasound (FUS) treatment planning. It is **NOT approved for clinical use**, **NOT a medical device**, and **NOT validated for patient care**.

This software is intended for:
- Research and development
- Algorithm validation studies
- Educational purposes
- Pre-clinical workflow simulation

## Overview

This pipeline implements a deterministic, safety-critical approach to medical image processing for focused ultrasound treatment planning. It demonstrates production-quality software engineering practices suitable for regulated medical environments.

### Key Features

- ✅ **Comprehensive input validation** - Rejects malformed, corrupted, or out-of-range data
- ✅ **Deterministic processing** - Reproducible results with fixed seeds
- ✅ **Quantitative metrics** - Physical measurements with explicit units (mm, mm³)
- ✅ **Structured logging** - Audit-ready logs in JSON format
- ✅ **Traceability** - File checksums and full configuration tracking
- ✅ **Professional testing** - Comprehensive unit test coverage
- ✅ **Clean architecture** - Modular design with separation of concerns

## Architecture

```
focused-ultrasound-imaging-pipeline/
├── src/
│   ├── pipeline/
│   │   ├── loader.py         # NIfTI image loading with validation
│   │   ├── validator.py      # Comprehensive data validation
│   │   ├── processor.py      # Target identification algorithms
│   │   ├── metrics.py        # Quantitative metric computation
│   │   ├── visualizer.py     # 2D/3D visualization generation
│   │   ├── config.py         # Type-safe configuration (Pydantic)
│   │   └── errors.py         # Custom exception hierarchy
│   └── utils/
│       ├── logging.py        # Structured logging
│       └── reproducibility.py # Determinism utilities
├── main.py                   # Pipeline entry point
├── tests/                    # Comprehensive test suite
├── docs/                     # Documentation
└── requirements.txt          # Dependencies
```

See [docs/architecture.md](docs/architecture.md) for detailed design documentation.

## Installation

### Requirements

- Python 3.10 or higher
- Linux operating system (recommended)
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

### Output

The pipeline generates:

- `metrics.json` - Quantitative measurements in JSON format
- `metrics_report.txt` - Human-readable metrics report
- `target_visualization.png` - Orthogonal slice views with target overlay
- `pipeline_<timestamp>.log` - Structured execution log

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

### Run with Coverage

```bash
pytest --cov=src --cov-report=html
```

### Run Specific Test Module

```bash
pytest tests/test_loader.py -v
```

## Configuration

The pipeline uses strongly-typed configuration via Pydantic. Key parameters:

```python
ProcessingConfig:
  - intensity_threshold_percentile: 70.0  # Segmentation threshold
  - minimum_component_volume_mm3: 100.0   # Min target volume
  - random_seed: 42                       # For reproducibility

VisualizationConfig:
  - generate_slice_views: True
  - generate_3d_rendering: False  # Computationally expensive
  - dpi: 150
```

## Validation Strategy

All input data undergoes comprehensive validation:

1. **File-level validation**: Format, extensions, accessibility
2. **Metadata validation**: Dimensions, voxel spacing, affine matrix
3. **Data quality validation**: NaN detection, infinity checks, range validation
4. **Sanity checks**: Variance, dimension sizes, physical units

See [docs/validation_strategy.md](docs/validation_strategy.md) for details.

## Safety Considerations

While this is research software, it follows safety-critical development principles:

- **Fail-fast philosophy**: Invalid data is rejected immediately
- **Explicit error messages**: Every failure mode has a descriptive error
- **Traceability**: All operations are logged with timestamps and checksums
- **Determinism**: Fixed seeds ensure reproducible results
- **Unit testing**: Every module has comprehensive test coverage

See [docs/safety_considerations.md](docs/safety_considerations.md) for full discussion.

## Limitations

- **Not validated for clinical use**
- **No regulatory approval** (FDA, CE, etc.)
- **Limited to NIfTI format** (DICOM support not implemented)
- **Single-target identification** (does not handle multiple targets)
- **No real-time processing** (batch processing only)

## Contributing

This is a demonstration project. For production medical software:

1. Implement full DICOM support with conformance testing
2. Add multi-target identification and tracking
3. Implement formal validation protocols (IQ/OQ/PQ)
4. Add user authentication and audit trails
5. Implement regulatory-compliant documentation
6. Add formal risk management (ISO 14971)

## License

MIT License - See LICENSE file

## Contact

For questions about this software engineering demonstration:
- Repository: <repository-url>
- Documentation: docs/

---

**Remember: This is research software. Never use for clinical decision-making.**
