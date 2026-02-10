"""
Upload PNG files to GitHub using GitHub API.

This bypasses git push issues by uploading files directly.
"""

import os
import base64
import requests
import json
from pathlib import Path

# GitHub config
GITHUB_API = "https://api.github.com"
REPO = "simomoxy/preference_learning"
BRANCH = "main"

# Get GitHub token from environment
token = os.getenv("GITHUB_TOKEN")

if not token:
    print("❌ GITHUB_TOKEN environment variable not set")
    print()
    print("To upload files to GitHub, you need a personal access token:")
    print("1. Go to: https://github.com/settings/tokens")
    print("2. Click 'Generate new token (classic)'")
    print("3. Select 'repo' scope")
    print("4. Generate token")
    print("5. Set environment variable:")
    print("   export GITHUB_TOKEN='your_token_here'")
    print()
    print("Or run this script with:")
    print("   GITHUB_TOKEN='your_token_here' python upload_to_github.py")
    exit(1)


def upload_file_to_github(file_path: Path, repo: str, branch: str = "main"):
    """
    Upload a single file to GitHub repository.

    Args:
        file_path: Path to file
        repo: Repository name (username/repo)
        branch: Branch name

    Returns:
        True if successful
    """
    filename = file_path.name

    # Read file
    with open(file_path, 'rb') as f:
        content = f.read()

    # Check size (GitHub limit is 100MB)
    size_mb = len(content) / (1024 * 1024)
    if size_mb > 100:
        print(f"❌ {filename}: {size_mb:.1f}MB - exceeds 100MB limit")
        return False

    print(f"Uploading {filename} ({size_mb:.1f}MB)...")

    # Base64 encode
    import base64
    content_b64 = base64.b64encode(content).decode('utf-8')

    # Create/update file via API
    url = f"{GITHUB_API}/repos/{repo}/contents/bronze_age/{filename}"

    data = {
        "message": f"Upload {filename}",
        "content": content_b64,
        "branch": branch
    }

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Check if file exists first
    check_response = requests.get(url, headers=headers)

    if check_response.status_code == 200:
        # File exists - update it
        sha = check_response.json().get('sha')
        data['sha'] = sha
        print(f"  Updating existing file (sha: {sha[:7]}...)")
    else:
        print(f"  Creating new file")

    # Upload
    response = requests.put(url, json=data, headers=headers)

    if response.status_code in [200, 201]:
        print(f"  ✅ Success")
        return True
    else:
        print(f"  ❌ Failed: {response.status_code}")
        print(f"  {response.text[:200]}")
        return False


def main():
    import sys

    # Find PNG files
    bronze_dir = Path("bronze_age")
    if not bronze_dir.exists():
        print(f"❌ Directory not found: {bronze_dir}")
        print("Run this script from the repository root")
        sys.exit(1)

    png_files = sorted(bronze_dir.glob("*.png"))

    if not png_files:
        print(f"❌ No PNG files found in {bronze_dir}")
        sys.exit(1)

    print(f"Found {len(png_files)} PNG files")
    print()

    # Upload each file
    success_count = 0
    for i, file_path in enumerate(png_files, 1):
        print(f"[{i}/{len(png_files)}] ", end="")

        if upload_file_to_github(file_path, REPO, BRANCH):
            success_count += 1
        else:
            print(f"Failed to upload {file_path.name}")

    print()
    print("="*60)
    print(f"Upload complete: {success_count}/{len(png_files)} files")
    print("="*60)

    if success_count == len(png_files):
        print("✅ All files uploaded to GitHub!")
        print()
        print("Now test the webapp:")
        print("  export DATA_SERVER_URL='https://raw.githubusercontent.com/simomoxy/preference_learning/main'")
        print("  cd preference_webapp")
        print("  .conda/bin/python -m streamlit run app_simple.py")
    else:
        print(f"⚠️  Only {success_count}/{len(png_files)} files uploaded")


if __name__ == "__main__":
    main()
