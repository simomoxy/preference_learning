"""
Summary page showing final results.

Simplified, focused on the winner and showing results to archaeologists.
Data is stored for the researcher to download later.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import numpy as np
import pandas as pd
import json
import logging
from datetime import datetime
from io import StringIO

logger = logging.getLogger(__name__)

from ui.theme import render_progress_indicator, COLORS


def show_summary_page():
    """
    Display the summary page with results.
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
        total_steps=3,
        step_names=['Load Data', 'Compare', 'Summary']
    )

    st.markdown("---")

    # Header
    st.markdown(f"""
    <div style="text-align: center; margin: 2rem 0;">
        <h1 style="color: {COLORS['text']};">Your Results</h1>
        <p style="color: {COLORS['text']}; font-size: 1.1rem;">
            Thank you for completing the preference study!
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)

    preferences = st.session_state.preferences
    valid_prefs = [p for p in preferences if p['preference'] != -1]
    left_wins = len([p for p in valid_prefs if p['preference'] == 0])
    right_wins = len([p for p in valid_prefs if p['preference'] == 1])
    ties = len([p for p in valid_prefs if p['preference'] == 2])
    skips = len([p for p in preferences if p['preference'] == -1])

    with col1:
        st.metric("Total Comparisons", len(valid_prefs))

    with col2:
        st.metric("Left Preferred", left_wins)

    with col3:
        st.metric("Right Preferred", right_wins)

    with col4:
        st.metric("Ties/Skips", ties + skips)

    # Cognitive Load Metrics
    st.markdown("### Cognitive Load Metrics")

    # Calculate response time statistics
    response_times = [p.get('response_time_seconds') for p in preferences if p.get('response_time_seconds') is not None]

    if response_times:
        import numpy as np
        avg_time = np.mean(response_times)
        median_time = np.median(response_times)
        std_time = np.std(response_times)
        min_time = np.min(response_times)
        max_time = np.max(response_times)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Avg Response Time", f"{avg_time:.1f}s")

        with col2:
            st.metric("Median Time", f"{median_time:.1f}s")

        with col3:
            st.metric("Std Dev", f"{std_time:.1f}s")

        with col4:
            st.metric("Skip Rate", f"{(skips/len(preferences)*100):.1f}%")
    else:
        st.info("Response time data not available for this session.")

    st.markdown("---")

    # Compute simple ranking based on wins
    ranking_data = compute_simple_ranking(preferences, len(st.session_state.masks))

    # Show top prediction (winner)
    if ranking_data:
        winner_idx = ranking_data[0]['idx']
        winner_score = ranking_data[0]['score']

        st.markdown(f"""
        <div class="winner-badge">
            Best Prediction: Mask {winner_idx + 1}
        </div>
        """, unsafe_allow_html=True)

        # Show winner image
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            masks = st.session_state.masks
            winner_mask = masks[winner_idx]
            mask_display = (winner_mask - winner_mask.min()) / (winner_mask.max() - winner_mask.min() + 1e-8)
            st.image(mask_display, clamp=True, width="stretch")

            st.markdown(f"**Score:** {winner_score:.2f}")

    st.markdown("---")

    # Ranking table
    st.header("Full Ranking")

    # Create dataframe for display - simpler version without metadata
    ranking_display = []
    for r in ranking_data[:10]:  # Show top 10
        ranking_display.append({
            'Rank': r['rank'],
            'Score': round(r['score'], 3),
            'Wins': r['wins'],
            'Losses': r['losses']
        })

    ranking_df = pd.DataFrame(ranking_display)
    st.dataframe(ranking_df, width="stretch")

    if len(ranking_data) > 10:
        st.caption(f"Showing top 10 of {len(ranking_data)} masks")

    st.markdown("---")

    # Data submission section
    st.header("Submit Your Data")

    st.markdown("""
    <div class="archaeology-card">
        <h3>Data Storage</h3>
        <p>
            <strong>Your preferences have been recorded.</strong>
            Please submit your data so the research team can collect and analyze all responses.
        </p>
        <p>
            Your input helps identify which LAMAP configurations produce the most plausible
            archaeological site predictions.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Try to upload to GitHub
    import os
    github_token = os.getenv("GITHUB_TOKEN")
    github_repo = os.getenv("GITHUB_DATA_REPO", "simomoxy/lamap-bronze-age-data")

    if github_token:
        st.markdown("### Uploading to GitHub...")
        st.info(f"Uploading to repository: {github_repo}")

        with st.spinner("Uploading your preferences..."):
            metadata = {
                'expert_name': st.session_state.expert_name,
                'period': st.session_state.period,
                'total_masks': len(st.session_state.masks)
            }

            from github_data_uploader import upload_preferences_to_github
            success, url, error = upload_preferences_to_github(
                preferences=valid_prefs,
                metadata=metadata,
                repo=github_repo
            )

        if success:
            st.success(f"Successfully uploaded your data!")
            st.markdown(f"View your submission: [GitHub Link]({url})")
        else:
            st.error(f"Upload failed: {error}")
            st.info("Please download your data manually using the buttons below.")
    else:
        st.warning("""
        **GitHub not configured** - Please download your data manually and send it to the research team.

        To enable automatic upload in the future, ask the research team to set up a GitHub token.
        """)
        st.caption("Automatic upload requires: GITHUB_TOKEN environment variable")

    # Manual download as backup
    st.markdown("---")
    st.markdown("### Backup Download")
    st.caption("Download a copy for your records:")

    col1, col2 = st.columns(2)

    # Export as CSV
    with col1:
        csv_data = generate_csv_export()

        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=f"preferences_{st.session_state.period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            width="stretch"
        )

    # Export as JSON
    with col2:
        json_data = generate_json_export()

        st.download_button(
            label="Download JSON",
            data=json_data,
            file_name=f"preferences_{st.session_state.period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            width="stretch"
        )

    st.markdown("---")

    # Restart option
    st.markdown("### Start New Session")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.button("Load New Data", use_container_width=True):
            # Reset session
            for key in list(st.session_state.keys()):
                if key not in ['masks_loaded']:  # Keep data loaded
                    del st.session_state[key]

            # Reinitialize
            st.session_state.current_step = 'welcome'
            st.session_state.masks_loaded = False
            st.rerun()


def compute_simple_ranking(preferences: list, num_masks: int) -> list:
    """
    Compute a simple ranking based on pairwise preferences.

    Args:
        preferences: List of preference dictionaries
        num_masks: Total number of masks

    Returns:
        List of dictionaries with ranking data
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
            'rank': 0,  # Will be set after sorting
            'idx': idx,
            'score': score,
            'wins': stats[idx]['wins'],
            'losses': stats[idx]['losses'],
            'ties': stats[idx]['ties']
        })

    # Sort by score descending
    ranking.sort(key=lambda x: x['score'], reverse=True)

    # Set ranks
    for i, item in enumerate(ranking):
        item['rank'] = i + 1

    return ranking


def generate_csv_export() -> str:
    """
    Generate CSV export of preference data.

    Returns:
        CSV string
    """
    preferences = st.session_state.preferences
    valid_prefs = [p for p in preferences if p['preference'] != -1]

    # Create dataframe
    data = []
    for pref in valid_prefs:
        pref_label = {0: 'Left', 1: 'Right', 2: 'Tie'}[pref['preference']]
        data.append({
            'Expert': st.session_state.expert_name,
            'Period': st.session_state.period,
            'Comparison': pref['comparison_number'],
            'Mask_A': pref['idx_a'],
            'Mask_B': pref['idx_b'],
            'Preference': pref_label,
            'Preference_Code': pref['preference']
        })

    df = pd.DataFrame(data)

    # Add metadata
    output = StringIO()
    output.write(f"# Preference Learning Export\n")
    output.write(f"# Expert: {st.session_state.expert_name}\n")
    output.write(f"# Period: {st.session_state.period}\n")
    output.write(f"# Date: {datetime.now().isoformat()}\n")
    output.write(f"# Total Comparisons: {len(valid_prefs)}\n")
    output.write(f"\n")

    df.to_csv(output, index=False)
    return output.getvalue()


def generate_json_export() -> str:
    """
    Generate JSON export of preference data.

    Returns:
        JSON string
    """
    preferences = st.session_state.preferences
    valid_prefs = [p for p in preferences if p['preference'] != -1]

    # Create export data
    data = {
        'metadata': {
            'expert_name': st.session_state.expert_name,
            'period': st.session_state.period,
            'export_date': datetime.now().isoformat(),
            'total_comparisons': len(valid_prefs),
            'total_masks': len(st.session_state.masks)
        },
        'summary': {
            'left_wins': len([p for p in valid_prefs if p['preference'] == 0]),
            'right_wins': len([p for p in valid_prefs if p['preference'] == 1]),
            'ties': len([p for p in valid_prefs if p['preference'] == 2]),
            'skips': len([p for p in preferences if p['preference'] == -1])
        },
        'preferences': []
    }

    # Add preferences
    for pref in valid_prefs:
        data['preferences'].append({
            'comparison_number': pref['comparison_number'],
            'mask_a': pref['idx_a'],
            'mask_b': pref['idx_b'],
            'preference': pref['preference'],
            'preference_label': {0: 'Left', 1: 'Right', 2: 'Tie'}[pref['preference']]
        })

    # Add ranking
    ranking = compute_simple_ranking(preferences, len(st.session_state.masks))
    data['ranking'] = [
        {
            'rank': r['rank'],
            'mask_id': r['idx'],
            'score': round(r['score'], 4),
            'wins': r['wins'],
            'losses': r['losses'],
            'ties': r['ties']
        }
        for r in ranking
    ]

    return json.dumps(data, indent=2)
