"""
Archaeology-themed styling for the preference learning webapp.

Color palette inspired by archaeological materials:
- Terracotta: Primary color for actions
- Sand: Secondary backgrounds
- Olive: Accent colors
- Parchment: Main background
- Dark Earth: Text
"""

import streamlit as st


# Archaeology-themed color palette
COLORS = {
    'primary': '#C97B63',      # Terracotta
    'secondary': '#8B9556',    # Olive
    'accent': '#D4B896',       # Sand
    'background': '#F5F0E6',   # Parchment
    'text': '#3D3B30',         # Dark earth
    'success': '#6B8E23',      # Olive green
    'warning': '#DAA520',      # Goldenrod
    'error': '#A0522D',        # Sienna
}


def apply_theme():
    """
    Apply archaeology-themed CSS styling to the Streamlit app.
    Call this once at the beginning of the app.
    """
    st.markdown(f"""
    <style>
    /* Main app background */
    .stApp {{
        background-color: {COLORS['background']};
    }}

    /* Text colors */
    .stApp {{
        color: {COLORS['text']};
    }}

    /* Header styling */
    h1, h2, h3 {{
        color: {COLORS['text']} !important;
        font-family: 'Georgia', serif;
    }}

    /* Custom button styles */
    .stButton > button {{
        background-color: {COLORS['primary']};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-size: 1rem;
        font-weight: 600;
        transition: all 0.2s;
    }}

    .stButton > button:hover {{
        background-color: #A8604A;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }}

    .stButton > button:active {{
        transform: translateY(1px);
    }}

    /* Primary action buttons */
    .stButton > button[kind="primary"] {{
        background-color: {COLORS['primary']};
        color: white;
        font-size: 1.1rem;
        padding: 0.75rem 2rem;
    }}

    /* Secondary buttons (not primary) */
    .stButton > button:not([kind="primary"]) {{
        background-color: {COLORS['accent']};
        color: {COLORS['text']};
    }}

    .stButton > button:not([kind="primary"]):hover {{
        background-color: #C4A882;
    }}

    /* Metric cards */
    [data-testid="stMetricValue"] {{
        color: {COLORS['primary']} !important;
        font-size: 2rem;
        font-weight: bold;
    }}

    [data-testid="stMetricDelta"] {{
        color: {COLORS['secondary']} !important;
    }}

    /* Progress bar */
    .stProgress > div > div > div > div {{
        background-color: {COLORS['primary']};
    }}

    /* Info boxes */
    .stAlert {{
        background-color: {COLORS['accent']};
        border-left: 4px solid {COLORS['primary']};
        border-radius: 4px;
    }}

    /* Success messages */
    .stSuccess {{
        background-color: #E8F5E9;
        border-left: 4px solid {COLORS['success']};
    }}

    /* Warning messages */
    .stWarning {{
        background-color: #FFF8E1;
        border-left: 4px solid {COLORS['warning']};
    }}

    /* Error messages */
    .stError {{
        background-color: #FFEBEE;
        border-left: 4px solid {COLORS['error']};
    }}

    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background-color: {COLORS['accent']};
    }}

    /* Input fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {{
        border-color: {COLORS['primary']};
        border-radius: 4px;
    }}

    /* Cards and containers */
    div[data-testid="stVerticalBlock"] > div[style*="background-color"] {{
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}

    /* Image containers */
    .stImage > img {{
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }}

    /* Tables */
    .stDataFrame {{
        border-radius: 8px;
        overflow: hidden;
    }}

    /* Custom classes for specific elements */
    .archaeology-header {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }}

    .archaeology-card {{
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin: 1rem 0;
    }}

    .comparison-container {{
        display: flex;
        gap: 2rem;
        justify-content: center;
        align-items: center;
        padding: 1rem;
    }}

    .mask-comparison {{
        flex: 1;
        text-align: center;
        padding: 1rem;
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }}

    .mask-comparison:hover {{
        transform: translateY(-4px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.15);
    }}

    .winner-badge {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 12px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        margin: 2rem 0;
        animation: pulse 2s infinite;
    }}

    @keyframes pulse {{
        0%, 100% {{
            transform: scale(1);
        }}
        50% {{
            transform: scale(1.02);
        }}
    }}
    </style>
    """, unsafe_allow_html=True)


def get_theme_config():
    """
    Get theme configuration for Streamlit config.toml.

    Returns:
        dict: Theme configuration
    """
    return {
        'primaryColor': COLORS['primary'],
        'backgroundColor': COLORS['background'],
        'secondaryBackgroundColor': COLORS['accent'],
        'textColor': COLORS['text'],
        'font': 'serif',
    }


def render_archaeology_header(title: str, subtitle: str = None, icon: str = ""):
    """
    Render an archaeology-themed header.

    Args:
        title: Main title text
        subtitle: Optional subtitle
        icon: Icon (default: empty)
    """
    st.markdown(f"""
    <div class="archaeology-header">
        <h1 style="color: white; margin: 0; font-size: 2.5rem;">
            {title}
        </h1>
        {f'<p style="color: white; margin: 0.5rem 0 0 0; font-size: 1.3rem; font-weight: 500;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def render_progress_indicator(current_step: int, total_steps: int, step_names: list):
    """
    Render a step-by-step progress indicator.

    Args:
        current_step: Current step number (1-indexed)
        total_steps: Total number of steps
        step_names: List of step names
    """
    progress_html = '<div style="display: flex; justify-content: space-between; align-items: center; margin: 2rem 0;">'

    for i in range(total_steps):
        step_number = i + 1
        is_active = step_number == current_step
        is_completed = step_number < current_step

        # Circle style
        if is_completed:
            circle_color = COLORS['success']
            circle_text = "✓"
        elif is_active:
            circle_color = COLORS['primary']
            circle_text = str(step_number)
        else:
            circle_color = COLORS['accent']
            circle_text = str(step_number)

        # Step circle
        progress_html += f'''
        <div style="text-align: center; flex: 1;">
            <div style="
                width: 50px;
                height: 50px;
                border-radius: 50%;
                background-color: {circle_color};
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.2rem;
                font-weight: bold;
                margin: 0 auto 0.5rem;
                border: 3px solid {'white' if is_active or is_completed else COLORS['accent']};
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            ">
                {circle_text}
            </div>
            <div style="font-size: 0.85rem; color: {COLORS['text']}; font-weight: {'bold' if is_active else 'normal'};">
                {step_names[i] if i < len(step_names) else f'Step {step_number}'}
            </div>
        </div>
        '''

        # Add connector line (except after last step)
        if i < total_steps - 1:
            line_color = COLORS['success'] if is_completed else COLORS['accent']
            progress_html += f'<div style="flex: 0.5; height: 3px; background-color: {line_color}; margin: 0 0.5rem 2rem;"></div>'

    progress_html += '</div>'

    st.markdown(progress_html, unsafe_allow_html=True)
