"""
GitHub data loader for preference learning webapp.

Loads PNG files directly from GitHub repositories using raw.githubusercontent.com URLs.
"""

import requests
import logging
from pathlib import Path
from typing import List, Tuple, Optional
from io import BytesIO

logger = logging.getLogger(__name__)


def load_from_github(
    repo: str,
    branch: str = "main",
    path: str = "",
    filenames: Optional[List[str]] = None
) -> Tuple[Optional[List], Optional[List]]:
    """
    Load masks from GitHub repository.

    Args:
        repo: Repository name (username/repo)
        branch: Branch name (default: main)
        path: Path to directory containing PNG files
        filenames: Optional list of expected filenames. If None, fetches from GitHub API.

    Returns:
        Tuple of (masks list, metadata list) or (None, None) if failed
    """
    import numpy as np
    from PIL import Image

    try:
        # Get file list from GitHub API if not provided
        if filenames is None:
            api_url = f"https://api.github.com/repos/{repo}/contents/{path}"
            logger.info(f"Fetching file list from GitHub API: {api_url}")

            filenames = []
            page = 1

            # Handle pagination
            while api_url:
                response = requests.get(api_url, timeout=60, params={'per_page': 100})
                if response.status_code != 200:
                    logger.error(f"GitHub API returned {response.status_code}")
                    return None, None

                contents = response.json()

                # Check if it's an error response
                if isinstance(contents, dict) and 'message' in contents:
                    logger.error(f"GitHub API error: {contents.get('message')}")
                    return None, None

                # Extract filenames from this page
                page_filenames = [item['name'] for item in contents if item.get('name', '').endswith('.png')]
                filenames.extend(page_filenames)

                logger.info(f"Page {page}: Found {len(page_filenames)} PNG files")

                # Check for Link header to see if there's a next page
                link_header = response.headers.get('Link', '')
                if 'next' in link_header:
                    # Extract next page URL
                    for link in link_header.split(','):
                        if 'rel="next"' in link:
                            api_url = link.split('<')[1].split('>')[0]
                            page += 1
                            break
                else:
                    api_url = None

            filenames = sorted(filenames)
            logger.info(f"Total PNG files found: {len(filenames)}")

            if not filenames:
                logger.error(f"No PNG files found in {repo}/{path}")
                return None, None

        logger.info(f"Loading {len(filenames)} files from GitHub...")

        masks = []
        metadata = []
        base_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"

        for filename in filenames:
            try:
                # Construct raw URL
                file_url = f"{base_url}/{filename}"

                # Download file
                logger.debug(f"Downloading: {file_url}")
                response = requests.get(file_url, timeout=60)  # Increased timeout

                if response.status_code != 200:
                    logger.warning(f"Failed to download {filename}: {response.status_code}")
                    continue

                # Load image
                img = Image.open(BytesIO(response.content))
                mask_array = np.array(img)

                # Convert to float and normalize
                if mask_array.dtype == np.uint8:
                    mask_array = mask_array.astype(float) / 255.0

                masks.append(mask_array)
                metadata.append({
                    'Mask ID': filename.replace('.png', ''),
                    'File': filename,
                    'Source': 'GitHub',
                    'URL': file_url
                })

                logger.info(f"Loaded {filename}")

            except Exception as e:
                logger.error(f"Error loading {filename}: {e}")
                continue

        if len(masks) == 0:
            logger.error("No masks could be loaded from GitHub")
            return None, None

        logger.info(f"Successfully loaded {len(masks)} masks from GitHub")
        return masks, metadata

    except requests.exceptions.Timeout:
        logger.error("GitHub API request timed out. Check your internet connection.")
        return None, None
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Could not connect to GitHub: {e}")
        return None, None
    except Exception as e:
        logger.error(f"Error loading from GitHub: {e}", exc_info=True)
        return None, None


def get_github_file_list(repo: str, path: str, branch: str = "main") -> Optional[List[str]]:
    """
    Get list of PNG files from GitHub repository.

    Args:
        repo: Repository name (username/repo)
        path: Path to directory
        branch: Branch name

    Returns:
        List of filenames or None if failed
    """
    try:
        api_url = f"https://api.github.com/repos/{repo}/contents/{path}"
        response = requests.get(api_url, timeout=10)

        if response.status_code != 200:
            return None

        contents = response.json()
        filenames = [item['name'] for item in contents if item['name'].endswith('.png')]
        return sorted(filenames)

    except Exception as e:
        logger.error(f"Error getting file list from GitHub: {e}")
        return None


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    # Test loading
    repo = "simomoxy/lamap-bronze-age-data"

    print(f"Testing GitHub loading from {repo}...")
    print()

    masks, metadata = load_from_github(repo)

    if masks:
        print(f"✅ SUCCESS! Loaded {len(masks)} masks")
        print()
        print("First few files:")
        for m in metadata[:3]:
            print(f"  - {m['Mask ID']}")
    else:
        print("❌ Failed to load")
