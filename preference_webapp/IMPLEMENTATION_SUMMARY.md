# Implementation Summary: Preference Learning Backend Components

## Overview

This document summarizes the implementation of the core backend components for the preference learning webapp. All components have been implemented and tested successfully.

## Date

2026-01-29

## Components Implemented

### 1. GP Strategy (`backend/strategies/gp_strategy.py`)

**Purpose**: Gaussian Process PBO learning strategy implementing the `LearningStrategy` interface.

**Key Features**:
- Integrates with existing `PreferenceGP` from `modules/toy_module.py`
- Uses difference vector formulation: `features[i] - features[j]`
- Trains with PyTorch Lightning via `model_manager`
- Computes Copeland score rankings
- Supports checkpoint save/load with scaler persistence
- Predicts preference probabilities

**Methods**:
- `train(preferences, features, scaler)`: Train GP on pairwise preferences
- `get_ranking(features, scaler)`: Compute Copeland score ranking
- `select_pairs(features, acquisition_fn, n_pairs)`: Select pairs using acquisition
- `save_checkpoint(path)`: Save model, likelihood, scaler
- `load_checkpoint(path)`: Load checkpoint
- `predict_preference(i, j, features)`: Predict P(i > j)

**Configuration**:
```python
config = {
    'max_epochs': 100,
    'patience': 10,
    'batch_size': 32,
    'num_inducing': 64,
    'learning_rate': 0.01,
    'device': 'cpu',
}
```

---

### 2. Session Manager (`backend/session_manager.py`)

**Purpose**: Session persistence with pickle-based storage.

**Key Features**:
- Create sessions with unique IDs (timestamp-based)
- Save/load sessions with complete state
- Auto-backup every N comparisons
- List all sessions with metadata
- Cleanup old backups
- Session info without full load

**Methods**:
- `create_session(config)`: Create new session with unique ID
- `save_session(session_id, session)`: Save to pickle
- `load_session(session_id)`: Load from pickle
- `list_sessions()`: List all session IDs
- `delete_session(session_id)`: Delete session
- `auto_backup(session, n)`: Backup every N comparisons
- `cleanup_old_backups(session_id, keep)`: Delete old backups
- `get_session_info(session_id)`: Get session metadata
- `list_sessions_info()`: List all sessions with info

**Session Structure**:
```python
session = {
    'session_id': str,
    'config': dict,
    'created_at': str,
    'updated_at': str,
    'preferences': List[Tuple[Tuple[int, int], int]],
    'iteration': int,
    'total_comparisons': int,
    'model': GP model,
    'likelihood': Bernoulli likelihood,
    'scaler': StandardScaler,
    'features': np.ndarray,
    'ranking': np.ndarray,
    'scores': np.ndarray,
    'converged': bool,
    'history': List[dict],
}
```

---

### 3. Active Learning Loop (`backend/active_learning_loop.py`)

**Purpose**: PBO orchestration for complete active learning workflow.

**Key Features**:
- End-to-end PBO workflow
- Encodes masks with `SegmentationFeatureEncoder`
- Uses `StandardScaler` for feature normalization
- Integrates GP strategy and acquisition functions
- Convergence detection (top-K stability)
- Progress tracking
- Session persistence

**Methods**:
- `get_next_batch(n_pairs)`: Get next pairs to query
- `add_preferences(pairs, preferences)`: Add preferences and retrain
- `get_ranking()`: Get current ranking and scores
- `has_converged()`: Check convergence status
- `get_progress()`: Get progress information
- `save_session(session_id)`: Save current state
- `load_session(session_id)`: Load session state

**Convergence Criteria**:
1. Top-K ranking stable over `convergence_window` iterations
2. At least `convergence_threshold` agreements
3. Maximum iterations reached

**Configuration**:
```python
config = {
    'encoder': 'handcrafted',
    'strategy': 'gp',
    'acquisition': 'thompson_sampling',
    'max_iterations': 100,
    'n_pairs_per_iteration': 10,
    'convergence_window': 5,
    'convergence_threshold': 4,
    'top_k': 5,
    'sessions_dir': 'data/sessions',
}
```

---

### 4. Model Manager (`backend/model_manager.py`)

**Purpose**: GP training wrapper with PyTorch Lightning.

**Key Features**:
- Trains `PreferenceGPModule` on preference data
- Uses difference vector formulation
- Handles binary preferences (0 or 1)
- Skips ties (non-binary preferences)
- Early stopping with patience
- Checkpoint save/load with features

**Functions**:
- `train_model(preferences, features, scaler, config)`: Train GP model
- `save_checkpoint(model, likelihood, scaler, features, iteration, path)`: Save checkpoint
- `load_checkpoint(path)`: Load checkpoint

**Training Details**:
- Prepares difference vectors: `X[i] - X[j]`
- Uses `TensorDataset` and `DataLoader`
- Early stopping on `train_loss`
- Returns trained model and likelihood

---

### 5. Handcrafted Encoder (`encoders/handcrafted_encoder.py`)

**Purpose**: Wrapper for `SegmentationFeatureEncoder` implementing `BaseEncoder`.

**Key Features**:
- Wraps existing `models/toy_encoder.py::SegmentationFeatureEncoder`
- Implements `BaseEncoder` interface
- Extracts 5 handcrafted features:
  1. Moran's I (spatial autocorrelation)
  2. Number of connected components
  3. Mean area of components
  4. Compactness of largest component
  5. Perimeter-area ratio

**Methods**:
- `encode(mask)`: Extract 5D feature vector
- `dim()`: Return 5
- `encode_batch(masks)`: Encode multiple masks

---

### 6. Encoder Registry (`encoders/registry.py`)

**Purpose**: Central registry for feature encoders.

**Registered Encoders**:
- `handcrafted` → `HandcraftedEncoder`
- `handcrafted_features` → `HandcraftedEncoder` (alias)

**Functions**:
- `get_encoder(name, **kwargs)`: Get encoder instance
- `list_encoders()`: List available encoders

---

### 7. Acquisition Functions (`acquisition/acquisition.py`)

**Purpose**: Active learning acquisition functions for pair selection.

**Implemented Functions**:

1. **RandomAcquisition** (`random`)
   - Selects pairs uniformly at random
   - Useful as baseline and for exploration

2. **ThompsonSamplingAcquisition** (`thompson_sampling`, `ts`)
   - Samples from GP posterior
   - Balances exploration and exploitation

3. **UCBAcquisition** (`ucb`)
   - Upper Confidence Bound
   - Focuses on high-uncertainty regions
   - Configurable `beta` parameter

4. **EIAcquisition** (`ei`)
   - Expected Improvement
   - Maximizes expected improvement in Copeland score
   - Configurable `xi` parameter

5. **VarianceAcquisition** (`variance`)
   - Pure exploration strategy
   - Maximizes posterior variance

**Common Parameters**:
- `rng`: Random number generator (optional)

---

### 8. Acquisition Registry (`acquisition/registry.py`)

**Purpose**: Central registry for acquisition functions.

**Registered Functions**:
- `random` → `RandomAcquisition`
- `thompson_sampling` → `ThompsonSamplingAcquisition`
- `ts` → `ThompsonSamplingAcquisition` (alias)
- `ucb` → `UCBAcquisition`
- `ei` → `EIAcquisition`
- `variance` → `VarianceAcquisition`

**Functions**:
- `get_acquisition(name, **kwargs)`: Get acquisition function instance
- `list_acquisitions()`: List available functions

---

## Testing

All components have been tested with `test_implementation.py`:

```
=== Testing Encoder ===
✓ Encoder test passed

=== Testing Acquisition Functions ===
✓ Acquisition test passed

=== Testing GP Strategy ===
✓ GP Strategy test passed

=== Testing Session Manager ===
✓ Session Manager test passed

=== Testing Active Learning Loop ===
✓ Active Learning Loop test passed

✓ All tests passed!
```

### Test Coverage

1. **Encoder Registry**: Lists encoders, gets encoder, encodes mask
2. **Acquisition Registry**: Lists functions, gets function, selects pairs
3. **GP Strategy**: Trains model, computes ranking, selects pairs, saves/loads checkpoints
4. **Session Manager**: Creates session, lists sessions, auto-backup, cleanup
5. **Active Learning Loop**: Complete workflow with encoding, training, ranking, session persistence

---

## Integration with Existing Code

### Dependencies from Parent Directory

The implementation imports from the parent directory:
- `modules/toy_module.py` → `PreferenceGP`, `PreferenceGPModule`
- `models/toy_encoder.py` → `SegmentationFeatureEncoder`
- `metrics/copeland_score.py` → `copeland_score`

### Import Strategy

To avoid circular imports, components import directly rather than through package `__init__` files:

```python
# Direct imports
from backend.strategies.gp_strategy import GPStrategy
from backend.session_manager import SessionManager
from backend.active_learning_loop import ActiveLearningLoop
from encoders.registry import get_encoder, list_encoders
from acquisition.registry import get_acquisition, list_acquisitions
```

---

## Key Implementation Decisions

### 1. Feature Scaling

- **Decision**: Use `StandardScaler` for all features
- **Rationale**: Critical for GP performance (as noted in CLAUDE.md)
- **Implementation**: Scaler saved with checkpoints and sessions

### 2. Difference Vector Formulation

- **Decision**: Use `features[i] - features[j]` for pairwise input
- **Rationale**: Standard for preference GP, reduces to binary classification
- **Alternative Considered**: Concatenation `[features[i], features[j]]` (rejected)

### 3. Tie Handling

- **Decision**: Skip non-binary preferences (ties) during training
- **Rationale**: Bernoulli likelihood requires 0 or 1
- **Implementation**: Check `pref in [0, 1]` before adding to training data

### 4. Checkpoint Format

- **Decision**: Use pickle for checkpoints and sessions
- **Rationale**: Simple, supports Python objects, no external dependencies
- **Trade-off**: Not compatible across Python versions/library versions

### 5. Session IDs

- **Decision**: Use timestamp-based IDs: `prefix_YYYYMMDD_HHMMSS`
- **Rationale**: Human-readable, sortable, unique
- **Format**: `{prefix}_{timestamp}`

### 6. Convergence Detection

- **Decision**: Top-K stability over sliding window
- **Rationale**: More robust than single-iteration comparison
- **Parameters**:
  - `convergence_window`: Number of iterations to check
  - `convergence_threshold`: Minimum agreements required
  - `top_k`: Number of top candidates to track

---

## Known Issues and Limitations

### 1. Circular Import Resolution

**Issue**: Initial circular import between `backend/__init__.py` and `backend/active_learning_loop.py`

**Solution**: Removed imports from package `__init__` files, use direct imports

**Status**: Resolved

### 2. PyTorch Lightning Warnings

**Issue**: Trainer warnings about GPU usage and DataLoader workers

**Impact**: Informational only, does not affect functionality

**Mitigation**: Can configure `Trainer(accelerator='gpu')` and `DataLoader(num_workers=N)` in production

### 3. Test Coverage

**Current**: Unit tests for individual components

**Missing**:
- Integration tests with real LAMAP data
- Performance benchmarks
- Convergence behavior validation

**Recommendation**: Add comprehensive integration tests

---

## Future Enhancements

### 1. Additional Encoders

- CNN-based encoders (e.g., frozen ResNet)
- Vision Transformer encoders
- Domain-specific archaeological features

### 2. Alternative Strategies

- Deep Kernel Learning (DKL)
- Random Forest preference learning
- Neural network-based preference models

### 3. Advanced Acquisition

- Batch acquisition (correlation-aware)
- Diversity-based selection
- Multi-objective acquisition

### 4. Convergence Improvements

- Adaptive convergence thresholds
- Confidence interval-based convergence
- Early stopping based on prediction confidence

### 5. Performance Optimization

- Caching feature encodings
- Parallel pair selection
- GPU acceleration for GP inference

---

## File Structure

```
preference_webapp/
├── backend/
│   ├── strategies/
│   │   ├── __init__.py
│   │   └── gp_strategy.py          [NEW]
│   ├── core/
│   │   ├── base_strategy.py
│   │   ├── base_encoder.py
│   │   ├── base_acquisition.py
│   │   └── registry.py
│   ├── session_manager.py          [NEW]
│   ├── model_manager.py            [NEW]
│   ├── active_learning_loop.py     [NEW]
│   └── __init__.py
├── encoders/
│   ├── __init__.py
│   ├── handcrafted_encoder.py      [NEW]
│   └── registry.py                 [NEW]
├── acquisition/
│   ├── __init__.py
│   ├── acquisition.py              [NEW]
│   └── registry.py                 [NEW]
└── test_implementation.py          [NEW]
```

---

## Usage Examples

### Basic Usage

```python
import numpy as np
from backend.active_learning_loop import ActiveLearningLoop

# Create masks
masks = [np.random.randint(0, 2, (64, 64)) for _ in range(100)]

# Configure
config = {
    'max_iterations': 50,
    'n_pairs_per_iteration': 10,
    'acquisition': 'thompson_sampling',
}

# Initialize loop
loop = ActiveLearningLoop(masks, config)

# Active learning loop
while not loop.has_converged():
    # Get pairs to query
    pairs = loop.get_next_batch()

    # Query oracle (human or virtual)
    preferences = [query_oracle(i, j) for i, j in pairs]

    # Add preferences and retrain
    loop.add_preferences(pairs, preferences)

    # Check progress
    progress = loop.get_progress()
    print(f"Iteration {progress['iteration']}: {progress['total_comparisons']} comparisons")

    # Save session periodically
    if progress['iteration'] % 10 == 0:
        loop.save_session()

# Get final ranking
ranking, scores = loop.get_ranking()
best_mask_idx = ranking[0]
print(f"Best mask: {best_mask_idx}")
```

### Using Individual Components

```python
from backend.strategies.gp_strategy import GPStrategy
from encoders.registry import get_encoder
from acquisition.registry import get_acquisition
from sklearn.preprocessing import StandardScaler

# Setup
encoder = get_encoder('handcrafted')
masks = [...]
features = encoder.encode_batch(masks)

scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

# Train
preferences = [((0, 1), 1), ((1, 2), 0)]
strategy = GPStrategy({'max_epochs': 100})
model, likelihood = strategy.train(preferences, features_scaled, scaler)

# Rank
ranking, scores = strategy.get_ranking(features_scaled, scaler)

# Select pairs
acq_fn = get_acquisition('ucb', beta=2.0)
pairs = strategy.select_pairs(features_scaled, acq_fn, n_pairs=10)

# Predict
prob = strategy.predict_preference(0, 1, features_scaled)
print(f"P(0 > 1) = {prob:.3f}")
```

---

## Conclusion

All requested components have been successfully implemented and tested:
1. ✓ GP Strategy with full LearningStrategy interface
2. ✓ Session Manager with persistence
3. ✓ Active Learning Loop for PBO orchestration
4. ✓ Model Manager for GP training
5. ✓ Handcrafted Encoder wrapper
6. ✓ Encoder Registry
7. ✓ Acquisition Functions and Registry

The implementation is ready for integration with the Streamlit UI and testing with real LAMAP data.
