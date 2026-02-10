"""
Test script for verifying the preference learning implementation.

Tests all components:
- Encoder registry
- Acquisition function registry
- GP strategy
- Session manager
- Active learning loop
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import numpy as np

# Import directly to avoid circular imports
from encoders.registry import list_encoders, get_encoder
from acquisition.registry import list_acquisitions, get_acquisition
from backend.strategies.gp_strategy import GPStrategy
from backend.session_manager import SessionManager
from backend.active_learning_loop import ActiveLearningLoop


def test_encoder():
    """Test encoder registry and handcrafted encoder."""
    print("\n=== Testing Encoder ===")

    # List encoders
    encoders = list_encoders()
    print(f"Available encoders: {encoders}")

    # Get encoder
    encoder = get_encoder('handcrafted')
    print(f"Encoder: {encoder}")
    print(f"Dimension: {encoder.dim()}")

    # Test encoding
    mask = np.random.randint(0, 2, (64, 64))
    features = encoder.encode(mask)
    print(f"Features shape: {features.shape}")
    print(f"Features dtype: {features.dtype}")
    assert features.shape == (5,), f"Expected shape (5,), got {features.shape}"

    print("✓ Encoder test passed")


def test_acquisition():
    """Test acquisition function registry."""
    print("\n=== Testing Acquisition Functions ===")

    # List acquisitions
    acquisitions = list_acquisitions()
    print(f"Available acquisitions: {acquisitions}")

    # Get acquisition function
    acq = get_acquisition('random')
    print(f"Acquisition: {acq}")

    # Test acquisition
    candidates = list(range(10))
    features = np.random.randn(10, 5)
    pairs = acq.acquire(None, None, candidates, features, n_pairs=3)
    print(f"Selected pairs: {pairs}")
    assert len(pairs) == 3, f"Expected 3 pairs, got {len(pairs)}"

    print("✓ Acquisition test passed")


def test_gp_strategy():
    """Test GP learning strategy."""
    print("\n=== Testing GP Strategy ===")

    # Create dummy data
    n_masks = 20
    n_features = 5
    features = np.random.randn(n_masks, n_features).astype(np.float32)

    # Create preferences
    preferences = [
        ((0, 1), 1),
        ((1, 2), 0),
        ((2, 3), 1),
        ((3, 4), 0),
        ((4, 5), 1),
    ]

    # Create strategy
    config = {
        'max_epochs': 10,  # Small for testing
        'patience': 3,
    }
    strategy = GPStrategy(config)
    print(f"Strategy: {strategy}")

    # Train
    print("Training GP model...")
    model, likelihood = strategy.train(preferences, features)
    print(f"Model trained: {model is not None}")
    print(f"Likelihood trained: {likelihood is not None}")
    assert strategy.is_trained(), "Model should be trained"

    # Get ranking
    ranking, scores = strategy.get_ranking(features)
    print(f"Ranking shape: {ranking.shape}")
    print(f"Scores shape: {scores.shape}")
    print(f"Top 5: {ranking[:5]}")
    assert ranking.shape == (n_masks,), f"Expected shape ({n_masks},), got {ranking.shape}"

    # Select pairs
    acq_fn = get_acquisition('random')
    pairs = strategy.select_pairs(features, acq_fn, n_pairs=3)
    print(f"Selected pairs: {pairs}")
    assert len(pairs) == 3, f"Expected 3 pairs, got {len(pairs)}"

    # Test checkpoint
    checkpoint_path = '/tmp/test_gp_checkpoint.pkl'
    strategy.save_checkpoint(checkpoint_path)
    print(f"Checkpoint saved to {checkpoint_path}")

    # Load checkpoint
    strategy2 = GPStrategy(config)
    strategy2.load_checkpoint(checkpoint_path)
    print(f"Checkpoint loaded")
    assert strategy2.is_trained(), "Loaded model should be trained"

    print("✓ GP Strategy test passed")


def test_session_manager():
    """Test session manager."""
    print("\n=== Testing Session Manager ===")

    # Create session manager
    manager = SessionManager(sessions_dir='/tmp/test_sessions')

    # Create session
    config = {'period': 'bronze_age', 'n_masks': 100}
    session_id = manager.create_session(config)
    print(f"Created session: {session_id}")

    # List sessions
    sessions = manager.list_sessions()
    print(f"Sessions: {sessions}")
    assert session_id in sessions, f"Session {session_id} should be in list"

    # Load session
    session = manager.load_session(session_id)
    print(f"Loaded session: {session['session_id']}")

    # Update session
    session['preferences'] = [((0, 1), 1)]
    session['total_comparisons'] = 1
    manager.save_session(session_id, session)

    # Get session info
    info = manager.get_session_info(session_id)
    print(f"Session info: {info}")

    # Test auto-backup
    for i in range(1, 12):
        session['total_comparisons'] = i
        backed_up = manager.auto_backup(session, n=5)
        if i % 5 == 0:
            assert backed_up, f"Should backup at comparison {i}"

    # Cleanup
    manager.delete_session(session_id)
    print(f"Deleted session: {session_id}")

    print("✓ Session Manager test passed")


def test_active_learning_loop():
    """Test active learning loop (integration test)."""
    print("\n=== Testing Active Learning Loop ===")

    # Create dummy masks
    n_masks = 30
    masks = [np.random.randint(0, 2, (64, 64)) for _ in range(n_masks)]

    # Config
    config = {
        'max_iterations': 3,
        'n_pairs_per_iteration': 3,
        'max_epochs': 5,  # Small for testing
        'acquisition': 'random',
        'sessions_dir': '/tmp/test_sessions',
    }

    # Create loop
    loop = ActiveLearningLoop(masks, config)
    print(f"ActiveLearningLoop created with {loop.n_masks} masks")
    print(f"Features shape: {loop.features.shape}")

    # Get initial batch
    pairs = loop.get_next_batch()
    print(f"Initial batch: {len(pairs)} pairs")

    # Add preferences
    preferences = [1, 0, 1]
    loop.add_preferences(pairs, preferences)
    print(f"Iteration 1 completed")

    # Check progress
    progress = loop.get_progress()
    print(f"Progress: {progress}")

    # Get ranking
    ranking, scores = loop.get_ranking()
    print(f"Ranking top 5: {ranking[:5]}")

    # Save session
    session_id = loop.save_session()
    print(f"Session saved: {session_id}")

    # Test loading
    loop2 = ActiveLearningLoop(masks, config)
    loop2.load_session(session_id)
    print(f"Session loaded: {loop2.iteration} iterations")

    print("✓ Active Learning Loop test passed")


if __name__ == '__main__':
    print("Starting implementation tests...")

    try:
        test_encoder()
        test_acquisition()
        test_gp_strategy()
        test_session_manager()
        test_active_learning_loop()

        print("\n" + "="*50)
        print("✓ All tests passed!")
        print("="*50)

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
