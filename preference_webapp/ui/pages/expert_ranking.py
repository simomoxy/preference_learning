"""
Expert ranking page for validating PBO recommendations.

After completing pairwise comparisons, experts rank the top 5 PBO-recommended
configurations to validate the model's predictions.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import numpy as np
import logging
from scipy.stats import kendalltau

logger = logging.getLogger(__name__)

from ui.theme import render_progress_indicator, COLORS


def train_simple_gp_on_preferences(preferences, num_masks):
    """
    Train a simple GP model on collected preferences.

    This is a simplified version that ranks masks based on pairwise wins.

    Args:
        preferences: List of preference dictionaries
        num_masks: Total number of masks

    Returns:
        Tuple of (ranking, scores) - ranking is sorted by preference
    """
    # Track wins/losses for each mask
    stats = {i: {'wins': 0, 'losses': 0, 'ties': 0} for i in range(num_masks)}

    for pref in preferences:
        if pref['preference'] == -1:  # Skip
            continue
        elif pref['preference'] == 2:  # Tie
            stats[pref['idx_a']]['ties'] += 1
            stats[pref['idx_b']]['ties'] += 1
        elif pref['preference'] == 0:  # Left (a) wins
            stats[pref['idx_a']]['wins'] += 1
            stats[pref['idx_b']]['losses'] += 1
        elif pref['preference'] == 1:  # Right (b) wins
            stats[pref['idx_b']]['wins'] += 1
            stats[pref['idx_a']]['losses'] += 1

    # Compute score (win rate)
    ranking = []
    for idx in range(num_masks):
        total_games = stats[idx]['wins'] + stats[idx]['losses'] + stats[idx]['ties']
        if total_games > 0:
            score = (stats[idx]['wins'] + 0.5 * stats[idx]['ties']) / total_games
        else:
            score = 0.0

        ranking.append({
            'idx': idx,
            'score': score,
            'wins': stats[idx]['wins'],
            'losses': stats[idx]['losses'],
            'ties': stats[idx]['ties']
        })

    # Sort by score descending
    ranking.sort(key=lambda x: x['score'], reverse=True)

    # Extract ranking and scores
    ranked_indices = [r['idx'] for r in ranking]
    scores = np.array([r['score'] for r in ranking])

    return ranked_indices, scores


def show_expert_ranking_page():
    """
    Display the expert ranking page.
    """
    # Check if data exists
    if 'preferences' not in st.session_state or len(st.session_state.preferences) == 0:
        st.warning("No preference data found. Please complete comparisons first.")
        if st.button("Go to Comparisons", use_container_width=True):
            st.session_state.current_step = 'compare'
            st.rerun()
        return

    # Apply theme
    render_progress_indicator(
        current_step=3,
        total_steps=4,
        step_names=['Load Data', 'Compare', 'Ranking', 'Summary']
    )

    st.markdown("---")

    # Header
    st.markdown(f"""
    <div style="text-align: center; margin: 2rem 0;">
        <h1 style="color: {COLORS['text']};">Verify PBO Recommendations</h1>
        <p style="color: {COLORS['text']}; font-size: 1.1rem;">
            Based on your preferences, PBO recommends these 5 configurations.
            Please rank them from best (1) to worst (5).
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Train GP and get top 5
    preferences = st.session_state.preferences
    num_masks = len(st.session_state.masks)

    with st.spinner("Training model on your preferences..."):
        ranking, scores = train_simple_gp_on_preferences(preferences, num_masks)

    # Get top 5
    top_5_indices = ranking[:5]

    st.markdown("---")

    # Ranking interface
    st.markdown("### Rank the Top 5 Configurations")
    st.caption("Use the selector to browse each configuration, then assign your ranking below.")

    # Selector to browse configurations
    config_labels = [f"PBO Rank #{i+1} — Mask #{top_5_indices[i]+1}" for i in range(5)]
    selected_label = st.selectbox(
        "Select configuration to view",
        options=config_labels,
        key="ranking_viewer_select"
    )
    selected_position = config_labels.index(selected_label)
    selected_idx = top_5_indices[selected_position]

    # Display the selected mask
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="background-color: {COLORS['accent']}; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; text-align: center;">
            <h3 style="margin: 0;">PBO Rank #{selected_position + 1}</h3>
            <p style="margin: 0.5rem 0 0 0;">Mask #{selected_idx + 1} &nbsp;|&nbsp; PBO Score: {scores[selected_idx]:.3f}</p>
        </div>
        """, unsafe_allow_html=True)

        masks = st.session_state.masks
        mask = np.array(masks[selected_idx], copy=True)
        mask_display = (mask - mask.min()) / (mask.max() - mask.min() + 1e-8)
        st.image(mask_display, clamp=True, width="stretch", output_format="PNG")

    st.markdown("---")

    # Ranking selectors for all 5
    st.markdown("### Assign Your Rankings")
    st.caption("Select a rank (1 = best, 5 = worst) for each configuration. Each rank must be used exactly once.")

    rank_options = [1, 2, 3, 4, 5]
    expert_ranks = {}

    cols = st.columns(5)
    for position, idx in enumerate(top_5_indices):
        with cols[position]:
            rank = st.selectbox(
                f"Mask #{idx + 1}",
                options=rank_options,
                index=position,
                key=f"expert_rank_{idx}",
                help=f"PBO Rank #{position + 1}"
            )
            expert_ranks[idx] = rank

    st.markdown("---")

    # Qualitative feedback section
    st.markdown("### Optional Feedback")
    st.caption("Help us understand what features you noticed when comparing predictions")

    qualitative_feedback = st.text_area(
        "What features did you notice when comparing predictions?",
        placeholder="Example: 'I preferred configurations with compact, clustered sites rather than scattered pixels. I also looked for realistic spatial patterns that match known archaeological distributions...'",
        height=150,
        key="qualitative_feedback"
    )

    st.markdown("---")

    # Confirm button
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.button("Confirm Rankings", type="primary", use_container_width=True):
            # Validate rankings (should be 1-5 each exactly once)
            rank_values = list(expert_ranks.values())
            if sorted(rank_values) != [1, 2, 3, 4, 5]:
                st.error("Please use each rank (1-5) exactly once!")
                return

            # Calculate agreement
            pbo_ranks = list(range(1, 6))  # PBO ranking is 1,2,3,4,5
            expert_ranks_list = [expert_ranks[idx] for idx in top_5_indices]

            tau, p_value = kendalltau(pbo_ranks, expert_ranks_list)

            # Save to session state
            st.session_state.expert_ranking_validation = {
                'pbo_ranking': top_5_indices,
                'expert_ranking': expert_ranks,
                'kendall_tau': float(tau) if not np.isnan(tau) else 0.0,
                'p_value': float(p_value) if not np.isnan(p_value) else 1.0
            }

            # Save qualitative feedback
            if qualitative_feedback:
                st.session_state.qualitative_feedback = qualitative_feedback

            # Navigate to summary
            st.session_state.current_step = 'summary'
            st.rerun()


def get_top_5_for_ranking():
    """
    Get top 5 masks for ranking page.

    Returns:
        List of 5 mask indices
    """
    if 'preferences' not in st.session_state or len(st.session_state.preferences) == 0:
        return []

    preferences = st.session_state.preferences
    num_masks = len(st.session_state.masks)

    ranking, _ = train_simple_gp_on_preferences(preferences, num_masks)

    return ranking[:5]
