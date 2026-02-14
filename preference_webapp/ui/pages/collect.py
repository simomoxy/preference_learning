"""
Data collection page for gathering pairwise preferences.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Import UI components
from ui.components import display_side_by_side_images, preference_buttons, progress_bar
from ui.utils import format_elapsed_time, estimate_time_remaining, create_comparison_summary


def show_collect_page():
    """
    Display the data collection page.
    """
    st.title("📊 Collect Preferences")
    st.markdown("Compare pairs of segmentation masks and provide your preferences.")

    # Check if session exists
    if st.session_state.active_learning_loop is None:
        st.warning("No active session. Please go to Configuration page to start a session.")
        if st.button("Go to Configuration"):
            st.session_state.current_page = 'config'
            st.rerun()
        return

    loop = st.session_state.active_learning_loop
    config = st.session_state.config
    batch_size = config['batch_size']
    max_comparisons = config['max_comparisons']
    decision_mode = config['decision_mode']

    # Get progress
    progress = loop.get_progress()
    current_iteration = progress['iteration']
    total_comparisons = progress['total_comparisons']

    # Progress section
    st.header("Progress")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Iteration", f"{current_iteration}/{loop.max_iterations}")

    with col2:
        st.metric("Total Comparisons", f"{total_comparisons}/{max_comparisons}")

    with col3:
        if progress['converged']:
            st.success("✓ Converged")
        else:
            st.caption("Convergence: In progress")

    # Progress bar
    if max_comparisons > 0:
        progress_bar(total_comparisons, max_comparisons)

    # Batch progress
    if st.session_state.current_batch:
        batch_completed = len(st.session_state.batch_preferences)
        st.caption(f"Batch Progress: {batch_completed}/{batch_size} comparisons")

    # Check if max comparisons reached
    if total_comparisons >= max_comparisons:
        st.warning("Maximum comparisons reached! Ready to train final model.")
        if st.button("Train Final Model", type="primary"):
            st.session_state.current_page = 'train'
            st.rerun()
        return

    # Check if converged
    if progress['converged']:
        st.success("Convergence reached! Ready to view results.")
        if st.button("View Results", type="primary"):
            st.session_state.current_page = 'results'
            st.rerun()
        return

    st.markdown("---")

    # Get next batch if needed
    if not st.session_state.current_batch:
        st.info("Generating next batch of comparisons...")

        # Get next batch from active learning loop
        pairs = loop.get_next_batch(n_pairs=batch_size)

        if not pairs:
            st.warning("No more pairs to compare!")
            return

        st.session_state.current_batch = pairs
        st.session_state.batch_preferences = {}
        st.session_state.batch_count += 1

        st.success(f"Generated {len(pairs)} comparisons for batch {st.session_state.batch_count}")

    # Display current comparison
    if st.session_state.current_batch:
        # Find first uncompleted comparison
        current_pair_idx = None
        for i, pair in enumerate(st.session_state.current_batch):
            if pair not in st.session_state.batch_preferences:
                current_pair_idx = i
                break

        # If all completed, show submit button
        if current_pair_idx is None:
            st.header("✅ Batch Complete")

            st.success(f"All {len(st.session_state.current_batch)} comparisons completed!")

            # Show summary
            summary = create_comparison_summary(list(st.session_state.batch_preferences.values()))
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total", summary['total'])
            col2.metric("Left Better", summary['left_better'])
            col3.metric("Right Better", summary['right_better'])
            col4.metric("Ties", summary['ties'])

            st.markdown("---")

            col1, col2, col3 = st.columns([1, 2, 1])

            with col2:
                if st.button("🔄 Submit & Train", type="primary"):
                    # Submit batch preferences
                    submit_batch()

                if st.button("💾 Save Progress"):
                    save_progress()

            return

        # Get current pair
        pair = st.session_state.current_batch[current_pair_idx]
        idx_a, idx_b = pair

        st.header(f"Comparison {current_pair_idx + 1}/{len(st.session_state.current_batch)}")

        # Get masks
        masks = st.session_state.masks
        metadata = st.session_state.mask_metadata

        mask_a = masks[idx_a]
        mask_b = masks[idx_b]

        meta_a = metadata[idx_a] if metadata else None
        meta_b = metadata[idx_b] if metadata else None

        # Display masks side by side
        display_side_by_side_images(mask_a, mask_b, meta_a, meta_b)

        st.markdown("---")

        # Decision mode
        if decision_mode == 'oracle':
            st.info("🤖 Virtual Oracle Mode: Preferences will be generated automatically")

            if st.button("Generate Oracle Preference", type="primary"):
                # Get oracle preference
                preference = get_oracle_preference(mask_a, mask_b, idx_a, idx_b)

                # Store preference
                st.session_state.batch_preferences[pair] = (idx_a, idx_b, preference)

                # Show feedback
                if preference == 0:
                    st.success(f"Oracle prefers Left (Mask {idx_a})")
                elif preference == 1:
                    st.success(f"Oracle prefers Right (Mask {idx_b})")
                else:
                    st.info("Oracle: Tie")

                # Auto-advance after short delay
                st.rerun()

        else:  # Human mode
            st.info("👤 Human Expert Mode: Please select your preference")

            # Preference buttons
            preference = preference_buttons()

            if preference is not None:
                # Store preference
                # preference: -1=skip, 0=left, 1=right, 2=tie
                if preference == -1:
                    # Skip - add to review queue
                    st.session_state.review_queue.append(pair)
                    st.info("Skipped - added to review queue")
                else:
                    # Store actual preference (0 or 1)
                    # Convert tie to None or special value
                    if preference == 2:
                        # Tie - store as None
                        st.session_state.batch_preferences[pair] = None
                        st.info("Recorded as Tie")
                    else:
                        st.session_state.batch_preferences[pair] = (idx_a, idx_b, preference)
                        if preference == 0:
                            st.success("Recorded: Left Better")
                        else:
                            st.success("Recorded: Right Better")

                # Auto-advance
                st.rerun()

        # Review queue info
        if st.session_state.review_queue:
            st.caption(f"⏭️ Review Queue: {len(st.session_state.review_queue)} skipped pairs")


def submit_batch():
    """
    Submit batch preferences and trigger training.
    """
    try:
        loop = st.session_state.active_learning_loop

        # Convert batch preferences to format expected by add_preferences
        pairs = []
        preferences = []

        for pair, pref in st.session_state.batch_preferences.items():
            if pref is not None:  # Skip ties
                # pref is already (idx_a, idx_b, preference)
                idx_a, idx_b, preference = pref
                pairs.append((idx_a, idx_b))
                preferences.append(preference)

        # Add preferences to loop (this triggers retraining)
        if pairs:
            loop.add_preferences(pairs, preferences)

            # Save session
            session_id = loop.save_session()
            st.session_state.session_id = session_id

            st.success(f"Batch submitted! Iteration {loop.iteration} completed.")

            # Clear batch
            st.session_state.current_batch = []
            st.session_state.batch_preferences = {}

            # Navigate to train page
            st.session_state.current_page = 'train'
            st.rerun()

    except Exception as e:
        st.error(f"Error submitting batch: {str(e)}")
        logger.error(f"Error submitting batch: {e}", exc_info=True)


def save_progress():
    """
    Save current progress without submitting batch.
    """
    try:
        loop = st.session_state.active_learning_loop
        loop.save_session()
        st.success("Progress saved!")
    except Exception as e:
        st.error(f"Error saving progress: {str(e)}")
        logger.error(f"Error saving progress: {e}", exc_info=True)


def get_oracle_preference(mask_a: np.ndarray, mask_b: np.ndarray, idx_a: int, idx_b: int) -> int:
    """
    Get preference from virtual oracle.

    Args:
        mask_a: First mask
        mask_b: Second mask
        idx_a: Index of first mask
        idx_b: Index of second mask

    Returns:
        Preference (0 for A, 1 for B, 2 for tie)
    """
    try:
        from backend.oracles.registry import get_oracle

        oracle_config = st.session_state.config.get('oracle_config', {})
        oracle_type = oracle_config.get('oracle_type', 'biased')

        # Get oracle instance
        oracle = get_oracle(oracle_type, **oracle_config)

        # Get preference (returns True if A preferred over B)
        prefers_a = oracle.prefer(mask_a, mask_b)

        # Convert to preference value
        if prefers_a:
            return 0  # Left (A) better
        else:
            return 1  # Right (B) better

    except Exception as e:
        st.error(f"Error getting oracle preference: {str(e)}")
        logger.error(f"Error getting oracle preference: {e}", exc_info=True)
        return 0  # Default to left
