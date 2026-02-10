# Quick Start - Deploy Your Webapp

## Status: Ready to Deploy!

**Data Repository:** https://github.com/simomoxy/lamap-bronze-age-data
- 26 PNG files (170MB) uploaded and accessible
- Ready for automatic loading

## Test Locally First

```bash
cd /Users/simonjaxy/Documents/vub/archaeology/preference_learning/preference_webapp

# Run the webapp
/Users/simonjaxy/Documents/vub/archaeology/preference_learning/.conda/bin/python -m streamlit run app_simple.py
```

**What you'll see:**
1. Welcome page with "Load Predictions" button
2. Select "bronze_age" period
3. Enter your name
4. 26 masks load automatically (from local files)
5. Complete comparisons
6. Summary page shows results

## Deploy to Streamlit Cloud

### 1. Create GitHub Token (for data upload)

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select **repo** scope
4. Generate and copy the token

### 2. Deploy

1. Go to: https://share.streamlit.io
2. Click "New app"
3. Connect: `simomoxy/preference_learning`
4. Main file: `preference_webapp/app_simple.py`
5. Environment variables:
   - `GITHUB_DATA_REPO` = `simomoxy/lamap-bronze-age-data`
   - `GITHUB_TOKEN` = (your token from step 1)
6. Click "Deploy"

### 3. Share with Archaeologists

Share the URL with your 3 experts:
```
https://your-app-name.streamlit.app
```

## What Happens

1. **Archaeologist opens link** → Webapp loads
2. **Enters name** → Selects "bronze_age"
3. **Clicks "Load Predictions"** → 26 masks load from GitHub
4. **Completes 50 comparisons** (~30 minutes)
5. **Reaches Summary page** → Data automatically uploads to GitHub
6. **Done!** → Researcher collects all data from GitHub

## Researcher: Download All Responses

After all experts finish:

```bash
# Go to data repo
cd /path/to/lamap-bronze-age-data
git pull

# Check responses folder
ls responses/
# preferences_bronze_age_expert1_20250210_143022.json
# preferences_bronze_age_expert2_20250210_151234.json
# preferences_bronze_age_expert3_20250210_163456.json
```

Or download from: https://github.com/simomoxy/lamap-bronze-age-data/tree/main/responses

## Features

- **Automatic data loading** from GitHub
- **Automatic data upload** when expert finishes
- **Backup downloads** (CSV/JSON) for records
- **No server needed** - your machine can be off!
- **Works worldwide** - just need internet connection

## Full Documentation

See `DEPLOYMENT_GUIDE.md` for detailed instructions.
