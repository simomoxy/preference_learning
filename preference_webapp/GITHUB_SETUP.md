# GitHub Setup for Your Data

**Your Repository:** https://github.com/simomoxy/preference_learning

## Status

✅ **Bronze Age:** 50 PNG files uploaded (~200KB total)
✅ **file_list.json:** Created and pushed

## Current Repository Structure

```
simomoxy/preference_learning/
└── bronze_age/
    ├── site_0000_mask.png
    ├── site_0001_mask.png
    ├── ... (50 files total)
    └── file_list.json ✨ (NEW!)
```

## Storage Used

- **Current:** ~200KB (bronze_age only)
- **With 3 periods:** ~600KB estimated
- **GitHub free limit:** 1GB
- **You're using:** 0.06% of your free storage! ✅

## Data Server URL

```
https://raw.githubusercontent.com/simomoxy/preference_learning/main
```

## Configure Webapp

### Option 1: Temporary (Current Session Only)

```bash
cd preference_webapp
export DATA_SERVER_URL="https://raw.githubusercontent.com/simomoxy/preference_learning/main"
.conda/bin/python -m streamlit run app_simple.py
```

### Option 2: Permanent (Add to Shell)

**Add to your `~/.zshrc` or `~/.bashrc`:**

```bash
export DATA_SERVER_URL="https://raw.githubusercontent.com/simomoxy/preference_learning/main"
```

Then reload:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

### Option 3: Streamlit Cloud (Deployment)

When deploying to Streamlit Cloud, add environment variable:

1. Go to your app on Streamlit Cloud
2. Settings → Secrets
3. Add secret:
   - Key: `DATA_SERVER_URL`
   - Value: `https://raw.githubusercontent.com/simomoxy/preference_learning/main`

## Adding More Periods

### Step 1: Add byzantine and roman folders

```bash
cd /path/to/your/local/repo
mkdir -p byzantine roman

# Copy your PNG files
cp /path/to/byzantine_images/*.png byzantine/
cp /path/to/roman_images/*.png roman/
```

### Step 2: Generate file lists

```bash
# For byzantine
ls byzantine/*.png | xargs -n1 basename | sort > byzantine_files.txt
python3 << PYTHON
import json
with open('byzantine_files.txt') as f:
    files = [line.strip() for line in f]
with open('byzantine/file_list.json', 'w') as f:
    json.dump({"files": files, "count": len(files), "period": "byzantine"}, f, indent=2)
PYTHON

# For roman
ls roman/*.png | xargs -n1 basename | sort > roman_files.txt
python3 << PYTHON
import json
with open('roman_files.txt') as f:
    files = [line.strip() for line in f]
with open('roman/file_list.json', 'w') as f:
    json.dump({"files": files, "count": len(files), "period": "roman"}, f, indent=2)
PYTHON
```

### Step 3: Commit and push

```bash
git add byzantine roman
git commit -m "Add byzantine and roman period data"
git push origin main
```

## Test Locally

```bash
cd preference_webapp
export DATA_SERVER_URL="https://raw.githubusercontent.com/simomoxy/preference_learning/main"
.conda/bin/python -m streamlit run app_simple.py
```

In the app:
1. Select "bronze_age"
2. Click "Load Predictions"
3. Should show "✅ Loaded 50 prediction maps"

## Troubleshooting

### "404: Not Found" when loading images

**Cause:** GitHub CDN hasn't updated yet (can take 1-2 minutes)

**Solution:** Wait a few minutes and try again

### Images don't load in webapp

**Check:**
1. URL is correct: `https://raw.githubusercontent.com/simomoxy/preference_learning/main`
2. Files exist in repo: https://github.com/simomoxy/preference_learning/tree/main/bronze_age
3. file_list.json exists: https://github.com/simomoxy/preference_learning/blob/main/bronze_age/file_list.json

### Want to update images?

```bash
# Replace files
cp new_images/*.png bronze_age/

# Update file_list.json if needed
# (if you added/removed files)

# Commit changes
git add bronze_age
git commit -m "Update bronze age images"
git push origin main
```

## Alternative Data URLs

If raw.githubusercontent.com is slow, you can also use:

### jsDelivr CDN (Faster)

```
https://cdn.jsdelivr.net/gh/simomoxy/preference_learning@main
```

Set as:
```bash
export DATA_SERVER_URL="https://cdn.jsdelivr.net/gh/simomoxy/preference_learning@main"
```

### GitHub Pages (Custom Domain)

You could also set up GitHub Pages for even faster loading.

## Next Steps

1. ✅ Bronze age data uploaded
2. ⏳ Add byzantine and roman data
3. ⏳ Test webapp locally
4. ⏳ Deploy to Streamlit Cloud
5. ⏳ Share URL with archaeologists

## Repository URL for Reference

- **Repo:** https://github.com/simomoxy/preference_learning
- **Bronze Age:** https://github.com/simomoxy/preference_learning/tree/main/bronze_age
- **Raw Base URL:** https://raw.githubusercontent.com/simomoxy/preference_learning/main

---

**Last updated:** 2025-02-09
