"""
Quantitative metrics computation for target regions.

All metrics include explicit units and validation.
"""
from typing import Dict, Any
from .processor import TargetRegion


def compute_target_metrics(target: TargetRegion) -> Dict[str, Any]:
    """
    Compute comprehensive metrics for identified target region.
    
    All spatial measurements are in millimeters (mm) or cubic millimeters (mm³).
    All coordinates are reported in both voxel and physical space.
    
    Args:
        target: Identified target region
        
    Returns:
        Dictionary of metrics with explicit units
    """
    metrics = {
        # Volume measurements
        'volume_mm3': target.volume_mm3,
        'voxel_count': target.voxel_count,
        
        # Centroid in voxel space
        'centroid_voxel_x': target.centroid_voxels[0],
        'centroid_voxel_y': target.centroid_voxels[1],
        'centroid_voxel_z': target.centroid_voxels[2],
        
        # Centroid in physical space (mm)
        'centroid_physical_x_mm': target.centroid_physical[0],
        'centroid_physical_y_mm': target.centroid_physical[1],
        'centroid_physical_z_mm': target.centroid_physical[2],
        
        # Bounding box in voxel space
        'bbox_x_min': target.bounding_box[0][0],
        'bbox_x_max': target.bounding_box[0][1],
        'bbox_y_min': target.bounding_box[1][0],
        'bbox_y_max': target.bounding_box[1][1],
        'bbox_z_min': target.bounding_box[2][0],
        'bbox_z_max': target.bounding_box[2][1],
        
        # Bounding box dimensions in voxels
        'bbox_width_voxels': target.bounding_box[0][1] - target.bounding_box[0][0] + 1,
        'bbox_height_voxels': target.bounding_box[1][1] - target.bounding_box[1][0] + 1,
        'bbox_depth_voxels': target.bounding_box[2][1] - target.bounding_box[2][0] + 1,
        
        # Bounding box dimensions in mm
        'bbox_width_mm': (
            (target.bounding_box[0][1] - target.bounding_box[0][0] + 1) * 
            target.voxel_spacing[0]
        ),
        'bbox_height_mm': (
            (target.bounding_box[1][1] - target.bounding_box[1][0] + 1) * 
            target.voxel_spacing[1]
        ),
        'bbox_depth_mm': (
            (target.bounding_box[2][1] - target.bounding_box[2][0] + 1) * 
            target.voxel_spacing[2]
        ),
        
        # Metadata
        'voxel_spacing_x_mm': target.voxel_spacing[0],
        'voxel_spacing_y_mm': target.voxel_spacing[1],
        'voxel_spacing_z_mm': target.voxel_spacing[2],
    }
    
    return metrics


def format_metrics_report(metrics: Dict[str, Any]) -> str:
    """
    Format metrics as human-readable report.
    
    Args:
        metrics: Metrics dictionary from compute_target_metrics
        
    Returns:
        Formatted report string
    """
    lines = [
        "=" * 60,
        "TARGET REGION METRICS REPORT",
        "=" * 60,
        "",
        "VOLUME:",
        f"  Total volume: {metrics['volume_mm3']:.2f} mm³",
        f"  Voxel count: {metrics['voxel_count']}",
        "",
        "CENTROID (Voxel Coordinates):",
        f"  X: {metrics['centroid_voxel_x']:.2f}",
        f"  Y: {metrics['centroid_voxel_y']:.2f}",
        f"  Z: {metrics['centroid_voxel_z']:.2f}",
        "",
        "CENTROID (Physical Coordinates):",
        f"  X: {metrics['centroid_physical_x_mm']:.2f} mm",
        f"  Y: {metrics['centroid_physical_y_mm']:.2f} mm",
        f"  Z: {metrics['centroid_physical_z_mm']:.2f} mm",
        "",
        "BOUNDING BOX (Voxel Space):",
        f"  X: [{metrics['bbox_x_min']}, {metrics['bbox_x_max']}]",
        f"  Y: [{metrics['bbox_y_min']}, {metrics['bbox_y_max']}]",
        f"  Z: [{metrics['bbox_z_min']}, {metrics['bbox_z_max']}]",
        "",
        "BOUNDING BOX DIMENSIONS:",
        f"  Width:  {metrics['bbox_width_voxels']} voxels ({metrics['bbox_width_mm']:.2f} mm)",
        f"  Height: {metrics['bbox_height_voxels']} voxels ({metrics['bbox_height_mm']:.2f} mm)",
        f"  Depth:  {metrics['bbox_depth_voxels']} voxels ({metrics['bbox_depth_mm']:.2f} mm)",
        "",
        "VOXEL SPACING:",
        f"  X: {metrics['voxel_spacing_x_mm']:.3f} mm",
        f"  Y: {metrics['voxel_spacing_y_mm']:.3f} mm",
        f"  Z: {metrics['voxel_spacing_z_mm']:.3f} mm",
        "=" * 60,
    ]
    
    return "\n".join(lines)
