# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

A command-line tool that finds duplicate files using MD5 checksums. The entire application is contained in a single Python script (`dupfinder.py`) with no external dependencies - uses only Python standard library.

## Development Commands

### Running the Tool
```bash
# Basic usage - scan directory recursively
python dupfinder.py /path/to/directory

# Or as executable
./dupfinder.py /path/to/directory

# Non-recursive scan
python dupfinder.py /path/to/directory --no-recursive

# With progress output
python dupfinder.py /path/to/directory -v

# Without file size information
python dupfinder.py /path/to/directory --no-size
```

### Testing
Currently there are no tests. When adding tests:
- Use Python's built-in `unittest` module to maintain zero external dependencies
- Create test files as `test_*.py` in the root directory
- Run tests with: `python -m unittest discover -s . -p "test_*.py"`

### Code Quality
No linters or formatters are currently configured. If adding code quality tools:
- Consider `black` for formatting
- Consider `pylint` or `flake8` for linting
- Consider `mypy` for type checking (note: code already has type hints)

## Architecture

### Single-File Design
The entire application is in `dupfinder.py` (~200 lines) with a simple, linear architecture:

1. **Argument Parsing** (`main()`): Uses `argparse` to handle CLI arguments
2. **File Discovery** (`find_duplicates()`): Recursively scans directories using `pathlib`
3. **MD5 Calculation** (`calculate_md5()`): Processes files in 8KB chunks to handle large files efficiently
4. **Duplicate Detection**: Uses `defaultdict` to group files by MD5 checksum
5. **Output Formatting** (`print_duplicates()`, `format_size()`): Human-readable display with size calculations

### Key Design Patterns
- **Chunked file reading**: Files are read in 8KB chunks to minimize memory usage
- **Type hints**: All functions use type hints (Dict, List, Path) for clarity
- **Error handling**: Graceful handling of IO errors, keyboard interrupts, and invalid directories
- **Progress tracking**: Optional verbose mode with progress updates every 100 files

### Data Flow
```
Directory Path → File Discovery → MD5 Calculation → Grouping by Checksum → Filter Duplicates → Format Output
```

### Important Implementation Details
- Uses `pathlib.Path` throughout (not `os.path`)
- MD5 checksums are sufficient for duplicate detection (not cryptographic use)
- Symlinks are treated as regular files
- Only files with 2+ instances are reported as duplicates
- Wasted space calculation: `file_size * (count - 1)` for each duplicate set

## Python Requirements
- **Python 3.8+** required (uses walrus operator `:=` in line 29)
- No external dependencies - pure standard library

## File Structure
- `dupfinder.py` - Main application (executable script)
- `README.md` - User documentation with examples
- `requirements.txt` - Empty (no dependencies)
- `.gitignore` - Standard Python ignore patterns

## Extending the Tool

### Adding New Features
When modifying `dupfinder.py`:
- Keep the single-file design unless complexity warrants splitting
- Maintain zero external dependencies if possible
- Add new CLI options to the `argparse` parser in `main()`
- Update the README.md with new usage examples
- Preserve the chunked reading pattern for memory efficiency

### Potential Enhancement Areas
- Alternative hash algorithms (SHA-256, SHA-1)
- Output formats (JSON, CSV)
- Duplicate file deletion/management features
- Size-based pre-filtering to skip small files
- Parallel file hashing using `concurrent.futures`
