"""
Main Streamlit application for preference learning webapp.

Multi-page navigation with session state management.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page imports
from ui.pages.config import show_config_page
from ui.pages.collect import show_collect_page
from ui.pages.train import show_train_page
from ui.pages.results import show_results_page

# Configure Streamlit page
st.set_page_config(
    page_title="Preference Learning for Archaeological Segmentation",
    page_icon="🏺",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """
    Initialize Streamlit session state variables.
    """
    # Core session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'config'

    if 'session_id' not in st.session_state:
        st.session_state.session_id = None

    if 'config' not in st.session_state:
        st.session_state.config = {}

    # Data collection state
    if 'current_batch' not in st.session_state:
        st.session_state.current_batch = []

    if 'batch_preferences' not in st.session_state:
        st.session_state.batch_preferences = {}

    if 'batch_count' not in st.session_state:
        st.session_state.batch_count = 0

    if 'total_comparisons' not in st.session_state:
        st.session_state.total_comparisons = 0

    if 'review_queue' not in st.session_state:
        st.session_state.review_queue = []

    # Backend components
    if 'active_learning_loop' not in st.session_state:
        st.session_state.active_learning_loop = None

    if 'masks' not in st.session_state:
        st.session_state.masks = None

    if 'mask_metadata' not in st.session_state:
        st.session_state.mask_metadata = None

    # Training state
    if 'training_progress' not in st.session_state:
        st.session_state.training_progress = {}

    if 'training_logs' not in st.session_state:
        st.session_state.training_logs = []

    # Results state
    if 'ranking' not in st.session_state:
        st.session_state.ranking = None

    if 'scores' not in st.session_state:
        st.session_state.scores = None

    if 'selected_mask_idx' not in st.session_state:
        st.session_state.selected_mask_idx = None

    # UI state
    if 'auto_save_enabled' not in st.session_state:
        st.session_state.auto_save_enabled = True

    if 'last_save_time' not in st.session_state:
        st.session_state.last_save_time = None


def show_sidebar():
    """
    Display sidebar with session information and navigation.
    """
    with st.sidebar:
        st.title("🏺 Preference Learning")
        st.markdown("---")

        # Session information
        if st.session_state.session_id:
            st.success(f"**Session:** {st.session_state.session_id}")

            # Progress summary
            if st.session_state.active_learning_loop:
                progress = st.session_state.active_learning_loop.get_progress()
                st.info(f"**Iteration:** {progress['iteration']}/{progress['max_iterations']}")
                st.info(f"**Comparisons:** {progress['total_comparisons']}")

                if progress['converged']:
                    st.success("✓ Converged")

        st.markdown("---")

        # Quick stats
        if st.session_state.masks is not None:
            st.metric("Total Masks", len(st.session_state.masks))

        if st.session_state.current_batch:
            st.metric("Current Batch", len(st.session_state.current_batch))

        st.markdown("---")

        # Navigation info
        st.markdown("### Navigation")
        st.caption("Use the page selector to navigate between steps.")


def main():
    """
    Main application entry point.
    """
    # Initialize session state
    initialize_session_state()

    # Show sidebar
    show_sidebar()

    # Multi-page navigation
    # Note: st.navigation is available in Streamlit 1.28+
    # We'll use a simpler approach with st.page_select for compatibility
    pages = {
        "⚙️ Configuration": "config",
        "📊 Collect Data": "collect",
        "🔄 Training": "train",
        "📈 Results": "results",
    }

    # Page selector in sidebar
    with st.sidebar:
        st.markdown("### Pages")
        selected_page_name = st.selectbox(
            "Select a page",
            options=list(pages.keys()),
            index=list(pages.values()).index(st.session_state.current_page),
            key="page_selector"
        )

    # Update current page
    st.session_state.current_page = pages[selected_page_name]

    # Show selected page
    if st.session_state.current_page == "config":
        show_config_page()
    elif st.session_state.current_page == "collect":
        show_collect_page()
    elif st.session_state.current_page == "train":
        show_train_page()
    elif st.session_state.current_page == "results":
        show_results_page()

    # Footer
    st.markdown("---")
    st.caption(
        "Preference Learning for Archaeological Image Segmentation | "
        "Preferential Bayesian Optimization (PBO)"
    )


if __name__ == "__main__":
    main()
