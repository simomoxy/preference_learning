# Google Drive Setup - Complete Guide

## Your Google Drive Folder
https://drive.google.com/drive/folders/1m_du5qd6HBfjZ5FrAV7fOyaHgqtg5_cc

## Step 1: Make Folder & Files Public (2 minutes)

### Make Folder Public:
1. Open the folder link above
2. Click "Share" button
3. Change "General access" to "Anyone with the link"
4. Click "Done"

### Make All PNG Files Public:
1. In the folder, select all PNG files (Ctrl+A or Cmd+A)
2. Right-click → "Share"
3. Change to "Anyone with the link"
4. Click "Done"

## Step 2: Extract File IDs (5 minutes)

### Option A: Use HTML Helper (Recommended)

1. Open: `preference_webapp/extract_file_ids_helper.html`
2. For each file in your Google Drive folder:
   - Double-click to open the file
   - Copy the URL from your browser
   - Paste into the HTML helper
3. After adding all files, click "Extract File IDs"
4. Copy the JSON output

### Option B: Manual Extraction

For each file:
1. Open file in Google Drive
2. Copy URL: `https://drive.google.com/file/d/FILE_ID/view`
3. Extract FILE_ID (part between /d/ and /view)

Example:
```
https://drive.google.com/file/d/1m_du5qd6HBfjZ5FrAV7fOyaHgqtg5_cc/view
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                            This is the file ID
```

## Step 3: Update Config File

1. Open: `preference_webapp/google_drive_files.json`
2. Replace `"ADD_FILE_ID_HERE"` with actual file IDs
3. Save the file

Format:
```json
{
  "bronze_age": {
    "files": {
      "filename1.png": "FILE_ID_1",
      "filename2.png": "FILE_ID_2",
      ...
    }
  }
}
```

## Step 4: Test Webapp

```bash
cd preference_webapp
.conda/bin/python -m streamlit run app_simple.py
```

In the webapp:
1. Period: "bronze_age"
2. Expert Name: (your name)
3. Click "Load Predictions"
4. Should load from Google Drive! ✅

## Troubleshooting

### "File IDs not configured"
- You need to complete Step 2 and Step 3

### "Could not load from Google Drive"
- Make sure folder and files are public (Step 1)
- Check that file IDs are correct in config file
- Wait 1-2 minutes for Google Drive permissions to update

### Files showing as 0 bytes
- Permissions haven't propagated yet
- Wait 2-3 minutes and try again

## File ID Quick Reference

After you extract file IDs, your config should look like:

```json
{
  "bronze_age": {
    "folder_id": "1m_du5qd6HBfjZ5FrAV7fOyaHgqtg5_cc",
    "files": {
      "20260209_114719...png": "YOUR_FILE_ID_1",
      "20260209_123301...png": "YOUR_FILE_ID_2",
      ...
    }
  }
}
```

## Need Help?

1. Open the HTML helper tool
2. Follow the steps above
3. Check config file format matches example
4. Make sure files are public on Google Drive

Once configured, the webapp loads directly from Google Drive every time!
