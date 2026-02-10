"""
Base class for feature encoders.

Encoders transform segmentation masks into feature vectors
for use in preference learning models.
"""

from abc import ABC, abstractmethod
from typing import Optional
import numpy as np


class BaseEncoder(ABC):
    """
    Abstract base class for feature encoders.

    Encoders convert binary segmentation masks into feature vectors
    that capture relevant properties for preference learning.

    Subclasses must implement the encode() method and dim() method.
    """

    def __init__(self, name: str = "Encoder"):
        """
        Initialize encoder.

        Args:
            name: Human-readable name for this encoder
        """
        self.name = name

    @abstractmethod
    def encode(self, mask: np.ndarray) -> np.ndarray:
        """
        Encode a segmentation mask into a feature vector.

        Args:
            mask: Binary segmentation mask (2D numpy array)

        Returns:
            Feature vector (1D numpy array)

        Example:
            >>> encoder = MyEncoder()
            >>> mask = np.random.randint(0, 2, (64, 64))
            >>> features = encoder.encode(mask)
            >>> print(f"Feature shape: {features.shape}")
        """
        raise NotImplementedError("BaseEncoder.encode() must be implemented by subclass")

    @abstractmethod
    def dim(self) -> int:
        """
        Return the dimensionality of the feature vector.

        Returns:
            Number of features in the encoded vector

        Example:
            >>> encoder = MyEncoder()
            >>> d = encoder.dim()
            >>> print(f"Feature dimension: {d}")
        """
        raise NotImplementedError("BaseEncoder.dim() must be implemented by subclass")

    def encode_batch(self, masks: list) -> np.ndarray:
        """
        Encode multiple masks efficiently.

        Args:
            masks: List of binary segmentation masks

        Returns:
            Feature matrix of shape (n_masks, n_features)

        Example:
            >>> encoder = MyEncoder()
            >>> masks = [mask1, mask2, mask3]
            >>> features = encoder.encode_batch(masks)
            >>> print(f"Features shape: {features.shape}")
        """
        features = []
        for mask in masks:
            features.append(self.encode(mask))
        return np.array(features)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', dim={self.dim()})"

    def __call__(self, mask: np.ndarray) -> np.ndarray:
        """
        Encode a mask (convenience method).

        Args:
            mask: Binary segmentation mask

        Returns:
            Feature vector
        """
        return self.encode(mask)
