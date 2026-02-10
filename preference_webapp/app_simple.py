"""
Main Streamlit application for simplified preference learning webapp.

Step-by-step wizard interface for archaeologists.
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

# Import theme
from ui.theme import apply_theme, get_theme_config

# Page imports
from ui.pages.welcome import show_welcome_page
from ui.pages.collect_simple import show_collect_page
from ui.pages.summary import show_summary_page

# Configure Streamlit page
st.set_page_config(
    page_title="Archaeological Preference Learning",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def initialize_session_state():
    """
    Initialize Streamlit session state variables.
    """
    # Current step in wizard
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 'welcome'

    # Data loading state
    if 'masks_loaded' not in st.session_state:
        st.session_state.masks_loaded = False

    if 'masks' not in st.session_state:
        st.session_state.masks = None

    if 'mask_metadata' not in st.session_state:
        st.session_state.mask_metadata = None

    # Expert info
    if 'expert_name' not in st.session_state:
        st.session_state.expert_name = ""

    if 'period' not in st.session_state:
        st.session_state.period = ""

    # Comparison state
    if 'comparisons_completed' not in st.session_state:
        st.session_state.comparisons_completed = 0

    if 'comparisons_total' not in st.session_state:
        st.session_state.comparisons_total = 50

    if 'current_pair_idx' not in st.session_state:
        st.session_state.current_pair_idx = 0

    if 'comparison_pairs' not in st.session_state:
        st.session_state.comparison_pairs = []

    if 'preferences' not in st.session_state:
        st.session_state.preferences = []

    # GitHub mode toggle
    if 'force_github' not in st.session_state:
        st.session_state.force_github = False


def show_header():
    """
    Show consistent header across all pages.
    """
    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        pass  # Empty spacer

    with col2:
        st.markdown("""
        <div style="text-align: center;">
            <h2 style="color: #C97B63; margin: 0;">Archaeological Preference Learning</h2>
            <p style="color: #3D3B30; margin: 0.5rem 0 0 0; font-size: 1.1rem; font-weight: 500;">
                Evaluating LAMAP predictions through expert comparisons
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        # Expert info in top right
        if st.session_state.expert_name:
            st.caption(f"Expert: {st.session_state.expert_name}")


def show_sidebar():
    """
    Display simplified sidebar with basic info.
    """
    with st.sidebar:
        st.markdown("---")
        st.markdown("### Session Info")

        if st.session_state.period:
            st.info(f"**Period:** {st.session_state.period.replace('_', ' ').title()}")

        if st.session_state.masks and st.session_state.masks_loaded:
            st.success(f"**Masks:** {len(st.session_state.masks)} loaded")

        if 'comparisons_completed' in st.session_state:
            st.metric(
                "Completed",
                f"{st.session_state.comparisons_completed}/{st.session_state.comparisons_total}"
            )

        st.markdown("---")

        # Data source toggle
        st.markdown("### Data Source")
        st.session_state.force_github = st.checkbox(
            "Force GitHub (for testing)",
            value=st.session_state.get('force_github', False),
            help="Enable to test GitHub loading instead of local files"
        )

        if st.session_state.force_github:
            st.caption("Will load from GitHub")

        st.markdown("---")

        # Navigation help
        st.markdown("### Navigation")
        st.caption("Use the buttons on each page to move between steps.")


def main():
    """
    Main application entry point.
    """
    # Apply theme
    apply_theme()

    # Initialize session state
    initialize_session_state()

    # Show header
    show_header()

    st.markdown("---")

    # Show sidebar
    show_sidebar()

    # Route to appropriate page
    if st.session_state.current_step == 'welcome':
        show_welcome_page()
    elif st.session_state.current_step == 'compare':
        show_collect_page()
    elif st.session_state.current_step == 'summary':
        show_summary_page()
    else:
        # Default to welcome
        st.session_state.current_step = 'welcome'
        show_welcome_page()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem; padding: 1rem;">
        Archaeological Preference Learning | Preferential Bayesian Optimization (PBO)
        <br>
        For questions, contact the research team
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
