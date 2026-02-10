# Quick Start: Using Your Google Drive Data

**Your Folder:** https://drive.google.com/drive/folders/1C7giVo5hPqBbYH9iLarAHkfbLna8ezra

## Easiest Method: Netlify Drop (5 minutes, Recommended)

**Why use Netlify instead of Google Drive directly?**
- ✅ Works perfectly with webapps
- ✅ Fast global CDN
- ✅ No file size limits
- ✅ Free SSL (HTTPS)
- ✅ Direct file URLs

### Steps:

1. **Download your Google Drive folder locally:**
   - Open your Google Drive folder
   - Select all files (Ctrl+A)
   - Right-click → Download
   - Extract to `bronze_age/`

2. **Upload to Netlify Drop:**
   - Go to https://app.netlify.com/drop
   - Drag the `bronze_age/` folder onto the page
   - Wait for upload (green checkmark)
   - Copy your URL (e.g., `https://amazing-jones-123456.netlify.app`)

3. **Configure webapp:**
   ```bash
   export DATA_SERVER_URL="https://amazing-jones-123456.netlify.app"
   cd preference_webapp
   python -m streamlit run app_simple.py
   ```

That's it! Your webapp will now load data from Netlify.

---

## Alternative: GitHub Method (10 minutes)

### Step 1: Download Google Drive Files

1. Open your Google Drive folder
2. Download all PNG files
3. Organize locally:
   ```
   github_data/
   └── bronze_age/
       ├── site_0001_mask.png
       ├── site_0002_mask.png
       └── ...
   ```

### Step 2: Create GitHub Repo

1. Go to https://github.com/new
2. Create repo: `archaeology-lamap-data`
3. Clone it:
   ```bash
   git clone https://github.com/YOUR_USERNAME/archaeology-lamap-data.git
   cd archaeology-lamap-data
   ```

### Step 3: Add Files

```bash
# Copy your files
cp -r /path/to/github_data/* .

# Generate file lists
python ../preference_webapp/migrate_gdrive_to_hosting.py --action filelist --period bronze_age

# Commit and push
git add .
git commit -m "Add LAMAP bronze age data"
git push
```

### Step 4: Configure Webapp

```bash
export DATA_SERVER_URL="https://raw.githubusercontent.com/YOUR_USERNAME/archaeology-lamap-data/main"
cd preference_webapp
python -m streamlit run app_simple.py
```

---

## If You MUST Use Google Drive Directly

### Make Files Public

1. Open your folder: https://drive.google.com/drive/folders/1C7giVo5hPqBbYH9iLarAHkfbLna8ezra
2. Select all files
3. Right-click → Share → "Anyone with the link" → Done

### Generate File List

After downloading files locally:

```bash
cd preference_webapp
python migrate_gdrive_to_hosting.py --action filelist --period bronze_age
```

This creates `file_list.json` with your file names.

### Update Webapp Code

Add Google Drive support to `ui/pages/welcome.py`:

```python
def load_from_gdrive_direct(folder_id: str):
    """Load from public Google Drive folder"""
    import requests

    # You'll need to maintain a list of file IDs
    # or use file_list.json approach

    base_url = f"https://drive.google.com/uc?export=download&id="

    # This requires manual file ID extraction
    # That's why GitHub/Netlify is easier!
```

---

## My Recommendation

**Use Netlify Drop** - it's the fastest and most reliable:

| Feature | Netlify | GitHub | Google Drive |
|---------|---------|--------|--------------|
| Setup time | 5 min | 10 min | 30+ min |
| Reliability | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Speed | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| Works with Streamlit | ✅ | ✅ | ⚠️ |
| Free | ✅ | ✅ | ✅ |

---

## Test Your Setup

After setting up, test locally:

```bash
cd preference_webapp
export DATA_SERVER_URL="your-url-here"
python -m streamlit run app_simple.py
```

Then in the app:
1. Select period: "bronze_age"
2. Click "Load Predictions"
3. Should show "✅ Loaded 50 prediction maps"

---

## Still Need Help?

Check these files:
- `GOOGLE_DRIVE_SETUP.md` - Detailed setup guide
- `migrate_gdrive_to_hosting.py` - Helper script
- `ARCHAEOLOGIST_GUIDE.md` - Full documentation

**Or just use Netlify Drop** - drag, drop, done! 🚀
