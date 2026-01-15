# Architecture Documentation

## Design Philosophy

This pipeline is structured as a **layered, modular architecture** following principles from safety-critical software engineering:

### Core Principles

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Fail-Fast**: Validation happens early; errors are explicit and traceable
3. **Immutability**: Data transformations create new objects rather than mutating
4. **Explicit Over Implicit**: No magic behaviors; all operations are documented
5. **Testability**: Every component can be tested in isolation

## Layer Architecture

\`\`\`
┌─────────────────────────────────────┐
│         Main Entry Point            │
│         (Orchestration)             │
└──────────────┬──────────────────────┘
               │
       ┌───────┴───────┐
       │               │
┌──────▼──────┐ ┌─────▼──────┐
│  Pipeline   │ │   Utils    │
│  Modules    │ │  Modules   │
└─────────────┘ └────────────┘
\`\`\`

### Layer 1: Pipeline Modules

#### loader.py
- **Responsibility**: Load volumetric medical imaging data (NIfTI)
- **Key Functions**:
  - File I/O with comprehensive error handling
  - Metadata extraction and validation
  - Checksum computation for traceability
- **Output**: `ImageData` container with validated data and metadata

#### validator.py
- **Responsibility**: Comprehensive data quality validation
- **Key Functions**:
  - NaN/Inf detection
  - Dimension validation
  - Value range checks
  - Metadata validation
- **Output**: `ValidationReport` with pass/fail for each check

#### processor.py
- **Responsibility**: Image processing algorithms for target identification
- **Key Functions**:
  - Intensity-based thresholding
  - Connected component analysis
  - Largest component extraction
- **Output**: `TargetRegion` with binary mask and properties

#### metrics.py
- **Responsibility**: Quantitative measurement computation
- **Key Functions**:
  - Volume calculation (mm³)
  - Centroid computation (voxel + physical space)
  - Bounding box extraction
- **Output**: Dictionary of measurements with explicit units

#### visualizer.py
- **Responsibility**: Generate visual outputs
- **Key Functions**:
  - 2D orthogonal slice visualization
  - Optional 3D surface rendering (VTK)
  - Overlay of target regions
- **Output**: PNG images

#### config.py
- **Responsibility**: Type-safe configuration management
- **Key Functions**:
  - Pydantic models for validation
  - Default value management
  - Configuration serialization
- **Output**: Validated configuration objects

#### errors.py
- **Responsibility**: Custom exception hierarchy
- **Key Functions**:
  - Explicit error types for each failure mode
  - Inheritance from base `PipelineError`
- **Purpose**: Enable precise error handling and meaningful messages

### Layer 2: Utility Modules

#### logging.py
- **Responsibility**: Structured, audit-ready logging
- **Key Functions**:
  - JSON-formatted log output
  - Stage-based logging (start/complete)
  - File and console handlers
- **Format**: ISO 8601 timestamps, structured fields

#### reproducibility.py
- **Responsibility**: Ensure deterministic execution
- **Key Functions**:
  - Seed management for all RNGs
  - Environment information tracking
  - Threading configuration for determinism

## Data Flow

\`\`\`
Input NIfTI File
      │
      ▼
┌──────────────┐
│    Loader    │ ← Loads data, computes checksum
└──────┬───────┘
       │ ImageData
       ▼
┌──────────────┐
│  Validator   │ ← Validates quality, rejects invalid
└──────┬───────┘
       │ ImageData (validated)
       ▼
┌──────────────┐
│  Processor   │ ← Identifies target region
└──────┬───────┘
       │ TargetRegion
       ▼
┌──────────────┐
│   Metrics    │ ← Computes measurements
└──────┬───────┘
       │ Metrics dict
       ▼
┌──────────────┐
│ Visualizer   │ ← Generates images
└──────┬───────┘
       │
       ▼
Output Files (JSON, PNG, TXT, LOG)
\`\`\`

## Error Handling Strategy

### Exception Hierarchy

\`\`\`
Exception
  └── PipelineError (base for all pipeline errors)
       ├── ImageLoadError
       ├── ValidationError
       │    ├── DimensionalityError
       │    ├── DataQualityError
       │    └── MetadataError
       ├── ProcessingError
       └── ConfigurationError
\`\`\`

### Error Handling Pattern

1. **Catch at lowest level**: Module functions catch library-specific errors
2. **Transform to pipeline errors**: Convert to appropriate `PipelineError` subclass
3. **Add context**: Include relevant information in error message
4. **Propagate**: Let caller handle pipeline errors
5. **Log**: All errors are logged with full context

## Design Decisions

### Why NIfTI over DICOM?

- **Simplicity**: NIfTI is simpler for research prototypes
- **Single file**: Easier to manage than DICOM series
- **Note**: Production systems should support DICOM with full conformance

### Why Pydantic for Configuration?

- **Type safety**: Runtime validation of configuration
- **Documentation**: Models serve as documentation
- **Serialization**: Easy JSON export for logging

### Why Not ORM/Database?

- **Scope**: This is a batch processing pipeline, not a data management system
- **Simplicity**: File-based I/O is sufficient for research use
- **Note**: Production systems may require database integration

### Why Structured Logging?

- **Auditability**: JSON logs can be parsed and analyzed
- **Compliance**: Supports regulatory requirements for traceability
- **Debugging**: Easier to filter and search structured data

## Testing Strategy

### Unit Tests

Each module has dedicated unit tests covering:
- **Happy path**: Normal operation with valid inputs
- **Error cases**: Each error condition explicitly tested
- **Edge cases**: Boundary conditions and corner cases

### Test Data

- **Synthetic data**: Generated programmatically for determinism
- **Fixtures**: Shared test data via pytest fixtures
- **No real data**: Avoids privacy/compliance issues

### Coverage Goals

- **Line coverage**: >90%
- **Branch coverage**: >85%
- **Function coverage**: 100%

## Future Architectural Improvements

For production deployment, consider:

1. **Plugin Architecture**: Support multiple file formats via plugins
2. **Pipeline DAG**: Directed acyclic graph for complex workflows
3. **Distributed Processing**: Support for large-scale batch processing
4. **Database Integration**: Store results in RDBMS with audit trail
5. **Web API**: RESTful interface for integration with clinical systems
6. **Docker Containers**: Reproducible deployment environments
7. **CI/CD Pipeline**: Automated testing and deployment

## Performance Considerations

### Current Approach

- **Single-threaded**: Determinism over performance
- **In-memory**: All data loaded into RAM
- **Batch processing**: One volume at a time

### Optimization Opportunities

- **Multi-threading**: Process multiple volumes in parallel
- **Chunking**: Stream large volumes to reduce memory
- **GPU acceleration**: CUDA/OpenCL for image processing
- **Caching**: Memoize expensive computations

**Note**: All optimizations must maintain determinism and traceability.

## Conclusion

This architecture prioritizes:
- **Correctness** over performance
- **Explicitness** over convenience
- **Safety** over features
- **Testability** over brevity

These priorities align with medical software development best practices.
