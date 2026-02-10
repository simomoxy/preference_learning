"""
Base class for learning strategies.

Learning strategies define how to train models and compute rankings
from preference data.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict, Any
import numpy as np


class LearningStrategy(ABC):
    """
    Abstract base class for learning strategies.

    A learning strategy defines the complete workflow for:
    1. Training a model on preference data
    2. Computing rankings from trained models
    3. Selecting informative pairs for querying
    4. Saving/loading model checkpoints

    Subclasses must implement all abstract methods.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize learning strategy.

        Args:
            config: Configuration dictionary with strategy-specific parameters
        """
        self.config = config
        self.model = None
        self.likelihood = None

    @abstractmethod
    def train(
        self,
        preferences: List[Tuple[Tuple[int, int], int]],
        features: np.ndarray,
        scaler: Optional[Any] = None
    ) -> Tuple[Any, Any]:
        """
        Train model on preference data.

        Args:
            preferences: List of ((i, j), preference) tuples
                       where preference is 0 or 1
            features: Feature matrix of shape (n_masks, n_features)
            scaler: Optional scaler object (e.g., StandardScaler)

        Returns:
            Tuple of (model, likelihood)

        Example:
            >>> strategy = GPStrategy(config)
            >>> model, likelihood = strategy.train(preferences, features, scaler)
        """
        raise NotImplementedError("LearningStrategy.train() must be implemented by subclass")

    @abstractmethod
    def get_ranking(
        self,
        features: np.ndarray,
        scaler: Optional[Any] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute ranking from trained model.

        Args:
            features: Feature matrix of shape (n_masks, n_features)
            scaler: Optional scaler object (e.g., StandardScaler)

        Returns:
            Tuple of (ranking, scores) where:
            - ranking: Array of indices sorted by preference (best first)
            - scores: Array of scores for each mask

        Example:
            >>> ranking, scores = strategy.get_ranking(features)
            >>> print(f"Best mask: {ranking[0]}")
            >>> print(f"Score: {scores[ranking[0]]}")
        """
        raise NotImplementedError("LearningStrategy.get_ranking() must be implemented by subclass")

    @abstractmethod
    def select_pairs(
        self,
        features: np.ndarray,
        acquisition_fn: Any,
        n_pairs: int = 10,
        **kwargs
    ) -> List[Tuple[int, int]]:
        """
        Select pairs for next query using acquisition function.

        Args:
            features: Feature matrix of shape (n_masks, n_features)
            acquisition_fn: Acquisition function to use
            n_pairs: Number of pairs to select
            **kwargs: Additional arguments for acquisition function

        Returns:
            List of (i, j) tuples representing selected pairs

        Example:
            >>> pairs = strategy.select_pairs(features, acq_fn, n_pairs=10)
            >>> print(f"Selected {len(pairs)} pairs")
        """
        raise NotImplementedError("LearningStrategy.select_pairs() must be implemented by subclass")

    @abstractmethod
    def save_checkpoint(self, path: str) -> None:
        """
        Save model checkpoint.

        Args:
            path: Path to save checkpoint

        Example:
            >>> strategy.save_checkpoint('checkpoints/model.pt')
        """
        raise NotImplementedError("LearningStrategy.save_checkpoint() must be implemented by subclass")

    @abstractmethod
    def load_checkpoint(self, path: str) -> None:
        """
        Load model checkpoint.

        Args:
            path: Path to load checkpoint from

        Example:
            >>> strategy.load_checkpoint('checkpoints/model.pt')
        """
        raise NotImplementedError("LearningStrategy.load_checkpoint() must be implemented by subclass")

    def is_trained(self) -> bool:
        """
        Check if model has been trained.

        Returns:
            True if model is trained, False otherwise
        """
        return self.model is not None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(config={self.config})"
