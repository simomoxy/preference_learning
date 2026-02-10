# Webapp Changes Summary

All requested issues have been fixed:

## Fixed Issues

1. **LAMAP name corrected** - Now correctly shows "A Locally-Adaptive Model of Archaeological Potential (LAMAP)"

2. **Export functionality changed** - Archaeologists no longer see export as primary action. Download buttons moved to bottom as "Backup Download (Optional)". Main message states data will be collected by research team.

3. **HTML rendering fixed** - Tips section now renders properly as HTML instead of showing tags

4. **Loading order fixed** - GitHub is tried first, then local files, then Dropbox (as last resort)

5. **Button styling fixed** - Buttons now use sand/accent background color instead of white. Text changed to "Left Option" and "Right Option"

6. **Statistics display** - Shows Site Count, Compactness, Spatial Coherence, and Coverage for each prediction. Added "What do these statistics mean?" expander with cheat sheet

7. **Keyboard shortcuts fixed** - JavaScript updated to properly find buttons by their key attribute

8. **Click to select** - Added "Select Left Option" and "Select Right Option" buttons below each image

9. **Buttons moved to top** - Preference buttons now appear before the images for better flow

10. **All emojis removed** - Cleaned up from all pages and components

11. **Subtitle visibility improved** - Made subtitle color white (full opacity) and increased font size to 1.3rem with font-weight 500

12. **Visual feedback** - Streamlit reruns after selection, showing "Recorded: Left/Right Option Preferred" message

13. **Image IDs hidden** - No longer showing mask filenames that contain parameter information

14. **Ranking page error fixed** - Removed problematic metadata access, simplified ranking display to show top 10

## Files Modified

- `ui/pages/welcome.py` - Fixed LAMAP name, loading order, HTML rendering, removed emojis
- `ui/pages/collect_simple.py` - Statistics display, cheat sheet, button text, buttons at top, click to select, removed IDs/emojis
- `ui/pages/summary.py` - Export moved to bottom, fixed ranking error, removed emojis
- `ui/theme.py` - Improved subtitle visibility, button background colors, removed emojis
- `app_simple.py` - Removed emojis, improved header subtitle

## Testing

Run with:
```bash
cd /Users/simonjaxy/Documents/vub/archaeology/preference_learning/preference_webapp
/Users/simonjaxy/Documents/vub/archaeology/preference_learning/.conda/bin/python -m streamlit run app_simple.py
```
