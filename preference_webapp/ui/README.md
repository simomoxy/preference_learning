# Preference Learning Webapp - UI Implementation

Complete Streamlit UI for the preference learning webapp with multi-page navigation and interactive components.

## Architecture

### Main Application (`app.py`)

**Multi-page navigation** with session state management:
- Pages: config, collect, train, results
- Session state initialization
- Sidebar with session info and navigation
- Consistent styling across pages

### UI Components (`ui/components.py`)

**Reusable UI components:**

- `display_side_by_side_images(mask_a, mask_b, metadata_a, metadata_b)` - Display two masks side by side
- `display_single_image(mask, title, metadata)` - Display single mask with title
- `preference_buttons()` - Three buttons: "Left Better", "Right Better", "Tie", plus "Skip" button
- `progress_bar(current, total, show_text)` - Progress bar with text
- `metrics_plot(ranking, scores, title, top_k)` - Bar chart with Plotly
- `session_info_sidebar(session)` - Display session info in sidebar
- `ranking_table(ranking, scores, metadata, key)` - Interactive ranking table
- `acquisition_history_plot(history)` - Plot acquisition history
- `learning_curves_plot(history)` - Plot learning curves
- `export_buttons(session, masks)` - Export buttons for session data

### UI Utilities (`ui/utils.py`)

**Utility functions:**

- `safe_execute(func, error_message, st_context)` - Execute function with error handling
- `format_timestamp(timestamp)` - Format timestamp for display
- `get_session_summary(session)` - Get session summary dict
- `validate_config(config)` - Validate configuration
- `load_lamap_masks(lamap_results_dir, period)` - Load LAMAP masks from directory
- `display_error_boundary(title)` - Decorator for error handling
- `format_elapsed_time(seconds)` - Format elapsed time
- `estimate_time_remaining(elapsed, current, total)` - Estimate remaining time
- `create_comparison_summary(preferences)` - Create summary statistics
- `display_loading_spinner(message, func)` - Display loading spinner

## Pages

### 1. Configuration Page (`ui/pages/config.py`)

**Features:**
- Data source selection: lamap_results directory path
- Period selection dropdown (bronze_age, byzantine, etc.)
- Learning strategy: GP only initially
- Acquisition function dropdown (auto-discovered from registry)
- Encoder selection: handcrafted initially
- Decision mode: Human Expert vs Virtual Oracle
- Virtual Oracle configuration:
  - Oracle type dropdown (Biased, Random, Custom)
  - Feature biases for Biased oracle (compactness, morans_i, components, area, perimeter_ratio)
  - Noise slider
- Settings:
  - Max comparisons (slider or number input, default 100)
  - Batch size (slider, default 10)
- Advanced Settings expander:
  - GP hyperparameters (max_epochs, learning_rate, patience)
  - Convergence parameters (window, threshold, top_k)
- "Start Session" button
- Configuration summary

**State management:**
- Stores config in `st.session_state.config`
- Loads masks and metadata into session state
- Initializes `ActiveLearningLoop`
- Creates session and saves to disk
- Navigates to collect page on start

### 2. Data Collection Page (`ui/pages/collect.py`)

**Features:**
- Progress display:
  - Progress bar: "X pairs collected out of Y max"
  - Batch counter: "A/B pairs in current batch"
  - Metrics: Total Comparisons, Iteration
- Side-by-side image display for current pair
- Metadata display below images (site ID, period, etc.)
- Three preference buttons: "⬅️ Left Better", "➡️ Right Better", "🤝 Tie"
- "⏭️ Skip" button (adds to review queue)
- Store preferences in `batch_preferences` dict
- "Submit Batch" button (only appears when batch complete):
  - Triggers training
  - Navigates to train page
- "Save Progress" button (manual backup)
- Auto-save every N comparisons (handled by backend)

**State management:**
- `current_batch` - List of pairs to compare
- `batch_preferences` - Dict of completed preferences
- `batch_count` - Number of batches completed
- `total_comparisons` - Total comparisons across all batches
- `review_queue` - List of skipped pairs

**Oracle mode:**
- Automatically generates preferences using virtual oracle
- Shows oracle decision after generation
- Auto-advances to next pair

### 3. Training Page (`ui/pages/train.py`)

**Features:**
- Display spinner: "Training model..."
- Show iteration counter: "Iteration X/Y"
- Show estimated time remaining
- Configuration expander (show training parameters)
- Progress bar with metrics
- Optional: Logs expander (show ELBO loss, etc.)
- Navigation buttons:
  - "View Results" - Compute ranking and navigate to results
  - "Continue Collecting" - Navigate back to collect page
- Session summary (statistics, model info, top-K)

**Implementation:**
- Currently simulates training with progress updates
- In production, would run actual GP training
- Saves checkpoint after training
- Computes ranking and scores

### 4. Results Page (`ui/pages/results.py`)

**Features:**
- Ranking table:
  - Columns: Rank, Mask ID, Copeland Score, metadata fields
  - Sortable by clicking headers
  - Click row to show enlarged preview
- Selected mask preview:
  - Large mask display
  - Statistics (rank, score, metadata)
  - Contributing pairs (which masks were compared)
  - Detailed mask statistics (area, perimeter, components)
- Metrics plots (interactive Plotly):
  - Copeland scores bar chart (top-K filter)
  - Learning curves
  - Acquisition history
- Export buttons:
  - "Save Session" (backup)
  - "Export Preferences (CSV)"
  - "Export Preferences (JSON)"
  - "New Session" (reset to config)

**Interactive features:**
- Click table row to view mask details
- Adjust top-K filter for plots
- Download preferences as CSV/JSON
- Save session checkpoint

## Running the Application

### Start the app:

```bash
cd preference_webapp
streamlit run app.py
```

### Default URL:
```
http://localhost:8501
```

### Configuration:
- Make sure LAMAP results are available in `lamap_results/` directory
- Select period and configure settings in Configuration page
- Click "Start Session" to begin

### Workflow:
1. **Configuration** - Set up session parameters and load data
2. **Collect** - Compare mask pairs and provide preferences
3. **Train** - Train model on collected preferences
4. **Results** - View ranking and analysis

## Session State Structure

```python
# Core session state
st.session_state.current_page  # Current page name
st.session_state.session_id    # Session identifier
st.session_state.config        # Configuration dict

# Data collection state
st.session_state.current_batch        # List of pairs
st.session_state.batch_preferences    # Dict of preferences
st.session_state.batch_count          # Batch counter
st.session_state.total_comparisons    # Total comparisons
st.session_state.review_queue         # Skipped pairs

# Backend components
st.session_state.active_learning_loop  # ActiveLearningLoop instance
st.session_state.masks                 # List of masks
st.session_state.mask_metadata         # List of metadata

# Training state
st.session_state.training_progress     # Training metrics
st.session_state.training_logs         # Training logs

# Results state
st.session_state.ranking              # Ranking array
st.session_state.scores               # Scores array
st.session_state.selected_mask_idx    # Selected mask

# UI state
st.session_state.auto_save_enabled    # Auto-save flag
st.session_state.last_save_time       # Last save timestamp
```

## Error Handling

All pages include comprehensive error handling:
- Try-catch blocks around backend operations
- User-friendly error messages
- Logging to console
- Graceful degradation

## Integration with Backend

The UI integrates seamlessly with backend components:
- `ActiveLearningLoop` - Main learning loop
- `SessionManager` - Session persistence
- `GPStrategy` - GP learning strategy
- `AcquisitionRegistry` - Acquisition functions
- `OracleRegistry` - Virtual oracles
- `HandcraftedEncoder` - Feature encoder

## Future Enhancements

Potential improvements:
1. Real-time training progress (async/threading)
2. Review queue management page
3. Multi-objective optimization visualization
4. Parallel batch collection
5. Advanced filtering and search in results
6. Export rankings with confidence intervals
7. Interactive mask comparison (overlay mode)
8. Session comparison and merging
9. Advanced analytics dashboard
10. Export model predictions

## Troubleshooting

**Issue:** "No active session" error
- **Solution:** Go to Configuration page and start a new session

**Issue:** "No mask files found" error
- **Solution:** Check that lamap_results_dir is correct and contains PNG/TIF files

**Issue:** "Model not trained" error
- **Solution:** Collect at least one batch of preferences before viewing results

**Issue:** Import errors
- **Solution:** Make sure you're running from `preference_webapp/` directory

**Issue:** Streamlit not found
- **Solution:** Install requirements: `pip install -r requirements.txt`
