# Archaeological Preference Learning Webapp

A simplified web application for collecting expert preferences on LAMAP archaeological site prediction maps.

## For Archaeologists

### Access the App

**URL:** [Link will be provided after deployment]

### Overview

This tool helps archaeologists compare different LAMAP (Locally Adaptive Multivariate Assemblage Probability) predictions to identify which hyperparameter configurations produce the most plausible archaeological site maps.

### How to Use

1. **Select Period**
   - Choose which archaeological period to evaluate (Bronze Age, Byzantine, Roman)
   - Enter your name or ID (optional, for tracking your dataset)
   - Click "Load Predictions"

2. **Compare Predictions**
   - You'll see 50 pairs of site prediction maps side-by-side
   - Click which one looks more plausible for archaeological sites
   - Options:
     - **Left is Better** - The left image is more plausible
     - **Right is Better** - The right image is more plausible
     - **Can't Decide** - Both images are equally good/bad
     - **Skip** - Move to the next comparison without recording a preference

3. **View Results**
   - After completing 50 comparisons, see the final ranking
   - Download your preference dataset (CSV or JSON)
   - Share the downloaded file with the research team

### Tips for Comparing Predictions

When evaluating predictions, consider:

- **Site Shape:** Prefer compact, coherent site shapes (not scattered pixels)
- **Archaeological Patterns:** Look for predictions that match known archaeological settlement patterns
- **Spatial Coherence:** Nearby pixels should be similar (spatial autocorrelation)
- **Trust Your Intuition:** If it "looks right" as an archaeological site, it probably is!

### Keyboard Shortcuts

Speed up your comparisons with keyboard shortcuts:

- `A` or `←` (Left Arrow): Left image is better
- `D` or `→` (Right Arrow): Right image is better
- `T`: Tie (both are equal)
- `S`: Skip this comparison

### Time Estimate

- **Total Time:** ~30 minutes for 50 comparisons
- **Per Comparison:** ~30-40 seconds

### Frequently Asked Questions

**Q: What if I'm not sure which is better?**
A: Use "Can't Decide" or "Skip" - it's okay to be uncertain!

**Q: Can I take a break?**
A: Yes! The app saves your progress. You can close it and come back later.

**Q: What happens to my data?**
A: Your preferences are downloaded as a file that you share with the research team. The data is used to improve LAMAP predictions.

**Q: Do I need technical knowledge?**
A: No! The tool is designed for archaeologists, not programmers. Just trust your expertise.

---

## For Developers

### Local Development

#### Prerequisites

- Conda environment at `../.conda/`
- Python 3.9+

#### Setup

```bash
# Activate conda environment
conda activate ../.conda

# Or use full path
.conda/bin/python --version

# Navigate to webapp directory
cd preference_webapp
```

#### Run Locally

```bash
# Activate environment
conda activate ../.conda

# Run the app
streamlit run app_simple.py

# Or with Python
.conda/bin/python -m streamlit run app_simple.py
```

The app will open at `http://localhost:8501`

#### Project Structure

```
preference_webapp/
├── .streamlit/
│   └── config.toml          # Streamlit theme and server config
├── ui/
│   ├── theme.py             # Archaeology-themed styling
│   ├── components.py        # Reusable UI components
│   └── pages/
│       ├── welcome.py       # Data loading page
│       ├── collect_simple.py # Comparison interface
│       └── summary.py       # Results and export
├── lamap_results_sample/    # Sample LAMAP prediction maps
│   ├── bronze_age/
│   ├── byzantine/
│   └── roman/
├── app_simple.py            # Main app entry point (simplified)
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

### Deployment

#### Option 1: Streamlit Cloud (Recommended)

1. **Push to GitHub**
   ```bash
   git add preference_webapp/
   git commit -m "Add simplified webapp for archaeologists"
   git push
   ```

2. **Deploy to Streamlit Cloud**
   - Go to https://share.streamlit.io
   - Connect your GitHub account
   - Select your repository
   - Set main page path: `preference_webapp/app_simple.py`
   - Click "Deploy"

3. **Share URL**
   - Your app will be available at `https://your-app-name.streamlit.app`
   - Share this URL with archaeologists

**Pros:** Free tier available, easy setup, auto-deploys on git push
**Cons:** Limited storage (~1GB), compute limits

#### Option 2: HPC + Tunnel (For Testing)

```bash
# On HPC or local machine
cd preference_webapp
conda activate ../.conda

# Run Streamlit
streamlit run app_simple.py --server.port 8501

# In another terminal, create tunnel
# Using ngrok (free, but expires)
ngrok http 8501

# OR using cloudflared (more stable)
cloudflared tunnel --url http://localhost:8501
```

**Pros:** Full control, no storage limits
**Cons:** Tunnel expires (ngrok free), requires keeping process running

#### Option 3: VPS/Cloud Server

For production deployment:

1. Rent a VPS (DigitalOcean, AWS EC2, etc.)
2. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install python3-pip
   pip install -r requirements.txt
   ```
3. Run with Gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8501 app_simple:app
   ```
4. Set up reverse proxy with Nginx
5. Configure SSL with Let's Encrypt

### Data Strategy

#### Current Setup (Bundled Data)

- 50 LAMAP PNG images per period (~15MB each)
- Stored in `lamap_results_sample/`
- Committed to Git repository
- Works for Streamlit Cloud free tier

#### Future Scaling (Large Datasets)

For larger datasets (>1GB):

**Option A: Streamlit Cloud Paid Tier**
- Upgrade to Pro plan ($20/month)
- More storage and compute

**Option B: GitHub LFS**
```bash
git lfs track "*.png"
git lfs track "*.tif"
git add .gitattributes
git commit -m "Track large files"
```

**Option C: Cloud Storage**
- Store data in S3, GCS, or Azure Blob
- Load via URL in the app
- Modify `load_period_data()` to fetch from URLs

**Option D: Google Drive Integration**
- Store data on Google Drive
- Use pydrive or google-api-python-client
- Load data via Google Drive share links

### Configuration

Edit `.streamlit/config.toml` to customize:

```toml
[theme]
primaryColor = "#C97B63"      # Terracotta
backgroundColor = "#F5F0E6"   # Parchment
secondaryBackgroundColor = "#D4B896"  # Sand
textColor = "#3D3B30"         # Dark earth

[client]
showErrorDetails = false
toolbarMode = "minimal"

[server]
maxUploadSize = 200  # MB
```

### Testing

```bash
# Run tests (when implemented)
pytest tests/

# Or run manually
streamlit run app_simple.py
```

### Troubleshooting

**Issue:** Data not loading
- Check that `lamap_results_sample/` exists
- Verify PNG files are present
- Check file permissions

**Issue:** Styling looks wrong
- Clear browser cache
- Check that `.streamlit/config.toml` is present
- Verify theme colors in `ui/theme.py`

**Issue:** Deployment fails
- Check `requirements.txt` has all dependencies
- Verify Python version (3.9+)
- Check Streamlit Cloud logs

**Issue:** Keyboard shortcuts not working
- Make sure you click on the page first (focus)
- Some shortcuts may conflict with browser defaults
- Use buttons as fallback

### Contributing

When modifying the app:

1. Keep the archaeology theme consistent
2. Test with sample data before deploying
3. Update README with any new features
4. Commit with descriptive messages

### License

This is research software for the Preference Learning for Archaeological Segmentation project.

### Contact

For questions or issues, contact the research team.
