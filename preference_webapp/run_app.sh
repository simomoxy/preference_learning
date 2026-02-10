#!/bin/bash

# Startup script for the simplified preference learning webapp
# This script activates the conda environment and runs the app

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=================================================="
echo "  Archaeological Preference Learning Webapp"
echo "=================================================="
echo ""

# Check if conda environment exists
if [ ! -d "$PROJECT_ROOT/.conda" ]; then
    echo "Error: Conda environment not found at $PROJECT_ROOT/.conda"
    echo "Please create the conda environment first."
    exit 1
fi

# Activate conda environment
echo "Activating conda environment..."
source "$PROJECT_ROOT/.conda/bin/activate"

# Verify activation
if [ -z "$CONDA_PREFIX" ]; then
    echo "Error: Failed to activate conda environment"
    exit 1
fi

echo "✓ Conda environment activated: $CONDA_PREFIX"
echo ""

# Navigate to webapp directory
cd "$SCRIPT_DIR"
echo "Working directory: $SCRIPT_DIR"
echo ""

# Check if sample data exists
if [ ! -d "lamap_results_sample" ]; then
    echo "Warning: Sample data directory not found"
    echo "Expected: lamap_results_sample/{bronze_age,byzantine,roman}/"
else
    # Count PNG files
    PNG_COUNT=$(find lamap_results_sample -name "*.png" 2>/dev/null | wc -l)
    echo "✓ Found $PNG_COUNT PNG files in lamap_results_sample/"
fi
echo ""

# Run the app
echo "=================================================="
echo "  Starting Streamlit app..."
echo "=================================================="
echo ""
echo "The app will open in your browser at:"
echo "  http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the app"
echo ""

# Run streamlit
python -m streamlit run app_simple.py "$@"
