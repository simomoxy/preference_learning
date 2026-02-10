#!/usr/bin/env python3
"""
One-time Dropbox setup - automatic!
"""

import json
from pathlib import Path

def setup_dropbox():
    print("="*60)
    print("Dropbox Setup - Super Simple!")
    print("="*60)
    print()
    print("Just follow these steps:")
    print()
    print("1. Upload your 26 PNG files to a Dropbox folder")
    print("2. Right-click the folder → Share → Create link")
    print("3. Set to 'Anyone with the link'")
    print("4. Copy the link (starts with https://www.dropbox.com/sh/...)")
    print()

    shared_url = input("Paste your Dropbox shared URL here: ").strip()

    if not shared_url or 'dropbox.com' not in shared_url:
        print("❌ Invalid Dropbox URL")
        return

    # Get local filenames
    bronze_dir = Path("bronze_age")
    if not bronze_dir.exists():
        bronze_dir = Path("../lamap_results_sample/bronze_age")

    files = sorted([f.name for f in bronze_dir.glob("*.png")])

    # Create config
    config = {
        "bronze_age": {
            "shared_url": shared_url,
            "files": files,
            "count": len(files)
        }
    }

    # Save config
    with open("dropbox_config.json", "w") as f:
        json.dump(config, f, indent=2)

    print()
    print("="*60)
    print("✅ Setup Complete!")
    print("="*60)
    print()
    print(f"Config created: dropbox_config.json")
    print(f"Files: {len(files)}")
    print(f"Shared URL: {shared_url}")
    print()
    print("Now test the webapp:")
    print("  cd preference_webapp")
    print("  .conda/bin/python -m streamlit run app_simple.py")
    print()
    print("Select 'bronze_age' → Load Predictions → DONE! 🎉")

if __name__ == "__main__":
    setup_dropbox()
