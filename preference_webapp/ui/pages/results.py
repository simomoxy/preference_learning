"""
Results page for displaying rankings and analysis.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Import UI components
from ui.components import (
    display_single_image,
    metrics_plot,
    ranking_table,
    export_buttons,
    acquisition_history_plot,
    learning_curves_plot
)
from ui.utils import format_timestamp, get_session_summary


def show_results_page():
    """
    Display the results page.
    """
    st.title("📈 Results")
    st.markdown("View ranking and analysis of segmentation masks.")

    # Check if session exists
    if st.session_state.active_learning_loop is None:
        st.warning("No active session. Please go to Configuration page to start a session.")
        if st.button("Go to Configuration"):
            st.session_state.current_page = 'config'
            st.rerun()
        return

    loop = st.session_state.active_learning_loop

    # Get ranking if not already computed
    if st.session_state.ranking is None or st.session_state.scores is None:
        try:
            ranking, scores = loop.get_ranking()
            st.session_state.ranking = ranking
            st.session_state.scores = scores
        except Exception as e:
            st.error(f"Error computing ranking: {str(e)}")
            logger.error(f"Error computing ranking: {e}", exc_info=True)
            return

    ranking = st.session_state.ranking
    scores = st.session_state.scores

    # Progress summary
    progress = loop.get_progress()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Comparisons", progress['total_comparisons'])

    with col2:
        st.metric("Iteration", progress['iteration'])

    with col3:
        if progress['converged']:
            st.success("✓ Converged")
        else:
            st.caption("Convergence: In progress")

    st.markdown("---")

    # Session info
    session_info = {
        'session_id': st.session_state.session_id,
        'config': st.session_state.config,
        'iteration': progress['iteration'],
        'total_comparisons': progress['total_comparisons'],
        'converged': progress['converged'],
    }

    # Ranking table
    st.header("Mask Ranking")

    ranking_table(
        ranking,
        scores,
        metadata=st.session_state.mask_metadata,
        key="main_ranking_table"
    )

    st.markdown("---")

    # Manual mask selection (since table selection not supported)
    st.header("View Mask Details")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("**Selection**")
        # Get top-K masks for selection
        # Initialize selected_rank from session state if not set
        if 'selected_rank' not in st.session_state:
            st.session_state.selected_rank = 1

        top_k_selection = st.number_input(
            "Select Rank",
            min_value=1,
            max_value=len(ranking),
            value=st.session_state.selected_rank,
            step=1,
            help="Enter rank to view that mask",
            key="rank_number_input"
        )

        # Update session state when number input changes
        st.session_state.selected_rank = int(top_k_selection)

        # Convert rank to index
        if 1 <= top_k_selection <= len(ranking):
            selected_mask_idx = ranking[top_k_selection - 1]
        else:
            selected_mask_idx = ranking[0]

        # Show top 5 quick links
        st.markdown("**Quick Select Top-5:**")
        for i in range(min(5, len(ranking))):
            if st.button(f"#{i+1}", key=f"quick_{i}"):
                st.session_state.selected_rank = i + 1
                st.rerun()

    with col2:
        # Display selected mask
        if selected_mask_idx is not None:
            masks = st.session_state.masks
            metadata = st.session_state.mask_metadata

            mask = masks[selected_mask_idx]
            rank = np.where(ranking == selected_mask_idx)[0][0] + 1
            score = scores[selected_mask_idx]

            subcol1, subcol2 = st.columns([2, 1])

            with subcol1:
                # Normalize for display
                mask_display = (mask - mask.min()) / (mask.max() - mask.min() + 1e-8)
                st.image(mask_display, clamp=True)

                st.markdown(f"**Mask {selected_mask_idx}** - Rank #{rank}, Score: {score:.4f}")

            with subcol2:
                st.markdown("**Statistics**")
                st.caption(f"Rank: #{rank}")
                st.caption(f"Copeland Score: {score:.4f}")
                st.caption(f"Mask ID: {selected_mask_idx}")

                if metadata and selected_mask_idx < len(metadata):
                    meta = metadata[selected_mask_idx]
                    st.markdown("**Metadata**")
                    for key, value in meta.items():
                        st.caption(f"{key}: {value}")

                # Show which pairs contributed to ranking
                st.markdown("**Contributing Pairs**")
                contributing_pairs = get_contributing_pairs(selected_mask_idx, loop.preferences)
                if contributing_pairs:
                    for pair in contributing_pairs[:5]:  # Show first 5
                        st.caption(f"vs Mask {pair}")
                    if len(contributing_pairs) > 5:
                        st.caption(f"... and {len(contributing_pairs) - 5} more")
                else:
                    st.caption("No direct comparisons")

    st.markdown("---")

    # Metrics plots
    st.header("Metrics Visualization")

    # Copeland scores plot
    col1, col2 = st.columns(2)

    with col1:
        top_k = st.number_input(
            "Show Top-K",
            min_value=5,
            max_value=len(ranking),
            value=min(20, len(ranking)),
            step=5
        )

    with col2:
        st.write("")  # Spacer

    metrics_plot(ranking, scores, title="Copeland Scores", top_k=top_k)

    st.markdown("---")

    # Learning curves and acquisition history
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Learning Curves")
        if loop.ranking_history:
            learning_curves_plot(loop.ranking_history)
        else:
            st.info("No learning history available")

    with col2:
        st.subheader("Acquisition History")
        if loop.ranking_history:
            acquisition_history_plot(loop.ranking_history)
        else:
            st.info("No acquisition history available")

    st.markdown("---")

    # Export buttons
    st.header("Export Options")

    export_buttons(session_info, st.session_state.masks)


def get_contributing_pairs(mask_idx: int, preferences: list) -> list:
    """
    Get list of masks that were compared with the given mask.

    Args:
        mask_idx: Index of mask
        preferences: List of ((i, j), pref) tuples

    Returns:
        List of mask indices that were compared with mask_idx
    """
    contributing = []

    for (i, j), pref in preferences:
        if i == mask_idx:
            contributing.append(j)
        elif j == mask_idx:
            contributing.append(i)

    return contributing


def show_comparison_history(mask_idx: int, preferences: list, masks: list):
    """
    Show detailed comparison history for a mask.

    Args:
        mask_idx: Index of mask
        preferences: List of ((i, j), pref) tuples
        masks: List of all masks
    """
    st.subheader("Comparison History")

    comparisons = []

    for (i, j), pref in preferences:
        if i == mask_idx or j == mask_idx:
            opponent_idx = j if i == mask_idx else i

            # Determine result
            if i == mask_idx:
                # mask_idx is i
                if pref == 0:
                    result = "Won"
                elif pref == 1:
                    result = "Lost"
                else:
                    result = "Tie"
            else:
                # mask_idx is j
                if pref == 0:
                    result = "Lost"
                elif pref == 1:
                    result = "Won"
                else:
                    result = "Tie"

            comparisons.append({
                'Opponent': opponent_idx,
                'Result': result,
                'Preference': pref
            })

    if comparisons:
        df = pd.DataFrame(comparisons)
        st.dataframe(df)
    else:
        st.info("No comparisons found")


def show_mask_details(mask_idx: int, masks: list, metadata: list = None):
    """
    Show detailed information about a specific mask.

    Args:
        mask_idx: Index of mask
        masks: List of masks
        metadata: Optional list of metadata
    """
    mask = masks[mask_idx]

    col1, col2 = st.columns([2, 1])

    with col1:
        st.image(mask, clamp=True)

    with col2:
        st.markdown("**Mask Statistics**")

        # Basic statistics
        st.caption(f"Shape: {mask.shape}")
        st.caption(f"Dtype: {mask.dtype}")
        st.caption(f"Min: {mask.min()}, Max: {mask.max}")
        st.caption(f"Mean: {mask.mean():.4f}")
        st.caption(f"Std: {mask.std():.4f}")

        # Advanced statistics
        if mask.ndim == 2:
            from scipy import ndimage

            # Connected components
            labeled, num_features = ndimage.label(mask)
            st.caption(f"Components: {num_features}")

            # Area
            area = np.sum(mask > 0)
            st.caption(f"Foreground Area: {area}")

            # Perimeter (approximate)
            from skimage.measure import perimeter
            try:
                peri = perimeter(mask.astype(bool))
                st.caption(f"Perimeter: {peri:.1f}")

                if area > 0:
                    ratio = peri / np.sqrt(area)
                    st.caption(f"Perimeter/√Area: {ratio:.4f}")
            except ImportError:
                st.caption("Perimeter: N/A (skimage not available)")

    # Metadata
    if metadata and mask_idx < len(metadata):
        st.markdown("**Metadata**")
        for key, value in metadata[mask_idx].items():
            st.caption(f"{key}: {value}")
