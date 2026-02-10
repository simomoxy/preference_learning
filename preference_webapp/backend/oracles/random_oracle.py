"""
Random Oracle for Baseline Comparison.

Provides uniform random preferences as a baseline for comparing
against more sophisticated oracles.
"""

import numpy as np
from typing import List
from backend.core.base_oracle import BaseOracle


class RandomOracle(BaseOracle):
    """
    Random oracle for baseline comparison.

    Returns uniformly random preferences, useful as a baseline
    to compare against biased oracles or human experts.

    This oracle essentially provides random noise, so any learning
    algorithm should perform no better than chance.
    """

    def __init__(self, seed: int = 42, name: str = "Random Oracle"):
        """
        Initialize random oracle.

        Args:
            seed: Random seed for reproducibility
            name: Human-readable name
        """
        super().__init__(name)
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def prefer(self, mask_a: np.ndarray, mask_b: np.ndarray) -> bool:
        """
        Return random preference between two masks.

        Args:
            mask_a: First segmentation mask (ignored)
            mask_b: Second segmentation mask (ignored)

        Returns:
            True or False with equal probability
        """
        return self.rng.random() < 0.5

    def rank_masks(self, masks: List[np.ndarray]) -> np.ndarray:
        """
        Return random ranking.

        Args:
            masks: List of segmentation masks

        Returns:
            Random permutation of indices
        """
        n = len(masks)
        return self.rng.permutation(n)

    def __repr__(self) -> str:
        return f"RandomOracle(name='{self.name}', seed={self.seed})"
