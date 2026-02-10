"""
Custom Oracle for User-Defined Preferences.

Allows users to define custom utility functions for experiments
with specific preference patterns.
"""

import numpy as np
from typing import Callable, List, Optional
from backend.core.base_oracle import BaseOracle


class CustomOracle(BaseOracle):
    """
    Custom oracle with user-defined utility function.

    Allows researchers to define arbitrary preference functions
    for experiments. The oracle preferences are based on comparing
    the utility scores of two masks.

    Example:
        >>> def my_utility(mask):
        ...     # Prefer masks with more pixels
        ...     return mask.sum()
        >>>
        >>> oracle = CustomOracle(my_utility, name="Pixel Count Oracle")
        >>> pref = oracle.prefer(mask1, mask2)
    """

    def __init__(
        self,
        utility_function: Callable[[np.ndarray], float],
        noise: float = 0.1,
        seed: int = 42,
        name: str = "Custom Oracle"
    ):
        """
        Initialize custom oracle.

        Args:
            utility_function: Function that takes a mask and returns a utility score
                            Higher scores = more preferred
            noise: Logistic noise level (lower = more deterministic)
            seed: Random seed for reproducibility
            name: Human-readable name
        """
        super().__init__(name)
        self.utility_function = utility_function
        self.noise = noise
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def prefer(self, mask_a: np.ndarray, mask_b: np.ndarray) -> bool:
        """
        Return preference based on custom utility function.

        Implements Bradley-Terry model with logistic noise:
        P(A ≻ B) = σ((U(A) - U(B)) / noise)

        Args:
            mask_a: First segmentation mask
            mask_b: Second segmentation mask

        Returns:
            True if mask_a is preferred over mask_b, False otherwise
        """
        ua = self.utility_function(mask_a)
        ub = self.utility_function(mask_b)

        # Logistic probability with clipping to avoid overflow
        diff = (ua - ub) / self.noise
        diff = np.clip(diff, -50, 50)
        prob_a = 1 / (1 + np.exp(-diff))

        # Sample from probability
        return self.rng.random() < prob_a

    def rank_masks(self, masks: List[np.ndarray]) -> np.ndarray:
        """
        Rank masks by their utility scores.

        Args:
            masks: List of segmentation masks

        Returns:
            Array of indices sorted by utility (best first)
        """
        utilities = [self.utility_function(mask) for mask in masks]
        return np.argsort(-np.array(utilities))

    def __repr__(self) -> str:
        return f"CustomOracle(name='{self.name}', noise={self.noise})"


class CompositeOracle(BaseOracle):
    """
    Composite oracle that combines multiple oracles.

    Combines preferences from multiple oracles using weighted voting.
    Useful for creating complex preference patterns from simple components.

    Example:
        >>> oracle1 = InteractiveBiasedOracle(...)
        >>> oracle2 = RandomOracle()
        >>> composite = CompositeOracle([oracle1, oracle2], weights=[0.8, 0.2])
        >>> pref = composite.prefer(mask1, mask2)
    """

    def __init__(
        self,
        oracles: List[BaseOracle],
        weights: Optional[List[float]] = None,
        name: str = "Composite Oracle"
    ):
        """
        Initialize composite oracle.

        Args:
            oracles: List of oracle instances to combine
            weights: Optional weights for each oracle (default: uniform)
            name: Human-readable name

        Raises:
            ValueError: If oracles is empty or weights don't match
        """
        super().__init__(name)

        if not oracles:
            raise ValueError("Must provide at least one oracle")

        if weights is None:
            weights = [1.0 / len(oracles)] * len(oracles)

        if len(weights) != len(oracles):
            raise ValueError(
                f"Number of weights ({len(weights)}) must match "
                f"number of oracles ({len(oracles)})"
            )

        # Normalize weights
        total = sum(weights)
        self.weights = [w / total for w in weights]
        self.oracles = oracles

    def prefer(self, mask_a: np.ndarray, mask_b: np.ndarray) -> bool:
        """
        Return weighted preference from all oracles.

        Args:
            mask_a: First segmentation mask
            mask_b: Second segmentation mask

        Returns:
            True if weighted vote prefers mask_a, False otherwise
        """
        # Get preferences from all oracles
        votes = []
        for oracle, weight in zip(self.oracles, self.weights):
            pref = oracle.prefer(mask_a, mask_b)
            votes.append(weight if pref else -weight)

        # Weighted majority vote
        return sum(votes) > 0

    def rank_masks(self, masks: List[np.ndarray]) -> np.ndarray:
        """
        Rank masks using weighted combination of oracle rankings.

        Args:
            masks: List of segmentation masks

        Returns:
            Array of indices sorted by weighted score (best first)
        """
        n = len(masks)
        scores = np.zeros(n)

        # Get rankings from each oracle
        for oracle, weight in zip(self.oracles, self.weights):
            ranking = oracle.rank_masks(masks)
            # Higher rank = better (rank 0 is best)
            # So we add weight based on reverse rank
            for rank, idx in enumerate(ranking):
                scores[idx] += weight * (n - rank)

        # Sort by score descending
        return np.argsort(-scores)

    def __repr__(self) -> str:
        oracle_names = [o.name for o in self.oracles]
        return f"CompositeOracle(name='{self.name}', oracles={oracle_names}, weights={self.weights})"
