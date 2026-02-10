# Quick Start: Preference Learning Webapp

## 🚀 Launch in 3 Commands

```bash
# 1. Navigate to project root
cd /Users/simonjaxy/Documents/vub/archaeology/preference_learning

# 2. Activate conda environment
conda activate preference_webapp

# 3. Launch the app
cd preference_webapp && streamlit run app.py
```

**Or use the launch script:**
```bash
./launch_webapp.sh
```

---

## ⚡ Quick Launch (One-Liner)

```bash
cd /Users/simonjaxy/Documents/vub/archaeology/preference_learning && conda activate preference_webapp && cd preference_webapp && streamlit run app.py
```

---

## 📋 First Time Setup (If Needed)

### Generate Sample Data

```bash
cd /Users/simonjaxy/Documents/vub/archaeology/preference_learning/preference_webapp
python generate_sample_data.py
```

Then in the app, click **"Use sample data"**.

---

## ❓ Troubleshooting

### "ModuleNotFoundError: No module named 'gpytorch'"

**Solution**: You forgot to activate the conda environment!

```bash
# From project root
conda activate preference_webapp

# Verify:
which python
# Should show: .../anaconda3/envs/preference_webapp/bin/python

# Then launch:
cd preference_webapp
streamlit run app.py
```

### "conda: command not found"

**Solution**: Initialize conda first

```bash
# For Anaconda:
source ~/anaconda3/etc/profile.d/conda.sh

# For Miniconda:
source ~/miniconda3/etc/profile.d/conda.sh

# Then activate:
conda activate preference_webapp
```

---

## 📖 Full Documentation

- **docs/LAUNCH_GUIDE.md** - Detailed launch instructions
- **docs/USER_GUIDE.md** - How to use the webapp
- **README.md** - Project overview

---

## ✅ Checklist

Before launching, ensure:

- [ ] You're in the project root directory (`.../preference_learning/`)
- [ ] Conda environment is activated: `conda activate preference_webapp`
- [ ] Verify Python: `which python` shows `preference_webapp/bin/python`
- [ ] In `preference_webapp/` directory when running `streamlit run app.py`

---

**Open your browser to**: http://localhost:8501

**Enjoy!** 🎉
