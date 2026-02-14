"""
Configuration page for setting up preference learning sessions.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import logging

logger = logging.getLogger(__name__)

# Import backend components
from backend.active_learning_loop import ActiveLearningLoop
from acquisition.registry import list_acquisitions
from backend.oracles.registry import list_oracles
from ui.utils import validate_config, load_lamap_masks, safe_execute


def show_config_page():
    """
    Display the configuration page.
    """
    st.title("⚙️ Configuration")
    st.markdown("Configure your preference learning session and load LAMAP data.")

    # Initialize config in session state if not exists
    if 'config' not in st.session_state or not st.session_state.config:
        st.session_state.config = {
            'lamap_results_dir': '/Users/simonjaxy/Documents/vub/archaeology/preference_learning/pylamap/results/cyprus',
            'period': 'bronze_age',
            'strategy': 'gp',
            'acquisition': 'thompson_sampling',
            'encoder': 'handcrafted',
            'decision_mode': 'human',
            'max_comparisons': 100,
            'batch_size': 10,
            'max_epochs': 20,
            'learning_rate': 0.01,
            'patience': 10,
            'convergence_window': 5,
            'convergence_threshold': 4,
            'top_k': 5,
        }

    config = st.session_state.config

    # Data Source Configuration
    st.header("📁 Data Source")

    col1, col2 = st.columns(2)

    with col1:
        # Use directory picker for easier browsing
        lamap_dir = st.text_input(
            "LAMAP Results Directory",
            value=config.get('lamap_results_dir', '/Users/simonjaxy/Documents/vub/archaeology/preference_learning/pylamap/results/cyprus'),
            help="Path to directory containing LAMAP outputs (e.g., /Users/simonjaxy/Documents/vub/archaeology/preference_learning/pylamap/results/cyprus)"
        )

        # Quick browse buttons for common locations
        st.markdown("**Quick Select:**")
        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            if st.button("📁 Use Default", help="Use the default Cyprus directory"):
                config['lamap_results_dir'] = '/Users/simonjaxy/Documents/vub/archaeology/preference_learning/pylamap/results/cyprus'
                st.rerun()

        with col_btn2:
            # Alternative: manually enter path
            alt_path = st.text_input(
                "Or enter path manually:",
                placeholder="/path/to/lamap/results",
                label_visibility="visible"
            )
            if st.button("Use Custom Path") and alt_path:
                config['lamap_results_dir'] = alt_path
                st.rerun()

        # Directory info
        if lamap_dir and Path(lamap_dir).exists():
            periods = [d.name for d in Path(lamap_dir).iterdir() if d.is_dir()]
            if periods:
                st.caption(f"✓ Found {len(periods)} periods: {', '.join(periods[:5])}" +
                             (f"..." if len(periods) > 5 else ""))
            else:
                st.caption("⚠️ No period subdirectories found")
        elif lamap_dir:
            st.caption("⚠️ Directory does not exist")

    with col2:
        # Period selection
        periods = ['bronze_age', 'byzantine', 'roman', 'neolithic', 'other']
        period_idx = periods.index(config['period']) if config['period'] in periods else 0
        period = st.selectbox(
            "Period",
            periods,
            index=period_idx,
            help="Archaeological period to analyze"
        )

    # Learning Configuration
    st.header("🤖 Learning Configuration")

    col1, col2 = st.columns(2)

    with col1:
        # Learning strategy (GP only initially)
        strategy = st.selectbox(
            "Learning Strategy",
            ['gp'],
            index=0,
            help="Strategy for learning from preferences",
            disabled=True
        )
        st.caption("Currently only GP (Gaussian Process) is supported")

    with col2:
        # Acquisition function (auto-discovered from registry)
        acquisitions = list_acquisitions()
        acq_idx = acquisitions.index(config['acquisition']) if config['acquisition'] in acquisitions else 0
        acquisition = st.selectbox(
            "Acquisition Function",
            acquisitions,
            index=acq_idx,
            help="Method for selecting pairs to compare"
        )

    col1, col2 = st.columns(2)

    with col1:
        # Encoder (handcrafted initially)
        encoder = st.selectbox(
            "Feature Encoder",
            ['handcrafted'],
            index=0,
            help="Method for encoding masks into features",
            disabled=True
        )
        st.caption("Currently only handcrafted features are supported")

    with col2:
        # Decision mode
        decision_mode = st.selectbox(
            "Decision Mode",
            ['human', 'oracle'],
            index=0 if config.get('decision_mode') == 'human' else 1,
            help="Who makes the preference decisions"
        )

    # Oracle Configuration (if oracle mode selected)
    if decision_mode == 'oracle':
        st.header("🔮 Virtual Oracle Configuration")

        col1, col2 = st.columns(2)

        with col1:
            # Oracle type
            oracles = list_oracles()
            oracle_config = config.get('oracle_config', {})
            oracle_type = oracle_config.get('oracle_type', 'biased')
            oracle_idx = oracles.index(oracle_type) if oracle_type in oracles else 0

            oracle_type = st.selectbox(
                "Oracle Type",
                oracles,
                index=oracle_idx,
                help="Type of virtual decision maker"
            )

            # Initialize oracle_config if not exists
            if 'oracle_config' not in config:
                config['oracle_config'] = {}

            config['oracle_config']['oracle_type'] = oracle_type

        with col2:
            # Noise slider
            noise = st.slider(
                "Decision Noise",
                min_value=0.0,
                max_value=1.0,
                value=oracle_config.get('noise', 0.1),
                step=0.05,
                help="Probability of random decision (0 = deterministic, 1 = random)"
            )
            config['oracle_config']['noise'] = noise

        # Biased oracle specific settings
        if oracle_type == 'biased':
            st.subheader("Feature Biases")

            col1, col2, col3 = st.columns(3)

            with col1:
                # V4 CHANGE: Entropy replaces compactness (which was always 1.0 on this data)
                entropy_bias = st.slider(
                    "Certainty Bias (low entropy)",
                    min_value=-1.0,
                    max_value=1.0,
                    value=oracle_config.get('entropy_bias', 0.0),
                    step=0.1,
                    help="Preference for confident/certain predictions (low entropy)"
                )
                config['oracle_config']['entropy_bias'] = entropy_bias

                morans_i_bias = st.slider(
                    "Moran's I Bias",
                    min_value=-1.0,
                    max_value=1.0,
                    value=oracle_config.get('morans_i_bias', 0.0),
                    step=0.1,
                    help="Preference for spatial autocorrelation"
                )
                config['oracle_config']['morans_i_bias'] = morans_i_bias

            with col2:
                components_bias = st.slider(
                    "Components Bias",
                    min_value=-1.0,
                    max_value=1.0,
                    value=oracle_config.get('components_bias', 0.0),
                    step=0.1,
                    help="Preference for number of connected components"
                )
                config['oracle_config']['components_bias'] = components_bias

                area_bias = st.slider(
                    "Area Bias",
                    min_value=-1.0,
                    max_value=1.0,
                    value=oracle_config.get('area_bias', 0.0),
                    step=0.1,
                    help="Preference for mask area"
                )
                config['oracle_config']['area_bias'] = area_bias

            with col3:
                perimeter_ratio_bias = st.slider(
                    "Perimeter Ratio Bias",
                    min_value=-1.0,
                    max_value=1.0,
                    value=oracle_config.get('perimeter_ratio_bias', 0.0),
                    step=0.1,
                    help="Preference for perimeter-to-area ratio"
                )
                config['oracle_config']['perimeter_ratio_bias'] = perimeter_ratio_bias

    # Session Settings
    st.header("⚙️ Session Settings")

    col1, col2 = st.columns(2)

    with col1:
        max_comparisons = st.number_input(
            "Max Comparisons",
            min_value=10,
            max_value=1000,
            value=config.get('max_comparisons', 100),
            step=10,
            help="Maximum number of pairwise comparisons to collect"
        )

    with col2:
        batch_size = st.number_input(
            "Batch Size",
            min_value=1,
            max_value=50,
            value=config.get('batch_size', 10),
            step=1,
            help="Number of comparisons per batch before retraining"
        )

    # Advanced Settings
    with st.expander("🔧 Advanced Settings"):
        col1, col2 = st.columns(2)

        with col1:
            max_epochs = st.number_input(
                "Max Training Epochs",
                min_value=10,
                max_value=500,
                value=config.get('max_epochs', 100),
                step=10,
                help="Maximum epochs for GP training"
            )

            learning_rate = st.number_input(
                "Learning Rate",
                min_value=0.001,
                max_value=0.1,
                value=config.get('learning_rate', 0.01),
                format="%.4f",
                help="Learning rate for GP optimization"
            )

        with col2:
            patience = st.number_input(
                "Early Stopping Patience",
                min_value=1,
                max_value=50,
                value=config.get('patience', 10),
                step=1,
                help="Epochs to wait before early stopping"
            )

            convergence_window = st.number_input(
                "Convergence Window",
                min_value=3,
                max_value=20,
                value=config.get('convergence_window', 5),
                step=1,
                help="Iterations to check for convergence"
            )

        col1, col2 = st.columns(2)

        with col1:
            convergence_threshold = st.number_input(
                "Convergence Threshold",
                min_value=1,
                max_value=10,
                value=config.get('convergence_threshold', 4),
                step=1,
                help="Agreements needed for convergence"
            )

        with col2:
            top_k = st.number_input(
                "Top-K for Convergence",
                min_value=3,
                max_value=20,
                value=config.get('top_k', 5),
                step=1,
                help="Number of top candidates to check for stability"
            )

    # Update config
    config.update({
        'lamap_results_dir': lamap_dir,
        'period': period,
        'strategy': strategy,
        'acquisition': acquisition,
        'encoder': encoder,
        'decision_mode': decision_mode,
        'max_comparisons': max_comparisons,
        'batch_size': batch_size,
        'max_epochs': max_epochs,
        'learning_rate': learning_rate,
        'patience': patience,
        'convergence_window': convergence_window,
        'convergence_threshold': convergence_threshold,
        'top_k': top_k,
    })

    st.session_state.config = config

    # Start Session button
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.button("🚀 Start Session", type="primary"):
            # Validate config
            is_valid, error_msg = validate_config(config)

            if not is_valid:
                st.error(f"Configuration Error: {error_msg}")
                return

            # Load masks
            with st.spinner("Loading LAMAP masks..."):
                try:
                    masks, metadata = load_lamap_masks(lamap_dir, period)

                    st.success(f"Loaded {len(masks)} masks from {period}")

                    # Store in session state
                    st.session_state.masks = masks
                    st.session_state.mask_metadata = metadata

                    # Initialize active learning loop
                    st.session_state.active_learning_loop = ActiveLearningLoop(masks, config)

                    # Create session
                    session_id = st.session_state.active_learning_loop.save_session()
                    st.session_state.session_id = session_id

                    # Reset state
                    st.session_state.current_batch = []
                    st.session_state.batch_preferences = {}
                    st.session_state.batch_count = 0
                    st.session_state.total_comparisons = 0
                    st.session_state.review_queue = []

                    st.success(f"Session '{session_id}' created successfully!")

                    # Navigate to collect page
                    st.session_state.current_page = 'collect'
                    st.session_state.batch_count = 0

                    st.success(f"Session '{session_id}' created successfully!")
                    st.rerun()

                except Exception as e:
                    st.error(f"Error loading masks: {str(e)}")
                    logger.error(f"Error loading masks: {e}", exc_info=True)

    # Display current config summary
    if st.session_state.config.get('lamap_results_dir'):
        st.markdown("---")
        st.subheader("Configuration Summary")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Data Source**")
            st.caption(f"Directory: `{config['lamap_results_dir']}`")
            st.caption(f"Period: {config['period']}")

        with col2:
            st.markdown("**Learning**")
            st.caption(f"Strategy: {config['strategy']}")
            st.caption(f"Acquisition: {config['acquisition']}")
            st.caption(f"Encoder: {config['encoder']}")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Decision Mode**")
            st.caption(f"Mode: {config['decision_mode']}")
            if config['decision_mode'] == 'oracle':
                oracle_type = config.get('oracle_config', {}).get('oracle_type', 'biased')
                st.caption(f"Oracle: {oracle_type}")

        with col2:
            st.markdown("**Session Limits**")
            st.caption(f"Max Comparisons: {config['max_comparisons']}")
            st.caption(f"Batch Size: {config['batch_size']}")
