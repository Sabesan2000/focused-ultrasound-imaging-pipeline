"""Tests for reproducibility utilities."""
import pytest
import numpy as np
from src.utils.reproducibility import set_seeds, ensure_deterministic_execution


def test_set_seeds_produces_reproducible_results() -> None:
    """Test that setting seeds produces reproducible random numbers."""
    set_seeds(42)
    result1 = np.random.randn(100)
    
    set_seeds(42)
    result2 = np.random.randn(100)
    
    np.testing.assert_array_equal(result1, result2)


def test_different_seeds_produce_different_results() -> None:
    """Test that different seeds produce different random numbers."""
    set_seeds(42)
    result1 = np.random.randn(100)
    
    set_seeds(123)
    result2 = np.random.randn(100)
    
    assert not np.array_equal(result1, result2)


def test_ensure_deterministic_execution_runs() -> None:
    """Test that ensure_deterministic_execution completes."""
    # Should not raise
    ensure_deterministic_execution()
