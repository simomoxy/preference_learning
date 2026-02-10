#!/usr/bin/env python
"""
Generate sample segmentation masks for testing the Streamlit UI.

Creates a sample LAMAP results directory with dummy data.
"""

import numpy as np
from pathlib import Path
from PIL import Image
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def create_sample_masks(n_masks: int = 50, output_dir: str = "lamap_results_sample"):
    """
    Create sample segmentation masks for testing.

    Args:
        n_masks: Number of masks to generate
        output_dir: Output directory path
    """
    output_path = Path(output_dir)

    # Create directory structure
    periods = ['bronze_age', 'byzantine', 'roman']

    for period in periods:
        period_dir = output_path / period
        period_dir.mkdir(parents=True, exist_ok=True)

        print(f"Generating {n_masks} masks for {period}...")

        for i in range(n_masks):
            # Generate random binary mask with some structure
            mask = generate_structured_mask(64, 64, seed=i)

            # Save as PNG
            mask_img = Image.fromarray((mask * 255).astype(np.uint8), mode='L')
            mask_path = period_dir / f"site_{i:04d}_mask.png"
            mask_img.save(mask_path)

        print(f"  ✓ Created {n_masks} masks in {period_dir}")

    print()
    print(f"✓ Sample data generated successfully!")
    print(f"  Location: {output_path.absolute()}")
    print()
    print("To use in the Streamlit app:")
    print(f"  1. In Configuration page, enter this path:")
    print(f"     {output_path.absolute()}")
    print(f"  2. Select a period: {periods[0]}")
    print(f"  3. Click 'Start Session'")


def generate_structured_mask(height: int, width: int, seed: int = None) -> np.ndarray:
    """
    Generate a structured binary mask.

    Creates masks with random shapes, blobs, and patterns
    to simulate archaeological site predictions.

    Args:
        height: Mask height
        width: Mask width
        seed: Random seed

    Returns:
        Binary mask (0 or 1)
    """
    if seed is not None:
        np.random.seed(seed)

    mask = np.zeros((height, width), dtype=bool)

    # Number of components (1-5)
    n_components = np.random.randint(1, 6)

    for _ in range(n_components):
        # Random center
        cy = np.random.randint(0, height)
        cx = np.random.randint(0, width)

        # Random size
        radius = np.random.randint(5, 20)

        # Create blob
        y, x = np.ogrid[:height, :width]
        mask_blob = ((x - cx)**2 + (y - cy)**2) <= radius**2

        # Add some noise/irregularity
        noise = np.random.rand(height, width) * 5
        mask_blob = mask_blob & (np.random.rand(height, width) > 0.1)

        mask = mask | mask_blob

    # Add some random noise
    mask = mask & (np.random.rand(height, width) > 0.05)

    return mask.astype(np.uint8)


def create_demo_session():
    """
    Create a demo session with pre-collected preferences.
    """
    from backend.active_learning_loop import ActiveLearningLoop

    print("Creating demo session with sample data...")

    # Generate sample masks
    n_masks = 20
    masks = [generate_structured_mask(64, 64, seed=i) for i in range(n_masks)]

    # Configure
    config = {
        'max_iterations': 5,
        'n_pairs_per_iteration': 5,
        'acquisition': 'thompson_sampling',
        'max_epochs': 10,
        'patience': 5,
    }

    # Initialize loop
    loop = ActiveLearningLoop(masks, config)

    # Simulate some preferences
    print("Simulating preferences...")
    for iteration in range(3):
        pairs = loop.get_next_batch(n_pairs=5)

        # Generate random preferences
        preferences = []
        for i, j in pairs:
            # Prefer masks with more components
            mask_i_sum = masks[i].sum()
            mask_j_sum = masks[j].sum()

            if mask_i_sum > mask_j_sum * 1.1:
                pref = 0  # i preferred
            elif mask_j_sum > mask_i_sum * 1.1:
                pref = 1  # j preferred
            else:
                pref = np.random.randint(0, 2)  # Random

            preferences.append(pref)

        # Add preferences
        loop.add_preferences(pairs, preferences)
        print(f"  Iteration {iteration + 1}: Added {len(pairs)} preferences")

    # Save session
    session_id = loop.save_session()
    print(f"✓ Demo session created: {session_id}")

    # Get ranking
    ranking, scores = loop.get_ranking()
    print(f"✓ Ranking computed: Top mask is #{ranking[0]}")

    return session_id


if __name__ == "__main__":
    print("=" * 80)
    print("Sample Data Generator for Preference Learning Webapp")
    print("=" * 80)
    print()

    # Create sample masks
    create_sample_masks(n_masks=50, output_dir="lamap_results_sample")

    print()
    print("=" * 80)
    print("Demo Session Generator")
    print("=" * 80)
    print()

    # Create demo session
    try:
        session_id = create_demo_session()
        print()
        print("Demo session is ready to view in the Results page!")
    except Exception as e:
        print(f"Note: Demo session creation requires full backend setup: {e}")

    print()
    print("=" * 80)
    print("Setup Complete!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Run the Streamlit app: streamlit run app.py")
    print("  2. Go to Configuration page")
    print("  3. Enter path: lamap_results_sample")
    print("  4. Select period: bronze_age")
    print("  5. Start exploring!")
    print()
