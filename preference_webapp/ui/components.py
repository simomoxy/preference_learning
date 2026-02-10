"""
Reusable UI components for the preference learning webapp.

Includes archaeology-themed styling components.
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
from typing import Dict, Any, Optional, List
import pandas as pd

from ui.theme import COLORS


def display_side_by_side_images(
    mask_a: np.ndarray,
    mask_b: np.ndarray,
    metadata_a: Optional[Dict[str, Any]] = None,
    metadata_b: Optional[Dict[str, Any]] = None
):
    """
    Display two segmentation masks side by side.

    Args:
        mask_a: First mask (2D numpy array)
        mask_b: Second mask (2D numpy array)
        metadata_a: Metadata for first mask (optional)
        metadata_b: Optional metadata_b (optional)
    """
    col1, col2 = st.columns(2)

    with col1:
        # Normalize and display mask
        mask_display = (mask_a - mask_a.min()) / (mask_a.max() - mask_a.min() + 1e-8)
        st.image(mask_display, clamp=True)
        if metadata_a:
            st.markdown(f"**{metadata_a.get('Mask ID', 'Left Image')}**")
            cols = st.columns(2)
            with cols[0]:
                st.caption(f"Site: {metadata_a.get('Site', 'N/A')}")
                st.caption(f"Coverage: {metadata_a.get('Coverage', 'N/A')}")
            with cols[1]:
                st.caption(f"Components: {metadata_a.get('Components', 'N/A')}")
                st.caption(f"Compactness: {metadata_a.get('Compactness', 'N/A')}")

    with col2:
        # Normalize and display mask
        mask_display = (mask_b - mask_b.min()) / (mask_b.max() - mask_b.min() + 1e-8)
        st.image(mask_display, clamp=True)
        if metadata_b:
            st.markdown(f"**{metadata_b.get('Mask ID', 'Right Image')}**")
            cols = st.columns(2)
            with cols[0]:
                st.caption(f"Site: {metadata_b.get('Site', 'N/A')}")
                st.caption(f"Coverage: {metadata_b.get('Coverage', 'N/A')}")
            with cols[1]:
                st.caption(f"Components: {metadata_b.get('Components', 'N/A')}")
                st.caption(f"Compactness: {metadata_b.get('Compactness', 'N/A')}")


def display_single_image(
    mask: np.ndarray,
    title: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Display a single mask with title and metadata.

    Args:
        mask: Mask to display (2D numpy array)
        title: Optional title
        metadata: Optional metadata dictionary
    """
    st.image(mask, clamp=True)

    if title:
        st.markdown(f"**{title}**")

    if metadata:
        for key, value in metadata.items():
            st.caption(f"{key}: {value}")


def preference_buttons() -> Optional[int]:
    """
    Display preference buttons and return user selection.

    Returns:
        -1 for skip, 0 for left better, 1 for right better, 2 for tie, None if no selection
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        left_better = st.button("⬅️ Left Better", key="left_better")

    with col2:
        right_better = st.button("➡️ Right Better", key="right_better")

    with col3:
        tie = st.button("🤝 Tie", key="tie")

    with col4:
        skip = st.button("⏭️ Skip", key="skip")

    if left_better:
        return 0
    elif right_better:
        return 1
    elif tie:
        return 2
    elif skip:
        return -1

    return None


def progress_bar(current: int, total: int, show_text: bool = True):
    """
    Display a progress bar with optional text.

    Args:
        current: Current progress value
        total: Total value
        show_text: Whether to show progress text
    """
    if total > 0:
        progress = current / total
    else:
        progress = 0.0

    if show_text:
        st.progress(progress, text=f"{current}/{total} ({progress*100:.1f}%)")
    else:
        st.progress(progress)


def metrics_plot(
    ranking: np.ndarray,
    scores: np.ndarray,
    title: str = "Copeland Scores",
    top_k: Optional[int] = None
):
    """
    Create an interactive bar chart of Copeland scores.

    Args:
        ranking: Array of mask indices sorted by preference
        scores: Array of Copeland scores
        title: Chart title
        top_k: Show only top K masks (None for all)
    """
    if top_k is not None:
        ranking = ranking[:top_k]
        scores = scores[:top_k]
        title = f"{title} (Top {top_k})"

    # Create dataframe for plotting
    df = pd.DataFrame({
        'Mask ID': [f"Mask {i}" for i in ranking],
        'Copeland Score': scores[ranking]
    })

    # Create interactive bar chart with archaeology theme
    fig = go.Figure(data=[
        go.Bar(
            x=df['Mask ID'],
            y=df['Copeland Score'],
            marker_color=COLORS['primary'],
            text=df['Copeland Score'].round(3),
            textposition='outside',
            marker_line_color=COLORS['text'],
            marker_line_width=1
        )
    ])

    fig.update_layout(
        title=title,
        xaxis_title="Mask ID",
        yaxis_title="Score",
        xaxis={'tickangle': -45},
        height=500,
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=COLORS['text'])
    )

    st.plotly_chart(fig)


def session_info_sidebar(session: Dict[str, Any]):
    """
    Display session information in sidebar.

    Args:
        session: Session dictionary
    """
    st.sidebar.markdown("### Session Info")

    st.sidebar.caption(f"**ID:** {session.get('session_id', 'N/A')}")
    st.sidebar.caption(f"**Created:** {session.get('created_at', 'N/A')}")

    if 'config' in session:
        config = session['config']
        with st.sidebar.expander("Configuration"):
            for key, value in config.items():
                st.caption(f"{key}: {value}")

    st.sidebar.caption(f"**Iteration:** {session.get('iteration', 0)}")
    st.sidebar.caption(f"**Total Comparisons:** {session.get('total_comparisons', 0)}")

    if session.get('converged'):
        st.sidebar.success("✓ Converged")


def ranking_table(
    ranking: np.ndarray,
    scores: np.ndarray,
    metadata: Optional[List[Dict[str, Any]]] = None,
    key: str = "ranking_table"
) -> Optional[int]:
    """
    Display an interactive ranking table.

    Args:
        ranking: Array of mask indices sorted by preference
        scores: Array of Copeland scores
        metadata: Optional list of metadata dictionaries for each mask
        key: Unique key for the widget

    Returns:
        Index of selected row, or None if no selection
    """
    # Prepare data
    data = {
        'Rank': list(range(1, len(ranking) + 1)),
        'Mask ID': ranking.tolist(),
        'Copeland Score': scores[ranking].round(4)
    }

    # Add metadata if available
    if metadata is not None:
        for i, idx in enumerate(ranking):
            if idx < len(metadata):
                meta = metadata[idx]
                for key, value in meta.items():
                    if key not in data:
                        data[key] = [None] * len(ranking)
                    data[key][i] = value

    # Create dataframe
    df = pd.DataFrame(data)

    # Display dataframe
    st.dataframe(df)

    return None  # Selection not supported in this Streamlit version


def acquisition_history_plot(history: List[Dict[str, Any]]):
    """
    Plot acquisition history showing pairs selected per iteration.

    Args:
        history: List of iteration history dictionaries
    """
    if not history:
        st.info("No acquisition history available")
        return

    # Extract data
    iterations = [h['iteration'] for h in history]

    # Track total comparisons over iterations
    total_comparisons = []
    for idx, h in enumerate(history):
        # Calculate cumulative comparisons up to this iteration
        # Each iteration adds batch_size comparisons (approximate)
        # We need to track this better in the future
        total_comparisons.append((idx + 1) * 10)  # Assuming batch_size=10

    # Create figure
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=iterations,
        y=total_comparisons,
        mode='lines+markers',
        name='Cumulative Comparisons',
        line=dict(color='rgb(55, 83, 109)'),
        fill='tozeroy'
    ))

    fig.update_layout(
        title="Data Collection Progress",
        xaxis_title="Iteration",
        yaxis_title="Total Comparisons",
        height=400,
        hovermode='x unified'
    )

    st.plotly_chart(fig)


def learning_curves_plot(history: List[Dict[str, Any]]):
    """
    Plot learning curves showing score progression.

    Args:
        history: List of iteration history dictionaries
    """
    if not history:
        st.info("No learning history available")
        return

    # Extract data
    iterations = [h['iteration'] for h in history]

    # Track top mask score over iterations
    top_scores = []
    for h in history:
        scores = h.get('scores')
        if scores is not None and len(scores) > 0:
            ranking = h.get('ranking')
            if ranking is not None and len(ranking) > 0:
                # Get score of top-ranked mask
                top_mask_idx = ranking[0]
                top_scores.append(float(scores[top_mask_idx]))
            else:
                top_scores.append(0.0)
        else:
            top_scores.append(0.0)

    # Track average score of top-5 masks
    avg_top5_scores = []
    for h in history:
        scores = h.get('scores')
        if scores is not None and len(scores) > 0:
            ranking = h.get('ranking')
            if ranking is not None and len(ranking) >= 5:
                # Get average score of top 5
                top5_scores = [float(scores[i]) for i in ranking[:5]]
                avg_top5_scores.append(sum(top5_scores) / 5.0)
            else:
                avg_top5_scores.append(0.0)
        else:
            avg_top5_scores.append(0.0)

    # Create figure
    fig = go.Figure()

    # Plot top mask score
    fig.add_trace(go.Scatter(
        x=iterations,
        y=top_scores,
        mode='lines+markers',
        name='Top Mask Score',
        line=dict(color=COLORS['primary'], width=3)
    ))

    # Plot average top-5 score
    fig.add_trace(go.Scatter(
        x=iterations,
        y=avg_top5_scores,
        mode='lines+markers',
        name='Avg Top-5 Score',
        line=dict(color=COLORS['secondary'], width=2)
    ))

    fig.update_layout(
        title="Learning Progress: Copeland Scores Over Iterations",
        xaxis_title="Iteration",
        yaxis_title="Copeland Score",
        height=400,
        hovermode='x unified',
        legend=dict(x=0.01, y=0.99)
    )

    st.plotly_chart(fig)


def export_buttons(session: Dict[str, Any], masks: Optional[List[np.ndarray]] = None):
    """
    Display export buttons for session data.

    Args:
        session: Session dictionary
        masks: Optional list of masks for export
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("💾 Save Session"):
            st.success("Session saved!")

    with col2:
        if st.button("📄 Export CSV"):
            # Export preferences as CSV
            import io
            import pandas as pd

            preferences = session.get('preferences', [])
            data = []
            for (i, j), pref in preferences:
                data.append({'mask_a': i, 'mask_b': j, 'preference': pref})

            df = pd.DataFrame(data)
            csv = df.to_csv(index=False)

            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"preferences_{session.get('session_id', 'session')}.csv",
                mime="text/csv"
            )

    with col3:
        if st.button("📋 Export JSON"):
            # Export preferences as JSON
            import json

            data = {
                'session_id': session.get('session_id'),
                'config': session.get('config'),
                'preferences': [
                    {'mask_a': i, 'mask_b': j, 'preference': pref}
                    for (i, j), pref in session.get('preferences', [])
                ],
                'ranking': session.get('ranking').tolist() if session.get('ranking') is not None else None,
                'scores': session.get('scores').tolist() if session.get('scores') is not None else None,
            }

            json_str = json.dumps(data, indent=2)

            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"session_{session.get('session_id', 'session')}.json",
                mime="application/json"
            )

    with col4:
        if st.button("🏠 New Session"):
            # Reset to config page
            st.session_state.current_page = 'config'
            st.session_state.session_id = None
            st.session_state.config = {}
            st.session_state.active_learning_loop = None
            st.rerun()
