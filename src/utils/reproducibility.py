"""
Utilities for ensuring reproducibility in the pipeline.

Provides tools for setting seeds, tracking versions, and ensuring determinism.
"""
import random
import numpy as np
from typing import Dict, Any
import sys


def set_seeds(seed: int) -> None:
    """
    Set random seeds for all libraries to ensure reproducibility.
    
    Args:
        seed: Random seed value
    """
    random.seed(seed)
    np.random.seed(seed)
    # Note: We don't use torch/tensorflow in this pipeline, but if we did:
    # torch.manual_seed(seed)
    # tf.random.set_seed(seed)


def get_environment_info() -> Dict[str, Any]:
    """
    Collect environment information for reproducibility tracking.
    
    Returns:
        Dictionary of environment information
    """
    import platform
    import numpy
    import scipy
    import nibabel
    
    return {
        'python_version': sys.version,
        'platform': platform.platform(),
        'numpy_version': numpy.__version__,
        'scipy_version': scipy.__version__,
        'nibabel_version': nibabel.__version__,
    }


def ensure_deterministic_execution() -> None:
    """
    Configure libraries for deterministic execution where possible.
    
    Note: Some operations (especially multi-threaded) may still have
    non-deterministic behavior. This function makes a best effort.
    """
    # NumPy uses deterministic algorithms by default
    # SciPy operations are deterministic with fixed seeds
    
    # Disable threading in NumPy for full determinism (at cost of performance)
    import os
    os.environ['OMP_NUM_THREADS'] = '1'
    os.environ['MKL_NUM_THREADS'] = '1'
    os.environ['OPENBLAS_NUM_THREADS'] = '1'
