#!/usr/bin/env python3
"""
Quick test to check if GitHub data is accessible.
"""

import requests
import json
import sys

def test_github_data():
    """Test loading data from GitHub."""
    
    base_url = "https://raw.githubusercontent.com/simomoxy/preference_learning/main"
    period = "bronze_age"
    
    print("=" * 60)
    print("Testing GitHub Data Access")
    print("=" * 60)
    print(f"\nRepository: https://github.com/simomoxy/preference_learning")
    print(f"Base URL: {base_url}")
    print(f"Period: {period}\n")
    
    # Test 1: file_list.json
    print("Test 1: file_list.json")
    print("-" * 40)
    file_list_url = f"{base_url}/{period}/file_list.json"
    
    try:
        response = requests.get(file_list_url, timeout=10)
        print(f"URL: {file_list_url}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS!")
            print(f"   Files: {data.get('count', 'N/A')}")
            print(f"   Period: {data.get('period', 'N/A')}")
            return True
        else:
            print(f"❌ FAILED")
            print(f"   Response: {response.text[:100]}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 2: Direct image
    print("\nTest 2: Direct image access")
    print("-" * 40)
    image_url = f"{base_url}/{period}/site_0000_mask.png"
    
    try:
        response = requests.get(image_url, timeout=10)
        print(f"URL: {image_url}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ SUCCESS!")
            print(f"   Size: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ FAILED")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("TROUBLESHOOTING")
    print("=" * 60)
    print("""
If tests failed, possible reasons:

1. Repository is PRIVATE
   - Solution: Make repository public
   - Go to: https://github.com/simomoxy/preference_learning/settings
   - Scroll to "Danger Zone" → "Change repository visibility"
   - Select "Public"

2. GitHub CDN hasn't updated yet
   - Solution: Wait 2-3 minutes and try again
   - Recent pushes can take a few minutes to propagate

3. Files aren't actually on GitHub
   - Check: https://github.com/simomoxy/preference_learning/tree/main/bronze_age
   - If files are visible there, they should be accessible via raw URLs

4. Wrong branch name
   - Current code uses: main
   - Check your branch: git branch
""")
    
    return False

if __name__ == "__main__":
    success = test_github_data()
    sys.exit(0 if success else 1)
