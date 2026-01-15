"""Unit tests for image processing module."""
import pytest
import numpy as np
from scipy import ndimage

from src.pipeline.processor import (
    apply_intensity_threshold,
    extract_largest_connected_component,
    TargetRegion
)


def test_apply_intensity_threshold():
    """Test intensity thresholding."""
    data = np.array([[[1, 2, 3], [4, 5, 6]], [[7, 8, 9], [10, 11, 12]]])
    
    # 50th percentile should be around 6.5
    mask = apply_intensity_threshold(data, 50.0)
    
    assert mask.shape == data.shape
    assert np.sum(mask) == 6  # Half the voxels


def test_extract_largest_component():
    """Test connected component extraction."""
    # Create mask with two components
    mask = np.zeros((20, 20, 20), dtype=np.uint8)
    mask[5:10, 5:10, 5:10] = 1  # Small component
    mask[12:18, 12:18, 12:18] = 1  # Larger component
    
    voxel_spacing = (1.0, 1.0, 1.0)
    
    largest = extract_largest_connected_component(mask, 100.0, voxel_spacing)
    
    assert largest is not None
    # Should select the larger component
    assert np.sum(largest) == 216  # 6x6x6


def test_extract_component_rejects_small_volumes():
    """Test that small components are rejected."""
    mask = np.zeros((20, 20, 20), dtype=np.uint8)
    mask[5:7, 5:7, 5:7] = 1  # Very small component (2x2x2 = 8 voxels)
    
    voxel_spacing = (1.0, 1.0, 1.0)
    
    # Minimum volume larger than component
    largest = extract_largest_connected_component(mask, 100.0, voxel_spacing)
    
    assert largest is None


def test_target_region_properties():
    """Test TargetRegion computes properties correctly."""
    mask = np.zeros((20, 20, 20), dtype=np.uint8)
    mask[5:15, 5:15, 5:15] = 1  # 10x10x10 cube
    
    voxel_spacing = (1.0, 1.0, 1.0)
    
    target = TargetRegion(mask, 1, voxel_spacing)
    
    assert target.voxel_count == 1000
    assert target.volume_mm3 == 1000.0
    
    # Centroid should be at center of cube
    assert np.allclose(target.centroid_voxels, (9.5, 9.5, 9.5), atol=0.1)
    
    # Bounding box
    assert target.bounding_box == ((5, 14), (5, 14), (5, 14))


def test_target_region_with_anisotropic_voxels():
    """Test TargetRegion with non-cubic voxels."""
    mask = np.zeros((10, 10, 10), dtype=np.uint8)
    mask[2:8, 2:8, 2:8] = 1  # 6x6x6 cube in voxels
    
    voxel_spacing = (1.0, 2.0, 3.0)  # Anisotropic
    
    target = TargetRegion(mask, 1, voxel_spacing)
    
    # Volume should account for voxel spacing
    expected_volume = 216 * (1.0 * 2.0 * 3.0)  # 216 voxels * voxel volume
    assert np.isclose(target.volume_mm3, expected_volume)
    
    # Physical centroid should scale by voxel spacing
    voxel_centroid = target.centroid_voxels
    expected_physical = (
        voxel_centroid[0] * 1.0,
        voxel_centroid[1] * 2.0,
        voxel_centroid[2] * 3.0
    )
    assert np.allclose(target.centroid_physical, expected_physical)
