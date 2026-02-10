"""
Base class for acquisition functions.

Acquisition functions select which pairs of candidates to query
in the active learning loop.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Any
import numpy as np


class AcquisitionFunction(ABC):
    """
    Abstract base class for acquisition functions.

    Acquisition functions determine which pairs of candidates are most
    informative to query the oracle about during active learning.

    Subclasses must implement the acquire() method.
    """

    def __init__(self, name: str):
        """
        Initialize acquisition function.

        Args:
            name: Human-readable name for this acquisition function
        """
        self.name = name
        self.history = []  # Track acquisition history for analysis

    @abstractmethod
    def acquire(
        self,
        model,
        likelihood,
        candidates: List[int],
        features: np.ndarray,
        n_pairs: int = 1,
        **kwargs
    ) -> List[Tuple[int, int]]:
        """
        Select pairs to query.

        Args:
            model: Trained preference model (GP or other)
            likelihood: Likelihood function for the model
            candidates: List of candidate indices to choose from
            features: Feature matrix of shape (n_candidates, n_features)
            n_pairs: Number of pairs to select
            **kwargs: Additional arguments specific to acquisition function

        Returns:
            List of (i, j) tuples representing selected pairs
            where i and j are indices into the candidates/features arrays

        Example:
            >>> acq = MyAcquisition()
            >>> pairs = acq.acquire(model, likelihood, [0,1,2,3], features, n_pairs=2)
            >>> print(pairs)
            [(0, 2), (1, 3)]
        """
        raise NotImplementedError("AcquisitionFunction.acquire() must be implemented by subclass")

    def reset_history(self):
        """Clear acquisition history."""
        self.history = []

    def get_history(self) -> List[dict]:
        """
        Get acquisition history.

        Returns:
            List of dictionaries with acquisition metadata
        """
        return self.history

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
