#!/usr/bin/env python
"""
Test the plugin registry system.

Run this to verify registries work correctly before building
any real plugins.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.registry import (
    AcquisitionRegistry,
    StrategyRegistry,
    OracleRegistry,
    EncoderRegistry,
)
from backend.core.base_acquisition import AcquisitionFunction
from backend.core.base_strategy import LearningStrategy
from backend.core.base_oracle import BaseOracle
from backend.core.base_encoder import BaseEncoder
import numpy as np


def test_acquisition_registry():
    """Test acquisition registry works."""
    print("\nTesting AcquisitionRegistry...")

    registry = AcquisitionRegistry()

    # Register a dummy acquisition function
    @registry.register('test_acquisition')
    class TestAcquisition(AcquisitionFunction):
        def __init__(self, param1=1.0):
            super().__init__("Test Acquisition")
            self.param1 = param1

        def acquire(self, model, likelihood, candidates, features, n_pairs=1, **kwargs):
            # Just return first n_pairs pairs
            pairs = []
            for i in range(min(n_pairs, len(candidates) // 2)):
                pairs.append((candidates[2*i], candidates[2*i + 1]))
            return pairs

    # Verify registration
    assert 'test_acquisition' in registry.list_available(), \
        "Failed to register 'test_acquisition'"
    print("  ✓ Registered test_acquisition")

    # Verify retrieval
    acq = registry.get('test_acquisition', param1=2.0)
    assert acq is not None, "Failed to get 'test_acquisition'"
    assert acq.param1 == 2.0, "Failed to pass parameter"
    print("  ✓ Retrieved test_acquisition with parameters")

    # Test acquire method
    candidates = [0, 1, 2, 3, 4, 5]
    features = np.random.randn(6, 5)
    pairs = acq.acquire(None, None, candidates, features, n_pairs=2)
    assert len(pairs) == 2, f"Expected 2 pairs, got {len(pairs)}"
    print(f"  ✓ Acquired {len(pairs)} pairs: {pairs}")

    # Test is_registered
    assert registry.is_registered('test_acquisition'), \
        "is_registered failed"
    print("  ✓ is_registered works")

    # Test unregister
    registry.unregister('test_acquisition')
    assert not registry.is_registered('test_acquisition'), \
        "unregister failed"
    print("  ✓ Unregistered test_acquisition")

    # Test error handling
    try:
        registry.get('nonexistent')
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Unknown" in str(e)
        print("  ✓ Error handling works for unknown acquisition")

    print("✓ AcquisitionRegistry tests passed")
    return True


def test_strategy_registry():
    """Test strategy registry works."""
    print("\nTesting StrategyRegistry...")

    registry = StrategyRegistry()

    # Register a dummy strategy
    @registry.register('test_strategy')
    class TestStrategy(LearningStrategy):
        def __init__(self, config):
            super().__init__(config)
            self.max_epochs = config.get('max_epochs', 10)

        def train(self, preferences, features, scaler=None):
            # Dummy training
            self.model = "dummy_model"
            self.likelihood = "dummy_likelihood"
            return self.model, self.likelihood

        def get_ranking(self, features, scaler=None):
            scores = np.random.randn(len(features))
            ranking = np.argsort(-scores)
            return ranking, scores

        def select_pairs(self, features, acquisition_fn, n_pairs=10, **kwargs):
            # Random pairs
            candidates = list(range(len(features)))
            pairs = []
            for _ in range(n_pairs):
                i, j = np.random.choice(candidates, 2, replace=False)
                pairs.append((int(i), int(j)))
            return pairs

        def save_checkpoint(self, path):
            pass

        def load_checkpoint(self, path):
            pass

    # Verify registration
    assert 'test_strategy' in registry.list_available(), \
        "Failed to register 'test_strategy'"
    print("  ✓ Registered test_strategy")

    # Verify retrieval
    strategy = registry.get('test_strategy', config={'max_epochs': 20})
    assert strategy is not None, "Failed to get 'test_strategy'"
    assert strategy.max_epochs == 20, "Failed to pass config"
    print("  ✓ Retrieved test_strategy with config")

    # Test train
    preferences = [((0, 1), 1), ((1, 2), 0)]
    features = np.random.randn(5, 3)
    model, likelihood = strategy.train(preferences, features)
    assert strategy.is_trained(), "Model should be trained"
    print("  ✓ Train method works")

    # Test get_ranking
    ranking, scores = strategy.get_ranking(features)
    assert len(ranking) == len(features), "Ranking length mismatch"
    assert len(scores) == len(features), "Scores length mismatch"
    print(f"  ✓ Get ranking works: {ranking}")

    # Test select_pairs
    pairs = strategy.select_pairs(features, None, n_pairs=3)
    assert len(pairs) == 3, f"Expected 3 pairs, got {len(pairs)}"
    print(f"  ✓ Select pairs works: {pairs}")

    print("✓ StrategyRegistry tests passed")
    return True


def test_oracle_registry():
    """Test oracle registry works."""
    print("\nTesting OracleRegistry...")

    registry = OracleRegistry()

    # Register a dummy oracle
    @registry.register('test_oracle')
    class TestOracle(BaseOracle):
        def __init__(self, noise=0.1):
            super().__init__("Test Oracle")
            self.noise = noise
            self.rng = np.random.default_rng(42)

        def prefer(self, mask_a, mask_b):
            # Random preference
            return self.rng.random() < 0.5

        def set_bias(self, feature_name, value):
            self.noise = value

        def get_biases(self):
            return {'noise': self.noise}

    # Verify registration
    assert 'test_oracle' in registry.list_available(), \
        "Failed to register 'test_oracle'"
    print("  ✓ Registered test_oracle")

    # Verify retrieval
    oracle = registry.get('test_oracle', noise=0.2)
    assert oracle is not None, "Failed to get 'test_oracle'"
    assert oracle.noise == 0.2, "Failed to pass noise parameter"
    print("  ✓ Retrieved test_oracle with parameters")

    # Test prefer
    mask1 = np.random.randint(0, 2, (32, 32))
    mask2 = np.random.randint(0, 2, (32, 32))
    preference = oracle.prefer(mask1, mask2)
    assert isinstance(preference, (bool, np.bool_)), \
        f"Expected bool, got {type(preference)}"
    print(f"  ✓ Prefer method works: {preference}")

    # Test set_bias/get_biases
    oracle.set_bias('noise', 0.5)
    biases = oracle.get_biases()
    assert biases['noise'] == 0.5, "Bias adjustment failed"
    print("  ✓ Bias adjustment works")

    # Test rank_masks
    masks = [np.random.randint(0, 2, (16, 16)) for _ in range(5)]
    ranking = oracle.rank_masks(masks)
    assert len(ranking) == len(masks), "Ranking length mismatch"
    print(f"  ✓ Rank masks works: {ranking}")

    print("✓ OracleRegistry tests passed")
    return True


def test_encoder_registry():
    """Test encoder registry works."""
    print("\nTesting EncoderRegistry...")

    registry = EncoderRegistry()

    # Register a dummy encoder
    @registry.register('test_encoder')
    class TestEncoder(BaseEncoder):
        def __init__(self, feature_dim=10):
            super().__init__("Test Encoder")
            self.feature_dim = feature_dim

        def encode(self, mask):
            # Dummy encoding: return random features
            return np.random.randn(self.feature_dim)

        def dim(self):
            return self.feature_dim

    # Verify registration
    assert 'test_encoder' in registry.list_available(), \
        "Failed to register 'test_encoder'"
    print("  ✓ Registered test_encoder")

    # Verify retrieval
    encoder = registry.get('test_encoder', feature_dim=15)
    assert encoder is not None, "Failed to get 'test_encoder'"
    assert encoder.dim() == 15, "Failed to pass feature_dim"
    print("  ✓ Retrieved test_encoder with parameters")

    # Test encode
    mask = np.random.randint(0, 2, (32, 32))
    features = encoder.encode(mask)
    assert len(features) == 15, f"Expected 15 features, got {len(features)}"
    print(f"  ✓ Encode method works: shape={features.shape}")

    # Test encode_batch
    masks = [np.random.randint(0, 2, (16, 16)) for _ in range(5)]
    features_batch = encoder.encode_batch(masks)
    assert features_batch.shape == (5, 15), \
        f"Expected shape (5, 15), got {features_batch.shape}"
    print(f"  ✓ Encode batch works: shape={features_batch.shape}")

    # Test __call__
    features = encoder(mask)
    assert len(features) == 15, "__call__ failed"
    print("  ✓ __call__ method works")

    print("✓ EncoderRegistry tests passed")
    return True


def main():
    """Run all registry tests."""
    print("=" * 60)
    print("REGISTRY SYSTEM TESTS")
    print("=" * 60)

    results = {
        "acquisition": test_acquisition_registry(),
        "strategy": test_strategy_registry(),
        "oracle": test_oracle_registry(),
        "encoder": test_encoder_registry(),
    }

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_passed = all(results.values())

    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")

    print("=" * 60)

    if all_passed:
        print("\n✅ Registry system validated - ready for plugins!")
        return 0
    else:
        print("\n❌ Registry system tests failed")
        return 1


if __name__ == "__main__":
    exit(main())
