"""
Configuration for the simplified preference learning webapp.

This file contains settings for data sources, deployment, and app behavior.
"""

import os
from pathlib import Path


# =============================================================================
# Data Source Configuration
# =============================================================================

# Server URL for loading LAMAP data
# Set this to a URL where your PNG files are hosted
# Examples:
# - Google Drive (via a proxy service like gdown or a CDN)
# - AWS S3 public bucket
# - GitHub Pages or other static hosting
# - Your own server
DATA_SERVER_URL = os.getenv("DATA_SERVER_URL", "")

# If DATA_SERVER_URL is empty, the app will use local files from:
# lamap_results_sample/{period}/

# Expected directory structure at DATA_SERVER_URL:
# {DATA_SERVER_URL}/
#   ├── bronze_age/
#   │   ├── site_0001_mask.png
#   │   ├── site_0002_mask.png
#   │   └── ...
#   ├── byzantine/
#   └── roman/

# Optional: Provide a file list URL for better performance
# This should return JSON like: {"files": ["site_0001_mask.png", ...]}
FILE_LIST_URL_TEMPLATE = "{base_url}/{period}/file_list.json"


# =============================================================================
# App Configuration
# =============================================================================

# Number of comparisons per expert
DEFAULT_NUM_COMPARISONS = 50

# Number of masks to use (max)
MAX_MASKS = 50

# Available periods
AVAILABLE_PERIODS = ["bronze_age", "byzantine", "roman"]


# =============================================================================
# Expert Identification
# =============================================================================

# Require expert name before starting
REQUIRE_EXPERT_NAME = False  # Set to True to force name entry


# =============================================================================
# Session Management
# =============================================================================

# Auto-save progress (for future enhancement)
AUTO_SAVE_ENABLED = True
AUTO_SAVE_INTERVAL = 5  # Save every N comparisons


# =============================================================================
# Styling
# =============================================================================

# Archaeology-themed colors
THEME_COLORS = {
    'primary': '#C97B63',      # Terracotta
    'secondary': '#8B9556',    # Olive
    'accent': '#D4B896',       # Sand
    'background': '#F5F0E6',   # Parchment
    'text': '#3D3B30',         # Dark earth
}


# =============================================================================
# Deployment Settings
# =============================================================================

# For local development
LOCAL_HOST = "localhost"
LOCAL_PORT = 8501

# For production deployment
PRODUCTION_HOST = os.getenv("PRODUCTION_HOST", "0.0.0.0")
PRODUCTION_PORT = int(os.getenv("PRODUCTION_PORT", "8501"))


# =============================================================================
# Data Export Settings
# =============================================================================

# Export formats
EXPORT_FORMATS = ["csv", "json"]

# Include metadata in exports
INCLUDE_METADATA = True

# Anonymize expert names in exports (for privacy)
ANONYMIZE_EXPERTS = False


# =============================================================================
# Logging
# =============================================================================

import logging

LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


# =============================================================================
# Helper Functions
# =============================================================================

def get_data_source_info():
    """
    Get information about the current data source configuration.

    Returns:
        dict: Data source info
    """
    return {
        'using_server': bool(DATA_SERVER_URL),
        'server_url': DATA_SERVER_URL if DATA_SERVER_URL else None,
        'fallback_to_local': True,
        'local_path': str(Path(__file__).parent / "lamap_results_sample"),
        'available_periods': AVAILABLE_PERIODS,
    }


def is_configured_for_deployment():
    """
    Check if the app is configured for deployment.

    Returns:
        bool: True if deployment-ready
    """
    # Check if data source is configured
    has_data = bool(DATA_SERVER_URL) or (Path(__file__).parent / "lamap_results_sample").exists()

    # Check if required packages are installed
    try:
        import streamlit
        import PIL
        import numpy
        import pandas
        return has_data
    except ImportError:
        return False


def print_config_summary():
    """
    Print a summary of the current configuration.
    """
    print("=" * 60)
    print("Preference Learning Webapp Configuration")
    print("=" * 60)

    data_info = get_data_source_info()
    print(f"Data Source: {'Server' if data_info['using_server'] else 'Local'}")
    if data_info['using_server']:
        print(f"  Server URL: {data_info['server_url']}")
    else:
        print(f"  Local Path: {data_info['local_path']}")

    print(f"\nAvailable Periods: {', '.join(AVAILABLE_PERIODS)}")
    print(f"Comparisons per Expert: {DEFAULT_NUM_COMPARISONS}")
    print(f"Max Masks: {MAX_MASKS}")

    print(f"\nDeployment Ready: {is_configured_for_deployment()}")
    print("=" * 60)


if __name__ == "__main__":
    print_config_summary()
