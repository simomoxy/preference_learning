# Quick Start - Use Local Files

## Test the Webapp Right Now

Your files are already in: `preference_webapp/bronze_age/`

### Step 1: Run the webapp

```bash
cd /Users/simonjaxy/Documents/vub/archaeology/preference_learning/preference_webapp
/Users/simonjaxy/Documents/vub/archaeology/preference_learning/.conda/bin/python -m streamlit run app_simple.py
```

### Step 2: In the webapp

1. Period: "bronze_age"
2. Expert Name: (your name)
3. Click "Load Predictions"
4. Should load 26 files locally!

### Step 3: Test comparisons

- Click "Begin Comparisons"
- Try comparing a few pairs
- Check if the ranking works

## For Deployment (Streamlit Cloud)

Since GitHub LFS has issues and Google Drive is complex, here are **3 easy options**:

### Option A: Include Compressed Files in Repo

```bash
# Compress to ~4.5MB each (from 6-7MB)
.conda/bin/python preference_webapp/compress_pngs.py --input preference_webapp/bronze_age --output preference_webapp/bronze_age_compressed

# Delete old files from GitHub
# (via GitHub web interface, then commit the deletion)

# Add compressed files
cp preference_webapp/bronze_age_compressed/* /path/to/repo/bronze_age/

# Push to GitHub
git commit -m "Add compressed LAMAP outputs"
git push origin main
```

### Option B: Use a Free File Hosting Service

**Recommended: Pinata or File.io** (free, direct URLs)

### Option C: Run on HPC with Tunnel

```bash
# On HPC:
cd preference_webapp
.conda/bin/python -m streamlit run app_simple.py --server.port 8501

# In another terminal:
cloudflared tunnel --url http://localhost:8501
```

## Which to Choose?

- **Testing now:** Use local files (works immediately)
- **Deployment:** Compressed GitHub files (easiest)
- **Alternative:** HPC + tunnel (free, no limits)

The local version works perfectly for you to test right now!
