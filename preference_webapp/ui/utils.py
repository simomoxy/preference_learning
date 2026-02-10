"""
UI utility functions for error handling, formatting, and validation.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, Callable
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from datetime import datetime

logger = logging.getLogger(__name__)


def safe_execute(
    func: Callable,
    error_message: str = "An error occurred",
    st_context: Optional[Any] = None,
    raise_error: bool = False
) -> Optional[Any]:
    """
    Execute function with error handling.

    Args:
        func: Function to execute
        error_message: Error message to display
        st_context: Streamlit context (st, st.error, st.warning, etc.)
        raise_error: Whether to raise the error after handling

    Returns:
        Function result or None if error occurred
    """
    try:
        return func()
    except Exception as e:
        logger.error(f"{error_message}: {e}", exc_info=True)

        if st_context:
            st_context.error(f"{error_message}: {str(e)}")
        elif st:
            st.error(f"{error_message}: {str(e)}")

        if raise_error:
            raise

        return None


def format_timestamp(timestamp: str) -> str:
    """
    Format ISO timestamp for display.

    Args:
        timestamp: ISO format timestamp string

    Returns:
        Formatted timestamp string
    """
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return timestamp


def get_session_summary(session: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get session summary for display.

    Args:
        session: Session dictionary

    Returns:
        Summary dictionary with key information
    """
    summary = {
        'session_id': session.get('session_id', 'N/A'),
        'created_at': format_timestamp(session.get('created_at', 'N/A')),
        'updated_at': format_timestamp(session.get('updated_at', 'N/A')),
        'iteration': session.get('iteration', 0),
        'total_comparisons': session.get('total_comparisons', 0),
        'converged': session.get('converged', False),
    }

    # Add config summary
    config = session.get('config', {})
    if config:
        summary['period'] = config.get('period', 'N/A')
        summary['strategy'] = config.get('strategy', 'N/A')
        summary['acquisition'] = config.get('acquisition', 'N/A')
        summary['encoder'] = config.get('encoder', 'N/A')
        summary['decision_mode'] = config.get('decision_mode', 'N/A')

    return summary


def validate_config(config: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate configuration dictionary.

    Args:
        config: Configuration dictionary

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Required fields
    required_fields = ['lamap_results_dir', 'period', 'decision_mode']
    missing_fields = [f for f in required_fields if f not in config or not config[f]]

    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"

    # Check lamap_results_dir exists
    lamap_dir = Path(config['lamap_results_dir'])
    if not lamap_dir.exists():
        return False, f"LAMAP results directory does not exist: {lamap_dir}"

    # Check period directory exists
    period_dir = lamap_dir / config['period']
    if not period_dir.exists():
        return False, f"Period directory does not exist: {period_dir}"

    # Validate max_comparisons
    max_comparisons = config.get('max_comparisons', 100)
    if not isinstance(max_comparisons, int) or max_comparisons <= 0:
        return False, "max_comparisons must be a positive integer"

    # Validate batch_size
    batch_size = config.get('batch_size', 10)
    if not isinstance(batch_size, int) or batch_size <= 0:
        return False, "batch_size must be a positive integer"

    # Validate decision_mode
    decision_mode = config['decision_mode']
    if decision_mode not in ['human', 'oracle']:
        return False, f"Invalid decision_mode: {decision_mode}"

    # If oracle mode, validate oracle_config
    if decision_mode == 'oracle':
        oracle_config = config.get('oracle_config', {})
        if 'oracle_type' not in oracle_config:
            return False, "oracle_type required for oracle mode"

        oracle_type = oracle_config['oracle_type']
        if oracle_type not in ['biased', 'random', 'custom']:
            return False, f"Invalid oracle_type: {oracle_type}"

    return True, ""


def load_lamap_masks(lamap_results_dir: str, period: str) -> tuple[list, Optional[list]]:
    """
    Load LAMAP segmentation masks from directory.

    Args:
        lamap_results_dir: Path to lamap_results directory
        period: Period name (e.g., 'bronze_age')

    Returns:
        Tuple of (masks_list, metadata_list)
    """
    from backend.active_learning_loop import ActiveLearningLoop
    from encoders.handcrafted_encoder import HandcraftedEncoder

    period_dir = Path(lamap_results_dir) / period

    # Find all mask files (only .tif files from LAMAP)
    mask_files = sorted(period_dir.glob("*.tif"))

    if not mask_files:
        raise ValueError(f"No mask files found in {period_dir}")

    import numpy as np
    from encoders.handcrafted_encoder import HandcraftedEncoder

    encoder = HandcraftedEncoder()
    masks = []
    metadata = []

    for idx, mask_file in enumerate(mask_files):
        # Load GeoTIFF using rasterio
        import rasterio
        with rasterio.open(mask_file) as src:
            mask = src.read(1)  # Read first band
            mask = mask.astype(np.float32)

        # Handle NaN values
        mask = np.nan_to_num(mask, nan=0.0)

        # Display: Keep original probability values for visualization
        # Store both display version and binary version for encoding
        mask_display = mask.copy()  # For display (probability map)
        mask_binary = (mask > 0.5).astype(np.uint8)  # For analysis

        masks.append(mask_display)

        # Extract features for statistics (use binary version)
        features = encoder.encode(mask_binary)

        # Count connected components
        from scipy import ndimage
        labeled, num_components = ndimage.label(mask_binary)
        components = num_components

        # Calculate coverage (percentage of foreground pixels)
        coverage = (mask_binary.sum() / mask_binary.size) * 100

        # Calculate compactness (4π * area / perimeter²)
        if mask_binary.sum() > 0:
            perimeter = ndimage.binary_erosion(mask_binary).sum()
            area = mask_binary.sum()
            if perimeter > area:
                compactness = (4 * 3.14159 * area) / (perimeter ** 2)
            else:
                compactness = 0.0
        else:
            compactness = 0.0

        # Extract site_id from filename if available
        # Assuming format: site_{id}_*.png or similar
        parts = mask_file.stem.split('_')
        if len(parts) >= 2 and parts[0] == 'site':
            site_id = parts[1][:10]  # Limit to 10 characters
        else:
            # Use just the numeric part if possible
            import re
            numbers = re.findall(r'\d+', mask_file.stem)
            site_id = numbers[0] if numbers else str(idx)

        # Create metadata with statistics
        meta = {
            'Mask ID': f"{idx}",
            'Site': site_id,
            'Coverage': f"{coverage:.1f}%",
            'Components': components,
            'Compactness': f"{compactness:.2f}",
        }

        metadata.append(meta)

    logger.info(f"Loaded {len(masks)} masks from {period_dir}")
    return masks, metadata


def display_error_boundary(title: str = "Error"):
    """
    Decorator to catch and display errors in Streamlit.

    Args:
        title: Error title
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
                st.error(f"**{title}**: {str(e)}")
                st.exception(e)
                return None
        return wrapper
    return decorator


def format_elapsed_time(seconds: float) -> str:
    """
    Format elapsed time in human-readable format.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted time string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def estimate_time_remaining(elapsed: float, current: int, total: int) -> Optional[float]:
    """
    Estimate remaining time based on progress.

    Args:
        elapsed: Elapsed time in seconds
        current: Current progress
        total: Total target

    Returns:
        Estimated remaining time in seconds, or None if unable to estimate
    """
    if current <= 0 or total <= 0:
        return None

    rate = current / elapsed
    if rate <= 0:
        return None

    remaining = (total - current) / rate
    return remaining


def create_comparison_summary(preferences: list) -> Dict[str, Any]:
    """
    Create summary statistics from preferences.

    Args:
        preferences: List of ((i, j), pref) tuples

    Returns:
        Summary dictionary
    """
    if not preferences:
        return {
            'total': 0,
            'left_better': 0,
            'right_better': 0,
            'ties': 0,
            'unique_masks': 0,
        }

    import numpy as np

    total = len(preferences)
    left_better = sum(1 for pref in preferences if pref[2] == 0)
    right_better = sum(1 for pref in preferences if pref[2] == 1)
    ties = sum(1 for pref in preferences if pref[2] == 2)

    # Count unique masks
    all_masks = set()
    for pref in preferences:
        all_masks.add(pref[0])
        all_masks.add(pref[1])

    return {
        'total': total,
        'left_better': left_better,
        'right_better': right_better,
        'ties': ties,
        'unique_masks': len(all_masks),
    }


def display_loading_spinner(message: str, func: Callable, *args, **kwargs) -> Any:
    """
    Display loading spinner while executing function.

    Args:
        message: Message to display
        func: Function to execute
        *args: Function arguments
        **kwargs: Function keyword arguments

    Returns:
        Function result
    """
    with st.spinner(message):
        return func(*args, **kwargs)
