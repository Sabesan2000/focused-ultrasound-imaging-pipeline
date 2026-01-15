"""
Image processing module for focused ultrasound target identification.

Implements deterministic algorithms for target segmentation and analysis.
"""
import numpy as np
from scipy import ndimage
from typing import Tuple, Optional

from .loader import ImageData
from .errors import ProcessingError
from .config import ProcessingConfig


class TargetRegion:
    """Container for identified target region."""
    
    def __init__(
        self,
        mask: np.ndarray,
        label: int,
        voxel_spacing: Tuple[float, float, float]
    ):
        """
        Initialize target region.
        
        Args:
            mask: Binary mask of target region
            label: Component label ID
            voxel_spacing: Voxel dimensions in mm
        """
        self.mask = mask
        self.label = label
        self.voxel_spacing = voxel_spacing
        
        # Compute properties
        self.voxel_count = int(np.sum(mask))
        self.volume_mm3 = self._compute_volume()
        self.centroid_voxels = self._compute_centroid()
        self.centroid_physical = self._compute_physical_centroid()
        self.bounding_box = self._compute_bounding_box()
    
    def _compute_volume(self) -> float:
        """Compute volume in mm³."""
        voxel_volume_mm3 = (
            self.voxel_spacing[0] *
            self.voxel_spacing[1] *
            self.voxel_spacing[2]
        )
        return float(self.voxel_count * voxel_volume_mm3)
    
    def _compute_centroid(self) -> Tuple[float, float, float]:
        """Compute centroid in voxel coordinates."""
        coords = np.argwhere(self.mask)
        centroid = np.mean(coords, axis=0)
        return (float(centroid[0]), float(centroid[1]), float(centroid[2]))
    
    def _compute_physical_centroid(self) -> Tuple[float, float, float]:
        """Compute centroid in physical coordinates (mm)."""
        voxel_centroid = self.centroid_voxels
        physical = (
            voxel_centroid[0] * self.voxel_spacing[0],
            voxel_centroid[1] * self.voxel_spacing[1],
            voxel_centroid[2] * self.voxel_spacing[2]
        )
        return physical
    
    def _compute_bounding_box(self) -> Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]:
        """Compute bounding box as ((x_min, x_max), (y_min, y_max), (z_min, z_max))."""
        coords = np.argwhere(self.mask)
        mins = np.min(coords, axis=0)
        maxs = np.max(coords, axis=0)
        return (
            (int(mins[0]), int(maxs[0])),
            (int(mins[1]), int(maxs[1])),
            (int(mins[2]), int(maxs[2]))
        )


def apply_intensity_threshold(
    data: np.ndarray,
    percentile: float
) -> np.ndarray:
    """
    Apply intensity-based thresholding.
    
    Args:
        data: 3D intensity array
        percentile: Threshold percentile (0-100)
        
    Returns:
        Binary mask of voxels above threshold
    """
    threshold_value = np.percentile(data, percentile)
    mask = data >= threshold_value
    return mask.astype(np.uint8)


def extract_largest_connected_component(
    binary_mask: np.ndarray,
    min_volume_mm3: float,
    voxel_spacing: Tuple[float, float, float]
) -> Optional[np.ndarray]:
    """
    Extract largest connected component from binary mask.
    
    Args:
        binary_mask: Binary segmentation mask
        min_volume_mm3: Minimum component volume in mm³
        voxel_spacing: Voxel dimensions in mm
        
    Returns:
        Binary mask of largest component, or None if no valid components
    """
    # Label connected components
    labeled_array, num_features = ndimage.label(binary_mask)
    
    if num_features == 0:
        return None
    
    # Compute volume of each component
    voxel_volume_mm3 = (
        voxel_spacing[0] * voxel_spacing[1] * voxel_spacing[2]
    )
    
    component_volumes = []
    for label in range(1, num_features + 1):
        component_size = np.sum(labeled_array == label)
        volume_mm3 = component_size * voxel_volume_mm3
        component_volumes.append((label, volume_mm3))
    
    # Sort by volume (descending)
    component_volumes.sort(key=lambda x: x[1], reverse=True)
    
    # Find largest component above minimum volume
    for label, volume in component_volumes:
        if volume >= min_volume_mm3:
            largest_component = (labeled_array == label).astype(np.uint8)
            return largest_component
    
    return None


def process_image_for_target_identification(
    image_data: ImageData,
    config: ProcessingConfig
) -> TargetRegion:
    """
    Process image to identify focused ultrasound target region.
    
    This implements a deterministic pipeline:
    1. Intensity-based thresholding
    2. Connected component analysis
    3. Selection of largest valid component
    
    Args:
        image_data: Loaded and validated image data
        config: Processing configuration
        
    Returns:
        TargetRegion containing identified target
        
    Raises:
        ProcessingError: If target identification fails
    """
    # Set random seed for reproducibility (though this algorithm is deterministic)
    np.random.seed(config.random_seed)
    
    data = image_data.data
    voxel_spacing = image_data.voxel_spacing
    
    # Step 1: Apply intensity threshold
    binary_mask = apply_intensity_threshold(
        data,
        config.intensity_threshold_percentile
    )
    
    voxels_above_threshold = int(np.sum(binary_mask))
    if voxels_above_threshold == 0:
        raise ProcessingError(
            f"No voxels above {config.intensity_threshold_percentile}th percentile"
        )
    
    # Step 2: Extract largest connected component
    largest_component = extract_largest_connected_component(
        binary_mask,
        config.minimum_component_volume_mm3,
        voxel_spacing
    )
    
    if largest_component is None:
        raise ProcessingError(
            f"No connected components above minimum volume "
            f"({config.minimum_component_volume_mm3} mm³)"
        )
    
    # Step 3: Create target region object
    target = TargetRegion(
        mask=largest_component,
        label=1,
        voxel_spacing=voxel_spacing
    )
    
    return target
