# Developer Guide: Preference Learning Webapp

This guide explains how to extend and modify the Preference Learning Webapp.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Adding New Features](#adding-new-features)
3. [Plugin System](#plugin-system)
4. [Code Organization](#code-organization)
5. [Testing](#testing)
6. [Debugging](#debugging)
7. [Contributing](#contributing)

---

## Architecture Overview

### Design Principles

1. **Separation of Concerns**: Backend (business logic) vs Frontend (UI)
2. **Plugin Architecture**: All major components are pluggable via registries
3. **No Streamlit in Backend**: Backend modules must NOT import streamlit
4. **State Management**: Use SessionManager for persistence, st.session_state for UI state

### Directory Structure

```
preference_webapp/
├── backend/              # Business logic (NO Streamlit imports)
│   ├── core/            # Base classes and registries
│   ├── strategies/      # Learning algorithms
│   ├── oracles/         # Virtual decision makers
│   ├── session_manager.py
│   ├── active_learning_loop.py
│   └── model_manager.py
├── encoders/            # Feature encoders
├── acquisition/         # Acquisition functions
├── ui/                  # Streamlit UI (Streamlit-specific code)
│   ├── components.py    # Reusable UI components
│   ├── utils.py         # UI helpers
│   └── pages/           # Page rendering logic
└── app.py              # Main application entry point
```

### Data Flow

```
1. LAMAP GeoTIFF files
   ↓ (LAMAPImageLoader)
2. Binary masks + metadata
   ↓ (SegmentationFeatureEncoder)
3. Raw features (5D spatial)
   ↓ (StandardScaler)
4. Scaled features
   ↓ (AcquisitionSelector)
5. Selected pairs (i, j)
   ↓ (UI: collect.py)
6. Human preferences
   ↓ (ActiveLearningLoop.add_preferences)
7. Retrain GP (ModelManager)
   ↓ (copeland_score)
8. Rankings → Display
```

---

## Adding New Features

### How to Add a New Acquisition Function

Acquisition functions select which pairs to query during active learning.

**Step 1**: Create new acquisition function

```python
# acquisition/custom/my_acquisition.py
from backend.core.base_acquisition import AcquisitionFunction
from acquisition.registry import register_acquisition
import numpy as np

@register_acquisition('my_custom_acquisition')
class MyCustomAcquisition(AcquisitionFunction):
    """My custom acquisition strategy."""

    def __init__(self, param1=1.0, param2=0.5):
        super().__init__("My Custom Acquisition")
        self.param1 = param1
        self.param2 = param2

    def acquire(self, model, likelihood, candidates, features, n_pairs=1, **kwargs):
        """
        Select pairs to query.

        Args:
            model: Trained GP model
            likelihood: Bernoulli likelihood
            candidates: List of candidate indices
            features: Feature matrix (n_candidates, n_features)
            n_pairs: Number of pairs to select

        Returns:
            List of (i, j) tuples
        """
        # Your custom logic here
        # Example: Select pairs with highest feature variance

        pairs = []
        for _ in range(n_pairs):
            # Compute some score for each candidate
            scores = np.var(features[candidates], axis=1)

            # Select top 2
            top_indices = np.argsort(-scores)[:2]
            i, j = candidates[top_indices[0]], candidates[top_indices[1]]
            pairs.append((int(i), int(j)))

        return pairs
```

**Step 2**: Import to register (or use auto-discovery)

```python
# acquisition/custom/__init__.py
from .my_acquisition import MyCustomAcquisition
```

**Step 3**: Use in UI (auto-discovered)

Your acquisition function will automatically appear in the config page dropdown!

---

### How to Add a New Learning Strategy

Learning strategies define how to train models and compute rankings.

**Step 1**: Create strategy class

```python
# backend/strategies/my_strategy.py
from backend.core.base_strategy import LearningStrategy
from backend.strategies.registry import register_strategy
import numpy as np

@register_strategy('my_custom_strategy')
class MyCustomStrategy(LearningStrategy):
    """My custom learning strategy."""

    def __init__(self, config: dict):
        super().__init__(config)
        self.hyperparam = config.get('hyperparam', 1.0)

    def train(self, preferences, features, scaler=None):
        """
        Train model on preferences.

        Args:
            preferences: List of ((i, j), preference) tuples
            features: Feature matrix (n_masks, n_features)
            scaler: Optional scaler

        Returns:
            (model, likelihood) tuple
        """
        # Your training logic here
        # Example: Simple linear model

        # Prepare training data
        X = []
        y = []
        for (i, j), pref in preferences:
            X.append(features[i] - features[j])  # Difference vector
            y.append(pref)

        X = np.array(X)
        y = np.array(y)

        # Train your model
        # ... (your training code)

        self.model = your_model
        self.likelihood = your_likelihood

        return self.model, self.likelihood

    def get_ranking(self, features, scaler=None):
        """
        Compute ranking from trained model.

        Args:
            features: Feature matrix (n_masks, n_features)
            scaler: Optional scaler

        Returns:
            (ranking, scores) tuple
        """
        # Compute scores for each mask
        scores = self.model.compute_scores(features)

        # Sort by score (descending)
        ranking = np.argsort(-scores)

        return ranking, scores

    def select_pairs(self, features, acquisition_fn, n_pairs=10, **kwargs):
        """
        Select pairs for next query.

        Args:
            features: Feature matrix
            acquisition_fn: Acquisition function
            n_pairs: Number of pairs

        Returns:
            List of (i, j) tuples
        """
        # Use acquisition function
        candidates = list(range(len(features)))
        pairs = acquisition_fn.acquire(
            self.model,
            self.likelihood,
            candidates,
            features,
            n_pairs=n_pairs
        )
        return pairs

    def save_checkpoint(self, path):
        """Save model checkpoint."""
        import torch
        torch.save({
            'model': self.model.state_dict(),
            'config': self.config
        }, path)

    def load_checkpoint(self, path):
        """Load model checkpoint."""
        import torch
        checkpoint = torch.load(path)
        self.model.load_state_dict(checkpoint['model'])
        self.config = checkpoint['config']
```

**Step 2**: Import to register

```python
# backend/strategies/__init__.py
from .my_strategy import MyCustomStrategy
```

**Step 3**: Appears in UI automatically!

---

### How to Add a New Oracle

Oracles provide automated preferences for testing.

**Step 1**: Create oracle class

```python
# backend/oracles/my_oracle.py
from backend.core.base_oracle import BaseOracle
from backend.oracles.registry import register_oracle
import numpy as np

@register_oracle('my_custom_oracle')
class MyCustomOracle(BaseOracle):
    """My custom virtual decision maker."""

    def __init__(self, my_param=1.0, name="My Custom Oracle"):
        super().__init__(name)
        self.my_param = my_param

    def prefer(self, mask_a, mask_b):
        """
        Return preference between two masks.

        Args:
            mask_a: First segmentation mask
            mask_b: Second segmentation mask

        Returns:
            True if mask_a preferred, False otherwise
        """
        # Compute utility scores
        score_a = self._compute_utility(mask_a)
        score_b = self._compute_utility(mask_b)

        # Add some noise
        noise = np.random.randn() * 0.1
        return (score_a - score_b + noise) > 0

    def _compute_utility(self, mask):
        """Compute utility score for a mask."""
        # Your custom utility function
        # Example: prefer masks with more pixels
        return mask.sum()

    def set_bias(self, feature_name, value):
        """Adjust bias (if applicable)."""
        # Optional: implement if your oracle supports bias adjustment
        pass

    def get_biases(self):
        """Get current biases."""
        # Optional: return current bias configuration
        return {}

    def rank_masks(self, masks):
        """Get ground truth ranking."""
        utilities = [self._compute_utility(m) for m in masks]
        return np.argsort(-np.array(utilities))
```

**Step 2**: Import to register

```python
# backend/oracles/__init__.py
from .my_oracle import MyCustomOracle
```

**Step 3**: Appears in UI dropdown!

---

### How to Add a New Encoder

Encoders transform masks into feature vectors.

**Step 1**: Create encoder class

```python
# encoders/my_encoder.py
from backend.core.base_encoder import BaseEncoder
from encoders.registry import register_encoder
import numpy as np

@register_encoder('my_custom_encoder')
class MyCustomEncoder(BaseEncoder):
    """My custom feature encoder."""

    def __init__(self, feature_dim=10, name="My Custom Encoder"):
        super().__init__(name)
        self.feature_dim = feature_dim

    def encode(self, mask):
        """
        Encode mask into feature vector.

        Args:
            mask: Binary segmentation mask (2D numpy array)

        Returns:
            Feature vector (1D numpy array)
        """
        # Extract features
        features = []

        # Example: simple statistics
        features.append(mask.sum())  # Total pixels
        features.append(mask.mean())  # Mean value
        features.append(mask.std())   # Standard deviation
        # ... add more features

        # Pad/truncate to feature_dim
        features = np.array(features[:self.feature_dim])
        if len(features) < self.feature_dim:
            features = np.pad(features, (0, self.feature_dim - len(features)))

        return features

    def dim(self):
        """Return feature dimension."""
        return self.feature_dim
```

**Step 2**: Import to register

```python
# encoders/__init__.py
from .my_encoder import MyCustomEncoder
```

**Step 3**: Select in config page!

---

## Plugin System

### Registry Pattern

All plugins use the registry pattern for extensibility:

```python
from backend.core.registry import Registry

class MyPluginRegistry(Registry[MyPluginType]):
    def __init__(self):
        super().__init__("MyPlugin")

# Global instance
my_plugin_registry = MyPluginRegistry()

# Decorator for registration
def register_my_plugin(name: str):
    return my_plugin_registry.register(name)
```

### Registering Plugins

```python
@register_my_plugin('my_plugin')
class MyPlugin(BasePlugin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize
```

### Using Plugins

```python
# Get plugin instance
plugin = my_plugin_registry.get('my_plugin', param1=value1)

# List available plugins
available = my_plugin_registry.list_available()

# Check if registered
if my_plugin_registry.is_registered('my_plugin'):
    # Use it
    pass
```

---

## Code Organization

### Backend (No Streamlit)

**Rule**: Backend modules must NOT import streamlit.

**Purpose**: Business logic, model training, data processing.

**Files**:
- `backend/core/`: Base classes and registries
- `backend/strategies/`: Learning algorithms
- `backend/oracles/`: Virtual decision makers
- `backend/session_manager.py`: Session persistence
- `backend/active_learning_loop.py`: PBO orchestration
- `backend/model_manager.py`: GP training

**Example**:
```python
# backend/my_module.py
# ❌ WRONG: Imports streamlit
import streamlit as st

# ✅ CORRECT: No streamlit imports
import numpy as np
from sklearn.preprocessing import StandardScaler

class MyBackendClass:
    def process_data(self, data):
        return np.array(data)
```

### Frontend (Streamlit-specific)

**Purpose**: UI rendering, user interaction, display.

**Files**:
- `app.py`: Main application
- `ui/components.py`: Reusable UI components
- `ui/utils.py`: UI helpers
- `ui/pages/`: Page rendering logic

**Example**:
```python
# ui/pages/my_page.py
import streamlit as st
import sys
sys.path.append('..')
from backend.my_module import MyBackendClass

def show_my_page():
    st.title("My Page")

    # Use backend
    backend = MyBackendClass()
    result = backend.process_data(data)

    # Display result
    st.write(result)
```

---

## Testing

### Unit Tests

Test individual components:

```python
# tests/test_my_module.py
import pytest
from backend.my_module import MyBackendClass

def test_my_backend_class():
    backend = MyBackendClass()
    data = [1, 2, 3]
    result = backend.process_data(data)
    assert len(result) == 3
```

Run tests:
```bash
pytest tests/unit/
```

### Integration Tests

Test complete workflows:

```python
# tests/integration/test_full_workflow.py
def test_full_workflow():
    # Create session
    manager = SessionManager()
    session_id = manager.create_session({...})

    # Run active learning
    al_loop = ActiveLearningLoop(masks, config)
    pairs = al_loop.get_next_batch(n_pairs=10)
    prefs = [1] * 10
    al_loop.add_preferences(pairs, prefs)

    # Check ranking
    ranking, scores = al_loop.get_ranking()
    assert len(ranking) == len(masks)
```

Run tests:
```bash
pytest tests/integration/
```

### UI Tests

Test UI components:

```python
# tests/test_ui_components.py
from ui.components import display_side_by_side_images
import numpy as np

def test_display_component():
    mask_a = np.random.randint(0, 2, (64, 64))
    mask_b = np.random.randint(0, 2, (64, 64))
    # Display (needs Streamlit context)
    display_side_by_side_images(mask_a, mask_b)
```

---

## Debugging

### Enable Debug Mode

Add to `app.py`:

```python
# Enable debug mode
DEBUG = True

if DEBUG:
    import logging
    logging.basicConfig(level=logging.DEBUG)
```

### Use Print Statements

```python
# In backend
print(f"DEBUG: features shape = {features.shape}")

# In UI
st.write(f"DEBUG: current_step = {st.session_state.current_step}")
```

### Check Session State

```python
# In UI
import streamlit as st

if st.sidebar.checkbox("Show Debug Info"):
    st.json(st.session_state)
```

### Use Python Debugger

```python
# In backend
import pdb; pdb.set_trace()

# Or use breakpoint() (Python 3.7+)
breakpoint()
```

### Streamlit Debugging

```python
# Use st.write to inspect objects
st.write(variable)

# Use st.json for structured data
st.json({"key": "value"})

# Use st.exception for errors
try:
    risky_operation()
except Exception as e:
    st.exception(e)
```

---

## Contributing

### Code Style

- Use **black** for formatting: `black .`
- Use **flake8** for linting: `flake8 .`
- Use **mypy** for type checking: `mypy .`

### Commit Messages

Format: `<type>: <description>`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `style`: Style changes
- `chore`: Maintenance

Examples:
- `feat: add custom acquisition function`
- `fix: correct feature scaling bug`
- `docs: update developer guide`

### Pull Request Process

1. Fork repository
2. Create branch: `git checkout -b feature/my-feature`
3. Make changes
4. Run tests: `pytest tests/`
5. Commit: `git commit -m "feat: add my feature"`
6. Push: `git push origin feature/my-feature`
7. Open pull request

### Adding Tests

For every new feature:
1. Add unit tests in `tests/unit/`
2. Add integration tests in `tests/integration/`
3. Ensure all tests pass
4. Add docstrings

Example:
```python
# tests/unit/test_my_feature.py
import pytest
from backend.my_feature import MyFeature

def test_my_feature_basic():
    feature = MyFeature()
    result = feature.do_something()
    assert result is not None

def test_my_feature_edge_case():
    feature = MyFeature()
    result = feature.do_something(edge_case=True)
    assert result == expected_value
```

---

## Best Practices

### 1. Keep Backend Streamlit-Free

**❌ Wrong**:
```python
# backend/session_manager.py
import streamlit as st

def save_session(session):
    st.write("Saving...")
```

**✅ Correct**:
```python
# backend/session_manager.py
import logging

def save_session(session):
    logging.info("Saving session...")
```

### 2. Use Type Hints

```python
def process_data(
    data: np.ndarray,
    config: dict
) -> Tuple[np.ndarray, dict]:
    """Process data and return result and metadata."""
    result = data * 2
    metadata = {"processed": True}
    return result, metadata
```

### 3. Add Docstrings

```python
class MyClass:
    """Brief description.

    Longer description if needed.

    Attributes:
        attr1: Description
        attr2: Description
    """

    def my_method(self, param1: str, param2: int) -> bool:
        """Brief description.

        Args:
            param1: Description
            param2: Description

        Returns:
            Description

        Raises:
            ValueError: When something goes wrong
        """
        pass
```

### 4. Handle Errors Gracefully

```python
def risky_operation():
    try:
        result = do_something_risky()
        return result
    except ValueError as e:
        logging.error(f"Value error: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise
```

### 5. Use Logging

```python
import logging

logger = logging.getLogger(__name__)

def my_function():
    logger.info("Starting function")
    logger.debug(f"Processing data: {data}")
    logger.warning("This is unusual")
    logger.error("Something went wrong")
```

---

## Resources

### Documentation

- [Streamlit Docs](https://docs.streamlit.io/)
- [GPyTorch Docs](https://docs.gpytorch.ai/)
- [PyTorch Lightning Docs](https://pytorch-lightning.readthedocs.io/)

### Code References

- `models/toy_gp.py`: GP model implementation
- `modules/toy_module.py`: Lightning training module
- `acquisition/acquisition.py`: Acquisition functions
- `metrics/copeland_score.py`: Copeland score computation

### Examples

- `notebooks/webapp_tutorial.ipynb`: Tutorial notebook
- `configs/examples/`: Example configurations
- `tests/`: Test examples

---

Happy coding! 🚀
