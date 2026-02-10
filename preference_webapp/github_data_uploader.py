"""
Upload preference data to GitHub for collection by researcher.

This module handles uploading expert preferences to a GitHub repository
so the researcher can collect all responses without needing the archaeologist's machine.
"""

import requests
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def upload_preferences_to_github(preferences, metadata, repo, token=None):
    """
    Upload preference data to GitHub repository.

    Args:
        preferences: List of preference dictionaries
        metadata: Dictionary with expert info (expert_name, period, etc.)
        repo: GitHub repository (username/repo)
        token: GitHub personal access token (optional, uses env var if not provided)

    Returns:
        Tuple of (success: bool, url: str or None, error: str or None)
    """
    import os

    if token is None:
        token = os.getenv("GITHUB_TOKEN")

    if not token:
        return False, None, "GITHUB_TOKEN environment variable not set"

    try:
        # Create file content
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        expert_name = metadata.get('expert_name', 'anonymous').replace(' ', '_').lower()
        period = metadata.get('period', 'unknown')
        filename = f"preferences_{period}_{expert_name}_{timestamp}.json"

        # Prepare data
        data = {
            'metadata': {
                'expert_name': metadata.get('expert_name', 'Anonymous'),
                'period': metadata.get('period', 'unknown'),
                'upload_timestamp': datetime.now().isoformat(),
                'total_comparisons': len([p for p in preferences if p.get('preference') != -1]),
                'total_masks': metadata.get('total_masks', 0)
            },
            'preferences': []
        }

        # Add preferences
        for pref in preferences:
            if pref.get('preference') != -1:  # Skip skipped comparisons
                data['preferences'].append({
                    'comparison_number': pref.get('comparison_number'),
                    'mask_a': pref.get('idx_a'),
                    'mask_b': pref.get('idx_b'),
                    'preference': pref.get('preference'),
                    'preference_label': {0: 'Left', 1: 'Right', 2: 'Tie'}[pref.get('preference')]
                })

        # Convert to JSON and base64 encode
        import base64
        content_json = json.dumps(data, indent=2)
        content_b64 = base64.b64encode(content_json.encode('utf-8')).decode('utf-8')

        # GitHub API URL
        api_url = f"https://api.github.com/repos/{repo}/contents/responses/{filename}"

        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

        # Check if file exists
        check_response = requests.get(api_url, headers=headers)

        request_data = {
            "message": f"Add preferences from {expert_name} for {period}",
            "content": content_b64
        }

        if check_response.status_code == 200:
            # File exists - update it
            sha = check_response.json().get('sha')
            request_data['sha'] = sha
            logger.info(f"Updating existing file: {filename}")
        else:
            logger.info(f"Creating new file: {filename}")

        # Upload
        response = requests.put(api_url, json=request_data, headers=headers)

        if response.status_code in [200, 201]:
            result = response.json()
            content = result.get('content', {})
            raw_url = content.get('raw_url', '')
            html_url = content.get('html_url', '')

            if html_url:
                logger.info(f"Successfully uploaded to GitHub: {html_url}")
                return True, html_url, None
            else:
                logger.info(f"Successfully uploaded (no HTML URL)")
                return True, None, None
        else:
            error_msg = f"GitHub API error: {response.status_code} - {response.text}"
            logger.error(error_msg)
            return False, None, error_msg

    except Exception as e:
        error_msg = f"Upload failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False, None, error_msg


def check_github_config():
    """
    Check if GitHub is configured for data upload.

    Returns:
        Dictionary with config status
    """
    import os

    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_DATA_REPO", "simomoxy/lamap-bronze-age-data")

    return {
        'token_set': token is not None,
        'repo': repo,
        'ready': token is not None
    }


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    # Test configuration
    config = check_github_config()
    print("GitHub Configuration:")
    print(f"  Token set: {config['token_set']}")
    print(f"  Repository: {config['repo']}")
    print(f"  Ready: {config['ready']}")

    if not config['ready']:
        print()
        print("To enable GitHub upload:")
        print("1. Create a GitHub personal access token:")
        print("   https://github.com/settings/tokens")
        print("2. Select 'repo' scope")
        print("3. Set environment variable:")
        print("   export GITHUB_TOKEN='your_token_here'")
