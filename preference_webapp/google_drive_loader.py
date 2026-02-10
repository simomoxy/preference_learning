"""
Google Drive data loader for preference learning webapp.

Loads PNG files from a public Google Drive folder using file IDs.
"""

import json
import requests
from pathlib import Path
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def load_google_drive_config(config_path: Path = None) -> dict:
    """
    Load Google Drive configuration.

    Args:
        config_path: Path to google_drive_files.json

    Returns:
        Configuration dictionary
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent / "google_drive_files.json"

    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        return {}

    with open(config_path) as f:
        return json.load(f)


def get_direct_download_url(file_id: str) -> str:
    """
    Convert Google Drive file ID to direct download URL.

    Args:
        file_id: Google Drive file ID

    Returns:
        Direct download URL
    """
    return f"https://drive.google.com/uc?export=download&id={file_id}"


def load_from_google_drive(period: str, config: dict = None) -> Tuple[Optional[List], Optional[List]]:
    """
    Load masks from Google Drive.

    Args:
        period: Period name (bronze_age, byzantine, roman)
        config: Google Drive configuration (optional, will load if not provided)

    Returns:
        Tuple of (masks list, metadata list) or (None, None) if failed
    """
    import numpy as np
    from PIL import Image
    from io import BytesIO

    # Load config if not provided
    if config is None:
        config = load_google_drive_config()

    if not config or period not in config:
        logger.error(f"Period '{period}' not found in Google Drive config")
        return None, None

    period_config = config[period]
    files_map = period_config.get('files', {})

    if not files_map:
        logger.error(f"No files found for {period}")
        return None, None

    masks = []
    metadata = []

    for filename, file_id in files_map.items():
        # Skip placeholder entries
        if file_id == "ADD_FILE_ID_HERE" or not file_id:
            logger.warning(f"Skipping {filename} - no file ID provided")
            continue

        # Construct download URL
        download_url = get_direct_download_url(file_id)

        try:
            # Download file
            response = requests.get(download_url, timeout=30)
            response.raise_for_status()

            # Load image
            img = Image.open(BytesIO(response.content))
            mask_array = np.array(img)

            # Convert to float and normalize if needed
            if mask_array.dtype == np.uint8:
                mask_array = mask_array.astype(float) / 255.0

            masks.append(mask_array)
            metadata.append({
                'Mask ID': filename.replace('.png', ''),
                'Period': period,
                'Source': 'Google Drive',
                'File': filename
            })

            logger.info(f"Loaded {filename} from Google Drive")

        except Exception as e:
            logger.error(f"Error loading {filename} from Google Drive: {e}")
            continue

    if len(masks) == 0:
        logger.error(f"No masks could be loaded from Google Drive for {period}")
        return None, None

    logger.info(f"Successfully loaded {len(masks)} masks from Google Drive for {period}")
    return masks, metadata


def check_file_ids_configured(period: str) -> bool:
    """
    Check if file IDs are configured (not placeholders).

    Args:
        period: Period name

    Returns:
        True if file IDs are configured
    """
    config = load_google_drive_config()

    if period not in config:
        return False

    files_map = config[period].get('files', {})

    # Check if any file has a real ID (not placeholder)
    for filename, file_id in files_map.items():
        if file_id != "ADD_FILE_ID_HERE" and file_id:
            return True

    return False


def get_configuration_status() -> dict:
    """
    Get configuration status for all periods.

    Returns:
        Dictionary with status for each period
    """
    config = load_google_drive_config()
    status = {}

    for period, period_config in config.items():
        if period.startswith('_'):
            continue

        files_map = period_config.get('files', {})
        total_files = len(files_map)
        configured_files = sum(1 for fid in files_map.values() if fid != "ADD_FILE_ID_HERE" and fid)

        status[period] = {
            'total': total_files,
            'configured': configured_files,
            'complete': configured_files == total_files,
            'folder_url': period_config.get('folder_url', '')
        }

    return status


if __name__ == "__main__":
    # Test loading
    logging.basicConfig(level=logging.INFO)

    status = get_configuration_status()
    print("Google Drive Configuration Status:")
    for period, info in status.items():
        print(f"  {period}: {info['configured']}/{info['total']} files configured")
