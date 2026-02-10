"""
Test script to verify all UI imports work correctly.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing UI imports...")

try:
    print("✓ Importing app.py...")
    import app
    print("  ✓ app.py imported successfully")
except Exception as e:
    print(f"  ✗ Error importing app.py: {e}")

try:
    print("✓ Importing ui.components...")
    from ui.components import (
        display_side_by_side_images,
        display_single_image,
        preference_buttons,
        progress_bar,
        metrics_plot,
        session_info_sidebar,
        ranking_table,
        export_buttons
    )
    print("  ✓ ui.components imported successfully")
except Exception as e:
    print(f"  ✗ Error importing ui.components: {e}")

try:
    print("✓ Importing ui.utils...")
    from ui.utils import (
        safe_execute,
        format_timestamp,
        get_session_summary,
        validate_config,
        load_lamap_masks
    )
    print("  ✓ ui.utils imported successfully")
except Exception as e:
    print(f"  ✗ Error importing ui.utils: {e}")

try:
    print("✓ Importing ui.pages.config...")
    from ui.pages.config import show_config_page
    print("  ✓ ui.pages.config imported successfully")
except Exception as e:
    print(f"  ✗ Error importing ui.pages.config: {e}")

try:
    print("✓ Importing ui.pages.collect...")
    from ui.pages.collect import show_collect_page
    print("  ✓ ui.pages.collect imported successfully")
except Exception as e:
    print(f"  ✗ Error importing ui.pages.collect: {e}")

try:
    print("✓ Importing ui.pages.train...")
    from ui.pages.train import show_train_page
    print("  ✓ ui.pages.train imported successfully")
except Exception as e:
    print(f"  ✗ Error importing ui.pages.train: {e}")

try:
    print("✓ Importing ui.pages.results...")
    from ui.pages.results import show_results_page
    print("  ✓ ui.pages.results imported successfully")
except Exception as e:
    print(f"  ✗ Error importing ui.pages.results: {e}")

print("\n✓ All UI imports successful!")
print("\nYou can now run the Streamlit app with:")
print("  streamlit run app.py")
