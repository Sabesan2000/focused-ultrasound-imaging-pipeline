"""Unit tests for metrics computation."""
import numpy as np
from src.pipeline.processor import TargetRegion
from src.pipeline.metrics import compute_target_metrics, format_metrics_report


def test_compute_target_metrics():
    """Test metrics computation."""
    mask = np.zeros((20, 20, 20), dtype=np.uint8)
    mask[5:15, 5:15, 5:15] = 1  # 10x10x10 cube
    
    voxel_spacing = (1.0, 1.5, 2.0)
    target = TargetRegion(mask, 1, voxel_spacing)
    
    metrics = compute_target_metrics(target)
    
    # Check all required fields present
    assert 'volume_mm3' in metrics
    assert 'voxel_count' in metrics
    assert 'centroid_voxel_x' in metrics
    assert 'centroid_physical_x_mm' in metrics
    assert 'bbox_x_min' in metrics
    assert 'bbox_width_mm' in metrics
    
    # Check values
    assert metrics['voxel_count'] == 1000
    assert metrics['volume_mm3'] == 1000 * (1.0 * 1.5 * 2.0)
    
    # Bounding box
    assert metrics['bbox_x_min'] == 5
    assert metrics['bbox_x_max'] == 14
    assert metrics['bbox_width_voxels'] == 10


def test_format_metrics_report():
    """Test metrics report formatting."""
    mask = np.zeros((10, 10, 10), dtype=np.uint8)
    mask[2:8, 2:8, 2:8] = 1
    
    target = TargetRegion(mask, 1, (1.0, 1.0, 1.0))
    metrics = compute_target_metrics(target)
    
    report = format_metrics_report(metrics)
    
    assert 'TARGET REGION METRICS REPORT' in report
    assert 'VOLUME:' in report
    assert 'CENTROID' in report
    assert 'BOUNDING BOX' in report
    assert 'mm' in report  # Units should be present
