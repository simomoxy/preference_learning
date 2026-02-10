"""
One-time Google Drive API setup.

Run this script once to authenticate and extract all file IDs automatically.
After that, the webapp can load from Google Drive without any manual work!
"""

import json
import os
from pathlib import Path

# Check if google-api-python-client is installed
try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    print("Installing required packages...")
    os.system("pip install google-api-python-client google-auth-oauthlib")
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow


FOLDER_ID = "1m_du5qd6HBfjZ5FrAV7fOyaHgqtg5_cc"
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


def authenticate():
    """
    Authenticate with Google Drive API one time.
    Opens browser for user to authorize.
    """
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json',
        scopes=SCOPES
    )

    # Run OAuth flow
    creds = flow.run_local_server(port=0)

    # Save credentials for future use
    with open('google_drive_credentials.json', 'w') as f:
        creds_data = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes
        }
        json.dump(creds_data, f, indent=2)

    return creds


def load_credentials():
    """Load saved credentials if they exist."""
    cred_path = Path('google_drive_credentials.json')
    if cred_path.exists():
        with open(cred_path) as f:
            creds_data = json.load(f)
        return Credentials(**creds_data)
    return None


def list_files_in_folder(service, folder_id):
    """List all files in a Google Drive folder."""
    results = []
    page_token = None

    while True:
        results += service.files().list(
            q=f"'{folder_id}' in parents",
            fields="nextPageToken, files(id, name)",
            pageSize=100,
            pageToken=page_token
        ).execute()

        files = results.get('files', [])
        page_token = results.get('nextPageToken')

        if not page_token:
            break

    return files


def main():
    print("="*60)
    print("Google Drive One-Time Setup")
    print("="*60)
    print()
    print("This will:")
    print("1. Open a browser window")
    print("2. Ask you to authorize access to Google Drive")
    print("3. Extract all file IDs from your folder")
    print("4. Save them to google_drive_files.json")
    print()
    print("You only need to do this ONCE. After that, it works automatically!")
    print("="*60)
    print()

    # Try to load existing credentials
    creds = load_credentials()

    if not creds:
        print("No credentials found. Starting authentication...")
        print()
        creds = authenticate()

    # Build Drive service
    service = build('drive', 'v3', credentials=creds)

    # List files
    print(f"Listing files in folder {FOLDER_ID}...")
    files = list_files_in_folder(service, FOLDER_ID)

    # Filter PNG files
    png_files = {f['name']: f['id'] for f in files if f['name'].endswith('.png')}

    print(f"✅ Found {len(png_files)} PNG files")

    # Save config
    config = {
        "bronze_age": {
            "folder_id": FOLDER_ID,
            "files": png_files
        }
    }

    with open('preference_webapp/google_drive_files.json', 'w') as f:
        json.dump(config, f, indent=2)

    print(f"✅ Saved to google_drive_files.json")
    print()
    print("="*60)
    print("DONE! Your webapp can now load from Google Drive automatically!")
    print("="*60)


if __name__ == "__main__":
    main()
