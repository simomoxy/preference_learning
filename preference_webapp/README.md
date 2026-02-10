# Preference Learning Webapp

A research-focused web application for preferential Bayesian optimization (PBO) of archaeological image segmentation. Experts compare image pairs pairwise, and the system learns preferences via Gaussian Process-based PBO to produce Copeland score rankings.

## Features

- **Interactive Pairwise Comparison**: Side-by-side image comparison with intuitive controls
- **Gaussian Process PBO**: State-of-the-art preference learning with GP models
- **Virtual Oracles**: Simulation mode with adjustable biases for testing
- **Multiple Acquisition Functions**: Thompson Sampling, UCB, EI, Random, and more
- **Multi-Objective Optimization**: Support for scalarization methods (future)
- **Session Persistence**: Save and load sessions for reproducibility
- **Export Options**: CSV, JSON for research publications

## Quick Start

### 1. Setup

```bash
# Navigate to project root
cd /path/to/preference_learning

# Activate conda environment
conda activate .conda

# Install Streamlit (if not already installed)
pip install streamlit plotly

# Navigate to webapp directory
cd preference_webapp
```

### 2. Run the Application

```bash
streamlit run app.py
```

The application will open at `http://localhost:8501`

### 3. Workflow

1. **Configure Session** (Step 1)
   - Select LAMAP data source (directory with GeoTIFF files)
   - Choose period (bronze_age, byzantine, etc.)
   - Select acquisition function (Thompson Sampling recommended)
   - Choose: Human Expert mode or Virtual Oracle (simulation)
   - Set max comparisons (e.g., 100) and batch size (e.g., 10)

2. **Collect Preferences** (Step 2)
   - Compare image pairs side-by-side
   - Click "⬅️ Left Better", "➡️ Right Better", or "🤝 Tie"
   - Click "⏭️ Skip" to review later
   - Submit batch when complete (triggers training)

3. **Train Model** (Step 3)
   - Watch training progress
   - View ELBO loss and metrics
   - Automatic checkpoint saving

4. **View Results** (Step 4)
   - See ranking table with Copeland scores
   - View selected image previews
   - Explore interactive plots
   - Export data (CSV/JSON)

## Project Structure

```
preference_webapp/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── backend/                        # Core backend logic (no Streamlit)
│   ├── core/                       # Base classes and registries
│   │   ├── registry.py             # Plugin registry system
│   │   ├── base_strategy.py        # Learning strategy ABC
│   │   ├── base_acquisition.py     # Acquisition function ABC
│   │   ├── base_oracle.py          # Oracle ABC
│   │   └── base_encoder.py         # Encoder ABC
│   ├── strategies/                 # Learning algorithms
│   │   └── gp_strategy.py          # Gaussian Process PBO
│   ├── oracles/                    # Virtual decision makers
│   │   ├── biased_oracle.py        # Interactive biased oracle
│   │   ├── random_oracle.py        # Random baseline
│   │   ├── custom_oracle.py        # User-defined oracle
│   │   └── registry.py             # Oracle registry
│   ├── session_manager.py          # Session persistence
│   ├── active_learning_loop.py     # PBO orchestration
│   └── model_manager.py            # GP training wrapper
├── encoders/                       # Feature encoders
│   ├── handcrafted_encoder.py      # Spatial features (Moran's I, etc.)
│   └── registry.py                 # Encoder registry
├── acquisition/                    # Acquisition functions
│   ├── acquisition.py              # All acquisition strategies
│   └── registry.py                 # Acquisition registry
├── ui/                             # Streamlit UI (UI-specific code)
│   ├── components.py               # Reusable UI components
│   ├── utils.py                    # UI utilities
│   └── pages/                      # Page rendering logic
│       ├── config.py               # Step 1: Configuration
│       ├── collect.py              # Step 2: Data collection
│       ├── train.py                # Step 3: Training display
│       └── results.py              # Step 4: Results & plots
└── data/                           # Data directory
    ├── sessions/                   # Saved sessions (pickle)
    ├── preferences/                # Exported preferences (CSV/JSON)
    └── checkpoints/                # Model checkpoints (PyTorch)
```

## Configuration Options

### Acquisition Functions

- **Thompson Sampling** (`thompson_sampling`): Sample from GP posterior, select uncertain pairs (recommended)
- **UCB** (`ucb`): Upper Confidence Bound, balance exploration/exploitation
- **EI** (`ei`): Expected Improvement
- **Random** (`random`): Random baseline
- **Variance** (`variance`): Pure exploration

### Decision Modes

#### Human Expert
Real expert preferences via UI. Requires manual pairwise comparisons.

#### Virtual Oracle (Simulation)
Automated preferences for testing and validation:

1. **Biased Oracle**: Adjustable feature biases
   - Compactness: Prefer circular regions (default: 2.0)
   - Moran's I: Prefer spatial autocorrelation (default: 1.5)
   - Components: Prefer fewer components (default: -1.0)
   - Area: Mean region area (default: 0.5)
   - Perimeter Ratio: Prefer lower ratios (default: -0.5)
   - Noise: Decision randomness (default: 0.3)

2. **Random Oracle**: Uniform random preferences (baseline)

3. **Custom Oracle**: User-defined utility function

## Using Real LAMAP Data

### Option 1: Use Existing LAMAP Results

If you have LAMAP outputs in `lamap_results/`:

1. In the Configuration page, select "Load from lamap_results/"
2. Choose period (e.g., bronze_age)
3. The app will load all GeoTIFF files from `lamap_results/{period}/`

### Option 2: Generate Sample Data

For testing without real LAMAP data:

```bash
cd preference_webapp
python generate_sample_data.py
```

This creates sample data in `lamap_results_sample/` with dummy masks.

## Session Management

Sessions are automatically saved with unique IDs:

```
Format: {period}_exp{N}_{YYYYMMDD}_{HHMMSS}
Example: bronze_age_exp1_20250129_130000
```

### Save/Load

- **Auto-save**: Every batch submission
- **Manual save**: "Save Progress" button in collect page
- **Auto-backup**: Every N comparisons (configurable)

### Session Data Structure

```python
{
    'session_id': 'bronze_age_exp1_20250129_130000',
    'config': {...},  # Configuration parameters
    'state': {
        'current_step': 2,  # 1=config, 2=collect, 3=train, 4=results
        'comparison_count': 23,
        'iteration': 2,
    },
    'model': {
        'checkpoint_path': '...',
        'scaler': StandardScaler object,
        'features': np.array,
    },
    'preferences': {
        'pairs': [(i, j, pref), ...],
        'skipped': [(i, j), ...],
    },
    'metadata': {
        'created_at': timestamp,
        'last_modified': timestamp,
    }
}
```

## Export Formats

### CSV (Human-readable)

```csv
timestamp,mask_i,mask_j,preference,note
2025-01-29T10:30:00,site_12_patch_3,site_15_patch_7,left,"Clearer boundaries"
```

### JSON (Machine-readable + Reproducibility)

```json
{
  "session_id": "bronze_age_exp1_20250129_130000",
  "config": {...},
  "preferences": [...],
  "rankings": {
    "copeland_scores": [0.87, 0.76, ...],
    "order": [12, 15, 3, ...]
  },
  "metadata": {...}
}
```

## Troubleshooting

### Issue: "No LAMAP data found"

**Solution**: Run `python generate_sample_data.py` to create sample data, or ensure your LAMAP results are in the correct directory structure.

### Issue: "ImportError: No module named 'streamlit'"

**Solution**: Activate conda environment and install Streamlit:
```bash
conda activate .conda
pip install streamlit plotly
```

### Issue: Training is slow

**Solution**: Reduce `max_epochs` in Advanced Settings (default: 20, try 5-10 for faster training).

### Issue: Out of memory

**Solution**: Reduce batch size or use fewer masks.

## Architecture

### Backend (No Streamlit)

- **SessionManager**: Session persistence (pickle)
- **ActiveLearningLoop**: PBO orchestration
- **ModelManager**: GP training with checkpoints
- **AcquisitionSelector**: Acquisition function wrapper
- **PreferenceStore**: Export functionality

### Frontend (Streamlit-specific)

- **app.py**: Navigation and routing
- **ui/pages/**: Page rendering logic
- **ui/components.py**: Reusable UI components
- **ui/utils.py**: UI helpers

### Plugin System

All components are pluggable via registries:

```python
# Add new acquisition function
@AcquisitionRegistry.register('my_acquisition')
class MyAcquisition(AcquisitionFunction):
    def acquire(self, ...):
        # Implementation
        pass

# Add new learning strategy
@StrategyRegistry.register('my_strategy')
class MyStrategy(LearningStrategy):
    def train(self, ...):
        # Implementation
        pass

# Add new oracle
@OracleRegistry.register('my_oracle')
class MyOracle(BaseOracle):
    def prefer(self, ...):
        # Implementation
        pass
```

## Citation

If you use this webapp for research, please cite:

```bibtex
@software{preference_learning_webapp,
  title = {Preference Learning Webapp for Archaeological Image Segmentation},
  author = {Your Name},
  year = {2025},
  url = {https://github.com/yourusername/preference_learning}
}
```

## License

[Your License Here]

## Contact

For questions or issues, please open a GitHub issue or contact [your email].

## Acknowledgments

- Built with Streamlit
- Uses GPyTorch for Gaussian Processes
- Powered by PyTorch Lightning
- Part of the LAMAP project for archaeological site prediction
