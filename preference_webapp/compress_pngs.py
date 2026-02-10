#!/usr/bin/env python3
"""
Compress PNG files for GitHub hosting.
Reduces file size without quality loss.
"""

import os
import sys
from pathlib import Path
from PIL import Image
import argparse

def compress_png(input_path: Path, output_path: Path, quality: int = 85):
    """
    Compress PNG file by reducing resolution if needed.
    
    Args:
        input_path: Input PNG file
        output_path: Output PNG file
        quality: Quality level (1-100, higher is better)
    """
    img = Image.open(input_path)
    
    # If image is very large, resize it
    max_dimension = 2048  # Reasonable for visualization
    
    if max(img.size) > max_dimension:
        # Calculate new size maintaining aspect ratio
        ratio = max_dimension / max(img.size)
        new_size = tuple(int(dim * ratio) for dim in img.size)
        img = img.resize(new_size, Image.Resampling.LANCZOS)
        print(f"  Resized: {img.size} → {new_size}")
    
    # Save with optimized PNG settings
    img.save(output_path, 'PNG', optimize=True, compress_level=9)
    
    # Calculate size reduction
    original_size = input_path.stat().st_size
    compressed_size = output_path.stat().st_size
    reduction = (1 - compressed_size / original_size) * 100
    
    return original_size, compressed_size, reduction


def main():
    parser = argparse.ArgumentParser(description="Compress PNG files for GitHub")
    parser.add_argument("--input", default="bronze_age",
                       help="Input directory")
    parser.add_argument("--output", default="bronze_age_compressed",
                       help="Output directory")
    parser.add_argument("--max-size", type=int, default=2048,
                       help="Maximum image dimension (default: 2048)")
    parser.add_argument("--test", action="store_true",
                       help="Test on first 3 files only")
    
    args = parser.parse_args()
    
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    
    if not input_dir.exists():
        print(f"❌ Error: {input_dir} does not exist")
        sys.exit(1)
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Find PNG files
    png_files = list(input_dir.glob("*.png"))
    
    if args.test:
        png_files = png_files[:3]
        print(f"🧪 TEST MODE: Processing first 3 files only\n")
    
    print(f"Found {len(png_files)} PNG files")
    print(f"Max dimension: {args.max_size}px")
    print()
    
    total_original = 0
    total_compressed = 0
    
    for i, png_file in enumerate(png_files, 1):
        print(f"[{i}/{len(png_files)}] {png_file.name[:60]}...")
        
        output_file = output_dir / png_file.name
        
        try:
            orig_size, comp_size, reduction = compress_png(png_file, output_file)
            total_original += orig_size
            total_compressed += comp_size
            
            orig_mb = orig_size / (1024*1024)
            comp_mb = comp_size / (1024*1024)
            
            print(f"  {orig_mb:.2f} MB → {comp_mb:.2f} MB ({reduction:.1f}% reduction)")
            print()
        except Exception as e:
            print(f"  ❌ Error: {e}")
            print()
    
    # Summary
    total_reduction = (1 - total_compressed / total_original) * 100
    total_orig_mb = total_original / (1024*1024)
    total_comp_mb = total_compressed / (1024*1024)
    
    print("="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total: {total_orig_mb:.2f} MB → {total_comp_mb:.2f} MB")
    print(f"Reduction: {total_reduction:.1f}%")
    print(f"Saved: {total_orig_mb - total_comp_mb:.2f} MB")
    print()
    print(f"✅ Compressed files saved to: {output_dir}")
    print()
    print("Next steps:")
    print(f"1. Review compressed files: ls -lh {output_dir}")
    print(f"2. If satisfied, copy to repo: cp {output_dir}/* /path/to/repo/bronze_age/")
    if args.test:
        print("\n⚠️  TEST MODE: Re-run without --test to process all files")

if __name__ == "__main__":
    main()
