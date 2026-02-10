"""
Model manager for training and managing GP models.

Provides a wrapper around PyTorch Lightning training for preference GP models.
"""

import sys
import os
# Add parent directory (project root) to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import logging
import pickle
from typing import Tuple, Any, Dict
from pathlib import Path

import numpy as np
import torch
from sklearn.preprocessing import StandardScaler
import lightning.pytorch as pl

# Import existing modules
from modules.toy_module import PreferenceGPModule

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def train_model(
    preferences: list,
    features: np.ndarray,
    scaler: StandardScaler,
    config: Dict[str, Any]
) -> Tuple[Any, Any]:
    """
    Train a preference GP model on pairwise comparison data.

    Args:
        preferences: List of ((i, j), pref) tuples where pref is 0 or 1
        features: Feature matrix of shape (n_masks, n_features)
        scaler: Fitted StandardScaler for feature normalization
        config: Configuration dictionary with training parameters:
            - max_epochs: Maximum training epochs (default: 100)
            - patience: Early stopping patience (default: 10)
            - batch_size: Batch size (default: 32)
            - num_inducing: Number of inducing points (default: 64)
            - learning_rate: Learning rate (default: 0.01)

    Returns:
        Tuple of (model, likelihood)

    Example:
        >>> preferences = [((0, 1), 1), ((1, 2), 0)]
        >>> features = np.random.randn(100, 5)
        >>> scaler = StandardScaler().fit(features)
        >>> config = {'max_epochs': 50}
        >>> model, likelihood = train_model(preferences, features, scaler, config)
    """
    # Extract config parameters
    max_epochs = config.get('max_epochs', 100)
    patience = config.get('patience', 10)
    batch_size = config.get('batch_size', 32)
    num_inducing = config.get('num_inducing', 64)
    learning_rate = config.get('learning_rate', 0.01)

    # Prepare training data
    # Use difference vector formulation: features[i] - features[j]
    X_train = []
    y_train = []

    for (i, j), pref in preferences:
        # Skip ties (pref == 0.5 or None)
        if pref not in [0, 1]:
            logger.warning(f"Skipping preference pair ({i}, {j}) with value {pref} (not binary)")
            continue

        # Compute difference vector with scaled features
        diff = features[i] - features[j]
        X_train.append(diff)
        y_train.append(pref)

    if len(X_train) == 0:
        raise ValueError("No valid preference data found (all pairs may be ties)")

    X_train = np.array(X_train, dtype=np.float32)
    y_train = np.array(y_train, dtype=np.float32)

    logger.info(f"Training on {len(X_train)} preference pairs with {X_train.shape[1]} features")

    # Create dataset and dataloader
    train_dataset = torch.utils.data.TensorDataset(
        torch.tensor(X_train),
        torch.tensor(y_train)
    )
    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True
    )

    # Initialize model
    input_dim = X_train.shape[1]
    num_data = len(X_train)

    module = PreferenceGPModule(input_dim=input_dim, num_data=num_data)

    # Configure optimizer learning rate
    module.configure_optimizers = lambda: torch.optim.Adam(
        module.parameters(), lr=learning_rate
    )

    # Setup trainer
    early_stop_callback = pl.callbacks.EarlyStopping(
        monitor='train_loss',
        patience=patience,
        mode='min'
    )

    trainer = pl.Trainer(
        max_epochs=max_epochs,
        callbacks=[early_stop_callback],
        enable_progress_bar=False,
        logger=False,
        accelerator='auto' if torch.cuda.is_available() else 'cpu'
    )

    # Train model
    logger.info("Starting GP training...")
    trainer.fit(module, train_loader)
    logger.info("Training completed")

    # Extract model and likelihood
    model = module.gp
    likelihood = module.likelihood

    return model, likelihood


def save_checkpoint(
    model: Any,
    likelihood: Any,
    scaler: StandardScaler,
    features: np.ndarray,
    iteration: int,
    path: str
) -> None:
    """
    Save model checkpoint including model, likelihood, scaler, and features.

    Args:
        model: Trained GP model
        likelihood: Bernoulli likelihood
        scaler: Fitted StandardScaler
        features: Feature matrix
        iteration: Current iteration number
        path: Path to save checkpoint

    Example:
        >>> save_checkpoint(model, likelihood, scaler, features, 5, 'checkpoints/iter5.pkl')
    """
    checkpoint = {
        'model': model,
        'likelihood': likelihood,
        'scaler': scaler,
        'features': features,
        'iteration': iteration,
    }

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'wb') as f:
        pickle.dump(checkpoint, f)

    logger.info(f"Checkpoint saved to {path}")


def load_checkpoint(path: str) -> Dict[str, Any]:
    """
    Load model checkpoint.

    Args:
        path: Path to checkpoint file

    Returns:
        Dictionary with keys: model, likelihood, scaler, features, iteration

    Example:
        >>> checkpoint = load_checkpoint('checkpoints/iter5.pkl')
        >>> model = checkpoint['model']
        >>> scaler = checkpoint['scaler']
    """
    with open(path, 'rb') as f:
        checkpoint = pickle.load(f)

    logger.info(f"Checkpoint loaded from {path}")
    return checkpoint
