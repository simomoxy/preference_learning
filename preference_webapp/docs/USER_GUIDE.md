# User Guide: Preference Learning Webapp

This guide will walk you through using the Preference Learning Webapp for archaeological image segmentation.

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Step-by-Step Tutorial](#step-by-step-tutorial)
4. [Understanding the Results](#understanding-the-results)
5. [Advanced Features](#advanced-features)
6. [Tips and Best Practices](#tips-and-best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The Preference Learning Webapp helps you find the best segmentation masks from LAMAP (Locally Adaptive Multivariate Assemblage Probability) outputs through **pairwise comparisons**.

### What is Pairwise Comparison?

Instead of scoring each mask individually, you compare two masks side-by-side and choose which one is better. The system learns from these comparisons and ranks all masks accordingly.

### Key Concepts

- **Mask**: A binary segmentation image showing predicted archaeological sites
- **Pair**: Two masks shown side-by-side for comparison
- **Preference**: Your choice between the two masks (Left, Right, or Tie)
- **Batch**: A group of comparisons (default: 10) before model retrains
- **Iteration**: One complete cycle of compare → train → rank
- **Copeland Score**: A score representing how often a mask wins against others

---

## Getting Started

### Prerequisites

1. **LAMAP Results**: GeoTIFF files from LAMAP runs
2. **Python Environment**: Conda environment with required packages
3. **Web Browser**: Chrome, Firefox, or Safari

### Launch the Application

```bash
# Navigate to project directory
cd /path/to/preference_learning

# Activate conda environment
conda activate .conda

# Navigate to webapp
cd preference_webapp

# Run the app
streamlit run app.py
```

The application will open in your browser at: `http://localhost:8501`

---

## Step-by-Step Tutorial

### Step 1: Configure Your Session

When you first open the app, you'll see the **Configuration** page.

#### 1.1 Data Source

**Option A: Use Existing LAMAP Results**
- Click "Browse lamap_results/ directory"
- Navigate to your LAMAP output folder
- Select a period (e.g., `bronze_age`, `byzantine`)

**Option B: Use Sample Data**
- Click "Use sample data"
- The app will use pre-generated dummy masks

#### 1.2 Learning Strategy

- **Strategy**: GP (Gaussian Process) - only option currently
- **Acquisition Function**: How pairs are selected
  - **Thompson Sampling** (recommended): Balances exploration and exploitation
  - **Random**: Selects pairs randomly (baseline)
  - **UCB**: Upper Confidence Bound
  - **EI**: Expected Improvement

#### 1.3 Decision Mode

**Option A: Human Expert** (Real Preferences)
- You will manually compare each pair
- Best for real research and publication

**Option B: Virtual Oracle** (Simulation)
- Automated preferences for testing
- Useful for:
  - Testing the system
  - Validating algorithms
  - Experimenting with different preference patterns

If you select **Virtual Oracle**:
- **Oracle Type**: Biased Oracle (recommended)
- **Adjust Feature Biases** (sliders):
  - **Compactness**: Prefer circular regions (higher = more important)
  - **Moran's I**: Prefer spatial autocorrelation
  - **Components**: Prefer fewer connected components (negative = fewer is better)
  - **Area**: Mean region area
  - **Perimeter Ratio**: Prefer lower perimeter/area ratio
  - **Noise**: Randomness in decisions (0.0 = deterministic, 1.0 = very random)

#### 1.4 Session Settings

- **Max Comparisons**: Maximum number of comparisons (default: 100)
  - More comparisons = better rankings but more time
- **Batch Size**: Comparisons per training cycle (default: 10)
  - Smaller = more frequent training (slower overall)
  - Larger = less frequent training (faster overall)

#### 1.5 Advanced Settings ▶

Click to expand and adjust:
- **Max Epochs**: Training iterations (default: 20)
  - Lower = faster training (may underfit)
  - Higher = better fit (slower)
- **Learning Rate**: Usually leave as default (0.01)
- **GP Parameters**: Inducing points, kernel settings (usually leave as default)

#### 1.6 Start Session

Click the **"▶️ Start Session"** button to proceed.

---

### Step 2: Collect Preferences

You'll now see the **Data Collection** page with two images side-by-side.

#### 2.1 Understanding the Display

- **Left Image**: Mask A
- **Right Image**: Mask B
- **Metadata**: Site ID, period, and other info below each image

#### 2.2 Making Comparisons

For each pair, choose one of:

1. **⬅️ Left Better**: The left mask is preferred
2. **➡️ Right Better**: The right mask is preferred
3. **🤝 Tie**: Both masks are equally good
4. **⏭️ Skip**: Skip this pair (will be reviewed later)

#### 2.3 Progress Tracking

- **Progress Bar**: Shows how many comparisons you've made
- **Batch Counter**: "X/Y pairs in current batch"
  - When you complete Y pairs, the "Submit Batch" button appears
- **Iteration Counter**: Current iteration number

#### 2.4 Submitting Batches

When you complete a batch:
1. Click **"Submit Batch & Train Model"**
2. The system will:
   - Train the GP model on your preferences
   - Compute new rankings
   - Generate the next batch of pairs
3. You'll be redirected to the Training page

#### 2.5 Saving Progress

- **Auto-save**: Every 5 comparisons
- **Manual save**: Click **"Save Progress"** button
- Sessions are saved in `data/sessions/`

---

### Step 3: Training

The **Training** page shows the model training progress.

#### What Happens During Training?

1. **Feature Extraction**: Masks are encoded into feature vectors
2. **Model Training**: GP learns from your preferences
3. **Ranking Computation**: Copeland scores are calculated
4. **Checkpoint Save**: Model is saved for later use

#### Training Display

- **Progress Bar**: Shows training progress
- **Iteration Info**: Current iteration number
- **Loss Metrics**: ELBO loss (lower is better)
- **Estimated Time**: Time remaining

When training completes, you'll be redirected to the Results page.

---

### Step 4: View Results

The **Results** page shows the final rankings.

#### 4.1 Ranking Table

The table shows:
- **Rank**: Position in ranking (1 = best)
- **Image ID**: Identifier for the mask
- **Copeland Score**: Preference score (higher = better)
- **95% CI**: Confidence interval (if available)

**Interacting with the Table**:
- Click any row to see the enlarged mask
- Sort by clicking column headers
- Filter using the search box

#### 4.2 Selected Image Preview

When you click a row:
- Large display of the selected mask
- Feature statistics (Moran's I, components, etc.)
- Contributing pairs (which comparisons affected this ranking)

#### 4.3 Metrics Plots

**Copeland Scores**:
- Bar chart showing scores for all masks
- Error bars show uncertainty
- Higher bars = better masks

**Acquisition History**:
- Line chart showing pairs selected per iteration
- Helps understand learning progress

**Learning Curves**:
- Shows how rankings changed over iterations
- Helps assess convergence

#### 4.4 Export Options

Click the export buttons to save your results:

1. **Save Session**: Backup the entire session
2. **Export Preferences (CSV)**: Human-readable comparison data
3. **Export Preferences (JSON)**: Machine-readable with metadata
4. **Export Rankings**: Save ranking table
5. **New Session**: Start over with new configuration

---

## Understanding the Results

### Copeland Score

The Copeland score represents **how often a mask wins against others**.

- **Score = 1.0**: Wins against all other masks (best)
- **Score = 0.5**: Ties with all other masks (average)
- **Score = 0.0**: Loses against all other masks (worst)

### Ranking Stability

**Stable Ranking**: Top-K masks don't change over iterations
- Indicates convergence
- System has learned preferences well

**Unstable Ranking**: Rankings keep changing
- May need more comparisons
- Preferences may be inconsistent

### Confidence Intervals

**Narrow CI**: High confidence in ranking
**Wide CI**: Low confidence (need more data)

---

## Advanced Features

### Virtual Oracle Mode

Use virtual oracle to test algorithms without manual comparisons:

1. **Biased Oracle**: Simulates expert with known preferences
   - Adjust sliders to change preference patterns
   - Test if system learns correct preferences

2. **Random Oracle**: Random preferences (baseline)
   - Compare against biased oracle
   - Measure algorithm performance

3. **Custom Oracle**: Define your own utility function
   - For specific preference patterns
   - For validation experiments

### Convergence Detection

The system automatically detects convergence:
- **Top-K Stable**: Top 5 masks don't change for 3 iterations
- **Max Budget**: Reached max comparisons
- **Early Stopping**: Click "Finish Early" button

### Session Management

**Load Previous Session**:
- Sessions are saved in `data/sessions/`
- Use SessionManager to load:
  ```python
  from backend.session_manager import SessionManager
  manager = SessionManager()
  session = manager.load_session('session_id')
  ```

**Session Info**:
- Session ID: `{period}_exp{N}_{timestamp}`
- Created/Modified timestamps
- Total comparisons
- Current iteration

---

## Tips and Best Practices

### 1. Start Small

- Use **10-20 masks** for your first session
- Set **max comparisons = 20-30**
- Set **batch size = 5**
- This helps you understand the workflow quickly

### 2. Use Thompson Sampling

- Thompson Sampling is recommended for most use cases
- Balances exploring uncertain pairs with exploiting known preferences
- Leads to faster convergence

### 3. Be Consistent

- Use the same criteria for all comparisons
- If you prefer compact masks, always prefer compact masks
- Inconsistent preferences lead to unstable rankings

### 4. Skip When Unsure

- Use the **Skip** button if masks are very similar
- Skipped pairs are reviewed later
- Don't force a choice if you're unsure

### 5. Check Convergence

- Look at the learning curves
- If rankings are stable, you can stop early
- More comparisons don't always help

### 6. Export Regularly

- Export preferences after each batch
- Save sessions frequently
- Keep backups of important sessions

### 7. Use Virtual Oracle for Testing

- Test your workflow with virtual oracle first
- Verify the system learns known preferences
- Then switch to human expert mode for real data

---

## Troubleshooting

### Issue: "No LAMAP data found"

**Cause**: Data directory is empty or path is wrong

**Solutions**:
1. Check that `lamap_results/` exists and has GeoTIFF files
2. Use "Browse" to select the correct directory
3. Use sample data for testing: `python generate_sample_data.py`

### Issue: Training is very slow

**Solutions**:
1. Reduce `Max Epochs` in Advanced Settings (try 5-10)
2. Use fewer masks (subset of your data)
3. Increase batch size (fewer training cycles)

### Issue: Rankings keep changing

**Cause**: Not enough comparisons or inconsistent preferences

**Solutions**:
1. Increase max comparisons
2. Be more consistent in your preferences
3. Check if preferences are truly learnable (some masks may be indistinguishable)

### Issue: Out of memory

**Solutions**:
1. Reduce batch size
2. Use fewer masks
3. Close other browser tabs/applications

### Issue: Can't distinguish between masks

**Solutions**:
1. Use **Tie** button for similar masks
2. Skip the pair and review later
3. Zoom in (if available) to see details

### Issue: Lost progress/session

**Solutions**:
1. Check `data/sessions/` for saved sessions
2. Sessions are auto-saved every batch
3. Use SessionManager to load previous session

---

## Example Workflow

Here's a complete example workflow:

```bash
# 1. Generate sample data (for testing)
python generate_sample_data.py

# 2. Start the app
streamlit run app.py

# 3. In the browser:
#    - Click "Use sample data"
#    - Select "bronze_age" period
#    - Choose "Thompson Sampling"
#    - Select "Human Expert"
#    - Set max comparisons = 30, batch size = 10
#    - Click "Start Session"

# 4. Compare 10 pairs:
#    - Click Left/Right/Tie for each pair
#    - Click "Submit Batch & Train Model"

# 5. Wait for training (few seconds)

# 6. View results:
#    - Click rows to see masks
#    - Explore plots
#    - Click "Export Preferences (JSON)"

# 7. Start new session or continue collecting
```

---

## Getting Help

- **GitHub Issues**: Report bugs or request features
- **Documentation**: See `docs/` folder for more details
- **Examples**: Check `notebooks/` for tutorials

---

## FAQ

**Q: How many comparisons do I need?**

A: Start with 20-30 for testing. For real research, 100-200 is typical. More comparisons = better rankings but diminishing returns.

**Q: What if I make a mistake?**

A: You can't undo individual comparisons, but you can skip pairs and review them later. Export data and manually edit if needed.

**Q: Can I change acquisition function mid-session?**

A: No, acquisition function is fixed per session. Start a new session to change.

**Q: How long does training take?**

A: Typically 10-30 seconds per iteration (depends on max_epochs, number of masks, and hardware).

**Q: Can I use my own acquisition function?**

A: Yes! See `docs/DEVELOPER_GUIDE.md` for adding custom plugins.

**Q: What's the difference between Human and Oracle mode?**

A:
- **Human**: You manually compare each pair (real research)
- **Oracle**: System automatically compares (testing/simulation)

---

Enjoy using the Preference Learning Webapp! 🚀
