"""
Gaussian Process PBO learning strategy.

Implements Preferential Bayesian Optimization using Gaussian Processes
with a Bernoulli likelihood for pairwise preference learning.
"""

import sys
import os
# Add parent directory (project root) to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import logging
import pickle
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path

import numpy as np
import torch
from sklearn.preprocessing import StandardScaler

from backend.core.base_strategy import LearningStrategy
from backend.model_manager import train_model, save_checkpoint, load_checkpoint

# Import copeland score from parent directory
from metrics.copeland_score import copeland_score

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GPStrategy(LearningStrategy):
    """
    Gaussian Process learning strategy for preference learning.

    Uses a variational GP with Bernoulli likelihood to model preferences
    and computes rankings via Copeland score.

    Attributes:
        config: Configuration dictionary
        model: Trained GP model
        likelihood: Bernoulli likelihood
        scaler: Fitted StandardScaler for feature normalization
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize GP strategy.

        Args:
            config: Configuration dictionary with parameters:
                - max_epochs: Maximum training epochs (default: 100)
                - patience: Early stopping patience (default: 10)
                - batch_size: Batch size (default: 32)
                - num_inducing: Number of inducing points (default: 64)
                - learning_rate: Learning rate (default: 0.01)
                - device: Device for computation ('cpu' or 'cuda', default: 'cpu')
        """
        super().__init__(config)
        self.scaler = None
        self.device = config.get('device', 'cpu')

    def train(
        self,
        preferences: List[Tuple[Tuple[int, int], int]],
        features: np.ndarray,
        scaler: Optional[StandardScaler] = None
    ) -> Tuple[Any, Any]:
        """
        Train GP model on preference data.

        Args:
            preferences: List of ((i, j), preference) tuples
                       where preference is 0 or 1
            features: Feature matrix of shape (n_masks, n_features)
            scaler: Optional scaler object (if None, creates new StandardScaler)

        Returns:
            Tuple of (model, likelihood)

        Example:
            >>> strategy = GPStrategy(config)
            >>> preferences = [((0, 1), 1), ((1, 2), 0)]
            >>> features = np.random.randn(100, 5)
            >>> model, likelihood = strategy.train(preferences, features)
        """
        # Fit or use provided scaler
        if scaler is None:
            self.scaler = StandardScaler()
            self.scaler.fit(features)
            logger.info("Fitted new StandardScaler on features")
        else:
            self.scaler = scaler
            logger.info("Using provided StandardScaler")

        # Scale features
        features_scaled = self.scaler.transform(features)

        # Train model using model_manager
        self.model, self.likelihood = train_model(
            preferences=preferences,
            features=features_scaled,
            scaler=self.scaler,
            config=self.config
        )

        logger.info("GP model trained successfully")
        return self.model, self.likelihood

    def get_ranking(
        self,
        features: np.ndarray,
        scaler: Optional[StandardScaler] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute Copeland score ranking from trained model.

        Args:
            features: Feature matrix of shape (n_masks, n_features)
            scaler: Optional scaler object (uses self.scaler if None)

        Returns:
            Tuple of (ranking, scores) where:
            - ranking: Array of indices sorted by preference (best first)
            - scores: Array of Copeland scores for each mask

        Example:
            >>> strategy = GPStrategy(config)
            >>> ranking, scores = strategy.get_ranking(features)
            >>> print(f"Best mask: {ranking[0]}, Score: {scores[ranking[0]]:.3f}")
        """
        if self.model is None or self.likelihood is None:
            raise ValueError("Model not trained. Call train() first.")

        # Use provided scaler or fall back to fitted scaler
        if scaler is not None:
            features_scaled = scaler.transform(features)
        elif self.scaler is not None:
            features_scaled = self.scaler.transform(features)
        else:
            raise ValueError("No scaler available. Provide a scaler or train the model first.")

        # Convert to tensor
        Z = torch.tensor(features_scaled, dtype=torch.float32)

        # Compute Copeland scores
        scores = copeland_score(
            model=self.model,
            likelihood=self.likelihood,
            Z=Z,
            use_difference=True
        )

        # Sort by score (descending)
        ranking = np.argsort(-scores)

        logger.info(f"Computed ranking for {len(ranking)} masks")
        return ranking, scores

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
            >>> from acquisition.registry import get_acquisition
            >>> strategy = GPStrategy(config)
            >>> acq_fn = get_acquisition('thompson_sampling')
            >>> pairs = strategy.select_pairs(features, acq_fn, n_pairs=10)
        """
        if self.model is None or self.likelihood is None:
            raise ValueError("Model not trained. Call train() first.")

        # Scale features
        if self.scaler is not None:
            features_scaled = self.scaler.transform(features)
        else:
            raise ValueError("No scaler available. Train the model first.")

        # Get all candidates
        candidates = list(range(len(features)))

        # Use acquisition function to select pairs
        try:
            pairs = acquisition_fn.acquire(
                model=self.model,
                likelihood=self.likelihood,
                candidates=candidates,
                features=features_scaled,
                n_pairs=n_pairs,
                **kwargs
            )
            logger.info(f"Selected {len(pairs)} pairs using {acquisition_fn.name}")
        except Exception as e:
            # Fallback to random selection if acquisition fails
            logger.error(f"Acquisition function failed: {e}. Falling back to random selection.")
            rng = np.random.default_rng()
            pairs = []
            for _ in range(n_pairs):
                i, j = rng.choice(candidates, size=2, replace=False)
                pairs.append((int(i), int(j)))

        return pairs

    def save_checkpoint(self, path: str) -> None:
        """
        Save model checkpoint.

        Args:
            path: Path to save checkpoint

        Example:
            >>> strategy.save_checkpoint('checkpoints/model.pkl')
        """
        if self.model is None or self.likelihood is None:
            raise ValueError("No model to save. Train the model first.")

        if self.scaler is None:
            raise ValueError("No scaler to save. Train the model first.")

        checkpoint = {
            'model': self.model,
            'likelihood': self.likelihood,
            'scaler': self.scaler,
            'config': self.config,
        }

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'wb') as f:
            pickle.dump(checkpoint, f)

        logger.info(f"Checkpoint saved to {path}")

    def load_checkpoint(self, path: str) -> None:
        """
        Load model checkpoint.

        Args:
            path: Path to load checkpoint from

        Example:
            >>> strategy.load_checkpoint('checkpoints/model.pkl')
        """
        with open(path, 'rb') as f:
            checkpoint = pickle.load(f)

        self.model = checkpoint['model']
        self.likelihood = checkpoint['likelihood']
        self.scaler = checkpoint['scaler']
        self.config = checkpoint.get('config', self.config)

        logger.info(f"Checkpoint loaded from {path}")

    def predict_preference(
        self,
        i: int,
        j: int,
        features: np.ndarray
    ) -> float:
        """
        Predict preference probability P(i > j).

        Args:
            i: Index of first mask
            j: Index of second mask
            features: Feature matrix

        Returns:
            Probability that mask i is preferred over mask j

        Example:
            >>> prob = strategy.predict_preference(0, 1, features)
            >>> print(f"P(0 > 1) = {prob:.3f}")
        """
        if self.model is None or self.likelihood is None:
            raise ValueError("Model not trained. Call train() first.")

        # Scale features
        if self.scaler is not None:
            features_scaled = self.scaler.transform(features)
        else:
            raise ValueError("No scaler available. Train the model first.")

        # Compute difference vector
        diff = features_scaled[i] - features_scaled[j]
        diff_tensor = torch.tensor(diff, dtype=torch.float32).unsqueeze(0)

        # Predict
        self.model.eval()
        self.likelihood.eval()
        with torch.no_grad():
            output = self.model(diff_tensor)
            prob = self.likelihood(output).mean.item()

        return prob
