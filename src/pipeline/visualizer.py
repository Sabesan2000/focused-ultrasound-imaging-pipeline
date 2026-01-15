"""
Visualization module for medical imaging data and target regions.

Generates publication-quality 2D slices and optional 3D renderings.
"""
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Optional

from .loader import ImageData
from .processor import TargetRegion
from .config import VisualizationConfig


def create_slice_visualization(
    image_data: ImageData,
    target: Optional[TargetRegion],
    output_path: Path,
    config: VisualizationConfig
) -> None:
    """
    Create 2D slice visualizations with target overlay.
    
    Generates orthogonal views (axial, sagittal, coronal) showing
    the original image with target region overlay.
    
    Args:
        image_data: Original image data
        target: Identified target region (optional)
        output_path: Path for output image file
        config: Visualization configuration
    """
    data = image_data.data
    
    # Determine slice indices (center of volume or target centroid)
    if target is not None:
        slice_x = int(target.centroid_voxels[0])
        slice_y = int(target.centroid_voxels[1])
        slice_z = int(target.centroid_voxels[2])
    else:
        slice_x = data.shape[0] // 2
        slice_y = data.shape[1] // 2
        slice_z = data.shape[2] // 2
    
    # Create figure with three subplots
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Compute intensity display range (1st to 99th percentile)
    vmin, vmax = np.percentile(data, [1, 99])
    
    # Axial slice (Z plane)
    axes[0].imshow(data[:, :, slice_z].T, cmap='gray', vmin=vmin, vmax=vmax, origin='lower')
    if target is not None:
        mask_slice = target.mask[:, :, slice_z].T
        axes[0].contour(mask_slice, levels=[0.5], colors='red', linewidths=2)
    axes[0].set_title(f'Axial (Z={slice_z})')
    axes[0].set_xlabel('X (voxels)')
    axes[0].set_ylabel('Y (voxels)')
    axes[0].grid(False)
    
    # Sagittal slice (X plane)
    axes[1].imshow(data[slice_x, :, :].T, cmap='gray', vmin=vmin, vmax=vmax, origin='lower')
    if target is not None:
        mask_slice = target.mask[slice_x, :, :].T
        axes[1].contour(mask_slice, levels=[0.5], colors='red', linewidths=2)
    axes[1].set_title(f'Sagittal (X={slice_x})')
    axes[1].set_xlabel('Y (voxels)')
    axes[1].set_ylabel('Z (voxels)')
    axes[1].grid(False)
    
    # Coronal slice (Y plane)
    axes[2].imshow(data[:, slice_y, :].T, cmap='gray', vmin=vmin, vmax=vmax, origin='lower')
    if target is not None:
        mask_slice = target.mask[:, slice_y, :].T
        axes[2].contour(mask_slice, levels=[0.5], colors='red', linewidths=2)
    axes[2].set_title(f'Coronal (Y={slice_y})')
    axes[2].set_xlabel('X (voxels)')
    axes[2].set_ylabel('Z (voxels)')
    axes[2].grid(False)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=config.dpi, bbox_inches='tight')
    plt.close()


def create_3d_rendering(
    target: TargetRegion,
    output_path: Path
) -> None:
    """
    Create 3D surface rendering of target region using VTK.
    
    Args:
        target: Target region to render
        output_path: Path for output image file
        
    Note:
        This is computationally expensive and optional.
        Requires VTK with rendering backend.
    """
    try:
        import vtk
        from vtk.util import numpy_support
    except ImportError:
        raise ImportError("VTK is required for 3D rendering")
    
    # Convert mask to VTK image data
    mask_vtk = vtk.vtkImageData()
    mask_vtk.SetDimensions(target.mask.shape)
    mask_vtk.SetSpacing(target.voxel_spacing)
    
    # Flatten and convert mask
    flat_mask = target.mask.ravel(order='F')
    vtk_array = numpy_support.numpy_to_vtk(flat_mask, deep=True)
    mask_vtk.GetPointData().SetScalars(vtk_array)
    
    # Create marching cubes surface
    surface = vtk.vtkMarchingCubes()
    surface.SetInputData(mask_vtk)
    surface.SetValue(0, 0.5)
    surface.Update()
    
    # Create mapper and actor
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(surface.GetOutputPort())
    
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(1.0, 0.0, 0.0)
    
    # Create renderer and window
    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.SetBackground(1.0, 1.0, 1.0)
    
    render_window = vtk.vtkRenderWindow()
    render_window.SetOffScreenRendering(1)
    render_window.AddRenderer(renderer)
    render_window.SetSize(800, 800)
    
    # Render and save
    render_window.Render()
    
    window_to_image = vtk.vtkWindowToImageFilter()
    window_to_image.SetInput(render_window)
    window_to_image.Update()
    
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(output_path))
    writer.SetInputConnection(window_to_image.GetOutputPort())
    writer.Write()
