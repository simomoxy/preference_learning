"""
Interactive Biased Oracle for Preference Learning.

Extends BiasedSegmentationOracle with runtime-adjustable biases
for testing and simulation.
"""

import numpy as np
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Use absolute imports from project root
from preference_webapp.backend.core.base_oracle import BaseOracle
from models.toy_encoder import SegmentationFeatureEncoder


class InteractiveBiasedOracle(BaseOracle):
    """
    Interactive oracle with adjustable feature biases.

    Extends the BiasedSegmentationOracle with runtime-adjustable
    bias weights via sliders in the UI. This allows researchers to:

    1. Test algorithms with known ground truth preferences
    2. Simulate different expert preference patterns
    3. Verify that PBO learns the correct preferences

    The oracle uses a Bradley-Terry model with logistic noise:
    P(A ≻ B) = σ((U(A) - U(B)) / noise)

    where U(mask) is a weighted sum of features.
    """

    def __init__(
        self,
        initial_weights: dict = None,
        noise: float = 0.3,
        seed: int = 42,
        name: str = "Interactive Biased Oracle"
    ):
        """
        Initialize oracle with configurable weights.

        Args:
            initial_weights: Dict with keys:
                - compactness: Weight for circular regions (default: 2.0)
                - morans_i: Weight for spatial autocorrelation (default: 1.5)
                - components: Weight for connected components (default: -1.0)
                - area: Weight for mean area (default: 0.5)
                - perimeter_ratio: Weight for perimeter/area ratio (default: -0.5)
            noise: Logistic noise level (lower = more deterministic)
            seed: Random seed for reproducibility
            name: Human-readable name
        """
        super().__init__(name)

        self.encoder = SegmentationFeatureEncoder()

        # Default weights (can be adjusted via UI or set_bias)
        self.weights = initial_weights or {
            "compactness": 2.0,
            "morans_i": 1.5,
            "components": -1.0,
            "area": 0.5,
            "perimeter_ratio": -0.5,
        }

        self.noise = noise
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def latent_utility(self, mask: np.ndarray) -> float:
        """
        Compute latent utility score for a mask.

        This is the ground truth preference function.
        Higher utility = more preferred.

        Args:
            mask: Binary segmentation mask (2D numpy array)

        Returns:
            Utility score (weighted sum of features)
        """
        features = self.encoder.encode(mask)

        # Features: [morans_I, connected_components, area_distribution,
        #            compactness, perimeter_area_ratio]
        utility = (
            self.weights["morans_i"] * features[0] +
            self.weights["components"] * features[1] +
            self.weights["area"] * features[2] +
            self.weights["compactness"] * features[3] +
            self.weights["perimeter_ratio"] * features[4]
        )

        return utility

    def prefer(self, mask_a: np.ndarray, mask_b: np.ndarray) -> bool:
        """
        Return preference between two masks.

        Implements Bradley-Terry model with logistic noise:
        P(A ≻ B) = σ((U(A) - U(B)) / noise)

        Args:
            mask_a: First segmentation mask
            mask_b: Second segmentation mask

        Returns:
            True if mask_a is preferred over mask_b, False otherwise
        """
        ua = self.latent_utility(mask_a)
        ub = self.latent_utility(mask_b)

        # Logistic probability with clipping to avoid overflow
        diff = (ua - ub) / self.noise
        diff = np.clip(diff, -50, 50)
        prob_a = 1 / (1 + np.exp(-diff))

        # Sample from probability
        return self.rng.random() < prob_a

    def set_bias(self, feature_name: str, value: float) -> None:
        """
        Adjust bias for a specific feature.

        This allows runtime adjustment of preferences via UI sliders.

        Args:
            feature_name: One of 'compactness', 'morans_i', 'components',
                         'area', 'perimeter_ratio'
            value: New bias weight

        Raises:
            ValueError: If feature_name is not recognized
        """
        if feature_name not in self.weights:
            valid = list(self.weights.keys())
            raise ValueError(
                f"Unknown feature '{feature_name}'. "
                f"Valid features: {valid}"
            )
        self.weights[feature_name] = value

    def get_biases(self) -> dict:
        """
        Get current bias configuration.

        Returns:
            Dictionary mapping feature names to bias weights
        """
        return self.weights.copy()

    def prefer_probability(
        self, mask_a: np.ndarray, mask_b: np.ndarray
    ) -> float:
        """
        Return probability that mask_a is preferred over mask_b.

        Useful for evaluation and debugging.

        Args:
            mask_a: First mask
            mask_b: Second mask

        Returns:
            Probability P(A ≻ B)
        """
        ua = self.latent_utility(mask_a)
        ub = self.latent_utility(mask_b)

        # Clip to avoid overflow
        diff = (ua - ub) / self.noise
        diff = np.clip(diff, -50, 50)
        return 1 / (1 + np.exp(-diff))

    def rank_masks(self, masks: list) -> np.ndarray:
        """
        Get ground truth ranking for a set of masks.

        Args:
            masks: List of segmentation masks

        Returns:
            Array of indices sorted by utility (best first)
        """
        utilities = [self.latent_utility(mask) for mask in masks]
        return np.argsort(-np.array(utilities))

    def get_features(self, mask: np.ndarray) -> dict:
        """
        Extract and return features for a mask.

        Useful for debugging and understanding preferences.

        Args:
            mask: Segmentation mask

        Returns:
            Dictionary of feature names and values
        """
        features = self.encoder.encode(mask)
        return {
            "morans_i": features[0],
            "components": features[1],
            "area": features[2],
            "compactness": features[3],
            "perimeter_ratio": features[4],
        }

    def __repr__(self) -> str:
        weights_str = ", ".join(f"{k}={v:.1f}" for k, v in self.weights.items())
        return f"InteractiveBiasedOracle(name='{self.name}', noise={self.noise}, weights={{{weights_str}}})"
