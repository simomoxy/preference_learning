# Quick Start - Simplified Preference Learning Webapp

## For Archaeologists

### Access the App

1. Click the link provided by the research team
2. Wait for the page to load (~5-10 seconds)
3. Enter your name (optional)
4. Select a period (Bronze Age, Byzantine, or Roman)
5. Click "Load Predictions"

### Making Comparisons

1. **Look at both images** side-by-side
2. **Ask yourself:** Which looks more like a real archaeological site?
3. **Click your choice:**
   - Left is Better
   - Right is Better
   - Can't Decide (if they're equal)
   - Skip (if unsure)

### Keyboard Shortcuts (Faster!)

- `A` or `←` : Left image is better
- `D` or `→` : Right image is better
- `T` : Tie
- `S` : Skip

### Tips

- **Trust your intuition** - if it looks right, it probably is
- **Look for compact shapes** - scattered pixels are usually wrong
- **Consider coherence** - nearby pixels should be similar
- **Take breaks** if needed - your progress is saved

### After 50 Comparisons

1. Click "Download CSV" or "Download JSON"
2. Save the file somewhere you can find it
3. Share the file with the research team

**Time estimate:** ~30 minutes

---

## For Developers - Local Testing

### Quick Start

```bash
# From the preference_webapp directory
./run_app.sh
```

Or manually:

```bash
# From project root
conda activate .conda
cd preference_webapp
python -m streamlit run app_simple.py
```

The app will open at http://localhost:8501

### Test with Sample Data

The app includes 150 sample images (50 per period):
- `lamap_results_sample/bronze_age/` - 50 PNG files
- `lamap_results_sample/byzantine/` - 50 PNG files
- `lamap_results_sample/roman/` - 50 PNG files

### Verify Installation

```bash
.conda/bin/python -c "
import sys
sys.path.insert(0, 'preference_webapp')
from ui.theme import COLORS
print('✓ Installation OK')
print('Theme:', COLORS['primary'])
"
```

---

## Troubleshooting

### "Data not loading"

**Solution:**
- Check that `lamap_results_sample/` exists and has PNG files
- Or set `DATA_SERVER_URL` environment variable for server-based loading

### "ImportError"

**Solution:**
```bash
conda activate .conda
pip install -r preference_webapp/requirements.txt
```

### "Port already in use"

**Solution:**
```bash
# Use a different port
streamlit run app_simple.py --server.port 8502
```

### Styling looks wrong

**Solution:**
- Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
- Check that `.streamlit/config.toml` exists

---

## Configuration

### Set Server Data URL

For server-based data loading:

```bash
export DATA_SERVER_URL="https://your-server.com/data"
```

Then the app will load from:
- `https://your-server.com/data/bronze_age/`
- `https://your-server.com/data/byzantine/`
- `https://your-server.com/data/roman/`

### Change Number of Comparisons

Edit `config.py`:

```python
DEFAULT_NUM_COMPARISONS = 50  # Change this number
```

---

**Last updated:** 2025-02-09
