"""
Handcrafted feature encoder for segmentation masks.

Wraps the existing SegmentationFeatureEncoder from models/toy_encoder.py
to implement the BaseEncoder interface.
"""

import sys
import os
# Add parent directory (project root) to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import numpy as np
from backend.core.base_encoder import BaseEncoder

# Import existing encoder from parent directory
from models.toy_encoder import SegmentationFeatureEncoder


class HandcraftedEncoder(BaseEncoder):
    """
    Handcrafted feature encoder for segmentation masks.

    Wraps the SegmentationFeatureEncoder to extract 5 spatial/statistical features:
    1. Moran's I (spatial autocorrelation)
    2. Number of connected components
    3. Mean area of components
    4. Compactness of largest component
    5. Perimeter-area ratio

    Attributes:
        base_encoder: Underlying SegmentationFeatureEncoder instance
    """

    def __init__(self, name: str = "HandcraftedEncoder"):
        """
        Initialize handcrafted encoder.

        Args:
            name: Human-readable name for this encoder
        """
        super().__init__(name=name)
        self.base_encoder = SegmentationFeatureEncoder()

    def encode(self, mask: np.ndarray) -> np.ndarray:
        """
        Encode a segmentation mask into a 5D feature vector.

        Args:
            mask: Binary segmentation mask (2D numpy array)

        Returns:
            Feature vector of shape (5,) with dtype float32

        Example:
            >>> encoder = HandcraftedEncoder()
            >>> mask = np.random.randint(0, 2, (64, 64))
            >>> features = encoder.encode(mask)
            >>> print(f"Feature shape: {features.shape}")
            (5,)
        """
        features = self.base_encoder.encode(mask)
        return features.astype(np.float32)

    def dim(self) -> int:
        """
        Return the dimensionality of the feature vector.

        Returns:
            Number of features (5)
        """
        return 5

    def encode_batch(self, masks: list) -> np.ndarray:
        """
        Encode multiple masks efficiently.

        Args:
            masks: List of binary segmentation masks

        Returns:
            Feature matrix of shape (n_masks, 5)

        Example:
            >>> encoder = HandcraftedEncoder()
            >>> masks = [mask1, mask2, mask3]
            >>> features = encoder.encode_batch(masks)
            >>> print(f"Features shape: {features.shape}")
            (3, 5)
        """
        features = []
        for mask in masks:
            features.append(self.encode(mask))
        return np.array(features, dtype=np.float32)
