# Launch Guide: Preference Learning Webapp

This guide will walk you through launching the Preference Learning Webapp.

## Prerequisites

### Required Software

1. **Conda Environment**: The project uses a local conda environment at `.conda/`
2. **Python**: Python 3.11 (installed via conda)
3. **Dependencies**: All required packages are pre-installed in `.conda/`

## Quick Start (3 Steps)

### Step 1: Navigate to Project Root

```bash
cd /Users/simonjaxy/Documents/vub/archaeology/preference_learning
```

**Important**: You MUST be in the project root directory (where `.conda/` is located), NOT in `preference_webapp/`.

### Step 2: Activate Conda Environment

```bash
conda activate .conda
```

**Verify activation**:
```bash
# You should see (.conda) in your prompt
which python
# Should output: /Users/simonjaxy/Documents/vub/archaeology/preference_learning/.conda/bin/python
```

### Step 3: Launch the Webapp

```bash
cd preference_webapp
streamlit run app.py
```

The application will open in your browser at: **http://localhost:8501**

---

## Complete Launch Script

Save this as `launch.sh` in the project root:

```bash
#!/bin/bash
# Launch script for Preference Learning Webapp

# Navigate to project root
cd "$(dirname "$0")"

# Activate conda environment
echo "Activating conda environment..."
conda activate .conda

# Check activation
if [ $? -ne 0 ]; then
    echo "❌ Failed to activate conda environment"
    echo "Please ensure conda is installed and .conda/ exists"
    exit 1
fi

echo "✓ Conda environment activated"

# Navigate to webapp directory
cd preference_webapp

# Launch Streamlit
echo "Launching Preference Learning Webapp..."
echo "Open your browser to: http://localhost:8501"
streamlit run app.py
```

Make it executable and run:
```bash
chmod +x launch.sh
./launch.sh
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'gpytorch'"

**Cause**: Conda environment not activated

**Solution**:
```bash
# From project root
conda activate .conda

# Verify
which python
# Should show: .../.conda/bin/python

# Then launch
cd preference_webapp
streamlit run app.py
```

### Issue: "conda: command not found"

**Cause**: Conda not installed or not in PATH

**Solution**:
```bash
# If using Anaconda
source ~/anaconda3/etc/profile.d/conda.sh

# If using Miniconda
source ~/miniconda3/etc/profile.d/conda.sh

# Then activate
conda activate .conda
```

### Issue: "Streamlit not installed"

**Cause**: Streamlit not in conda environment

**Solution**:
```bash
conda activate .conda
pip install streamlit plotly
```

### Issue: Port 8501 already in use

**Cause**: Another Streamlit app is running

**Solution**:
```bash
# Use a different port
streamlit run app.py --server.port 8502
```

### Issue: Can't find LAMAP data

**Solution**: Generate sample data for testing
```bash
cd preference_webapp
python generate_sample_data.py
```

Then in the app, click "Use sample data".

---

## Verifying Installation

Before launching, verify everything is set up correctly:

```bash
# 1. Navigate to project root
cd /Users/simonjaxy/Documents/vub/archaeology/preference_learning

# 2. Activate conda environment
conda activate .conda

# 3. Check Python
python --version
# Should output: Python 3.11.x

# 4. Check critical packages
python -c "import streamlit; print('✓ Streamlit:', streamlit.__version__)"
python -c "import torch; print('✓ PyTorch:', torch.__version__)"
python -c "import gpytorch; print('✓ GPyTorch:', gpytorch.__version__)"
python -c "import lightning; print('✓ Lightning:', lightning.__version__)"

# 5. Check webapp imports
cd preference_webapp
python -c "from backend.core.registry import AcquisitionRegistry; print('✓ Backend imports OK')"

# 6. Launch
streamlit run app.py
```

---

## Common Workflows

### Workflow 1: First Time Setup

```bash
# 1. Navigate to project
cd /Users/simonjaxy/Documents/vub/archaeology/preference_learning

# 2. Activate environment
conda activate .conda

# 3. Generate sample data (for testing)
cd preference_webapp
python generate_sample_data.py

# 4. Launch app
streamlit run app.py

# 5. In browser: Click "Use sample data" → Configure → Start comparing!
```

### Workflow 2: Using Real LAMAP Data

```bash
# 1. Ensure LAMAP data exists
ls lamap_results/
# Should see: bronze_age/, byzantine/, etc.

# 2. Activate and launch
conda activate .conda
cd preference_webapp
streamlit run app.py

# 3. In browser:
#    - Click "Browse lamap_results/ directory"
#    - Select period folder
#    - Configure session
#    - Start comparing!
```

### Workflow 3: Development Mode

```bash
# 1. Activate environment
conda activate .conda

# 2. Run with file watching (auto-reload on changes)
cd preference_webapp
streamlit run app.py --server.runOnSave true

# 3. Edit Python files and save
#    Streamlit will auto-reload the app
```

---

## System Requirements

### Minimum Requirements

- **OS**: macOS, Linux, or Windows
- **RAM**: 4 GB (8 GB recommended)
- **Storage**: 500 MB for conda environment
- **Python**: 3.9+ (project uses 3.11)

### Recommended Setup

- **OS**: macOS or Linux
- **RAM**: 8 GB or more
- **Storage**: 2 GB or more
- **Browser**: Chrome, Firefox, or Safari (latest version)

---

## Performance Tips

### For Faster Launch

1. **Use fewer masks**: Start with 10-20 masks for testing
2. **Reduce max_epochs**: Set to 5-10 in Advanced Settings
3. **Increase batch size**: Use 20 instead of 10

### For Better Performance

1. **Use GPU** (if available):
   ```bash
   # Check if GPU available
   python -c "import torch; print(torch.cuda.is_available())"

   # If True, GPU will be used automatically
   ```

2. **Close unused browser tabs**: Frees up memory

3. **Use smaller images**: Resize masks if they're very large

---

## Getting Help

### If You're Still Having Issues

1. **Check the logs**: Streamlit shows errors in the terminal
2. **Verify conda activation**: Run `which python` - should show `.conda/bin/python`
3. **Check file paths**: Ensure you're in the correct directory
4. **Read documentation**:
   - `README.md` - Overview
   - `docs/USER_GUIDE.md` - Detailed tutorial
   - `docs/TROUBLESHOOTING.md` - Common issues (if available)

### Useful Commands

```bash
# Check conda environment
conda info --envs

# List packages in environment
conda activate .conda
conda list

# Check Python path
which python
python -c "import sys; print('\n'.join(sys.path))"

# Test Streamlit
streamlit hello

# Check webapp imports
cd preference_webapp
python -c "from backend.session_manager import SessionManager; print('✓ OK')"
```

---

## Next Steps After Launch

Once the app is running:

1. **Configure Your Session** (Step 1)
   - Choose data source or use sample data
   - Select acquisition function (Thompson Sampling recommended)
   - Choose Human Expert or Virtual Oracle mode
   - Set max comparisons (start with 30 for testing)

2. **Collect Preferences** (Step 2)
   - Compare image pairs side-by-side
   - Click Left/Right/Tie for each pair
   - Submit batch when complete (triggers training)

3. **View Results** (Step 4)
   - See ranking table with Copeland scores
   - Click rows to view masks
   - Explore interactive plots
   - Export data (CSV/JSON)

---

## Quick Reference Card

```
┌─────────────────────────────────────────┐
│  LAUNCH COMMANDS                        │
├─────────────────────────────────────────┤
│  # From project root                    │
│  conda activate .conda                  │
│  cd preference_webapp                  │
│  streamlit run app.py                   │
│                                         │
│  # Generate sample data                 │
│  python generate_sample_data.py         │
│                                         │
│  # Use different port                   │
│  streamlit run app.py --server.port 8502│
└─────────────────────────────────────────┘
```

---

**That's it!** The webapp should now be running. Enjoy using the Preference Learning Webapp! 🚀
