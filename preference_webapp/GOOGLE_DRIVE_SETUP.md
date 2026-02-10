# Using Google Drive for Webapp Data

**Your Folder:** https://drive.google.com/drive/folders/1C7giVo5hPqBbYH9iLarAHkfbLna8ezra

## Quick Setup (5 minutes)

### Step 1: Make Folder Public

1. Open your Google Drive folder
2. Right-click the folder → **Share**
3. Under "General access", select **"Anyone with the link"**
4. Click **Done**

### Step 2: Make Files Public

**For each PNG file in the folder:**

1. Select all files (Ctrl+A or Cmd+A)
2. Right-click → **Share**
3. Select **"Anyone with the link"**
4. Click **Done**

### Step 3: Create File List

Create a `file_list.json` file in the same folder:

```json
{
  "files": [
    "site_0001_mask.png",
    "site_0002_mask.png",
    "site_0003_mask.png",
    ...
  ]
}
```

To get this list easily, use this Python script:

```python
"""
Generate file_list.json from Google Drive folder
"""

# Get file names from your Google Drive folder
# Method 1: Download folder and list files
import os
from pathlib import Path
import json

# After downloading folder from Google Drive
folder_path = "bronze_age"  # Path to downloaded folder
files = sorted([f for f in os.listdir(folder_path) if f.endswith('.png')])

with open('file_list.json', 'w') as f:
    json.dump({"files": files}, f, indent=2)

print(f"Created file_list.json with {len(files)} files")
```

### Step 4: Configure Webapp

Set the environment variable:

```bash
export DATA_SERVER_URL="https://drive.google.com/drive/folders/1C7giVo5hPqBbYH9iLarAHkfbLna8ezra"
```

---

## Alternative: Better Free Hosting Options

Google Drive is **not ideal** for webapp hosting. Consider these **better, free alternatives**:

### Option A: GitHub Pages (Recommended, Free)

**Advantages:**
- Free forever
- Fast CDN
- Direct HTTPS URLs
- Works perfectly with Streamlit Cloud

**Steps:**
1. Create a new GitHub repo: `archaeology-lamap-data`
2. Create folder structure:
   ```
   archaeology-lamap-data/
   ├── bronze_age/
   │   ├── site_0001_mask.png
   │   ├── site_0002_mask.png
   │   └── ...
   ├── byzantine/
   └── roman/
   ```
3. Push files to GitHub
4. Enable GitHub Pages
5. Use URLs like:
   ```
   https://raw.githubusercontent.com/yourusername/archaeology-lamap-data/main/bronze_age/site_0001_mask.png
   ```

**Data URL:**
```bash
export DATA_SERVER_URL="https://raw.githubusercontent.com/yourusername/archaeology-lamap-data/main"
```

### Option B: Cloudflare R2 (Free Tier)

**Advantages:**
- 10GB free storage
- S3-compatible API
- Fast global CDN
- No egress fees

### Option C: Netlify Drop (Easiest)

**Advantages:**
- Drag and drop
- Instant hosting
- Free SSL
- Fast CDN

**Steps:**
1. Go to https://app.netlify.com/drop
2. Drag your `bronze_age/`, `byzantine/`, `roman/` folders
3. Get your URL: `https://random-name.netlify.app`
4. Use as `DATA_SERVER_URL`

---

## Quick Recommendation

**For immediate deployment today:**

1. **Download your Google Drive folder** locally
2. **Upload to Netlify Drop** (2 minutes)
3. **Use the Netlify URL** as `DATA_SERVER_URL`

This is faster than setting up Google Drive properly and more reliable!

---

## If You Still Want to Use Google Drive

### Method: Direct Download Links

Update the webapp code to handle Google Drive URLs:

```python
# In ui/pages/welcome.py, modify load_from_server():

def load_from_gdrive(folder_url: str, period: str):
    """Load from Google Drive folder"""
    import requests

    # For Google Drive, we need individual file IDs
    # This is why file_list.json is needed

    file_list_url = f"{folder_url}/file_list.json"

    try:
        response = requests.get(file_list_url)
        file_list = response.json()

        masks = []
        for filename in file_list['files'][:50]:
            # Construct Google Drive direct download URL
            file_url = f"{folder_url}/{filename}"
            # Load and process...

        return masks
    except:
        return None
```

---

## My Recommendation

**Use GitHub + GitHub Pages:**

1. It's free
2. It's fast
3. It's reliable
4. It works perfectly with Streamlit Cloud
5. Version control for your data
6. Easy to update

**Time to set up:** 10 minutes
**Reliability:** 99.9%
**Cost:** Free

Would you like me to help you set up GitHub hosting instead?
