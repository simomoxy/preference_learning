"""
Acquisition functions for active learning.

Implements various strategies for selecting informative pairs to query
during the preference learning process.
"""

import sys
import os
# Add parent directory (project root) to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import numpy as np
import torch
from typing import List, Tuple, Any
from backend.core.base_acquisition import AcquisitionFunction


class RandomAcquisition(AcquisitionFunction):
    """
    Random acquisition function.

    Selects pairs uniformly at random from all candidates.
    Useful as a baseline and for exploration.
    """

    def __init__(self, name: str = "Random"):
        """
        Initialize random acquisition.

        Args:
            name: Human-readable name
        """
        super().__init__(name=name)

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
        Select random pairs.

        Args:
            model: Trained preference model (unused for random)
            likelihood: Likelihood function (unused for random)
            candidates: List of candidate indices
            features: Feature matrix (unused for random)
            n_pairs: Number of pairs to select
            **kwargs: Additional arguments (unused)

        Returns:
            List of (i, j) tuples representing selected pairs
        """
        rng = kwargs.get('rng', np.random.default_rng())
        pairs = []

        for _ in range(n_pairs):
            i, j = rng.choice(candidates, size=2, replace=False)
            pairs.append((int(i), int(j)))

        return pairs


class ThompsonSamplingAcquisition(AcquisitionFunction):
    """
    Thompson sampling acquisition function.

    Samples from the GP posterior and selects pairs that maximize
    information gain. Good for balancing exploration and exploitation.
    """

    def __init__(self, name: str = "ThompsonSampling"):
        """
        Initialize Thompson sampling acquisition.

        Args:
            name: Human-readable name
        """
        super().__init__(name=name)

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
        Select pairs using Thompson sampling.

        Args:
            model: Trained GP model
            likelihood: Bernoulli likelihood
            candidates: List of candidate indices
            features: Feature matrix (n_candidates, n_features)
            n_pairs: Number of pairs to select
            **kwargs: Additional arguments (e.g., rng)

        Returns:
            List of (i, j) tuples representing selected pairs
        """
        rng = kwargs.get('rng', np.random.default_rng())
        model.eval()
        likelihood.eval()

        # Convert features to tensor
        Z = torch.tensor(features[candidates], dtype=torch.float32)

        # Sample utility values from posterior
        with torch.no_grad():
            f_dist = model(Z)
            f_samples = f_dist.sample()

        # Sort candidates by sampled utility
        # Ensure f_samples is 1D numpy array with correct length
        f_values = f_samples.detach().cpu().numpy()
        f_values = f_values.flatten()  # Ensure 1D

        # Verify shapes match
        if len(f_values) != len(candidates):
            # If shapes don't match, use first len(candidates) values or pad
            if len(f_values) > len(candidates):
                f_values = f_values[:len(candidates)]
            else:
                # Pad with zeros if fewer values
                f_values_padded = np.zeros(len(candidates))
                f_values_padded[:len(f_values)] = f_values
                f_values = f_values_padded

        # Sort candidates by sampled utility (descending)
        ranking = np.argsort(-f_values)
        sorted_indices = [candidates[i] for i in ranking]

        # Select pairs from top candidates
        pairs = []
        top_k = min(n_pairs * 2, len(sorted_indices))
        for _ in range(n_pairs):
            i, j = rng.choice(sorted_indices[:top_k], size=2, replace=False)
            pairs.append((int(i), int(j)))

        return pairs


class UCBAcquisition(AcquisitionFunction):
    """
    Upper Confidence Bound (UCB) acquisition function.

    Selects pairs that maximize uncertainty in the GP posterior.
    Focuses on exploration of uncertain regions.
    """

    def __init__(self, name: str = "UCB"):
        """
        Initialize UCB acquisition.

        Args:
            name: Human-readable name
        """
        super().__init__(name=name)

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
        Select pairs using UCB.

        Args:
            model: Trained GP model
            likelihood: Bernoulli likelihood
            candidates: List of candidate indices
            features: Feature matrix (n_candidates, n_features)
            n_pairs: Number of pairs to select
            **kwargs: Additional arguments (e.g., beta, rng)

        Returns:
            List of (i, j) tuples representing selected pairs
        """
        rng = kwargs.get('rng', np.random.default_rng())
        beta = kwargs.get('beta', 2.0)  # Exploration parameter
        model.eval()
        likelihood.eval()

        # Convert features to tensor
        Z = torch.tensor(features[candidates], dtype=torch.float32)

        # Compute posterior mean and variance
        with torch.no_grad():
            f_dist = model(Z)
            mean = f_dist.mean
            std = f_dist.stddev

        # Compute UCB scores
        ucb_scores = mean.numpy() + beta * std.numpy()

        # Select candidates with highest uncertainty
        sorted_indices = candidates[np.argsort(-ucb_scores)]

        # Select pairs from top uncertain candidates
        pairs = []
        top_k = min(n_pairs * 2, len(sorted_indices))
        for _ in range(n_pairs):
            i, j = rng.choice(sorted_indices[:top_k], size=2, replace=False)
            pairs.append((int(i), int(j)))

        return pairs


class EIAcquisition(AcquisitionFunction):
    """
    Expected Improvement (EI) acquisition function.

    Selects pairs that maximize expected improvement in the Copeland score.
    Balances exploration and exploitation.
    """

    def __init__(self, name: str = "EI"):
        """
        Initialize EI acquisition.

        Args:
            name: Human-readable name
        """
        super().__init__(name=name)

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
        Select pairs using Expected Improvement.

        Args:
            model: Trained GP model
            likelihood: Bernoulli likelihood
            candidates: List of candidate indices
            features: Feature matrix (n_candidates, n_features)
            n_pairs: Number of pairs to select
            **kwargs: Additional arguments (e.g., xi, rng)

        Returns:
            List of (i, j) tuples representing selected pairs
        """
        rng = kwargs.get('rng', np.random.default_rng())
        xi = kwargs.get('xi', 0.01)  # Exploration parameter
        model.eval()
        likelihood.eval()

        # Convert features to tensor
        Z = torch.tensor(features[candidates], dtype=torch.float32)

        # Compute posterior
        with torch.no_grad():
            f_dist = model(Z)
            mean = f_dist.mean.numpy()
            std = f_dist.stddev.numpy()

        # Current best (maximum mean)
        best = mean.max()

        # Compute EI scores
        # EI = E[max(f - best - xi, 0)]
        from scipy.stats import norm
        z = (mean - best - xi) / (std + 1e-8)
        ei_scores = (mean - best - xi) * norm.cdf(z) + std * norm.pdf(z)

        # Select candidates with highest EI
        sorted_indices = candidates[np.argsort(-ei_scores)]

        # Select pairs from top candidates
        pairs = []
        top_k = min(n_pairs * 2, len(sorted_indices))
        for _ in range(n_pairs):
            i, j = rng.choice(sorted_indices[:top_k], size=2, replace=False)
            pairs.append((int(i), int(j)))

        return pairs


class VarianceAcquisition(AcquisitionFunction):
    """
    Variance-based acquisition function.

    Selects pairs that maximize posterior variance.
    Pure exploration strategy.
    """

    def __init__(self, name: str = "Variance"):
        """
        Initialize variance acquisition.

        Args:
            name: Human-readable name
        """
        super().__init__(name=name)

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
        Select pairs using posterior variance.

        Args:
            model: Trained GP model
            likelihood: Bernoulli likelihood
            candidates: List of candidate indices
            features: Feature matrix (n_candidates, n_features)
            n_pairs: Number of pairs to select
            **kwargs: Additional arguments (e.g., rng)

        Returns:
            List of (i, j) tuples representing selected pairs
        """
        rng = kwargs.get('rng', np.random.default_rng())
        model.eval()
        likelihood.eval()

        # Convert features to tensor
        Z = torch.tensor(features[candidates], dtype=torch.float32)

        # Compute posterior variance
        with torch.no_grad():
            f_dist = model(Z)
            variance = f_dist.variance.numpy()

        # Select candidates with highest variance
        sorted_indices = candidates[np.argsort(-variance)]

        # Select pairs from top candidates
        pairs = []
        top_k = min(n_pairs * 2, len(sorted_indices))
        for _ in range(n_pairs):
            i, j = rng.choice(sorted_indices[:top_k], size=2, replace=False)
            pairs.append((int(i), int(j)))

        return pairs
