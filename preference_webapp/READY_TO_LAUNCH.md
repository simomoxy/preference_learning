# ✅ Ready to Launch!

## Environment Setup Complete

Your conda environment has been successfully created and all packages installed!

**Environment Name**: `preference_webapp`

**Location**: `/Users/simonjaxy/anaconda3/envs/preference_webapp`

**Python Version**: 3.11.14

**Installed Packages**:
- ✅ GPyTorch 1.15.1
- ✅ PyTorch 2.10.0
- ✅ PyTorch Lightning 2.6.0
- ✅ Streamlit 1.53.1
- ✅ Plotly 6.5.2
- ✅ All other dependencies

---

## 🚀 How to Launch

### Option 1: Using the Launch Script (Recommended)

```bash
cd /Users/simonjaxy/Documents/vub/archaeology/preference_learning
./launch_webapp.sh
```

### Option 2: Manual Launch

```bash
# Navigate to project root
cd /Users/simonjaxy/Documents/vub/archaeology/preference_learning

# Activate environment (simple name, no full path needed!)
conda activate preference_webapp

# Launch the app
cd preference_webapp
streamlit run app.py
```

### Option 3: One-Liner

```bash
cd /Users/simonjaxy/Documents/vub/archaeology/preference_learning && conda activate preference_webapp && cd preference_webapp && streamlit run app.py
```

---

## 📱 Open Your Browser

Once launched, open: **http://localhost:8501**

---

## ⚠️ Important Reminders

1. **Activate with simple name** (no full path needed!):
   ```bash
   conda activate preference_webapp
   ```

2. **Verify you're using the correct Python**:
   ```bash
   which python
   # Should show: /Users/simonjaxy/anaconda3/envs/preference_webapp/bin/python
   ```

3. **If conda command not found**, initialize first:
   ```bash
   source ~/anaconda3/etc/profile.d/conda.sh
   ```

---

## 📚 Documentation

- `QUICKSTART.md` - Quick reference
- `docs/LAUNCH_GUIDE.md` - Detailed instructions
- `docs/USER_GUIDE.md` - How to use the webapp
- `docs/TROUBLESHOOTING.md` - Common issues

---

## 🎯 Next Steps

1. **Launch the app** using one of the methods above
2. **Generate sample data** for testing (optional):
   ```bash
   cd preference_webapp
   python generate_sample_data.py
   ```
3. **Start comparing** image pairs!
4. **Export your results** when done

---

**That's it!** You're ready to use the Preference Learning Webapp! 🎉

**Simple activation command**: `conda activate preference_webapp` ✨
