# Quick Start Guide: Preference Learning Backend

## Setup

```bash
# Activate conda environment
conda activate .conda

# Or use full path
.conda/bin/python your_script.py
```

## Core Components

### 1. Active Learning Loop (Recommended)

The easiest way to use the system:

```python
from backend.active_learning_loop import ActiveLearningLoop
import numpy as np

# Load masks
masks = [np.random.randint(0, 2, (64, 64)) for _ in range(100)]

# Configure
config = {
    'max_iterations': 50,
    'n_pairs_per_iteration': 10,
    'acquisition': 'thompson_sampling',  # or 'random', 'ucb', 'ei', 'variance'
    'convergence_window': 5,
    'top_k': 5,
}

# Initialize
loop = ActiveLearningLoop(masks, config)

# Run active learning
while not loop.has_converged():
    pairs = loop.get_next_batch()
    preferences = [get_preference(i, j) for i, j in pairs]  # Your oracle here
    loop.add_preferences(pairs, preferences)
    loop.save_session()  # Auto-saves if session_id exists

# Get results
ranking, scores = loop.get_ranking()
best_mask = masks[ranking[0]]
```

### 2. Individual Components

#### Encoder

```python
from encoders.registry import get_encoder

# Get encoder
encoder = get_encoder('handcrafted')

# Encode single mask
features = encoder.encode(mask)  # Returns (5,) array

# Encode batch
features = encoder.encode_batch(masks)  # Returns (n_masks, 5) array
```

#### GP Strategy

```python
from backend.strategies.gp_strategy import GPStrategy
from sklearn.preprocessing import StandardScaler

# Setup
features = encoder.encode_batch(masks)
scaler = StandardScaler().fit(features)
preferences = [((0, 1), 1), ((1, 2), 0)]

# Train
strategy = GPStrategy({'max_epochs': 100})
model, likelihood = strategy.train(preferences, features, scaler)

# Rank
ranking, scores = strategy.get_ranking(features, scaler)

# Select pairs
from acquisition.registry import get_acquisition
acq_fn = get_acquisition('ucb', beta=2.0)
pairs = strategy.select_pairs(features, acq_fn, n_pairs=10)

# Save/load
strategy.save_checkpoint('model.pkl')
strategy.load_checkpoint('model.pkl')
```

#### Session Manager

```python
from backend.session_manager import SessionManager

manager = SessionManager('data/sessions')

# Create session
session_id = manager.create_session({'period': 'bronze_age'})

# Save session
session = {'preferences': [...], 'iteration': 1}
manager.save_session(session_id, session)

# Load session
session = manager.load_session(session_id)

# List sessions
sessions = manager.list_sessions()
infos = manager.list_sessions_info()

# Auto-backup (every N comparisons)
session['total_comparisons'] = 10
if manager.auto_backup(session, n=5):
    print("Backup created!")
```

## Configuration Options

### GP Strategy

```python
config = {
    'max_epochs': 100,        # Max training epochs
    'patience': 10,           # Early stopping patience
    'batch_size': 32,         # Training batch size
    'num_inducing': 64,       # Number of inducing points
    'learning_rate': 0.01,    # Learning rate
    'device': 'cpu',          # 'cpu' or 'cuda'
}
```

### Acquisition Functions

```python
# Random
acq_fn = get_acquisition('random')

# Thompson Sampling
acq_fn = get_acquisition('thompson_sampling')

# UCB (Upper Confidence Bound)
acq_fn = get_acquisition('ucb', beta=2.0)  # Higher beta = more exploration

# EI (Expected Improvement)
acq_fn = get_acquisition('ei', xi=0.01)    # Higher xi = more exploration

# Variance
acq_fn = get_acquisition('variance')
```

### Active Learning Loop

```python
config = {
    'max_iterations': 100,
    'n_pairs_per_iteration': 10,
    'acquisition': 'thompson_sampling',
    'convergence_window': 5,       # Window for stability check
    'convergence_threshold': 4,    # Min agreements for convergence
    'top_k': 5,                    # Top-K to check for convergence
    'sessions_dir': 'data/sessions',
    'max_epochs': 100,             # Passed to GP strategy
    'patience': 10,                # Passed to GP strategy
}
```

## Common Patterns

### Loading LAMAP Results

```python
import numpy as np
from pathlib import Path

# Load masks from LAMAP results
lamap_dir = Path('../lamap_results/bronze_age')
mask_files = sorted(lamap_dir.glob('*.npy'))  # Adjust pattern as needed

masks = [np.load(f) for f in mask_files]

# Run active learning
loop = ActiveLearningLoop(masks, config)
```

### Saving Results

```python
# Save ranking
np.save('ranking.npy', ranking)
np.save('scores.npy', scores)

# Save best masks
best_indices = ranking[:10]
best_masks = [masks[i] for i in best_indices]
np.save('best_masks.npy', np.array(best_masks))
```

### Resuming from Session

```python
# Create new loop with same config
loop2 = ActiveLearningLoop(masks, config)

# Load existing session
loop2.load_session('session_20260129_130000')

# Continue active learning
while not loop2.has_converged():
    pairs = loop2.get_next_batch()
    preferences = [get_preference(i, j) for i, j in pairs]
    loop2.add_preferences(pairs, preferences)
```

## Data Formats

### Preferences

List of tuples: `[((i, j), pref), ...]`

- `i, j`: Mask indices
- `pref`: 0 or 1 (binary preference)
- Ties (0.5, None) are skipped during training

Example:
```python
preferences = [
    ((0, 1), 1),   # Mask 0 preferred over mask 1
    ((1, 2), 0),   # Mask 2 preferred over mask 1
    ((2, 3), 1),   # Mask 2 preferred over mask 3
]
```

### Features

Numpy array of shape `(n_masks, n_features)`:

```python
# Handcrafted encoder: (n_masks, 5)
features = encoder.encode_batch(masks)
# features.shape = (100, 5)
```

### Ranking

Numpy array of indices sorted by preference:

```python
ranking, scores = loop.get_ranking()

# Best mask
best_idx = ranking[0]
best_mask = masks[best_idx]
best_score = scores[best_idx]

# Top-K
top_k_indices = ranking[:5]
top_k_masks = [masks[i] for i in top_k_indices]
```

## Troubleshooting

### Import Errors

```python
# Use direct imports, not package imports
from backend.strategies.gp_strategy import GPStrategy  # ✓
from backend import GPStrategy  # ✗ (won't work)

from encoders.registry import get_encoder  # ✓
from encoders import get_encoder  # ✗ (won't work)
```

### Model Not Trained

```python
# Always train before getting ranking
strategy.train(preferences, features, scaler)
ranking, scores = strategy.get_ranking(features, scaler)

# Or use active learning loop
loop.add_preferences(pairs, preferences)  # Trains automatically
ranking, scores = loop.get_ranking()
```

### Convergence Issues

If not converging:
1. Increase `max_iterations`
2. Decrease `convergence_threshold`
3. Increase `n_pairs_per_iteration`
4. Try different acquisition function
5. Check preference data quality

### Memory Issues

For large datasets:
1. Reduce `num_inducing` (default: 64)
2. Reduce `batch_size` (default: 32)
3. Process masks in batches
4. Use incremental training

## Testing

Run tests to verify installation:

```bash
python test_implementation.py
```

Expected output:
```
✓ All tests passed!
```

## Streamlit Webapp UI

### Quick Start

```bash
# Run the Streamlit app
streamlit run app.py

# App will open at http://localhost:8501
```

### Workflow

1. **Configuration Page**
   - Set LAMAP results directory path
   - Select period (bronze_age, byzantine, etc.)
   - Choose decision mode (Human Expert or Virtual Oracle)
   - Configure learning parameters
   - Click "Start Session"

2. **Collect Page**
   - View pairs of masks side-by-side
   - Click preference buttons: Left Better, Right Better, or Tie
   - Skip difficult pairs for later review
   - Submit batch when complete to trigger training

3. **Training Page**
   - Watch training progress
   - View metrics and logs
   - Navigate to results when complete

4. **Results Page**
   - View ranking table with scores
   - Click rows to inspect masks
   - Export preferences (CSV/JSON)
   - Start new session or continue collecting

### Decision Modes

**Human Expert Mode:**
- You manually compare masks
- Provides expert feedback
- Best for high-quality data

**Virtual Oracle Mode:**
- Automatic preference generation
- Configurable biases (compactness, spatial autocorrelation, etc.)
- Adjustable noise level
- Good for testing and simulation

### Configuration

**Basic Settings:**
- Max Comparisons: Total number of comparisons (default: 100)
- Batch Size: Comparisons per batch (default: 10)

**Advanced Settings:**
- Max Epochs: GP training epochs (default: 100)
- Learning Rate: Optimization learning rate (default: 0.01)
- Convergence Window: Iterations to check stability (default: 5)
- Convergence Threshold: Agreements needed (default: 4)

**Acquisition Functions:**
- `thompson_sampling` - Bayesian exploration
- `random` - Random selection
- `ucb` - Upper Confidence Bound
- `ei` - Expected Improvement
- `variance` - High variance selection

### Session Management

Sessions are automatically saved to `data/sessions/`:
- Auto-save every batch
- Manual save with "Save Progress" button
- Load existing sessions (coming soon)
- Export preferences and rankings

### Troubleshooting UI

**Issue:** "No active session"
- Go to Configuration page and start a new session

**Issue:** "No mask files found"
- Check LAMAP results directory path
- Ensure period folder contains PNG/TIF files

**Issue:** "Model not trained"
- Collect at least one batch of preferences
- Submit batch to trigger training

## Next Steps

1. Test with real LAMAP data
2. Tune hyperparameters for your use case
3. Implement custom acquisition functions
4. Add visualization components
5. Integrate with existing workflows

See `IMPLEMENTATION_SUMMARY.md` for detailed documentation and `ui/README.md` for UI details.
