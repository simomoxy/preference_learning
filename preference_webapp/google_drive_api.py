"""
Google Drive API loader - automatic file listing!

Uses Google Drive API to list and load files from a public folder.
No manual file ID entry needed.
"""

import requests
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import re

logger = logging.getLogger(__name__)


# Google Drive API endpoint
DRIVE_API_BASE = "https://www.googleapis.com/drive/v3/files"


def list_files_in_folder(folder_id: str, api_key: Optional[str] = None) -> List[Dict]:
    """
    List all files in a Google Drive folder using the API.

    Args:
        folder_id: Google Drive folder ID
        api_key: Google API key (optional for public folders)

    Returns:
        List of file info dicts with 'id', 'name', 'webContentLink'
    """
    files = []
    page_token = None

    # Construct API URL
    # For public folders, we can try without API key first
    params = {
        "q": f"'{folder_id}' in parents",
        "fields": "files(id,name,webContentLink,webViewLink,size)",
        "pageSize": 100
    }

    if api_key:
        params["key"] = api_key

    try:
        while True:
            if page_token:
                params["pageToken"] = page_token

            response = requests.get(DRIVE_API_BASE, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                files.extend(data.get("files", []))

                # Check for more pages
                page_token = data.get("nextPageToken")
                if not page_token:
                    break
            elif response.status_code == 403:
                logger.error("API access forbidden - folder may not be public")
                return []
            else:
                logger.error(f"API error: {response.status_code} - {response.text}")
                return []

    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return []

    return files


def extract_folder_id_from_url(folder_url: str) -> str:
    """
    Extract folder ID from Google Drive URL.

    Args:
        folder_url: Google Drive folder URL

    Returns:
        Folder ID string
    """
    # Match various Google Drive URL formats
    patterns = [
        r'/folders/([a-zA-Z0-9_-]+)',
        r'id=([a-zA-Z0-9_-]+)',
        r'/d/([a-zA-Z0-9_-]+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, folder_url)
        if match:
            return match.group(1)

    raise ValueError(f"Could not extract folder ID from URL: {folder_url}")


def load_masks_from_google_drive_folder(
    folder_url: str,
    api_key: Optional[str] = None
) -> Tuple[Optional[List], Optional[List]]:
    """
    Load all PNG masks from a Google Drive folder.

    Args:
        folder_url: Google Drive folder URL
        api_key: Optional API key (for private folders)

    Returns:
        Tuple of (masks list, metadata list) or (None, None) if failed
    """
    import numpy as np
    from PIL import Image
    from io import BytesIO

    try:
        # Extract folder ID
        folder_id = extract_folder_id_from_url(folder_url)
        logger.info(f"Loading from Google Drive folder: {folder_id}")

        # List files
        files = list_files_in_folder(folder_id, api_key)

        if not files:
            logger.error(f"No files found in folder {folder_id}")
            return None, None

        # Filter PNG files
        png_files = [f for f in files if f['name'].lower().endswith('.png')]

        if not png_files:
            logger.error("No PNG files found in folder")
            return None, None

        logger.info(f"Found {len(png_files)} PNG files")

        # Load masks
        masks = []
        metadata = []

        for file_info in png_files:
            try:
                file_id = file_info['id']
                filename = file_info['name']

                # Direct download URL
                download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

                # Download
                response = requests.get(download_url, timeout=30)
                response.raise_for_status()

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
                    'Source': 'Google Drive',
                    'File ID': file_id
                })

                logger.info(f"Loaded {filename}")

            except Exception as e:
                logger.error(f"Error loading {file_info.get('name', 'unknown')}: {e}")
                continue

        if len(masks) == 0:
            logger.error("No masks could be loaded")
            return None, None

        logger.info(f"Successfully loaded {len(masks)} masks from Google Drive")
        return masks, metadata

    except Exception as e:
        logger.error(f"Error loading from Google Drive: {e}", exc_info=True)
        return None, None


def get_folder_info(folder_url: str, api_key: Optional[str] = None) -> Dict:
    """
    Get information about a Google Drive folder.

    Args:
        folder_url: Google Drive folder URL
        api_key: Optional API key

    Returns:
        Dictionary with folder info
    """
    try:
        folder_id = extract_folder_id_from_url(folder_url)
        files = list_files_in_folder(folder_id, api_key)

        png_files = [f for f in files if f['name'].lower().endswith('.png')]

        return {
            'folder_id': folder_id,
            'total_files': len(files),
            'png_files': len(png_files),
            'accessible': len(png_files) > 0
        }
    except Exception as e:
        return {
            'error': str(e),
            'accessible': False
        }


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    # Test with your folder
    folder_url = "https://drive.google.com/drive/folders/1m_du5qd6HBfjZ5FrAV7fOyaHgqtg5_cc"

    print(f"Testing Google Drive API access...")
    print(f"Folder URL: {folder_url}")
    print()

    # Get folder info
    info = get_folder_info(folder_url)

    if 'error' in info:
        print(f"❌ Error: {info['error']}")
        print()
        print("Make sure:")
        print("1. The folder is public (Share → Anyone with the link)")
        print("2. All PNG files in the folder are also public")
        sys.exit(1)

    print(f"✅ Folder accessible!")
    print(f"   Folder ID: {info['folder_id']}")
    print(f"   Total files: {info['total_files']}")
    print(f"   PNG files: {info['png_files']}")
    print()

    if info['accessible']:
        print("Testing image load...")
        masks, metadata = load_masks_from_google_drive_folder(folder_url)

        if masks:
            print(f"✅ SUCCESS! Loaded {len(masks)} masks")
            print(f"   First mask shape: {masks[0].shape}")
            print(f"   First mask dtype: {masks[0].dtype}")
        else:
            print("❌ Failed to load masks")
    else:
        print("❌ No PNG files found")
