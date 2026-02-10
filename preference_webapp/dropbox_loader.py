"""
Dropbox data loader for preference learning webapp.

Simple, reliable file loading from Dropbox shared folders.
"""

import json
import requests
import re
import logging
from pathlib import Path
from typing import List, Tuple, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def get_dropbox_direct_url(shared_url: str) -> str:
    """
    Convert Dropbox shared URL to direct download URL.

    Args:
        shared_url: Dropbox shared URL

    Returns:
        Direct download URL
    """
    # Method 1: Replace www.dropbox.com with dl.dropboxusercontent.com
    if 'www.dropbox.com' in shared_url or 'dropbox.com' in shared_url:
        # For shared links: https://www.dropbox.com/sh/ABC/filename?dl=0
        # Convert to: https://www.dropbox.com/sh/ABC/filename?dl=1
        if '?' in shared_url:
            base, params = shared_url.split('?', 1)
            if 'dl=0' in params:
                direct_url = base + '?dl=1'
                return direct_url

    # Method 2: Use dl.dropboxusercontent.com for direct links
    # Pattern: https://www.dropbox.com/s/FILEID/filename
    match = re.search(r'dropbox\.com/s/([a-zA-Z0-9_-]+)', shared_url)
    if match:
        file_id = match.group(1)
        return f"https://dl.dropboxusercontent.com/s/{file_id}"

    # Return original if no pattern matched
    return shared_url


def load_from_dropbox(shared_url: str, filenames: List[str]) -> Tuple[Optional[List], Optional[List]]:
    """
    Load masks from Dropbox shared folder.

    Args:
        shared_url: Dropbox shared folder URL
        filenames: List of expected filenames

    Returns:
        Tuple of (masks list, metadata list)
    """
    import numpy as np
    from PIL import Image
    from io import BytesIO

    masks = []
    metadata = []

    # Handle both old and new Dropbox URL formats
    # New format: https://www.dropbox.com/scl/fo/FOLDER_ID/FILENAME?rlkey=...&st=...&dl=0
    # Old format: https://www.dropbox.com/sh/ABC/FILENAME?dl=0

    for filename in filenames:
        try:
            # Construct direct download URL
            if 'scl/fo/' in shared_url:
                # New Dropbox shared link format
                # Extract base URL and construct file-specific link
                base_url = shared_url.split('?')[0]  # Remove query params
                # Remove dl=0 if present and add dl=1 for direct download
                if base_url.endswith('?dl=0'):
                    base_url = base_url[:-4]
                direct_url = f"{base_url}/{filename}?dl=1"
            elif '?' in shared_url:
                base_url = shared_url.split('?')[0]
                direct_url = f"{base_url}/{filename}?dl=1"
            else:
                direct_url = f"{shared_url}/{filename}?dl=1"

            logger.info(f"Trying URL: {direct_url}")

            # Download
            response = requests.get(direct_url, timeout=30)
            response.raise_for_status()

            # Check if we got actual image data
            content_type = response.headers.get('content-type', '')
            if 'text/html' in content_type or 'json' in content_type:
                logger.warning(f"Got HTML/JSON instead of image for {filename}")
                logger.warning(f"Response (first 200 chars): {response.text[:200]}")
                continue

            # Load image
            img = Image.open(BytesIO(response.content))
            mask_array = np.array(img)

            # Convert to float
            if mask_array.dtype == np.uint8:
                mask_array = mask_array.astype(float) / 255.0

            masks.append(mask_array)
            metadata.append({
                'Mask ID': filename.replace('.png', ''),
                'File': filename,
                'Source': 'Dropbox'
            })

            logger.info(f"Loaded {filename} from Dropbox")

        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            continue

    if len(masks) == 0:
        logger.error("No masks could be loaded from Dropbox")
        return None, None

    logger.info(f"Successfully loaded {len(masks)} masks from Dropbox")
    return masks, metadata


def load_dropbox_config(config_path: Path = None) -> dict:
    """
    Load Dropbox configuration.

    Args:
        config_path: Path to dropbox_config.json

    Returns:
        Configuration dictionary
    """
    if config_path is None:
        config_path = Path(__file__).parent / "dropbox_config.json"

    if not config_path.exists():
        logger.error(f"Dropbox config not found: {config_path}")
        return {}

    with open(config_path) as f:
        return json.load(f)


def auto_populate_dropbox_config(shared_url: str, period: str = "bronze_age"):
    """
    Auto-populate Dropbox config with files from local directory.

    Args:
        shared_url: Dropbox shared URL
        period: Period name
    """
    import json

    # Get local files
    local_dir = Path(__file__).parent / period
    if not local_dir.exists():
        local_dir = Path(__file__).parent.parent / "lamap_results_sample" / period

    files = sorted([f.name for f in local_dir.glob("*.png")])

    config = {
        period: {
            "shared_url": shared_url,
            "files": files,
            "count": len(files)
        }
    }

    output_path = Path(__file__).parent / "dropbox_config.json"
    with open(output_path, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"✅ Created dropbox_config.json")
    print(f"   Period: {period}")
    print(f"   Files: {len(files)}")
    print(f"   Shared URL: {shared_url}")

    return config


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    # Quick test
    shared_url = input("Enter Dropbox shared URL: ").strip()

    if not shared_url:
        print("Usage: python dropbox_loader.py")
        print()
        print("Or auto-populate config:")
        print("  python dropbox_loader.py --auto https://www.dropbox.com/sh/YOUR_LINK")
        sys.exit(1)

    # Test loading
    print(f"Testing Dropbox loading...")
    print(f"Shared URL: {shared_url}")
    print()

    # Try to load with some test filenames
    test_files = ["test1.png", "test2.png"]

    masks, metadata = load_from_dropbox(shared_url, test_files)

    if masks:
        print(f"✅ SUCCESS! Loaded {len(masks)} masks")
    else:
        print("❌ Failed to load - check shared URL and permissions")
        print()
        print("Make sure:")
        print("1. Folder is shared (Anyone with the link)")
        print("2. Link permissions allow downloading")
        print("3. Filenames match exactly")
