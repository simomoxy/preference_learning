#!/usr/bin/env python
"""
Foundation validation tests.

Run this from the parent directory with: python preference_webapp/test_foundation.py
Or from within preference_webapp/: python test_foundation.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports (where models/, scripts/, etc. are)
script_dir = Path(__file__).parent
parent_dir = script_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))


def test_imports():
    """Verify all imports work."""
    print("Testing imports...")

    try:
        import streamlit as st
        print("  ✓ streamlit")
    except ImportError as e:
        print(f"  ✗ streamlit: {e}")
        return False

    try:
        import torch
        print("  ✓ torch")
    except ImportError as e:
        print(f"  ✗ torch: {e}")
        return False

    try:
        import gpytorch
        print("  ✓ gpytorch")
    except ImportError as e:
        print(f"  ✗ gpytorch: {e}")
        return False

    try:
        import pytorch_lightning
        print("  ✓ pytorch_lightning")
    except ImportError as e:
        print(f"  ✗ pytorch_lightning: {e}")
        return False

    try:
        import rasterio
        print("  ✓ rasterio")
    except ImportError as e:
        print(f"  ✗ rasterio: {e}")
        return False

    try:
        import matplotlib
        print("  ✓ matplotlib")
    except ImportError as e:
        print(f"  ✗ matplotlib: {e}")
        return False

    try:
        import plotly
        print("  ✓ plotly")
    except ImportError as e:
        print(f"  ✗ plotly: {e}")
        return False

    try:
        from sklearn.preprocessing import StandardScaler
        print("  ✓ sklearn")
    except ImportError as e:
        print(f"  ✗ sklearn: {e}")
        return False

    print("\n✓ All imports successful")
    return True


def test_existing_code():
    """Verify existing preference learning code works."""
    print("\nTesting existing code...")

    try:
        from models.toy_encoder import SegmentationFeatureEncoder
        encoder = SegmentationFeatureEncoder()
        print("  ✓ SegmentationFeatureEncoder imported")
    except ImportError as e:
        print(f"  ✗ SegmentationFeatureEncoder: {e}")
        return False

    try:
        import numpy as np
        dummy_mask = np.random.randint(0, 2, (64, 64))
        features = encoder.encode(dummy_mask)
        assert len(features) == 5, f"Expected 5 features, got {len(features)}"
        print(f"  ✓ Feature encoder works (5D features: {features})")
    except Exception as e:
        print(f"  ✗ Feature encoder test failed: {e}")
        return False

    try:
        # Check if the file exists first
        acquisition_path = parent_dir / "acquisition" / "acquisition.py"
        if not acquisition_path.exists():
            print(f"  ✗ Acquisition function: file not found at {acquisition_path}")
            return False

        from acquisition.acquisition import get_acquisition_function
        acq_fn = get_acquisition_function('random')
        print("  ✓ Acquisition function imported")
    except Exception as e:
        print(f"  ✗ Acquisition function: {e}")
        import traceback
        traceback.print_exc()
        return False

    try:
        from metrics.copeland_score import copeland_score
        print("  ✓ Copeland score function imported")
    except ImportError as e:
        print(f"  ✗ Copeland score: {e}")
        return False

    try:
        from models.toy_gp import PreferenceGP
        print("  ✓ PreferenceGP imported")
    except ImportError as e:
        print(f"  ✗ PreferenceGP: {e}")
        return False

    try:
        from modules.toy_module import PreferenceGPModule
        print("  ✓ PreferenceGPModule imported")
    except ImportError as e:
        print(f"  ✗ PreferenceGPModule: {e}")
        return False

    try:
        from scripts.biased_oracle import BiasedSegmentationOracle
        oracle = BiasedSegmentationOracle()
        print("  ✓ BiasedSegmentationOracle imported")
    except ImportError as e:
        print(f"  ✗ BiasedSegmentationOracle: {e}")
        return False

    print("\n✓ All existing code tests passed")
    return True


def test_directory_structure():
    """Verify webapp directory structure exists."""
    print("\nTesting directory structure...")

    # Get the webapp root directory (parent of this script)
    webapp_root = Path(__file__).parent

    required_dirs = [
        "backend/core",
        "backend/strategies",
        "backend/oracles",
        "encoders",
        "acquisition",
        "ui/pages",
        "data/sessions",
        "data/preferences",
        "data/checkpoints",
    ]

    all_exist = True
    for dir_path in required_dirs:
        path = webapp_root / dir_path
        if path.exists() and path.is_dir():
            print(f"  ✓ {dir_path}")
        else:
            print(f"  ✗ {dir_path} (missing)")
            all_exist = False

    if all_exist:
        print("\n✓ All directories exist")
    return all_exist


def main():
    """Run all foundation tests."""
    print("=" * 60)
    print("FOUNDATION VALIDATION TESTS")
    print("=" * 60)

    results = {
        "imports": test_imports(),
        "existing_code": test_existing_code(),
        "directory_structure": test_directory_structure(),
    }

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_passed = all(results.values())

    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")

    print("=" * 60)

    if all_passed:
        print("\n✅ Foundation validated - ready to build!")
        return 0
    else:
        print("\n❌ Foundation validation failed - fix issues before proceeding")
        return 1


if __name__ == "__main__":
    exit(main())
