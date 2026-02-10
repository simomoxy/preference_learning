#!/usr/bin/env python3
"""
Generate file_list.json from files in a directory and push to GitHub.

Usage:
    cd /path/to/preference_learning
    python ../preference_webapp/update_github_filelist.py --period bronze_age
"""

import os
import sys
import json
import argparse
from pathlib import Path
import subprocess


def generate_file_list(directory: Path, period: str) -> dict:
    """
    Generate file_list.json from PNG files in directory.
    
    Args:
        directory: Path to directory containing PNG files
        period: Period name (bronze_age, byzantine, roman)
    
    Returns:
        Dictionary with files list
    """
    if not directory.exists():
        print(f"❌ Error: Directory not found: {directory}")
        sys.exit(1)
    
    # Find all PNG files
    png_files = sorted([f for f in os.listdir(directory) if f.lower().endswith('.png')])
    
    if len(png_files) == 0:
        print(f"❌ Error: No PNG files found in {directory}")
        sys.exit(1)
    
    # Create file list
    file_list = {
        "files": png_files,
        "count": len(png_files),
        "period": period
    }
    
    return file_list


def write_file_list(file_list: dict, output_path: Path):
    """
    Write file_list.json to file.
    
    Args:
        file_list: File list dictionary
        output_path: Output file path
    """
    with open(output_path, 'w') as f:
        json.dump(file_list, f, indent=2)
    
    print(f"✅ Created: {output_path}")
    print(f"   Files: {file_list['count']}")
    print(f"   Period: {file_list['period']}")


def git_commit_and_push(file_path: Path, period: str):
    """
    Commit and push file_list.json to GitHub.
    
    Args:
        file_path: Path to file_list.json
        period: Period name
    """
    # Check if we're in a git repo
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError:
        print("❌ Error: Not in a git repository")
        return False
    
    # Add file
    print(f"\n📝 Committing to git...")
    subprocess.run(['git', 'add', str(file_path)], check=True)
    
    # Commit
    commit_msg = f"Update file_list.json for {period} ({file_list['count']} files)"
    subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
    
    # Push
    print(f"📤 Pushing to GitHub...")
    subprocess.run(['git', 'push', 'origin', 'main'], check=True)
    
    print("✅ Pushed to GitHub!")
    print("\n⏳ Wait 2-3 minutes for GitHub CDN to update...")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Generate and push file_list.json to GitHub")
    parser.add_argument("--period", required=True, 
                       choices=["bronze_age", "byzantine", "roman"],
                       help="Period to generate file_list for")
    parser.add_argument("--dir", default=".",
                       help="Path to repository root (default: current directory)")
    parser.add_argument("--no-push", action="store_true",
                       help="Generate file_list.json but don't push to GitHub")
    
    args = parser.parse_args()
    
    # Paths
    repo_root = Path(args.dir)
    period_dir = repo_root / args.period
    file_list_path = period_dir / "file_list.json"
    
    print(f"Generating file_list.json for {args.period}...")
    print(f"Directory: {period_dir}")
    
    # Generate file list
    file_list = generate_file_list(period_dir, args.period)
    
    # Write file
    write_file_list(file_list, file_list_path)
    
    # Show sample files
    print(f"\nSample files ({min(5, len(file_list['files']))} of {file_list['count']}):")
    for filename in file_list['files'][:5]:
        print(f"  - {filename}")
    if len(file_list['files']) > 5:
        print(f"  ... and {len(file_list['files']) - 5} more")
    
    # Commit and push
    if not args.no_push:
        git_commit_and_push(file_list_path, args.period)
        
        print("\n" + "="*60)
        print("Next steps:")
        print("="*60)
        print("1. Wait 2-3 minutes for GitHub CDN to update")
        print("2. Test the webapp:")
        print(f"   export DATA_SERVER_URL=\"https://raw.githubusercontent.com/simomoxy/preference_learning/main\"")
        print("   cd preference_webapp")
        print("   .conda/bin/python -m streamlit run app_simple.py")
    else:
        print("\n✅ file_list.json created (not pushed)")
        print(f"   To push manually:")
        print(f"   git add {file_list_path}")
        print(f"   git commit -m 'Add file_list.json for {args.period}'")
        print(f"   git push origin main")


if __name__ == "__main__":
    main()
