"""
Active learning loop for Preferential Bayesian Optimization.

Orchestrates the complete PBO workflow:
1. Select pairs using acquisition function
2. Query oracle for preferences
3. Update model with new preferences
4. Compute ranking and check convergence
"""

import sys
import os
# Add parent directory (project root) to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import logging
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path

import numpy as np
from sklearn.preprocessing import StandardScaler

from backend.strategies.gp_strategy import GPStrategy
from backend.session_manager import SessionManager
from encoders.handcrafted_encoder import HandcraftedEncoder

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ActiveLearningLoop:
    """
    Active learning loop for preference learning.

    Manages the iterative process of selecting pairs, collecting preferences,
    and updating the model to find the best segmentation masks.

    Attributes:
        masks: List of binary segmentation masks
        config: Configuration dictionary
        encoder: Feature encoder
        strategy: Learning strategy (GP)
        session_manager: Session persistence manager
        session_id: Current session ID
        features: Encoded features (scaled)
        scaler: Fitted StandardScaler
        preferences: List of ((i, j), pref) tuples
        iteration: Current iteration number
        ranking_history: History of rankings over iterations
        converged: Whether convergence has been reached
    """

    def __init__(self, masks: List[np.ndarray], config: Dict[str, Any]):
        """
        Initialize active learning loop.

        Args:
            masks: List of binary segmentation masks (2D numpy arrays)
            config: Configuration dictionary with parameters:
                - encoder: Encoder name (default: 'handcrafted')
                - strategy: Strategy name (default: 'gp')
                - acquisition: Acquisition function name (default: 'thompson_sampling')
                - max_iterations: Maximum iterations (default: 100)
                - n_pairs_per_iteration: Pairs per iteration (default: 10)
                - convergence_window: Window for stability check (default: 5)
                - convergence_threshold: Min agreements for convergence (default: 4)
                - top_k: Top-K to check for convergence (default: 5)
                - sessions_dir: Directory for session storage (default: 'data/sessions')

        Example:
            >>> masks = [np.random.randint(0, 2, (64, 64)) for _ in range(100)]
            >>> config = {'max_iterations': 50, 'n_pairs_per_iteration': 5}
            >>> loop = ActiveLearningLoop(masks, config)
        """
        self.masks = masks
        self.config = config
        self.n_masks = len(masks)

        # Initialize encoder
        encoder_name = config.get('encoder', 'handcrafted')
        self.encoder = HandcraftedEncoder()

        # Encode masks
        logger.info(f"Encoding {self.n_masks} masks...")
        features = self.encoder.encode_batch(masks)
        logger.info(f"Features shape: {features.shape}")

        # Initialize scaler
        self.scaler = StandardScaler()
        self.features = self.scaler.fit_transform(features)

        # Initialize strategy
        strategy_config = {
            'max_epochs': config.get('max_epochs', 100),
            'patience': config.get('patience', 10),
            'batch_size': config.get('batch_size', 32),
            'learning_rate': config.get('learning_rate', 0.01),
        }
        self.strategy = GPStrategy(strategy_config)

        # Initialize session manager
        sessions_dir = config.get('sessions_dir', 'data/sessions')
        self.session_manager = SessionManager(sessions_dir)

        # State variables
        self.session_id = None
        self.preferences = []
        self.iteration = 0
        self.ranking_history = []
        self.converged = False

        # Convergence parameters
        self.max_iterations = config.get('max_iterations', 100)
        self.n_pairs_per_iteration = config.get('n_pairs_per_iteration', 10)
        self.convergence_window = config.get('convergence_window', 5)
        self.convergence_threshold = config.get('convergence_threshold', 4)
        self.top_k = config.get('top_k', 5)

        logger.info("ActiveLearningLoop initialized")

    def get_next_batch(self, n_pairs: Optional[int] = None) -> List[Tuple[int, int]]:
        """
        Get next batch of pairs to query.

        Args:
            n_pairs: Number of pairs (uses config default if None)

        Returns:
            List of (i, j) tuples representing selected pairs

        Example:
            >>> pairs = loop.get_next_batch(n_pairs=10)
            >>> print(f"Selected {len(pairs)} pairs")
        """
        if n_pairs is None:
            n_pairs = self.n_pairs_per_iteration

        # First iteration: select random pairs
        if self.iteration == 0 or not self.strategy.is_trained():
            from acquisition.acquisition import RandomAcquisition
            acq_fn = RandomAcquisition()
            pairs = acq_fn.acquire(
                model=None,
                likelihood=None,
                candidates=list(range(self.n_masks)),
                features=self.features,
                n_pairs=n_pairs
            )
            logger.info(f"Iteration 0: Selected {len(pairs)} random pairs")
            return pairs

        # Use configured acquisition function
        from acquisition.registry import get_acquisition
        acquisition_name = self.config.get('acquisition', 'thompson_sampling')
        acq_fn = get_acquisition(acquisition_name)

        pairs = self.strategy.select_pairs(
            features=self.features,
            acquisition_fn=acq_fn,
            n_pairs=n_pairs
        )

        logger.info(f"Iteration {self.iteration}: Selected {len(pairs)} pairs")
        return pairs

    def add_preferences(self, pairs: List[Tuple[int, int]], preferences: List[int]) -> None:
        """
        Add preferences and trigger model retraining.

        Args:
            pairs: List of (i, j) tuples
            preferences: List of preference values (0 or 1)

        Example:
            >>> pairs = [(0, 1), (2, 3)]
            >>> prefs = [1, 0]
            >>> loop.add_preferences(pairs, prefs)
        """
        if len(pairs) != len(preferences):
            raise ValueError("Number of pairs must match number of preferences")

        # Add new preferences
        for pair, pref in zip(pairs, preferences):
            # Skip ties
            if pref not in [0, 1]:
                logger.warning(f"Skipping tie preference: {pair} -> {pref}")
                continue

            self.preferences.append((pair, pref))

        logger.info(f"Added {len(pairs)} preferences (total: {len(self.preferences)})")

        # Retrain model
        self._retrain()

        # Update iteration
        self.iteration += 1

        # Compute ranking
        ranking, scores = self.strategy.get_ranking(self.features, self.scaler)

        # Store history
        self.ranking_history.append({
            'iteration': self.iteration,
            'ranking': ranking.copy(),
            'scores': scores.copy(),
            'top_k': ranking[:self.top_k].tolist(),
        })

        # Check convergence
        self.converged = self._check_convergence()

        logger.info(f"Iteration {self.iteration} completed")

        # Auto-backup session
        if self.session_id is not None:
            session = self._build_session_dict()
            if self.session_manager.auto_backup(session, n=10):
                logger.info("Auto-backup created")

    def get_ranking(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get current ranking and scores.

        Returns:
            Tuple of (ranking, scores) where ranking is sorted by preference

        Example:
            >>> ranking, scores = loop.get_ranking()
            >>> print(f"Best mask: {ranking[0]}")
        """
        if not self.strategy.is_trained():
            raise ValueError("Model not trained. Add preferences first.")

        return self.strategy.get_ranking(self.features, self.scaler)

    def has_converged(self) -> bool:
        """
        Check if convergence has been reached.

        Returns:
            True if converged, False otherwise

        Example:
            >>> if loop.has_converged():
            ...     print("Converged!")
        """
        return self.converged

    def get_progress(self) -> Dict[str, Any]:
        """
        Get progress information.

        Returns:
            Dictionary with progress metrics

        Example:
            >>> progress = loop.get_progress()
            >>> print(f"Iteration: {progress['iteration']}")
        """
        ranking, scores = None, None
        if self.strategy.is_trained():
            ranking, scores = self.get_ranking()

        progress = {
            'iteration': self.iteration,
            'total_comparisons': len(self.preferences),
            'max_iterations': self.max_iterations,
            'converged': self.converged,
            'ranking': ranking.tolist() if ranking is not None else None,
            'scores': scores.tolist() if scores is not None else None,
            'top_k': ranking[:self.top_k].tolist() if ranking is not None else None,
        }

        return progress

    def save_session(self, session_id: Optional[str] = None) -> str:
        """
        Save current state to session.

        Args:
            session_id: Session ID (creates new if None)

        Returns:
            Session ID

        Example:
            >>> session_id = loop.save_session('my_session')
        """
        if session_id is None:
            # Create new session
            session_id = self.session_manager.create_session(self.config)
            self.session_id = session_id

        # Build session dictionary
        session = self._build_session_dict()
        session['session_id'] = session_id

        # Save
        self.session_manager.save_session(session_id, session)

        logger.info(f"Session saved: {session_id}")
        return session_id

    def load_session(self, session_id: str) -> None:
        """
        Load session state.

        Args:
            session_id: Session ID to load

        Example:
            >>> loop.load_session('my_session')
        """
        session = self.session_manager.load_session(session_id)

        self.session_id = session_id
        self.preferences = session.get('preferences', [])
        self.iteration = session.get('iteration', 0)
        self.ranking_history = session.get('history', [])
        self.converged = session.get('converged', False)

        # Load model if available
        if session.get('model') is not None:
            self.strategy.model = session['model']
            self.strategy.likelihood = session['likelihood']
            self.strategy.scaler = session['scaler']
            logger.info("Model loaded from session")

        logger.info(f"Session loaded: {session_id}")

    def _retrain(self) -> None:
        """Retrain model on all preferences."""
        if len(self.preferences) == 0:
            logger.warning("No preferences to train on")
            return

        self.strategy.train(
            preferences=self.preferences,
            features=self.features,
            scaler=self.scaler
        )

    def _check_convergence(self) -> bool:
        """
        Check if top-K ranking has stabilized.

        Returns:
            True if converged, False otherwise
        """
        # Check max iterations
        if self.iteration >= self.max_iterations:
            logger.info(f"Reached max iterations ({self.max_iterations})")
            return True

        # Need at least convergence_window iterations
        if len(self.ranking_history) < self.convergence_window:
            return False

        # Check top-K stability
        recent_rankings = [h['top_k'] for h in self.ranking_history[-self.convergence_window:]]

        # Count how many times each candidate appears in top-K
        from collections import Counter
        all_candidates = [c for ranking in recent_rankings for c in ranking]
        counts = Counter(all_candidates)

        # Check if at least threshold candidates appear consistently
        stable_count = sum(1 for count in counts.values() if count >= self.convergence_threshold)

        if stable_count >= self.top_k:
            logger.info(f"Converged: {stable_count}/{self.top_k} top-K candidates stable")
            return True

        return False

    def _build_session_dict(self) -> Dict[str, Any]:
        """Build session dictionary for saving."""
        ranking, scores = None, None
        if self.strategy.is_trained():
            ranking, scores = self.get_ranking()

        session = {
            'session_id': self.session_id,
            'config': self.config,
            'preferences': self.preferences,
            'iteration': self.iteration,
            'total_comparisons': len(self.preferences),
            'model': self.strategy.model,
            'likelihood': self.strategy.likelihood,
            'scaler': self.scaler,
            'features': self.features,
            'ranking': ranking,
            'scores': scores,
            'converged': self.converged,
            'history': self.ranking_history,
        }

        return session
