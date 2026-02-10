# Troubleshooting Guide

## Common Issues and Solutions

### ❌ Issue: "ModuleNotFoundError: No module named 'gpytorch'"

**Most Common Issue!** This means the conda environment is not activated.

#### Solution:

```bash
# ❌ WRONG: Running from preference_webapp/ without activation
cd preference_webapp
streamlit run app.py
# Error: ModuleNotFoundError: No module named 'gpytorch'

# ✅ CORRECT: Activate environment first
cd /Users/simonjaxy/Documents/vub/archaeology/preference_learning
conda activate .conda
cd preference_webapp
streamlit run app.py
# Success! ✓
```

#### How to Verify:

```bash
# Check which Python you're using
which python

# Should show:
# /Users/simonjaxy/Documents/vub/archaeology/preference_learning/.conda/bin/python

# If it shows:
# /usr/bin/python  (or system Python)
# /opt/homebrew/bin/python  (or other Python)
# Then conda environment is NOT activated!
```

#### Quick Fix:

```bash
# From project root (where .conda/ is located)
conda activate .conda

# Then launch
cd preference_webapp
streamlit run app.py
```

---

### ❌ Issue: "conda: command not found"

Conda is not initialized in your shell.

#### Solution (Choose One):

**Option 1: Initialize conda**
```bash
# For Anaconda:
source ~/anaconda3/etc/profile.d/conda.sh

# For Miniconda:
source ~/miniconda3/etc/profile.d/conda.sh

# Then activate:
conda activate .conda
```

**Option 2: Use full path**
```bash
# Use full path to conda
/Users/simonjaxy/anaconda3/bin/conda activate .conda

# Or if using miniconda
/Users/simonjaxy/miniconda3/bin/conda activate .conda
```

**Option 3: Add to ~/.zshrc or ~/.bash_profile**
```bash
# Add this line to your shell config:
# >>> conda initialize >>>
# conda config --set auto_activate_base false
# <<< conda initialize <<<

# Then restart your terminal
```

---

### ❌ Issue: "No module named 'streamlit'"

Streamlit is not installed in the conda environment.

#### Solution:

```bash
# Make sure conda environment is activated
conda activate .conda

# Install streamlit
pip install streamlit plotly

# Verify installation
python -c "import streamlit; print('Streamlit version:', streamlit.__version__)"
```

---

### ❌ Issue: Port 8501 already in use

Another Streamlit app is already running.

#### Solution:

```bash
# Use a different port
streamlit run app.py --server.port 8502

# Or kill the existing process
lsof -ti:8501 | xargs kill -9
# Then retry
streamlit run app.py
```

---

### ❌ Issue: "No LAMAP data found"

The app can't find the LAMAP results directory.

#### Solution 1: Generate Sample Data

```bash
cd preference_webapp
python generate_sample_data.py
```

Then in the app, click **"Use sample data"**.

#### Solution 2: Use Real Data

1. In the Config page, click **"Browse lamap_results/ directory"**
2. Navigate to your LAMAP output folder
3. Select a period (e.g., `bronze_age`)

#### Solution 3: Check Directory Structure

```
Expected structure:
lamap_results/
├── bronze_age/
│   ├── site_1.tif
│   ├── site_2.tif
│   └── ...
├── byzantine/
│   └── ...
```

---

### ❌ Issue: Training is very slow

GP training is taking too long.

#### Solutions:

1. **Reduce max_epochs** (in Advanced Settings):
   - Default: 20
   - Try: 5-10 for faster training

2. **Use fewer masks**:
   - Start with 10-20 masks for testing
   - Not all 100+ masks

3. **Increase batch size**:
   - Default: 10 pairs per batch
   - Try: 20 pairs (fewer training cycles)

4. **Use GPU** (if available):
   ```bash
   # Check GPU availability
   python -c "import torch; print('GPU available:', torch.cuda.is_available())"
   ```

---

### ❌ Issue: Out of memory

The app is using too much RAM.

#### Solutions:

1. **Reduce batch size**:
   - From 10 to 5 pairs per batch

2. **Use fewer masks**:
   - Subset of your data

3. **Close other applications**:
   - Free up memory

4. **Reduce image size**:
   - Resize masks if they're very large

---

### ❌ Issue: Page not loading / Blank screen

Streamlit page is not displaying correctly.

#### Solutions:

1. **Check browser console**:
   - Press F12
   - Look for JavaScript errors

2. **Clear browser cache**:
   - Cmd+Shift+R (Mac)
   - Ctrl+Shift+R (Windows/Linux)

3. **Try different browser**:
   - Chrome, Firefox, or Safari

4. **Restart Streamlit**:
   ```bash
   # Press Ctrl+C in terminal
   # Then restart
   streamlit run app.py
   ```

---

### ❌ Issue: Import errors in backend

Backend modules can't be imported.

#### Solution:

```bash
# Check you're in the correct directory
pwd
# Should be: .../preference_learning/preference_webapp

# Test imports
python -c "from backend.session_manager import SessionManager; print('✓ OK')"

# If this fails, check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

---

### ❌ Issue: Session not saving

Can't save or load sessions.

#### Solutions:

1. **Check data directory exists**:
   ```bash
   ls data/sessions/
   ```

2. **Create if missing**:
   ```bash
   mkdir -p data/sessions
   mkdir -p data/preferences
   mkdir -p data/checkpoints
   ```

3. **Check permissions**:
   ```bash
   # Make sure directories are writable
   ls -la data/
   ```

---

### ❌ Issue: Rankings keep changing

Copeland scores are unstable across iterations.

#### Solutions:

1. **Be more consistent** in your preferences
2. **Use more comparisons** (increase max_comparisons)
3. **Skip indistinguishable masks** (use Tie button)
4. **Wait for convergence** (3-5 iterations minimum)

---

## Diagnostic Commands

### Check Your Setup

```bash
# 1. Check conda environment
conda info --envs
# Look for: .conda  *  (the * means active)

# 2. Check Python version and location
python --version
which python

# 3. Verify critical packages
python -c "import streamlit; print('✓ Streamlit:', streamlit.__version__)"
python -c "import torch; print('✓ PyTorch:', torch.__version__)"
python -c "import gpytorch; print('✓ GPyTorch:', gpytorch.__version__)"
python -c "import lightning; print('✓ Lightning:', lightning.__version__)"

# 4. Test backend imports
cd preference_webapp
python -c "from backend.session_manager import SessionManager; print('✓ SessionManager OK')"
python -c "from backend.active_learning_loop import ActiveLearningLoop; print('✓ ActiveLearningLoop OK')"
python -c "from acquisition.registry import acquisition_registry; print('✓ Acquisition Registry OK')"
```

### Test Streamlit

```bash
# Run Streamlit hello world
streamlit hello

# If this works, Streamlit is installed correctly
# Press Ctrl+C to stop
# Then run the actual app
streamlit run app.py
```

---

## Getting More Help

If none of these solutions work:

1. **Check the logs**: Look at the terminal output for error messages
2. **Read the documentation**:
   - `docs/LAUNCH_GUIDE.md` - Detailed launch instructions
   - `docs/USER_GUIDE.md` - User tutorial
   - `README.md` - Project overview
3. **Verify your environment**:
   ```bash
   conda activate .conda
   python -c "import sys; print('\n'.join(sys.path))"
   ```
4. **Try a fresh start**:
   ```bash
   # Deactivate and reactivate
   conda deactivate
   conda activate .conda
   cd preference_webapp
   streamlit run app.py
   ```

---

## Most Common Mistake

**Forgetting to activate the conda environment!**

Always remember:
```bash
# ❌ WRONG
cd preference_webapp
streamlit run app.py  # Error!

# ✅ CORRECT
conda activate .conda  # Don't forget this!
cd preference_webapp
streamlit run app.py  # Success!
```

---

**Still stuck?** Check `docs/LAUNCH_GUIDE.md` for detailed instructions.
