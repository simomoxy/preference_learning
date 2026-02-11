# Archaeological Preference Learning Webapp

A Streamlit web application for collecting expert preferences on LAMAP (Locally Adaptive Adaptive Multivariate Assemblage Probability) predictions through pairwise comparisons.

## Quick Start

### Running Locally

```bash
cd preference_webapp

# Install dependencies (first time only)
pip install -r requirements.txt

# Run the webapp
streamlit run app_simple.py
```

### Loading Data

The webapp automatically loads LAMAP prediction masks from:
- **GitHub**: `simomoxy/lamap-bronze-age-data` (default for deployment)
- **Local files**: `preference_webapp/bronze_age/` (for testing)

## Deployment to Streamlit Cloud

1. **Push code to GitHub** (already done at `simomoxy/preference_learning`)

2. **Deploy to Streamlit Cloud**:
   - Go to https://share.streamlit.io
   - Click "New app"
   - Select repository: `simomoxy/preference_learning`
   - Main file path: `preference_webapp/app_simple.py`
   - Click "Deploy"

3. **Set environment variables** (in Streamlit Cloud app settings):
   - `GITHUB_DATA_REPO`: `simomoxy/lamap-bronze-age-data`
   - `GITHUB_TOKEN`: Your GitHub personal access token (for uploading responses)
   - `GITHUB_BRANCH`: `main` (optional)

### Troubleshooting Deployment

If the app crashes on Streamlit Cloud:
1. Check the app logs in Streamlit Cloud dashboard
2. Common issues:
   - Missing environment variables (set `GITHUB_DATA_REPO` at minimum)
   - Large memory usage (Streamlit Cloud free tier has limited RAM)
   - Timeout when loading many images from GitHub

## Usage

1. Select archaeological period (bronze_age, byzantine, roman)
2. Enter expert name
3. Load prediction maps
4. Complete 30 pairwise comparisons
5. View results and export data

## Features

- **Archaeology-themed UI** with earth tones and clean design
- **Pairwise comparison interface** for intuitive expert feedback
- **Statistics display**: Moran's I, Components, Compactness, Coverage
- **Automatic data upload** to GitHub for researcher collection
- **CSV/JSON export** for backup

## Project Structure

```
preference_webapp/
├── app_simple.py          # Main application entry point
├── requirements.txt        # Python dependencies
├── ui/                     # User interface components
│   ├── pages/
│   │   ├── welcome.py      # Data loading page
│   │   ├── collect_simple.py  # Comparison interface
│   │   └── summary.py      # Results and export
│   └── theme.py            # Archaeology-themed styling
├── github_loader.py        # Load masks from GitHub
├── github_data_uploader.py # Upload results to GitHub
└── bronze_age/             # Local test data (26 LAMAP outputs)
```

## For Archaeologists

Your task is to compare pairs of site prediction maps and choose which looks more plausible for archaeological sites. Consider:
- Site shape and compactness
- Spatial coherence
- Archaeological realism

Time estimate: ~20 minutes for 30 comparisons

## For Researchers

### Data Collection Flow

1. Deploy webapp to Streamlit Cloud
2. Share URL with expert archaeologists
3. Experts complete comparisons and data auto-uploads to GitHub
4. Download all responses from: `simomoxy/lamap-bronze-age-data/tree/main/responses`

### Environment Variables

- `GITHUB_DATA_REPO`: Repository containing LAMAP masks (default: `simomoxy/lamap-bronze-age-data`)
- `GITHUB_TOKEN`: Personal access token for uploading expert data
- `GITHUB_BRANCH`: Branch to use (default: `main`)

## Citation

This webapp was developed for the research project on **Preferential Bayesian Optimization (PBO)** for evaluating ambiguous segmentation outputs in archaeological site prediction.

## License

MIT License - See LICENSE file for details.
