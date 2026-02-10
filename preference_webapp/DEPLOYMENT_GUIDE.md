# Deployment Guide for Streamlit Cloud

## Overview

Deploy the preference learning webapp to Streamlit Cloud for data collection from archaeologists.

**Data flow:**
1. Masks load from GitHub (simomoxy/lamap-bronze-age-data)
2. Archaeologists complete 50 pairwise comparisons
3. Data automatically uploads to GitHub (simomoxy/lamap-bronze-age-data/responses/)
4. Researcher downloads all responses

## Step 1: Prepare GitHub Repository

Your data repository already exists:
- **Data repo:** https://github.com/simomoxy/lamap-bronze-age-data
- **Contains:** 26 LAMAP bronze age outputs (170MB)

Create a `responses/` folder for storing expert data:

```bash
# Clone the data repo
git clone git@github.com:simomoxy/lamap-bronze-age-data.git
cd lamap-bronze-age-data

# Create responses folder
mkdir responses
echo "# Expert Preference Data" > responses/README.md

# Commit and push
git add responses/
git commit -m "Add responses folder for expert data"
git push origin main
```

## Step 2: Create GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Set scopes: Check **repo** (full control of private repositories)
4. Generate token
5. **Copy the token** - you'll only see it once!

## Step 3: Deploy to Streamlit Cloud

1. Go to: https://share.streamlit.io
2. Click "New app"
3. Connect your GitHub: `simomoxy/preference_learning` (main code repo)
4. Configure:
   - **Main file path:** `preference_webapp/app_simple.py`
   - **Python version:** 3.11
5. **Environment Variables:**
   - `GITHUB_DATA_REPO` = `simomoxy/lamap-bronze-age-data`
   - `GITHUB_TOKEN` = (your token from Step 2)
6. Click "Deploy"

## Step 4: Test the Deployment

Once deployed:

1. Open the Streamlit Cloud URL
2. **Period:** Select "bronze_age"
3. **Expert Name:** Enter your name
4. **Click:** "Load Predictions"
5. **Should load:** 26 files from GitHub automatically!
6. Complete a few comparisons
7. Go to Summary page
8. **Check:** Data automatically uploaded to GitHub

## Step 5: Collect Data from Archaeologists

Share the Streamlit Cloud URL with your 3 archaeologists:

```
https://your-app-name.streamlit.app
```

Instructions for them:
1. Open the link
2. Enter your name
3. Click "Load Predictions"
4. Complete 50 pairwise comparisons (~30 minutes)
5. On the Summary page, data is **automatically uploaded**
6. Done!

## Step 6: Download All Responses

After all archaeologists finish:

```bash
cd lamap-bronze-age-data/responses
git pull

# You'll see files like:
# preferences_bronze_age_expert1_20250210_143022.json
# preferences_bronze_age_expert2_20250210_151234.json
# preferences_bronze_age_expert3_20250210_163456.json

# Or download via GitHub:
# https://github.com/simomoxy/lamap-bronze-age-data/tree/main/responses
```

## Environment Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `GITHUB_DATA_REPO` | Repository containing LAMAP masks | `simomoxy/lamap-bronze-age-data` |
| `GITHUB_TOKEN` | Token for uploading expert data | `ghp_xxxxxxxxxxxx` |
| `GITHUB_BRANCH` | Branch to use (optional) | `main` |

## Troubleshooting

**GitHub upload fails:**
- Check that `GITHUB_TOKEN` is set in Streamlit Cloud secrets
- Verify token has `repo` scope
- Check that the responses folder exists in the data repository

**Masks don't load:**
- Verify `GITHUB_DATA_REPO` is set correctly
- Check that the data repository is public
- Ensure PNG files are in the root of the repository

**App is slow:**
- Statistics are cached after first load
- Images are ~6-7MB each, 26 files total
- This is expected for first load

## Local Testing

To test locally with GitHub:

```bash
cd /Users/simonjaxy/Documents/vub/archaeology/preference_learning/preference_webapp

# Set GitHub token
export GITHUB_TOKEN="your_token_here"

# Run webapp
/Users/simonjaxy/Documents/vub/archaeology/preference_learning/.conda/bin/python -m streamlit run app_simple.py
```

**Note:** Local will use files from `bronze_age/` folder first (faster). GitHub is used when local files don't exist (like on Streamlit Cloud).
