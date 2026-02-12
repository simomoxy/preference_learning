"""
Welcome page for loading LAMAP masks.

Simple data loading interface that hides technical complexity.
"""

import sys
from pathlib import Path


def ensure_2d_mask(mask_array):
    """
    Ensure mask is a 2D grayscale array.

    Handles RGB/RGBA images and various array shapes.

    Args:
        mask_array: numpy array from PIL Image

    Returns:
        2D numpy array (grayscale)
    """
    from PIL import Image
    import numpy as np

    # Remove singleton dimensions
    while mask_array.ndim > 2:
        if mask_array.ndim == 3 and mask_array.shape[2] in [3, 4]:  # RGB or RGBA
            # Convert back to PIL and then to grayscale
            # This is more reliable than manual conversion
            if mask_array.max() <= 1.0:
                # Probability map - convert carefully
                img = Image.fromarray((mask_array * 255).astype(np.uint8))
            else:
                img = Image.fromarray(mask_array.astype(np.uint8))
            img_gray = img.convert('L')
            mask_array = np.array(img_gray)
        else:
            mask_array = np.squeeze(mask_array)

    return mask_array

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import numpy as np
from PIL import Image
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

from ui.theme import render_archaeology_header


def show_welcome_page():
    """
    Display the welcome page for data loading.
    """
    # Apply archaeology theme
    render_archaeology_header(
        "Archaeological Preference Learning",
        "Compare LAMAP predictions to identify the best hyperparameter configurations",
        icon=""
    )

    # Introduction
    st.markdown("""
    <div class="archaeology-card">
        <h2>Welcome, Archaeologist!</h2>
        <p>
            This tool helps you compare different LAMAP (A Locally-Adaptive Model of Archaeological Potential)
            predictions to identify which configurations produce the most plausible archaeological site maps.
        </p>
        <p>
            <strong>Your task:</strong> You will see pairs of site prediction maps side-by-side.
            Simply choose which one looks more plausible for archaeological sites.
        </p>
        <p>
            <strong>Time estimate:</strong> ~20 minutes for all comparisons
        </p>
        <p>
            <strong>Data storage:</strong> Your responses will be automatically uploaded to GitHub
            for the research team to analyze. You can also download a copy for your records.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Data loading section
    st.header("Load Prediction Maps")

    # Period selection
    col1, col2, col3 = st.columns(3)

    with col1:
        period = st.selectbox(
            "Select Archaeological Period",
            options=["bronze_age", "byzantine", "roman"],
            index=0,
            help="Choose which period's predictions to evaluate"
        )

    with col2:
        # Expert identification
        expert_name = st.text_input(
            "Your Name (optional)",
            placeholder="Expert ID",
            help="Enter your name or ID to identify your dataset"
        )

    with col3:
        st.write("")  # Spacer
        st.write("")  # Spacer
        load_button = st.button("Load Predictions", type="primary", use_container_width=True)

    # Load data when button clicked
    if load_button:
        with st.spinner("Loading prediction maps..."):
            success = load_period_data(period, expert_name)

        if not success:
            st.error(f"Could not load prediction maps for {period}. Please check the data directory.")
            return  # Don't continue

    # Show data summary if masks are loaded (regardless of which button was clicked)
    if st.session_state.get('masks_loaded', False):
        st.success(f"Loaded {len(st.session_state.masks)} prediction maps for {period.replace('_', ' ').title()}!")

        # Show data summary
        st.markdown("### Data Summary")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Masks", len(st.session_state.masks))

        with col2:
            st.metric("Target Comparisons", "50")

        with col3:
            st.metric("Expert", expert_name if expert_name else "Anonymous")

        # Preview sample images
        st.markdown("### Sample Predictions")
        st.caption("Here are a few examples of the prediction maps you will evaluate:")

        # Show first 4 masks in a grid
        masks = st.session_state.masks
        sample_indices = [0, 1, 2, 3] if len(masks) >= 4 else list(range(len(masks)))

        col1, col2, col3, col4 = st.columns(4)
        cols = [col1, col2, col3, col4]

        for idx, mask_idx in enumerate(sample_indices):
            with cols[idx]:
                mask = masks[mask_idx]
                # Normalize for display
                mask_display = (mask - mask.min()) / (mask.max() - mask.min() + 1e-8)
                st.image(mask_display, clamp=True, width="stretch")
                st.caption(f"Mask {mask_idx + 1}")

        st.markdown("---")

        # Start button
        st.markdown("### Ready to Start?")
        if st.button("Begin Comparisons", type="primary", use_container_width=True, key="begin_comparisons_button"):
            st.session_state.current_step = 'compare'
            st.session_state.comparisons_completed = 0
            st.session_state.comparisons_total = 30  # Updated to 30 configs
            st.session_state.preferences = []
            st.session_state.current_pair_idx = 0

            # Store masks for later use (avoid recomputing)
            st.session_state.masks_for_comparison = masks

            # Always use random pairs for reproducibility
            st.session_state.active_loop = None
            st.session_state.use_active_learning = False
            st.session_state.comparison_pairs = generate_comparison_pairs(len(masks), 50)

            st.rerun()

        # Stop here - don't show instructions if data is loaded
        return

    # Instructions
    st.markdown("---")
    st.markdown("### How It Works")
    st.markdown("""
    1. **Select Period:** Choose which archaeological period to evaluate
    2. **Load Data:** Click "Load Predictions" to load probability maps
    3. **Compare:** You will see pairs of predictions side-by-side
    4. **Choose:** Select which prediction looks more plausible for archaeological sites
    5. **View Results:** After 50 comparisons, see your preferences
    """)

    st.markdown("#### Tips for Comparing Predictions")
    st.markdown("""
    - Look for **compact, coherent site shapes** (not scattered pixels)
    - Prefer predictions that **match known archaeological patterns**
    - Consider **spatial autocorrelation** (nearby pixels should be similar)
    - Trust your intuition - if it "looks right", it probably is!
    """)


def load_period_data(period: str, expert_name: str) -> bool:
    """
    Load LAMAP prediction masks for a specific period.

    Data sources (tried in order):
    1. Local files (fastest, most reliable)
    2. GitHub (for deployment)
    3. Dropbox (if configured)

    Args:
        period: Archaeological period (bronze_age, byzantine, roman)
        expert_name: Name/ID of the expert

    Returns:
        True if successful, False otherwise
    """
    try:
        masks, metadata = None, None

        # Check if GitHub mode is forced
        force_github = st.session_state.get('force_github', False)

        # 1. Try GitHub FIRST if forced or for deployment
        import os

        if force_github:
            st.info("Forcing GitHub mode (for testing)")

        github_repo = os.getenv("GITHUB_DATA_REPO", "simomoxy/lamap-bronze-age-data")
        github_branch = os.getenv("GITHUB_BRANCH", "main")
        github_path = os.getenv("GITHUB_PATH", "")  # Empty = root of repo

        if github_repo and (force_github or masks is None):
            try:
                st.info(f"Loading from GitHub ({github_repo})...")
                from github_loader import load_from_github

                masks, metadata = load_from_github(
                    repo=github_repo,
                    branch=github_branch,
                    path=github_path
                )

                if masks is not None:
                    logger.info(f"Loaded {len(masks)} masks from GitHub")
                    st.session_state.data_source = f"GitHub ({github_repo})"
                else:
                    if force_github:
                        st.error("GitHub loading failed!")
                        return False
                    st.warning("GitHub loading failed or timed out. Trying local files...")
            except ImportError:
                logger.warning("github_loader not available")
                if force_github:
                    st.error("GitHub loader not available!")
                    return False
            except Exception as e:
                logger.warning(f"GitHub loading failed: {e}")
                if force_github:
                    st.error(f"GitHub unavailable: {str(e)}")
                    return False
                st.warning(f"GitHub unavailable: {str(e)}")

        # 2. Try LOCAL files if GitHub failed and not forced
        if masks is None and not force_github:
            local_dir = Path(__file__).parent.parent.parent / period
            if not local_dir.exists():
                local_dir = Path(__file__).parent.parent / period

            if local_dir.exists():
                try:
                    st.info(f"Loading from local files...")
                    masks, metadata = load_from_local(local_dir)
                    if masks is not None:
                        logger.info(f"Loaded {len(masks)} masks from local files")
                        st.session_state.data_source = "Local"
                except Exception as e:
                    logger.warning(f"Local loading failed: {e}")

        # 3. Try Dropbox as last resort
        if masks is None:
            try:
                from dropbox_loader import load_dropbox_config, load_from_dropbox
                dropbox_config = load_dropbox_config()

                if dropbox_config and period in dropbox_config:
                    st.info("Loading from Dropbox...")
                    shared_url = dropbox_config[period]['shared_url']
                    filenames = dropbox_config[period].get('files', [])

                    masks, metadata = load_from_dropbox(shared_url, filenames)
                    if masks is not None:
                        logger.info(f"Loaded {len(masks)} masks from Dropbox")
                        st.session_state.data_source = "Dropbox"
            except ImportError:
                pass
            except Exception as e:
                logger.warning(f"Dropbox loading failed: {e}")

        # Check if loading succeeded
        if masks is None or len(masks) == 0:
            logger.error("No masks could be loaded from any source")
            st.error(f"""
            ### Could not load prediction maps for {period}

            **Troubleshooting:**

            1. **Local files (recommended):**
               - Place PNG files in: `{local_dir}`
               - Expected: 26 PNG files

            2. **GitHub:**
               - Set `GITHUB_DATA_REPO` environment variable
               - Default: `simomoxy/lamap-bronze-age-data`
               - Verify internet connection

            3. **Dropbox:**
               - Configure `dropbox_config.json`
               - Share folder with "Anyone with link" permissions
            """)
            return False

        # Store masks in session state (already compressed from loader)
        st.session_state.masks = masks
        st.session_state.mask_metadata = metadata
        st.session_state.period = period
        st.session_state.expert_name = expert_name if expert_name else "Anonymous"
        st.session_state.masks_loaded = True

        total_memory_mb = sum(m.nbytes for m in masks) // 1024 // 1024
        logger.info(f"Loaded {len(masks)} masks (~{total_memory_mb}MB total)")
        return True

    except Exception as e:
        logger.error(f"Error loading period data: {e}", exc_info=True)
        st.error(f"Error loading data: {str(e)}")
        return False


def load_from_local(data_dir: Path):
    """
    Load masks from local directory.

    Args:
        data_dir: Path to directory containing PNG files

    Returns:
        Tuple of (masks list, metadata list) or (None, None) if failed
    """
    try:
        # Load all PNG files
        mask_files = sorted(data_dir.glob("*.png"))

        if len(mask_files) == 0:
            return None, None

        # Load masks
        masks = []
        metadata = []

        for mask_file in mask_files[:50]:  # Limit to 50 masks
            img = Image.open(mask_file)
            mask_array = np.array(img)

            # Ensure 2D using helper function
            mask_array = ensure_2d_mask(mask_array)

            # COMPRESS: Downsample to 1/4 resolution
            if mask_array.shape[0] > 1000:
                try:
                    from skimage.transform import resize
                    mask_array = resize(mask_array, (mask_array.shape[0]//4, mask_array.shape[1]//4),
                                   preserve_range=True, anti_aliasing=True)
                except ImportError:
                    mask_array = mask_array[::4, ::4]

            # Convert to uint8 to save memory
            if mask_array.dtype in [np.float64, np.float32, np.float16]:
                if mask_array.max() <= 1.0:
                    mask_array = (mask_array * 255).astype(np.uint8)
                else:
                    mask_array = mask_array.astype(np.uint8)

            masks.append(mask_array)

            # Extract metadata from filename
            mask_id = mask_file.stem
            metadata.append({
                'Mask ID': mask_id,
                'File': str(mask_file.name)
            })

        return masks, metadata

    except Exception as e:
        logger.error(f"Error loading from local: {e}", exc_info=True)
        return None, None


def generate_comparison_pairs(num_masks: int, num_pairs: int) -> List[tuple]:
    """
    Generate random pairs for comparison.

    Args:
        num_masks: Total number of masks
        num_pairs: Number of pairs to generate

    Returns:
        List of (idx_a, idx_b) tuples
    """
    import random

    pairs = []
    seen = set()

    while len(pairs) < num_pairs:
        idx_a = random.randint(0, num_masks - 1)
        idx_b = random.randint(0, num_masks - 1)

        # Ensure different masks and no duplicate pairs
        if idx_a != idx_b:
            # Create ordered tuple to avoid duplicates (a,b) vs (b,a)
            pair = tuple(sorted((idx_a, idx_b)))

            if pair not in seen:
                seen.add(pair)
                pairs.append((idx_a, idx_b))

    return pairs
