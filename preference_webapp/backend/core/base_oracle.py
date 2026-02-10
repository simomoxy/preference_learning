"""
Base class for oracles (virtual decision makers).

Oracles simulate or provide expert preferences for testing and evaluation.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import numpy as np


class BaseOracle(ABC):
    """
    Abstract base class for oracles (virtual decision makers).

    Oracles provide preferences between pairs of alternatives.
    They can be used for:
    1. Testing and validating algorithms
    2. Simulating different preference patterns
    3. Benchmarking

    Subclasses must implement the prefer() method.
    """

    def __init__(self, name: str = "Oracle"):
        """
        Initialize oracle.

        Args:
            name: Human-readable name for this oracle
        """
        self.name = name

    @abstractmethod
    def prefer(self, mask_a: np.ndarray, mask_b: np.ndarray) -> bool:
        """
        Return preference between two masks.

        Args:
            mask_a: First segmentation mask (binary numpy array)
            mask_b: Second segmentation mask (binary numpy array)

        Returns:
            True if mask_a is preferred over mask_b, False otherwise

        Example:
            >>> oracle = MyOracle()
            >>> preference = oracle.prefer(mask1, mask2)
            >>> if preference:
            ...     print("Prefer mask1")
            ... else:
            ...     print("Prefer mask2")
        """
        raise NotImplementedError("BaseOracle.prefer() must be implemented by subclass")

    def set_bias(self, feature_name: str, value: float) -> None:
        """
        Adjust bias for a specific feature.

        This is an optional method for oracles that support
        runtime adjustment of feature biases.

        Args:
            feature_name: Name of the feature to adjust
            value: New bias value

        Raises:
            NotImplementedError: If oracle doesn't support bias adjustment
            ValueError: If feature_name is not valid for this oracle

        Example:
            >>> oracle.set_bias('compactness', 2.5)  # Prefer more compact masks
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support bias adjustment")

    def get_biases(self) -> Dict[str, float]:
        """
        Get current bias configuration.

        Returns:
            Dictionary mapping feature names to bias values

        Raises:
            NotImplementedError: If oracle doesn't support bias adjustment

        Example:
            >>> biases = oracle.get_biases()
            >>> print(f"Current biases: {biases}")
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support bias adjustment")

    def rank_masks(self, masks: list) -> np.ndarray:
        """
        Get ground truth ranking for a set of masks.

        This is an optional method for computing the true ranking
        according to the oracle's latent utility function.

        Args:
            masks: List of segmentation masks

        Returns:
            Array of indices sorted by preference (best first)

        Example:
            >>> masks = [mask1, mask2, mask3]
            >>> ranking = oracle.rank_masks(masks)
            >>> print(f"Best mask index: {ranking[0]}")
        """
        # Default implementation: use pairwise comparisons
        n = len(masks)
        scores = np.zeros(n)

        for i in range(n):
            for j in range(i + 1, n):
                if self.prefer(masks[i], masks[j]):
                    scores[i] += 1
                else:
                    scores[j] += 1

        # Sort by score (descending)
        ranking = np.argsort(-scores)
        return ranking

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
