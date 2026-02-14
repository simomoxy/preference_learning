"""
Simplified data collection page for pairwise comparisons.

Focused, clean interface designed for archaeologists with minimal technical jargon.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import numpy as np
import logging

logger = logging.getLogger(__name__)

from ui.theme import render_progress_indicator, COLORS


# Use the same encoder as HPC experiments (7D normalized features)
def compute_mask_statistics(mask_idx):
    """
    Compute statistics for a mask using the same SegmentationFeatureEncoder
    as the GP/Bradley-Terry experiments (7D normalized [0,1] features).
    """
    from models.toy_encoder import SegmentationFeatureEncoder

    try:
        masks = st.session_state.masks
        mask = masks[mask_idx]

        # Ensure 2D grayscale float in [0, 1]
        mask_2d = np.squeeze(np.array(mask))
        if mask_2d.ndim == 3:
            mask_2d = np.mean(mask_2d, axis=2)
        mask_float = mask_2d.astype(float)
        if mask_float.max() > 1.0:
            mask_float = mask_float / 255.0

        # Use the same encoder as experiments
        encoder = SegmentationFeatureEncoder()
        features = encoder.encode(mask_float)  # 7D normalized [0, 1]
        names = encoder.get_feature_names()

        return {name: round(float(val), 3) for name, val in zip(names, features)}

    except Exception as e:
        logger.error(f"Error computing statistics for mask {mask_idx}: {e}", exc_info=True)
        return {
            'morans_i': 0.0, 'components': 0.0, 'area': 0.0,
            'variance': 0.0, 'perimeter_ratio': 0.0,
            'entropy': 0.0, 'mean_confidence': 0.0,
        }


def show_collect_page():
    """
    Display the simplified comparison page.
    """
    # Check if data is loaded
    if 'masks' not in st.session_state or not st.session_state.masks_loaded:
        st.warning("Please load prediction maps first.")
        if st.button("Go to Data Loading"):
            st.session_state.current_step = 'welcome'
            st.rerun()
        return

    # Initialize ActiveLearningLoop if needed (deferred from welcome page to avoid freeze)
    use_active_learning = st.session_state.get('use_active_learning', False)
    if use_active_learning and st.session_state.get('active_loop') is None:
        # Get masks - use stored version to avoid recomputing
        if 'masks_for_comparison' in st.session_state:
            masks = st.session_state.masks_for_comparison
        else:
            masks = st.session_state.masks

        with st.spinner("Initializing active learning model (this takes a moment)..."):
            from backend.active_learning_loop import ActiveLearningLoop

            config = {
                'encoder': 'handcrafted',
                'strategy': 'gp',
                'acquisition': 'thompson_sampling',
                'max_iterations': 100,
                'n_pairs_per_iteration': 10,
            }

            st.session_state.active_loop = ActiveLearningLoop(masks, config)
            st.session_state.masks = masks  # Ensure masks are set

        # Clear the spinner after initialization
        st.rerun()
        return

    # Apply theme
    render_progress_indicator(
        current_step=2,
        total_steps=4,
        step_names=['Load Data', 'Compare', 'Ranking', 'Summary']
    )

    st.markdown("---")

    # Progress header
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.header(f"Comparison {st.session_state.comparisons_completed + 1} of {st.session_state.comparisons_total}")

    with col2:
        progress_pct = (st.session_state.comparisons_completed / st.session_state.comparisons_total) * 100
        st.metric("Progress", f"{progress_pct:.0f}%")

    with col3:
        st.metric("Remaining", st.session_state.comparisons_total - st.session_state.comparisons_completed)

    # Progress bar
    st.progress(st.session_state.comparisons_completed / st.session_state.comparisons_total)

    st.markdown("---")

    # Check if all comparisons are done
    if st.session_state.comparisons_completed >= st.session_state.comparisons_total:
        show_completion_message()
        return

    # Get current pair (support active learning adaptive batches)
    active_loop = st.session_state.get('active_loop')

    if active_loop is not None:
        # Active learning mode: get next batch when needed
        if st.session_state.current_pair_idx >= len(st.session_state.comparison_pairs):
            # Need more pairs - get next batch from active learning loop
            if st.session_state.comparisons_completed >= 10:  # Only train after some preferences
                # Train model and get new pairs
                try:
                    new_pairs = active_loop.get_next_batch(n_pairs=10)
                    st.session_state.comparison_pairs.extend(new_pairs)
                except Exception as e:
                    logger.error(f"Error getting next batch: {e}")
                    # Fall back to random pairs
                    from welcome import generate_comparison_pairs
                    remaining = st.session_state.comparisons_total - st.session_state.comparisons_completed
                    new_pairs = generate_comparison_pairs(len(st.session_state.masks), min(remaining, 10))
                    st.session_state.comparison_pairs.extend(new_pairs)
            else:
                # Not enough data yet - use random pairs
                from welcome import generate_comparison_pairs
                remaining = st.session_state.comparisons_total - st.session_state.comparisons_completed
                new_pairs = generate_comparison_pairs(len(st.session_state.masks), min(remaining, 10))
                st.session_state.comparison_pairs.extend(new_pairs)

    # Get current pair
    pairs = st.session_state.comparison_pairs
    current_idx = st.session_state.current_pair_idx

    if current_idx >= len(pairs):
        show_completion_message()
        return

    idx_a, idx_b = pairs[current_idx]
    masks = st.session_state.masks

    # Record when this comparison was first shown (for timing)
    comparison_key = f"comparison_{current_idx}"
    if comparison_key not in st.session_state:
        from datetime import datetime
        st.session_state[comparison_key] = {
            'shown_at': datetime.now().isoformat()
        }

    mask_a = masks[idx_a]
    mask_b = masks[idx_b]

    # Compute statistics (cached for performance)
    stats_a = compute_mask_statistics(idx_a)
    stats_b = compute_mask_statistics(idx_b)

    # Preference buttons AT THE TOP
    st.markdown("### Your Preference")

    # Use custom CSS for button styling
    st.markdown(f"""
    <style>
    .stButton button {{
        height: 3rem;
        font-size: 1rem;
        font-weight: 600;
    }}
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Left Option Better", type="primary", use_container_width=True, key="left_better"):
            record_preference(idx_a, idx_b, 0)

    with col2:
        if st.button("Right Option Better", type="primary", use_container_width=True, key="right_better"):
            record_preference(idx_a, idx_b, 1)

    with col3:
        if st.button("Cannot Decide", use_container_width=True, key="tie"):
            record_preference(idx_a, idx_b, 2)

    st.markdown("---")

    # Display comparison question
    st.markdown(f"""
    <div style="text-align: center; margin: 1rem 0;">
        <h2 style="color: {COLORS['text']};">
            Which prediction looks more plausible for archaeological sites?
        </h2>
        <p style="color: {COLORS['text']}; font-size: 1rem;">
            Consider: site shape, spatial coherence, and archaeological realism
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Display masks side by side
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div style="text-align: center;">
            <div style="font-size: 1.1rem; margin-bottom: 0.5rem; font-weight: bold;">LEFT OPTION (Mask #{idx_a + 1})</div>
        </div>
        """, unsafe_allow_html=True)

        mask_display = (mask_a - mask_a.min()) / (mask_a.max() - mask_a.min() + 1e-8)
        st.image(mask_display, clamp=True, width="stretch")

        # Show statistics (7D features matching experiments)
        st.markdown(f"""
        <div style="background-color: {COLORS['accent']}; padding: 0.75rem; border-radius: 0.5rem; text-align: center; font-size: 0.9rem;">
            <strong>Moran's I:</strong> {stats_a['morans_i']} &nbsp;|&nbsp;
            <strong>Components:</strong> {stats_a['components']} &nbsp;|&nbsp;
            <strong>Area:</strong> {stats_a['area']} &nbsp;|&nbsp;
            <strong>Variance:</strong> {stats_a['variance']}<br>
            <strong>Perim. Ratio:</strong> {stats_a['perimeter_ratio']} &nbsp;|&nbsp;
            <strong>Entropy:</strong> {stats_a['entropy']} &nbsp;|&nbsp;
            <strong>Confidence:</strong> {stats_a['mean_confidence']}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="text-align: center;">
            <div style="font-size: 1.1rem; margin-bottom: 0.5rem; font-weight: bold;">RIGHT OPTION (Mask #{idx_b + 1})</div>
        </div>
        """, unsafe_allow_html=True)

        mask_display = (mask_b - mask_b.min()) / (mask_b.max() - mask_b.min() + 1e-8)
        st.image(mask_display, clamp=True, width="stretch")

        # Show statistics (7D features matching experiments)
        st.markdown(f"""
        <div style="background-color: {COLORS['accent']}; padding: 0.75rem; border-radius: 0.5rem; text-align: center; font-size: 0.9rem;">
            <strong>Moran's I:</strong> {stats_b['morans_i']} &nbsp;|&nbsp;
            <strong>Components:</strong> {stats_b['components']} &nbsp;|&nbsp;
            <strong>Area:</strong> {stats_b['area']} &nbsp;|&nbsp;
            <strong>Variance:</strong> {stats_b['variance']}<br>
            <strong>Perim. Ratio:</strong> {stats_b['perimeter_ratio']} &nbsp;|&nbsp;
            <strong>Entropy:</strong> {stats_b['entropy']} &nbsp;|&nbsp;
            <strong>Confidence:</strong> {stats_b['mean_confidence']}
        </div>
        """, unsafe_allow_html=True)

    # Statistics explanation below the images
    with st.expander("What do these statistics mean?"):
        st.markdown("""
        All features are normalized to **[0, 1]** where higher = better.

        **Moran's I:** Spatial autocorrelation. Higher = more coherent spatial clustering.

        **Components:** Connected regions (inverted log scale). Higher = fewer, more coherent clusters.

        **Area:** Mean component size (log scale). Higher = larger, more substantial sites.

        **Variance:** Variation in probability values. Higher = more distinct high/low confidence regions.

        **Perimeter Ratio:** Boundary smoothness (inverted). Higher = smoother, more compact boundaries.

        **Entropy:** Prediction certainty (inverted). Higher = more confident, less uncertain predictions.

        **Mean Confidence:** Average prediction probability. Higher = stronger overall prediction.

        **What to look for:**
        - Prefer predictions with **compact, coherent** site shapes
        - Look for **realistic spatial clustering** patterns
        - Consider whether the site density matches archaeological expectations
        """)

    st.markdown("---")


def record_preference(idx_a: int, idx_b: int, preference: int):
    """
    Record a preference and advance to next comparison.

    Args:
        idx_a: Index of first mask
        idx_b: Index of second mask
        preference: 0=left, 1=right, 2=tie, -1=skip
    """
    from datetime import datetime

    # Calculate response time
    current_idx = st.session_state.current_pair_idx
    comparison_key = f"comparison_{current_idx}"
    response_time_seconds = None

    if comparison_key in st.session_state:
        shown_at = st.session_state[comparison_key].get('shown_at')
        if shown_at:
            try:
                from datetime import datetime
                shown_time = datetime.fromisoformat(shown_at)
                response_time = datetime.now() - shown_time
                response_time_seconds = round(response_time.total_seconds(), 2)
            except:
                pass

    # Record preference with timing data
    preference_data = {
        'idx_a': idx_a,
        'idx_b': idx_b,
        'preference': preference,
        'preference_label': {0: 'Left', 1: 'Right', 2: 'Tie', -1: 'Skipped'}[preference],
        'comparison_number': st.session_state.comparisons_completed + 1,
        'timestamp': datetime.now().isoformat()
    }

    # Add response time if available
    if response_time_seconds is not None:
        preference_data['response_time_seconds'] = response_time_seconds

    st.session_state.preferences.append(preference_data)

    # Update active learning loop if active
    active_loop = st.session_state.get('active_loop')
    if active_loop is not None and preference in [0, 1]:  # Only feed non-tie preferences
        try:
            active_loop.add_preferences(
                pairs=[(idx_a, idx_b)],
                preferences=[preference]
            )
        except Exception as e:
            logger.error(f"Error updating active learning loop: {e}")

    # Update progress
    if preference != -1:
        st.session_state.comparisons_completed += 1

    # Move to next pair
    st.session_state.current_pair_idx += 1

    # Rerun to show next comparison (no feedback message for speed)
    st.rerun()


def show_completion_message():
    """
    Show completion message and navigation to results.
    """
    # Calculate cognitive load statistics
    preferences = st.session_state.preferences
    response_times = [p.get('response_time_seconds') for p in preferences if p.get('response_time_seconds') is not None]

    avg_time = "N/A"
    if response_times:
        import numpy as np
        avg_time = f"{np.mean(response_times):.1f}s"

    st.markdown(f"""
    <div class="winner-badge">
        All Comparisons Complete!
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="archaeology-card" style="text-align: center;">
        <h2>Thank You!</h2>
        <p>
            You have completed all {st.session_state.comparisons_total} comparisons.
            Your preferences have been recorded.
        </p>
        <p>
            <strong>Total comparisons:</strong> {len([p for p in preferences if p['preference'] != -1])}<br>
            <strong>Skipped:</strong> {len([p for p in preferences if p['preference'] == -1])}<br>
            <strong>Ties:</strong> {len([p for p in preferences if p['preference'] == 2])}<br>
            <strong>Avg response time:</strong> {avg_time}
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    if st.button("Proceed to Ranking", type="primary", use_container_width=True):
        st.session_state.current_step = 'ranking'
        st.rerun()
