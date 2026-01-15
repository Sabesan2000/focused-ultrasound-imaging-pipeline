"""
Strongly-typed configuration for the imaging pipeline.

Uses Pydantic for validation and type safety.
"""
from pathlib import Path
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator


class ProcessingConfig(BaseModel):
    """Configuration for image processing parameters."""
    
    intensity_threshold_percentile: float = Field(
        default=70.0,
        ge=0.0,
        le=100.0,
        description="Percentile threshold for target segmentation"
    )
    
    minimum_component_volume_mm3: float = Field(
        default=100.0,
        ge=0.0,
        description="Minimum volume (mm³) for connected components"
    )
    
    random_seed: int = Field(
        default=42,
        description="Random seed for reproducibility"
    )
    
    @field_validator('intensity_threshold_percentile')
    @classmethod
    def validate_percentile(cls, v: float) -> float:
        """Ensure percentile is in valid range."""
        if not 0.0 <= v <= 100.0:
            raise ValueError(f"Percentile must be between 0 and 100, got {v}")
        return v


class VisualizationConfig(BaseModel):
    """Configuration for visualization outputs."""
    
    generate_slice_views: bool = Field(
        default=True,
        description="Generate 2D slice visualizations"
    )
    
    generate_3d_rendering: bool = Field(
        default=False,
        description="Generate 3D surface rendering (computationally expensive)"
    )
    
    slice_axis: Literal['axial', 'sagittal', 'coronal'] = Field(
        default='axial',
        description="Primary slice orientation for visualization"
    )
    
    dpi: int = Field(
        default=150,
        ge=50,
        le=600,
        description="Output image resolution (DPI)"
    )


class PipelineConfig(BaseModel):
    """Complete configuration for the imaging pipeline."""
    
    input_path: Path = Field(
        description="Path to input NIfTI file"
    )
    
    output_directory: Path = Field(
        default=Path("output"),
        description="Directory for output files"
    )
    
    processing: ProcessingConfig = Field(
        default_factory=ProcessingConfig
    )
    
    visualization: VisualizationConfig = Field(
        default_factory=VisualizationConfig
    )
    
    log_level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR'] = Field(
        default='INFO',
        description="Logging verbosity"
    )
    
    @field_validator('input_path')
    @classmethod
    def validate_input_exists(cls, v: Path) -> Path:
        """Verify input file exists."""
        if not v.exists():
            raise FileNotFoundError(f"Input file not found: {v}")
        return v
    
    def model_post_init(self, __context: object) -> None:
        """Create output directory after validation."""
        self.output_directory.mkdir(parents=True, exist_ok=True)
