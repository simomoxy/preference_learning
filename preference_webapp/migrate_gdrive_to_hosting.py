#!/usr/bin/env python3
"""
Helper script to migrate Google Drive data to better hosting options.

This helps you:
1. Generate file_list.json from local files
2. Prepare for GitHub hosting
3. Test data loading
"""

import os
import sys
import json
from pathlib import Path
import argparse


def generate_file_list(data_dir: Path, output_file: str = "file_list.json"):
    """
    Generate file_list.json from a directory of PNG files.

    Args:
        data_dir: Directory containing PNG files
        output_file: Output file path
    """
    if not data_dir.exists():
        print(f"❌ Error: Directory not found: {data_dir}")
        return False

    # Find all PNG files
    png_files = sorted([f for f in os.listdir(data_dir) if f.lower().endswith('.png')])

    if len(png_files) == 0:
        print(f"❌ Error: No PNG files found in {data_dir}")
        return False

    # Create file list
    file_list = {
        "files": png_files,
        "count": len(png_files),
        "period": data_dir.name
    }

    # Write to JSON
    output_path = data_dir / output_file
    with open(output_path, 'w') as f:
        json.dump(file_list, f, indent=2)

    print(f"✅ Created {output_file}")
    print(f"   Found {len(png_files)} PNG files")
    print(f"   Output: {output_path}")

    return True


def prepare_github_structure(source_dir: Path, output_dir: Path):
    """
    Prepare data for GitHub hosting.

    Creates a proper directory structure for GitHub Pages.

    Args:
        source_dir: Source directory (e.g., lamap_results_sample)
        output_dir: Output directory for GitHub repo
    """
    print(f"📦 Preparing GitHub structure...")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Copy period folders
    periods = ["bronze_age", "byzantine", "roman"]

    for period in periods:
        source_period = source_dir / period
        target_period = output_dir / period

        if source_period.exists():
            print(f"   Copying {period}...")
            target_period.mkdir(exist_ok=True)

            # Copy PNG files
            png_files = list(source_period.glob("*.png"))
            for png_file in png_files[:50]:  # Limit to 50
                import shutil
                shutil.copy2(png_file, target_period / png_file.name)

            # Generate file_list.json
            generate_file_list(target_period)

            print(f"   ✅ {period}: {len(png_files)} files")
        else:
            print(f"   ⚠️  {period}: not found")

    # Create README
    readme_content = """# LAMAP Results Data

This repository contains LAMAP prediction maps for the preference learning webapp.

## Structure

```
├── bronze_age/    # Bronze Age site predictions (50 PNG files)
├── byzantine/     # Byzantine period predictions (50 PNG files)
└── roman/         # Roman period predictions (50 PNG files)
```

## Usage

Set the environment variable:
```bash
export DATA_SERVER_URL="https://raw.githubusercontent.com/YOUR_USERNAME/REPO_NAME/main"
```

Then the webapp will load from:
- `https://raw.githubusercontent.com/YOUR_USERNAME/REPO_NAME/main/bronze_age/`
- `https://raw.githubusercontent.com/YOUR_USERNAME/REPO_NAME/main/byzantine/`
- `https://raw.githubusercontent.com/YOUR_USERNAME/REPO_NAME/main/roman/`

## Data Format

Each folder contains:
- `site_XXXX_mask.png` - LAMAP probability maps
- `file_list.json` - List of files for easy loading
"""
    with open(output_dir / "README.md", 'w') as f:
        f.write(readme_content)

    print(f"\n✅ GitHub structure created at: {output_dir}")
    print(f"\nNext steps:")
    print(f"   1. Create a new GitHub repository")
    print(f"   2. Copy files from {output_dir}")
    print(f"   3. Push to GitHub")
    print(f"   4. Set DATA_SERVER_URL to your raw.githubusercontent.com URL")


def generate_raw_urls(username: str, repo: str, branch: str = "main"):
    """
    Generate GitHub raw URLs for testing.

    Args:
        username: GitHub username
        repo: Repository name
        branch: Branch name (default: main)
    """
    base_url = f"https://raw.githubusercontent.com/{username}/{repo}/{branch}"

    print(f"📋 GitHub Raw URLs:")
    print(f"\nBase URL: {base_url}")
    print(f"\nPeriod URLs:")
    for period in ["bronze_age", "byzantine", "roman"]:
        print(f"   {period}: {base_url}/{period}/")

    print(f"\n✅ Set environment variable:")
    print(f"   export DATA_SERVER_URL=\"{base_url}\"")


def test_local_loading(data_dir: Path):
    """
    Test loading data from local directory.

    Args:
        data_dir: Path to data directory
    """
    print(f"🧪 Testing local data loading...")

    periods = ["bronze_age", "byzantine", "roman"]

    for period in periods:
        period_dir = data_dir / period
        if period_dir.exists():
            png_files = list(period_dir.glob("*.png"))
            print(f"   ✅ {period}: {len(png_files)} PNG files")

            # Test loading first image
            if png_files:
                from PIL import Image
                try:
                    img = Image.open(png_files[0])
                    print(f"      Sample: {png_files[0].name} ({img.size})")
                except Exception as e:
                    print(f"      ⚠️  Error loading {png_files[0].name}: {e}")
        else:
            print(f"   ❌ {period}: directory not found")


def main():
    parser = argparse.ArgumentParser(description="Migrate Google Drive data to web hosting")
    parser.add_argument("--action", choices=["filelist", "github", "urls", "test"],
                       required=True, help="Action to perform")
    parser.add_argument("--source", type=str, default="lamap_results_sample",
                       help="Source data directory")
    parser.add_argument("--output", type=str, default="github_data",
                       help="Output directory for GitHub structure")
    parser.add_argument("--period", type=str, help="Specific period to process")

    # GitHub-specific args
    parser.add_argument("--username", type=str, help="GitHub username")
    parser.add_argument("--repo", type=str, help="GitHub repository name")
    parser.add_argument("--branch", type=str, default="main", help="GitHub branch")

    args = parser.parse_args()

    if args.action == "filelist":
        if args.period:
            data_dir = Path(args.source) / args.period
        else:
            data_dir = Path(args.source)

        generate_file_list(data_dir)

    elif args.action == "github":
        prepare_github_structure(Path(args.source), Path(args.output))

    elif args.action == "urls":
        if not args.username or not args.repo:
            print("❌ Error: --username and --repo required for URL generation")
            sys.exit(1)
        generate_raw_urls(args.username, args.repo, args.branch)

    elif args.action == "test":
        test_local_loading(Path(args.source))


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Interactive mode
        print("🔧 Data Migration Helper")
        print("=" * 50)

        data_dir = Path("lamap_results_sample")
        if not data_dir.exists():
            data_dir = Path("preference_webapp/lamap_results_sample")

        print(f"\n📁 Found data directory: {data_dir}")

        print("\nChoose an action:")
        print("1. Generate file_list.json for all periods")
        print("2. Prepare GitHub structure")
        print("3. Test local data loading")
        print("4. Generate GitHub URLs")

        choice = input("\nEnter choice (1-4): ").strip()

        if choice == "1":
            for period in ["bronze_age", "byzantine", "roman"]:
                period_dir = data_dir / period
                if period_dir.exists():
                    generate_file_list(period_dir)
                    print()

        elif choice == "2":
            output_dir = input("Output directory (default: github_data): ").strip()
            if not output_dir:
                output_dir = "github_data"
            prepare_github_structure(data_dir, Path(output_dir))

        elif choice == "3":
            test_local_loading(data_dir)

        elif choice == "4":
            username = input("GitHub username: ").strip()
            repo = input("Repository name: ").strip()
            generate_raw_urls(username, repo)

    else:
        main()
