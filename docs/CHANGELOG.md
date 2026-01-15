# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-01-14

### Added
- GitHub Actions CI/CD pipeline with multi-version Python testing
- Comprehensive negative test suite for all validation checks
- Affine matrix validation (shape, finiteness, singularity)
- Physical constraints for voxel spacing validation (0.01-50mm range)
- Integration tests for full pipeline execution
- Explicit exception types (DimensionalityError, DataQualityError, MetadataError)
- Flake8 configuration for code linting
- Coverage enforcement (≥85%) in CI pipeline
- Development guidelines documentation
- Example YAML configuration file
- This CHANGELOG

### Changed
- Enhanced validator with stricter medical-grade validation rules
- Improved error messages with quantitative context
- Extended test coverage from ~70% to >85%
- Updated README with CI badges and expanded documentation

### Fixed
- Voxel spacing validation now checks for zero and negative values
- Affine matrix validation catches singular matrices
- Validation now properly classifies error types for specific exceptions

## [0.1.0] - 2024-01-10

### Added
- Initial pipeline implementation
- NIfTI image loading with metadata extraction
- Basic validation (dimensionality, NaN/Inf checks)
- Deterministic processing with seed management
- Quantitative metrics computation
- Structured JSON logging
- Visualization with slice views
- Unit tests for core modules
- Documentation (README, architecture, safety, validation)

[0.2.0]: https://github.com/YOUR_ORG/focused-ultrasound-imaging-pipeline/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/YOUR_ORG/focused-ultrasound-imaging-pipeline/releases/tag/v0.1.0
