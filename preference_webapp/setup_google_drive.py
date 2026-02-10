"""
Setup script for loading data from Google Drive.

This script helps configure Google Drive as a data source for the webapp.
"""

import os
import streamlit as st
from pathlib import Path


def convert_gdrive_to_direct_url(share_url: str) -> str:
    """
    Convert a Google Drive share URL to a direct download URL.

    Args:
        share_url: Google Drive share URL (e.g., https://drive.google.com/file/d/FILE_ID/view)

    Returns:
        Direct download URL
    """
    # Extract file ID from various Google Drive URL formats
    if "/file/d/" in share_url:
        file_id = share_url.split("/file/d/")[1].split("/")[0]
    elif "id=" in share_url:
        file_id = share_url.split("id=")[1].split("&")[0]
    else:
        raise ValueError(f"Could not extract file ID from URL: {share_url}")

    return f"https://drive.google.com/uc?export=download&id={file_id}"


def setup_gdrive_data_source():
    """
    Interactive setup for Google Drive data source.
    """
    st.title("🔧 Google Drive Data Source Setup")

    st.markdown("""
    This tool helps you configure Google Drive as the data source for the webapp.

    ### Steps:
    1. Make your Google Drive folder public
    2. Get the share links for your PNG files
    3. Choose an option below
    """)

    st.markdown("---")

    option = st.radio(
        "Choose setup method:",
        [
            "Option 1: Direct file URLs (manual setup)",
            "Option 2: File list JSON (recommended for many files)",
            "Option 3: Google Drive API (advanced)"
        ]
    )

    if option == "Option 1: Direct file URLs (manual setup)":
        setup_direct_urls()

    elif option == "Option 2: File list JSON (recommended for many files)":
        setup_file_list()

    elif option == "Option 3: Google Drive API (advanced)":
        setup_gdrive_api()


def setup_direct_urls():
    """
    Setup using direct Google Drive URLs.
    """
    st.subheader("Direct File URLs Setup")

    st.markdown("""
    ### Instructions:

    1. **Make your Google Drive folder public:**
       - Right-click folder → Share → General access → "Anyone with the link"
       - Copy the folder URL

    2. **For each PNG file:**
       - Right-click file → Share → "Anyone with the link"
       - Copy the share link
       - Paste below to convert it

    ### Your Folder URL:
    """)

    folder_url = st.text_input(
        "Google Drive folder URL",
        placeholder="https://drive.google.com/drive/folders/...",
        help="The URL you shared from Google Drive"
    )

    if folder_url:
        st.info(f"Folder URL: {folder_url}")

        # Extract folder ID
        try:
            if "/folders/" in folder_url:
                folder_id = folder_url.split("/folders/")[1].split("?")[0]
                st.success(f"✓ Folder ID extracted: {folder_id}")

                # Show base URL pattern
                base_url = f"https://drive.google.com/drive/folders/{folder_id}"
                st.code(f"""
# Files in this folder can be accessed via:
Folder: {base_url}

Note: Individual files still need to be made shareable
and converted to direct download links.
                """)

                st.markdown("### Next Steps:")
                st.markdown("""
                1. Make individual PNG files shareable (Right-click → Share → "Anyone with the link")
                2. Create a `file_list.json` with the converted URLs
                3. See Option 2 below for the JSON format
                """)

        except Exception as e:
            st.error(f"Error parsing URL: {e}")

    st.markdown("---")

    st.subheader("Convert Individual File Links")

    share_link = st.text_input(
        "Google Drive file share link",
        placeholder="https://drive.google.com/file/d/...",
        help="Share link for a single PNG file"
    )

    if share_link:
        try:
            direct_url = convert_gdrive_to_direct_url(share_link)
            st.success("✓ Converted!")
            st.code(f"Direct URL: {direct_url}")

            # Test the URL
            if st.button("Test URL", key="test_direct"):
                import requests
                try:
                    response = requests.head(direct_url, timeout=10)
                    if response.status_code == 200:
                        st.success("✓ URL is accessible!")
                    else:
                        st.warning(f"Status code: {response.status_code}")
                except Exception as e:
                    st.error(f"Error testing URL: {e}")

        except Exception as e:
            st.error(f"Error converting link: {e}")


def setup_file_list():
    """
    Setup using a file list JSON.
    """
    st.subheader("File List JSON Setup")

    st.markdown("""
    ### Instructions:

    1. **Create a `file_list.json` file** with your Google Drive file IDs

    2. **Format:**
    ```json
    {
      "files": [
        "FILE_ID_1",
        "FILE_ID_2",
        "FILE_ID_3"
      ]
    }
    ```

    3. **Place `file_list.json` in each period folder on Google Drive**

    ### How to get File IDs:
    - Open file in Google Drive
    - Copy URL: `https://drive.google.com/file/d/FILE_ID/view`
    - The FILE_ID is the part between `/d/` and `/view`
    """)

    st.markdown("### Generate file_list.json")

    # Input for Google Drive folder URL
    folder_url = st.text_input(
        "Your Google Drive folder URL",
        placeholder="https://drive.google.com/drive/folders/...",
        key="filelist_folder_url"
    )

    if folder_url:
        st.info("📝 Manual process:")
        st.markdown("""
        Since Google Drive doesn't provide a direct API to list files without authentication,
        you'll need to:

        1. Open each file in your Google Drive folder
        2. Copy the file ID from the URL
        3. Paste it below

        Alternatively, use Google Drive downloader tools or the Python script below.
        """)

    st.markdown("---")

    st.subheader("Create file_list.json Manually")

    file_ids = st.text_area(
        "Paste file IDs (one per line)",
        placeholder="1C7giVo5hPqBbYH9iLarAHkfbLna8ezra\n...",
        help="Copy from Google Drive URLs"
    )

    if file_ids:
        ids = [line.strip() for line in file_ids.strip().split("\n") if line.strip()]

        import json
        file_list = {"files": ids}

        st.success(f"✓ Parsed {len(ids)} file IDs")

        st.json(file_list)

        # Download button
        st.download_button(
            "Download file_list.json",
            data=json.dumps(file_list, indent=2),
            file_name="file_list.json",
            mime="application/json"
        )

        # Show direct URLs
        st.markdown("### Direct Download URLs")
        for file_id in ids[:5]:  # Show first 5
            direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            st.code(direct_url)

        if len(ids) > 5:
            st.info(f"... and {len(ids) - 5} more files")


def setup_gdrive_api():
    """
    Setup using Google Drive API (advanced).
    """
    st.subheader("Google Drive API Setup")

    st.markdown("""
    ### This requires:
    - Google Cloud Project
    - Google Drive API enabled
    - OAuth credentials
    - Service account or OAuth client

    ### Recommended Alternatives:
    - Use **Option 2** (file list) - simpler
    - Use **GitHub** or **static hosting** - more reliable

    ### If you still want to use Google Drive API:

    1. Create a Google Cloud Project
    2. Enable Google Drive API
    3. Create OAuth credentials
    4. Download credentials.json
    5. Install: `pip install pydrive google-api-python-client`

    The webapp can then authenticate and list files automatically.
    """)

    st.warning("⚠️ API setup is complex and requires ongoing maintenance.")
    st.info("💡 Recommendation: Use Option 2 or host data on GitHub/static server instead.")


def create_gdrive_loader_script():
    """
    Create a helper script to list files from a public Google Drive folder.
    """
    st.subheader("Helper Script: List Google Drive Files")

    st.markdown("""
    ### Python script to generate file_list.json from Google Drive folder

    This script uses the Google Drive folder structure to generate the file list.
    """)

    script = '''
"""
Script to generate file_list.json from Google Drive folder.

Requires: pip install requests beautifulsoup4
"""

import requests
from bs4 import BeautifulSoup
import json

def list_gdrive_folder(folder_url: str) -> list:
    """
    List files in a public Google Drive folder.

    Args:
        folder_url: Public Google Drive folder URL

    Returns:
        List of file IDs
    """
    # This is a simplified approach - Google Drive HTML structure may change
    # For production, use the official Google Drive API

    # For now, you'll need to manually extract file IDs
    # or use Google Drive API

    raise NotImplementedError(
        "Google Drive folder listing requires authentication. "
        "Use Google Drive API or manual file ID extraction."
    )

# Alternative: Use gdown
# pip install gdown

# import gdown
#
# def download_folder(folder_url, output_path):
#     gdown.download_folder(folder_url, output=output_path, quiet=False)

# Or use Google Drive API
# pip install pydrive
'''

    st.code(script, language="python")

    st.info("💡 For production deployment, consider using:")
    st.markdown("""
    - **GitHub** - Push PNG files to a repo, use raw.githubusercontent.com URLs
    - **GitHub Pages** - Host PNG files as static content
    - **Cloudflare R2** - Free S3-compatible storage
    - **Netlify Drop** - Drag and drop for instant hosting
    """)


if __name__ == "__main__":
    import streamlit as st
    st.set_page_config(page_title="Google Drive Setup", layout="wide")
    setup_gdrive_data_source()
