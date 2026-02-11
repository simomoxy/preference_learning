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


# Statistics computation using same features as GP learning
def compute_mask_statistics(mask_idx):
    """
    Compute statistics for a mask using same features as GP experiments.
    Cached for performance - only index needed, retrieves mask from session_state.
    """
    from skimage import measure
    from scipy import ndimage

    try:
        # Get mask from session state
        masks = st.session_state.masks
        mask = masks[mask_idx]

        # Squeeze to remove singleton dimensions (e.g., (H, W, 1) -> (H, W))
        mask_squeezed = np.squeeze(mask)

        # If still 3D, take first channel
        if mask_squeezed.ndim == 3:
            mask_squeezed = mask_squeezed[:, :, 0]

        # Ensure we're working with float and normalize to 0-1
        mask_float = mask_squeezed.astype(float)
        if mask_float.max() > 1.0:
            mask_float = mask_float / 255.0

        # For probability maps, use 0.5 threshold
        mask_binary = (mask_float > 0.5).astype(int)

        # 1. Moran's I (spatial autocorrelation)
        mean = mask_float.mean()
        var = mask_float.var()
        if var > 1e-10:
            shifted = np.roll(mask_float, 1, axis=0)
            morans_i = np.sum((mask_float - mean) * (shifted - mean)) / (np.sum((mask_float - mean) ** 2) + 1e-10)
        else:
            morans_i = 0.0

        # 2. Connected components
        labeled, num_components = ndimage.label(mask_binary)

        # 3. Area distribution (mean component size)
        regions = measure.regionprops(labeled)
        areas = [r.area for r in regions] if len(regions) > 0 else [0]
        area_dist = np.mean(areas) if len(areas) > 0 else 0.0

        # 4. Compactness (area to bbox ratio)
        if len(regions) > 0:
            largest_region = max(regions, key=lambda r: r.area)
            bbox_area = largest_region.area_bbox  # Fixed deprecation warning
            region_area = largest_region.area
            compactness = region_area / bbox_area if bbox_area > 0 else 0.0
        else:
            compactness = 0.0

        # 5. Perimeter-area ratio (approximated with edge detection)
        total_area = np.sum(mask_binary)
        if total_area > 0:
            from skimage import filters
            edges = filters.sobel(mask_binary)
            total_perimeter = np.sum(edges > 0.1)
            perim_area_ratio = total_perimeter / np.sqrt(total_area + 1e-6)
        else:
            perim_area_ratio = 0.0

        # Coverage (percentage of active pixels)
        coverage = (np.sum(mask_binary) / mask_binary.size) * 100

        return {
            'morans_i': round(float(morans_i), 3),
            'components': int(num_components),
            'area_dist': round(float(area_dist), 1),
            'compactness': round(float(compactness), 3),
            'perim_area': round(float(perim_area_ratio), 3),
            'coverage': round(float(coverage), 1)
        }

    except Exception as e:
        logger.error(f"Error computing statistics for mask {mask_idx}: {e}", exc_info=True)
        return {
            'morans_i': 0.0,
            'components': 0,
            'area_dist': 0.0,
            'compactness': 0.0,
            'perim_area': 0.0,
            'coverage': 0.0
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

    # Apply theme
    render_progress_indicator(
        current_step=2,
        total_steps=3,
        step_names=['Load Data', 'Compare', 'Summary']
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

    # Cheat sheet toggle
    with st.expander("What do these statistics mean?"):
        st.markdown("""
        **Moran's I:** Spatial autocorrelation. Higher values indicate more clustered patterns.

        **Components:** Number of distinct connected regions (clusters of nearby pixels).

        **Area Distribution:** Average size of connected components.

        **Compactness:** Shape circularity (0-1). Higher values indicate more circular, compact shapes.

        **Perimeter-Area Ratio:** Boundary efficiency. Lower values indicate smoother boundaries.

        **Coverage:** Percentage of area predicted as archaeological sites.

        **What to look for:**
        - Prefer predictions with **compact, coherent** site shapes
        - Look for **realistic spatial clustering** patterns
        - Consider whether the site density matches archaeological expectations
        """)

    # Preference buttons AT THE TOP - all same height
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

    # Large, accessible buttons
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("Left Option Better", type="primary", use_container_width=True, key="left_better"):
            record_preference(idx_a, idx_b, 0)

    with col2:
        if st.button("Right Option Better", type="primary", use_container_width=True, key="right_better"):
            record_preference(idx_a, idx_b, 1)

    with col3:
        if st.button("Cannot Decide", use_container_width=True, key="tie"):
            record_preference(idx_a, idx_b, 2)

    with col4:
        if st.button("Skip", use_container_width=True, key="skip"):
            record_preference(idx_a, idx_b, -1)

    st.markdown("---")

    # Display comparison question
    st.markdown(f"""
    <div style="text-align: center; margin: 1rem 0;">
        <h2 style="color: {COLORS['text']};">
            Which prediction looks more plausible for archaeological sites?
        </h2>
        <p style="color: {COLORS['text']}; font-size: 1rem;">
            Consider: site shape, compactness, spatial coherence, and archaeological realism
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Display masks side by side - centered and closer together
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div style="text-align: center;">
            <div style="font-size: 1.1rem; margin-bottom: 0.5rem; font-weight: bold;">LEFT OPTION (Mask #{idx_a + 1})</div>
        </div>
        """, unsafe_allow_html=True)

        # Normalize for display - use container width
        mask_display = (mask_a - mask_a.min()) / (mask_a.max() - mask_a.min() + 1e-8)
        st.image(mask_display, clamp=True, width="stretch")

        # Show statistics
        st.markdown(f"""
        <div style="background-color: {COLORS['accent']}; padding: 0.75rem; border-radius: 0.5rem; text-align: center;">
            <strong>Moran's I:</strong> {stats_a['morans_i']} &nbsp;|&nbsp;
            <strong>Components:</strong> {stats_a['components']} &nbsp;|&nbsp;
            <strong>Compactness:</strong> {stats_a['compactness']}<br>
            <strong>Coverage:</strong> {stats_a['coverage']}%
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="text-align: center;">
            <div style="font-size: 1.1rem; margin-bottom: 0.5rem; font-weight: bold;">RIGHT OPTION (Mask #{idx_b + 1})</div>
        </div>
        """, unsafe_allow_html=True)

        # Normalize for display - use container width
        mask_display = (mask_b - mask_b.min()) / (mask_b.max() - mask_b.min() + 1e-8)
        st.image(mask_display, clamp=True, width="stretch")

        # Show statistics
        st.markdown(f"""
        <div style="background-color: {COLORS['accent']}; padding: 0.75rem; border-radius: 0.5rem; text-align: center;">
            <strong>Moran's I:</strong> {stats_b['morans_i']} &nbsp;|&nbsp;
            <strong>Components:</strong> {stats_b['components']} &nbsp;|&nbsp;
            <strong>Compactness:</strong> {stats_b['compactness']}<br>
            <strong>Coverage:</strong> {stats_b['coverage']}%
        </div>
        """, unsafe_allow_html=True)

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

    if st.button("View Summary", type="primary", use_container_width=True):
        st.session_state.current_step = 'summary'
        st.rerun()
