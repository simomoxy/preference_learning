"""
Surface Feature Encoder with Normalization (FIXED v4 + 7D with variance)

Extracts and normalizes surface statistics for preference learning.

All features are normalized to [0, 1] to ensure each contributes
proportionally to its assigned weight in utility function.

Features (7D for probability maps, 5D for binary masks):
1. morans_i: Spatial autocorrelation on continuous probability map [-1, 1] → normalized to [0, 1]
2. components: Number of connected components (binary mask, log scale)
3. area: Mean area of connected components (binary mask, log scale)
4. variance: Variance of probability values [REPLACED compactness] (continuous map)
5. perimeter_ratio: Perimeter / sqrt(area), normalized via log transform (binary mask)
6. entropy: Shannon entropy of probability distribution (continuous map)
7. mean_confidence: Average probability value (continuous map)

CRITICAL FIXES (v4):
    1. components_log bound increased from log(500) to log(50000) for actual data range
    2. entropy now uses MEAN per pixel instead of SUM (was causing overflow)
    3. entropy bound changed from log(2) to 1.0 (proper normalization)
    4. compactness REMOVED (was always 1.0 on this data) and replaced with variance

Morphological features (components, area, perimeter) use a THRESHOLDED binary mask.

Continuous features (morans_i, variance, entropy, mean_confidence) use the full probability map.
"""

import numpy as np
import skimage.measure as measure
from typing import Dict, Optional, Tuple


class SegmentationFeatureEncoder:
    """
    Extracts and normalizes surface features from probability maps.

    CRITICAL FIX: Threshold probability maps for morphological features to fix
    the measure.label() bug where continuous values were converted to integers.

    All features are normalized to [0, 1] for fair weighting in utility.
    """

    # Threshold for binary mask generation from probability maps
    BINARY_THRESHOLD = 0.5

    # Normalization bounds (FIXED v4 - based on actual data analysis)
    # Format: (min, max) for clipping, then normalize to [0, 1]
    BOUNDS = {
        'morans_i': (-1.0, 1.0),           # Theoretical bounds
        'components_log': (0, np.log(50000)), # FIXED: was 500, actual data has 38000+ components
        'area_log': (0, np.log(10000)),     # Log of mean area
        'variance': (0.0, 1.0),              # Variance normalized by 0.25 (max for [0,1] values)
        'perimeter_log': (0, np.log(5)),    # Log of perimeter/sqrt(area)
        'entropy': (0.0, 1.0),              # FIXED: was log(2), now use mean entropy per pixel
        'mean_confidence': (0.0, 1.0),     # Already in [0, 1] for prob maps
    }

    def __init__(
        self,
        bounds: Optional[Dict] = None,
        binary_threshold: float = 0.5
    ):
        """
        Initialize encoder with optional custom bounds.

        Args:
            bounds: Dict with keys matching BOUNDS above to override defaults
            binary_threshold: Threshold for converting prob maps to binary (default 0.5)
        """
        if bounds:
            self.BOUNDS.update(bounds)
        self.binary_threshold = binary_threshold

    def morans_I(self, mask: np.ndarray) -> float:
        """
        Compute Moran's I (spatial autocorrelation) on CONTINUOUS mask.

        Range: [-1, 1] where 1 = perfect positive autocorrelation,
        -1 = perfect negative autocorrelation, 0 = random.

        Normalized to [0, 1] via: (morans_i + 1) / 2

        Note: Uses continuous probability map to capture spatial confidence patterns.
        """
        mask = mask.astype(float)
        mean = mask.mean()
        var = np.var(mask)
        if var == 0:
            return 0.5  # Midpoint when no variation

        # Compute spatial lag (shift by 1 pixel)
        shifted = np.roll(mask, 1, axis=0)
        numerator = np.sum((mask - mean) * (shifted - mean))
        denominator = np.sum((mask - mean) ** 2)

        morans_i = numerator / denominator if denominator > 0 else 0
        morans_i = np.clip(morans_i, -1, 1)

        # Normalize to [0, 1]
        return (morans_i + 1) / 2

    def connected_components(self, mask: np.ndarray) -> float:
        """
        Count connected components, normalized via log transform.

        Uses THRESHOLDED BINARY MASK to correctly identify regions from probability maps.

        Fewer components = more coherent prediction (better).
        """
        # CRITICAL FIX: Threshold probability map before morphological operations
        binary = (mask >= self.binary_threshold).astype(np.uint8)

        labeled = measure.label(binary)
        n_components = labeled.max()

        if n_components <= 1:
            return 1.0  # Best: single component

        # Log transform, then normalize to [0, 1] (inverted)
        log_comp = np.log(n_components)
        min_log, max_log = self.BOUNDS['components_log']
        norm = np.clip((log_comp - min_log) / (max_log - min_log), 0, 1)

        # Invert: fewer components = higher value
        return 1 - norm

    def area_distribution(self, mask: np.ndarray) -> float:
        """
        Mean area of connected components, normalized via log transform.

        Uses THRESHOLDED BINARY MASK to correctly identify regions from probability maps.

        Larger areas = more substantial predictions (better).
        """
        # CRITICAL FIX: Threshold probability map before morphological operations
        binary = (mask >= self.binary_threshold).astype(np.uint8)

        labeled = measure.label(binary)
        regions = measure.regionprops(labeled)

        if len(regions) == 0:
            return 0.0

        areas = [r.area for r in regions]
        mean_area = np.mean(areas)

        # Log transform, then normalize
        log_area = np.log(mean_area + 1)
        min_log, max_log = self.BOUNDS['area_log']
        norm = np.clip((log_area - min_log) / (max_log - min_log), 0, 1)

        return norm

    def variance_measure(self, mask: np.ndarray) -> float:
        """
        Variance of probability values.

        Uses CONTINUOUS PROBABILITY MAP to measure prediction variation.

        Higher variance = more distinct high/low confidence regions.
        Normalized to [0, 1] by dividing by max theoretical variance (0.25 for uniform in [0,1]).

        This REPLACES compactness which was always saturated at 1.0 for this data.
        """
        var = np.var(mask)
        max_var = 0.25  # Maximum variance for values in [0, 1]
        return np.clip(var / max_var, 0, 1)

    def perimeter_area_ratio(self, mask: np.ndarray) -> float:
        """
        Perimeter-to-area ratio, normalized (lower = more compact).

        Uses THRESHOLDED BINARY MASK to correctly identify regions from probability maps.

        Uses perimeter / sqrt(area) which is scale-invariant.
        """
        # CRITICAL FIX: Threshold probability map before morphological operations
        binary = (mask >= self.binary_threshold).astype(np.uint8)

        labeled = measure.label(binary)
        regions = measure.regionprops(labeled)

        if len(regions) == 0:
            return 0.0

        # Compute mean ratio across components
        ratios = []
        for r in regions:
            if r.area > 0:
                ratio = r.perimeter / np.sqrt(r.area)
                ratios.append(ratio)

        if not ratios:
            return 0.0

        mean_ratio = np.mean(ratios)

        # Log transform, then normalize (inverted: lower = better)
        log_ratio = np.log(mean_ratio + 1)
        min_log, max_log = self.BOUNDS['perimeter_log']
        norm = np.clip((log_ratio - min_log) / (max_log - min_log), 0, 1)

        # Invert: lower ratio = higher value
        return 1 - norm

    def entropy(self, mask: np.ndarray) -> float:
        """
        Shannon entropy of probability distribution.

        Uses CONTINUOUS PROBABILITY MAP to capture uncertainty.

        FIXED: Now uses mean entropy per pixel instead of sum.
        H_mean = -mean(p * log(p)) for all pixels p in [0, 1]

        Higher entropy = more uncertainty/less confident predictions.
        For binary masks, entropy is 0; for uniform probability, entropy is max.

        Normalized to [0, 1] where 0 = certain (binary), 1 = maximum uncertainty.
        """
        # Clip to valid probability range
        mask = np.clip(mask, 1e-10, 1.0 - 1e-10)

        # FIXED: Compute mean entropy per pixel (not sum)
        mean_entropy = -np.mean(mask * np.log(mask + 1e-10))

        # Max entropy for pixel distribution is around 0.7 for typical images
        # (theoretical max for uniform distribution in [0,1] varies, 0.7 is safe upper bound)
        max_entropy = 0.7

        # Normalize to [0, 1]
        norm_entropy = mean_entropy / max_entropy

        # Invert: lower entropy = better (more certain)
        return 1.0 - np.clip(norm_entropy, 0, 1)

    def mean_confidence(self, mask: np.ndarray) -> float:
        """
        Mean confidence (average probability value).

        Uses CONTINUOUS PROBABILITY MAP to capture overall prediction confidence.

        Higher mean confidence = more confident overall prediction.

        Already in [0, 1] for probability maps.
        """
        return float(np.clip(np.mean(mask), 0, 1))

    def encode(self, mask: np.ndarray) -> np.ndarray:
        """
        Extract and normalize all features (7D for probability maps).

        Returns:
            np.array of shape (7,) with all features in [0, 1]

        Note: Continuous features (morans_i, variance, entropy, mean_confidence) use full prob map.
              Morphological features (components, area, perimeter_ratio) use thresholded binary mask.
        """
        return np.array([
            self.morans_I(mask),                # Continuous: spatial pattern
            self.connected_components(mask),     # Binary: region count
            self.area_distribution(mask),        # Binary: region sizes
            self.variance_measure(mask),         # Continuous: prediction variance
            self.perimeter_area_ratio(mask),    # Binary: boundary quality
            self.entropy(mask),                 # Continuous: uncertainty
            self.mean_confidence(mask),           # Continuous: confidence
        ], dtype=np.float32)

    def encode_5d(self, mask: np.ndarray) -> np.ndarray:
        """
        Extract and normalize 5D features (original set for compatibility).

        Returns:
            np.array of shape (5,) with all features in [0, 1]
        """
        return np.array([
            self.morans_I(mask),                # Continuous
            self.connected_components(mask),     # Binary (fixed)
            self.area_distribution(mask),        # Binary (fixed)
            self.perimeter_area_ratio(mask),    # Binary (fixed)
            self.entropy(mask),                 # Continuous (replaces compactness for 5D)
        ], dtype=np.float32)

    def encode_raw(self, mask: np.ndarray) -> np.ndarray:
        """
        Extract features WITHOUT normalization (for debugging).

        Returns:
            np.array of shape (7,) with raw feature values
        """
        # For raw features, use thresholded mask for morphology
        binary = (mask >= self.binary_threshold).astype(np.uint8)
        labeled_b = measure.label(binary)
        regions_b = measure.regionprops(labeled_b)

        # Raw morans_i (continuous)
        mask_f = mask.astype(float)
        mean = mask_f.mean()
        var = np.var(mask_f)
        if var == 0:
            morans_i = 0
        else:
            shifted = np.roll(mask_f, 1, axis=0)
            morans_i = np.sum((mask_f - mean) * (shifted - mean)) / np.sum((mask_f - mean) ** 2)

        # Raw components (binary)
        n_components = labeled_b.max()

        # Raw area (binary)
        areas = [r.area for r in regions_b] if regions_b else [0]
        mean_area = np.mean(areas)

        # Raw compactness (binary)
        if regions_b:
            comp = np.mean([(4 * np.pi * r.area) / (r.perimeter ** 2 + 1e-6)
                           for r in regions_b])
        else:
            comp = 0

        # Raw perimeter ratio (binary)
        if regions_b:
            ratio = np.mean([r.perimeter / np.sqrt(r.area + 1e-6) for r in regions_b])
        else:
            ratio = 0

        # Raw entropy (continuous)
        mask_c = np.clip(mask, 1e-10, 1.0 - 1e-10)
        entropy = -np.sum(mask_c * np.log(mask_c + 1e-10))

        # Raw mean confidence (continuous)
        mean_conf = np.mean(mask)

        return np.array([
            morans_i,
            n_components,
            mean_area,
            comp,
            ratio,
            entropy,
            mean_conf
        ], dtype=np.float32)

    def get_feature_names(self) -> list:
        """Return list of feature names for interpretability."""
        return ['morans_i', 'components', 'area', 'variance', 'perimeter_ratio',
                'entropy', 'mean_confidence']

    def get_feature_names_5d(self) -> list:
        """Return 5D feature names for compatibility."""
        return ['morans_i', 'components', 'area', 'perimeter_ratio', 'entropy']

    def dim(self) -> int:
        """Return feature dimensionality (7D)."""
        return 7

    def dim_5d(self) -> int:
        """Return 5D feature dimensionality."""
        return 5
