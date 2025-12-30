# Duplicate File Finder

A command-line tool to find duplicate files in a directory using MD5 checksums. Developed with assistance from Warp (see *AI* below).

## Features

- **Fast MD5 checksum calculation** - Efficiently processes files using chunked reading
- **Recursive scanning** - Optionally scan subdirectories
- **Human-readable output** - Clear display of duplicate file groups with size information
- **Space savings calculation** - Shows how much storage is wasted by duplicates
- **Verbose mode** - Track progress while scanning large directories
- **Pure Python** - No external dependencies, uses only the standard library

## Requirements

- Python 3.8 or higher
- No external dependencies required

## Installation

1. Clone or download this repository
2. Make the script executable (optional):
   ```bash
   chmod +x dupfinder.py
   ```

## Usage

### Basic usage

Find duplicates in a directory (recursive by default):
```bash
python dupfinder.py /path/to/directory
```

Or if you made it executable:
```bash
./dupfinder.py /path/to/directory
```

### Options

```
usage: dupfinder.py [-h] [-r] [-v] [--no-size] [--show-dirs] directory

Find duplicate files using MD5 checksums

positional arguments:
  directory          Directory to scan for duplicate files

options:
  -h, --help         show this help message and exit
  -r, --no-recursive Do not scan subdirectories (default: recursive)
  -v, --verbose      Print progress information
  --no-size          Do not display file sizes
  --show-dirs        Show directories containing duplicates instead of individual files
```

### Examples

Find duplicates in the current directory and all subdirectories:
```bash
python dupfinder.py .
```

Search only the specified directory (non-recursive):
```bash
python dupfinder.py ~/Documents --no-recursive
```

Show progress while scanning:
```bash
python dupfinder.py /media/photos -v
```

Find duplicates without showing file sizes:
```bash
python dupfinder.py ~/Music --no-size
```

Show which directories contain duplicate files:
```bash
python dupfinder.py ~/Photos --show-dirs
```

## Output

The tool displays:
- Groups of duplicate files with the same MD5 checksum by file or directory
- File size for each duplicate group
- Wasted storage space per group
- Total summary of duplicate files and wasted space 

Example output:
```
Found 2 sets of duplicate files:
================================================================================

Set #1 - MD5: 5d41402abc4b2a76b9719d911017c592
  Size: 1.50 MB each, 1.50 MB wasted
  2 copies:
    - /home/user/documents/file1.pdf
    - /home/user/backup/file1.pdf

Set #2 - MD5: 7d793037a0760186574b0282f2f435e7
  Size: 523.00 KB each, 1.02 MB wasted
  3 copies:
    - /home/user/photos/image.jpg
    - /home/user/photos/copy.jpg
    - /home/user/downloads/image.jpg

================================================================================
Summary:
  Total duplicate sets: 2
  Total duplicate files: 3
  Total wasted space: 2.52 MB
```

## How It Works

1. **Scan**: The tool recursively scans the specified directory for all files
2. **Hash**: Calculates MD5 checksums for each file using efficient chunked reading
3. **Compare**: Groups files with identical checksums
4. **Report**: Displays duplicate file groups with size and location information
5. **Directories**: optionally displays duplicate files by containing directory and shows directories containing duplicates

## Performance

- Uses chunked file reading (8KB chunks) to handle large files efficiently
- Minimal memory footprint - processes files one at a time
- Progress tracking in verbose mode for long-running scans

## Limitations

- Uses MD5 checksums, which while fast, are not cryptographically secure. For this use case (finding duplicate files), MD5 is sufficient.
- Does not handle symlinks specially - they are treated as regular files
- Requires read permissions for all files in the scanned directory

## AI 

Yeah, I know, AI.  But no, this isn't "vibe coded".  I actually know how to code in Python. I reviewed the code and will make manual tweaks as needed.

## License

This project is provided as-is for educational and practical use.

## Contributing

Feel free to submit issues or pull requests to improve the tool!
