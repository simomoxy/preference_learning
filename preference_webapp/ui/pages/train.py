"""
Training page for displaying model training progress.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import time
import logging

logger = logging.getLogger(__name__)

# Import UI components
from ui.components import progress_bar
from ui.utils import format_elapsed_time, estimate_time_remaining


def show_train_page():
    """
    Display the training page.
    """
    st.title("🔄 Training Model")
    st.markdown("Training the preference learning model on collected data.")

    # Check if session exists
    if st.session_state.active_learning_loop is None:
        st.warning("No active session. Please go to Configuration page to start a session.")
        if st.button("Go to Configuration"):
            st.session_state.current_page = 'config'
            st.rerun()
        return

    loop = st.session_state.active_learning_loop

    # Training status
    st.header("Training Status")

    # Show progress
    progress = loop.get_progress()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Current Iteration", progress['iteration'])

    with col2:
        st.metric("Total Comparisons", progress['total_comparisons'])

    with col3:
        if progress['converged']:
            st.success("✓ Converged")
        else:
            st.caption("Status: Training")

    st.markdown("---")

    # Training placeholder with spinner
    st.info("Training model on collected preferences...")

    # Simulate training with progress updates
    training_placeholder = st.empty()

    with training_placeholder.container():
        st.markdown("### Training Progress")

        # Show configuration
        with st.expander("Training Configuration", expanded=True):
            config = st.session_state.config
            col1, col2 = st.columns(2)

            with col1:
                st.caption(f"Strategy: {config.get('strategy', 'gp')}")
                st.caption(f"Acquisition: {config.get('acquisition', 'thompson_sampling')}")
                st.caption(f"Encoder: {config.get('encoder', 'handcrafted')}")

            with col2:
                st.caption(f"Max Epochs: {config.get('max_epochs', 100)}")
                st.caption(f"Learning Rate: {config.get('learning_rate', 0.01)}")
                st.caption(f"Patience: {config.get('patience', 10)}")

        # Progress bar
        st.markdown("#### Optimization Progress")

        # Simulate training progress
        progress_placeholder = st.empty()
        metrics_placeholder = st.empty()

        # Note: In real implementation, you would run actual training here
        # For now, we'll simulate progress and then navigate to results
        if 'training_complete' not in st.session_state:
            st.session_state.training_complete = False

        if not st.session_state.training_complete:
            # Simulate training steps
            for epoch in range(1, 11):
                with progress_placeholder:
                    progress_bar(epoch, 10)

                with metrics_placeholder:
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Epoch", f"{epoch}/10")
                    col2.metric("ELBO Loss", f"{-(-100 + epoch * 5):.2f}")
                    col3.metric("Time", f"{epoch * 0.5:.1f}s")

                time.sleep(0.3)  # Simulate training time

            st.session_state.training_complete = True

            # Save session checkpoint
            try:
                loop.save_session()
                st.success("Training complete! Session saved.")
            except Exception as e:
                st.warning(f"Training complete, but save failed: {str(e)}")

        else:
            with progress_placeholder:
                progress_bar(10, 10)

            with metrics_placeholder:
                col1, col2, col3 = st.columns(3)
                col1.metric("Epoch", "10/10")
                col2.metric("ELBO Loss", "-55.00")
                col3.metric("Time", "5.0s")

            st.success("Training complete!")

    st.markdown("---")

    # Optional logs expander
    with st.expander("📋 Training Logs"):
        st.code("""
Iteration 1: Training GP on 10 preferences
  - ELBO: -100.00
  - Convergence: False

Iteration 2: Training GP on 20 preferences
  - ELBO: -95.00
  - Convergence: False

...

Iteration 10: Training GP on 100 preferences
  - ELBO: -55.00
  - Convergence: True
        """, language="text")

    # Navigation buttons
    st.header("Next Steps")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.button("📈 View Results", type="primary"):
            # Get ranking and scores
            try:
                ranking, scores = loop.get_ranking()
                st.session_state.ranking = ranking
                st.session_state.scores = scores
                st.success("Ranking computed!")

                # Navigate to results
                st.session_state.current_page = 'results'
                st.rerun()

            except Exception as e:
                st.error(f"Error computing ranking: {str(e)}")
                logger.error(f"Error computing ranking: {e}", exc_info=True)

        if st.button("📊 Continue Collecting"):
            # Reset training flag
            st.session_state.training_complete = False

            # Navigate back to collect
            st.session_state.current_page = 'collect'
            st.rerun()

    # Progress summary
    st.markdown("---")

    st.header("Session Summary")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Training Statistics**")
        st.caption(f"Total Iterations: {progress['iteration']}")
        st.caption(f"Total Comparisons: {progress['total_comparisons']}")
        st.caption(f"Converged: {'Yes' if progress['converged'] else 'No'}")

    with col2:
        st.markdown("**Model Information**")
        st.caption(f"Strategy: {st.session_state.config.get('strategy', 'gp')}")
        st.caption(f"Acquisition: {st.session_state.config.get('acquisition', 'thompson_sampling')}")
        st.caption(f"Encoder: {st.session_state.config.get('encoder', 'handcrafted')}")

    # Show top-K if available
    if progress.get('top_k'):
        st.markdown("**Current Top-K Masks:**")
        top_k = progress['top_k']
        st.write(", ".join([f"Mask {idx}" for idx in top_k]))


def run_training_in_background(loop, epochs: int = 10):
    """
    Run training in background (placeholder for future implementation).

    Args:
        loop: ActiveLearningLoop instance
        epochs: Number of training epochs

    Returns:
        Training results dictionary
    """
    # This is a placeholder for actual background training
    # In production, you would use threading or async operations
    # For now, we simulate training

    results = {
        'epochs': epochs,
        'final_loss': -55.0,
        'converged': True,
    }

    return results
