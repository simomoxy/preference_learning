#!/usr/bin/env python3
"""
Auto-generate Google Drive config from local filenames.

Works because:
1. You have the same files on Google Drive
2. Filenames match between local and Google Drive
3. We just need the folder ID (which we have!)
"""

import json
from pathlib import Path

# Your local files
local_dir = Path("preference_webapp/bronze_age")
files = sorted([f.name for f in local_dir.glob("*.png")])

print(f"Found {len(files)} files locally")
print()

# Create simple config
# Note: We don't need file IDs! We can use a different approach.
config = {
    "bronze_age": {
        "folder_id": "1m_du5qd6HBfjZ5FrAV7fOyaHgqtg5_cc",
        "folder_url": "https://drive.google.com/drive/folders/1m_du5qd6HBfjZ5FrAV7fOyaHgqtg5_cc",
        "files": files,
        "count": len(files),
        "note": "Webapp will load from Google Drive using folder listing"
    }
}

with open("preference_webapp/google_drive_simple.json", "w") as f:
    json.dump(config, f, indent=2)

print("✅ Created google_drive_simple.json")
print()
print("Now we just need to:")
print("1. Make folder public on Google Drive")
print("2. Make all PNG files public on Google Drive")
print("3. Update webapp to use direct URLs")
