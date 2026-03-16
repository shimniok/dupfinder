#!/usr/bin/env python3
"""
Duplicate File Finder - Find duplicate files using MD5 checksums
"""

import os
import sys
import hashlib
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set


def calculate_md5(filepath: Path, chunk_size: int = 8192) -> str:
    """
    Calculate MD5 checksum of a file.
    
    Args:
        filepath: Path to the file
        chunk_size: Size of chunks to read (default 8192 bytes)
    
    Returns:
        MD5 checksum as hexadecimal string
    """
    md5_hash = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(chunk_size):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    except (IOError, OSError) as e:
        print(f"Error reading file {filepath}: {e}", file=sys.stderr)
        return None


def find_duplicates(directory: Path, recursive: bool = True, verbose: bool = False) -> Dict[str, List[Path]]:
    """
    Find duplicate files in a directory.
    
    Args:
        directory: Directory to scan
        recursive: Whether to scan subdirectories
        verbose: Print progress information
    
    Returns:
        Dictionary mapping MD5 checksums to lists of file paths
    """
    checksums: Dict[str, List[Path]] = defaultdict(list)
    file_count = 0
    
    # Collect all files
    if recursive:
        files = [f for f in directory.rglob('*') if f.is_file()]
    else:
        files = [f for f in directory.glob('*') if f.is_file()]
    
    total_files = len(files)
    
    if verbose:
        print(f"Scanning {total_files} files in {directory}...")
    
    # Calculate checksums for all files
    for filepath in files:
        file_count += 1

        # display progress
        if verbose and file_count % 100 == 0:
            print(f"Processed {file_count}/{total_files} files...", end='\r')
        
        md5_sum = calculate_md5(filepath)
        if md5_sum:
            checksums[md5_sum].append(filepath)
    
    if verbose:
        print(f"\nProcessed {file_count} files.")
    
    # Filter to only duplicates (checksums with more than one file)
    duplicates = {k: v for k, v in checksums.items() if len(v) > 1}
    
    return duplicates


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable form."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def print_directory_summary(duplicates: Dict[str, List[Path]], show_size: bool = True):
    """
    Print directories that contain duplicate files.
    
    Args:
        duplicates: Dictionary of MD5 checksums to file paths
        show_size: Whether to display file sizes
    """
    if not duplicates:
        print("No duplicate files found.")
        return
    
    # Build a map of directories to their duplicate file info and related directories
    dir_duplicates: Dict[Path, Dict] = defaultdict(lambda: {'count': 0, 'waste': 0, 'related_dirs': set()})
    
    for md5_sum, files in duplicates.items():
        # Get unique directories for this duplicate set
        dirs = set(f.parent for f in files)
        file_size = files[0].stat().st_size
        
        # Each directory that has duplicates gets credit for its files
        for directory in dirs:
            dir_files_count = sum(1 for f in files if f.parent == directory)
            dir_duplicates[directory]['count'] += dir_files_count
            # Waste is only for extra copies (count - 1 per set in this dir)
            if dir_files_count > 0:
                dir_duplicates[directory]['waste'] += file_size * dir_files_count
            
            # Track which other directories have duplicates of files in this directory
            other_dirs = dirs - {directory}
            dir_duplicates[directory]['related_dirs'].update(other_dirs)
    
    # Sort directories by number of duplicate files
    sorted_dirs = sorted(dir_duplicates.items(), key=lambda x: x[1]['count'], reverse=True)
    
    print(f"\nFound {len(sorted_dirs)} directories containing duplicate files:")
    print("=" * 80)
    
    total_files = sum(info['count'] for _, info in sorted_dirs)
    total_waste = sum(info['waste'] for _, info in sorted_dirs)
    
    for directory, info in sorted_dirs:
        print(f"\n{directory}")
        if show_size:
            print(f"  {info['count']} duplicate files, {format_size(info['waste'])} total")
        else:
            print(f"  {info['count']} duplicate files")
        
        # Show related directories where duplicates are found
        if info['related_dirs']:
            related = sorted(info['related_dirs'])
            print(f"  Duplicates also in:")
            for rel_dir in related:
                print(f"    - {rel_dir}")
    
    print("\n" + "=" * 80)
    print(f"Summary:")
    print(f"  Directories with duplicates: {len(sorted_dirs)}")
    print(f"  Total duplicate file instances: {total_files}")
    if show_size:
        print(f"  Total space used by duplicates: {format_size(total_waste)}")


def print_duplicates(duplicates: Dict[str, List[Path]], show_size: bool = True):
    """
    Print duplicate files in a readable format.
    
    Args:
        duplicates: Dictionary of MD5 checksums to file paths
        show_size: Whether to display file sizes
    """
    if not duplicates:
        print("No duplicate files found.")
        return
    
    total_duplicates = sum(len(files) - 1 for files in duplicates.values())
    total_waste = 0
    
    print(f"\nFound {len(duplicates)} sets of duplicate files:")
    print("=" * 80)
    
    for idx, (md5_sum, files) in enumerate(duplicates.items(), 1):
        file_size = files[0].stat().st_size
        waste = file_size * (len(files) - 1)
        total_waste += waste
        
        print(f"\nSet #{idx} - MD5: {md5_sum}")
        if show_size:
            print(f"  Size: {format_size(file_size)} each, {format_size(waste)} wasted")
        print(f"  {len(files)} copies:")
        
        for filepath in sorted(files):
            print(f"    - {filepath}")
    
    print("\n" + "=" * 80)
    print(f"Summary:")
    print(f"  Total duplicate sets: {len(duplicates)}")
    print(f"  Total duplicate files: {total_duplicates}")
    if show_size:
        print(f"  Total wasted space: {format_size(total_waste)}")


def main():
    """Main entry point for the duplicate file finder."""
    parser = argparse.ArgumentParser(
        description='Find duplicate files using MD5 checksums',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/directory          # Find duplicates recursively
  %(prog)s . --no-recursive            # Search current directory only
  %(prog)s ~/Documents -v              # Verbose output
  %(prog)s /media/photos --no-size     # Don't show file sizes
  %(prog)s ~/Photos --show-dirs        # Show directories with duplicates
        """
    )
    
    parser.add_argument(
        'directory',
        type=str,
        help='Directory to scan for duplicate files'
    )
    
    parser.add_argument(
        '-r', '--no-recursive',
        action='store_true',
        help='Do not scan subdirectories (default: recursive)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Print progress information'
    )
    
    parser.add_argument(
        '--no-size',
        action='store_true',
        help='Do not display file sizes'
    )
    
    parser.add_argument(
        '--show-dirs',
        action='store_true',
        help='Show directories containing duplicates instead of individual files'
    )
    
    args = parser.parse_args()
    
    # Validate directory
    directory = Path(args.directory).resolve()
    if not directory.exists():
        print(f"Error: Directory '{directory}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    if not directory.is_dir():
        print(f"Error: '{directory}' is not a directory.", file=sys.stderr)
        sys.exit(1)
    
    # Find duplicates
    try:
        duplicates = find_duplicates(
            directory,
            recursive=not args.no_recursive,
            verbose=args.verbose
        )
        
        # Print results
        if args.show_dirs:
            print_directory_summary(duplicates, show_size=not args.no_size)
        else:
            print_duplicates(duplicates, show_size=not args.no_size)
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
