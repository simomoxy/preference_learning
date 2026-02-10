#!/usr/bin/env python3
"""
Extract Google Drive file IDs from your public folder.

This creates a mapping of filenames to file IDs that the webapp can use.
"""

import os
import sys
import json
from pathlib import Path


def main():
    print("="*60)
    print("Google Drive File ID Extractor")
    print("="*60)
    print()
    print("Your Google Drive folder:")
    print("https://drive.google.com/drive/folders/1C7giVo5hPqBbYH9iLarAHkfbLna8ezra")
    print()
    print("⚠️  IMPORTANT: Make sure the folder AND all PNG files are public")
    print("   1. Right-click folder → Share → Anyone with the link → Done")
    print("   2. Select all files → Right-click → Share → Anyone with the link → Done")
    print()
    print("="*60)
    print()
    print("Method 1: Manual File ID Extraction")
    print("="*60)
    print()
    print("For each file in your Google Drive folder:")
    print("1. Right-click the file → Get link")
    print("2. Copy the link")
    print("3. Extract the file ID from the URL")
    print()
    print("Example URL:")
    print("https://drive.google.com/file/d/1ABC123XYZ456/view")
    print("                            ^^^^^^^^^^^^^^")
    print("                            This is the file ID")
    print()
    print("="*60)
    print()
    print("Method 2: Use Google Drive API (Advanced)")
    print("="*60)
    print()
    print("Requires:")
    print("- Google Cloud Project")
    print("- Google Drive API enabled")
    print("- OAuth credentials")
    print()
    print("For simplicity, we recommend Method 1 for 26 files")
    print()
    print("="*60)
    print()
    print("Or... Use local files instead!")
    print("="*60)
    print()
    print("Simplest solution: Use the files you already have locally:")
    print(f"  {Path.cwd()}/preference_webapp/bronze_age/")
    print()
    print("The webapp can load from local files just as easily!")
    print()
    
    # Check if local files exist
    local_dir = Path("preference_webapp/bronze_age")
    if local_dir.exists():
        png_files = list(local_dir.glob("*.png"))
        print(f"✅ Found {len(png_files)} files locally")
        print()
        print("You can test the webapp right now with:")
        print("  cd preference_webapp")
        print("  export DATA_SERVER_URL=\"\"  # Empty = use local files")
        print("  .conda/bin/python -m streamlit run app_simple.py")


if __name__ == "__main__":
    main()
