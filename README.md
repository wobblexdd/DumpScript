# Project Packer Script

This script generates a full project dump into a single .txt file. It scans directories, builds a file tree, and includes readable file contents while skipping binaries and large files.

## Features
- Full directory tree generation
- Reads all text files with encoding fallback
- Skips binary files automatically
- Skips large files (>2MB)
- Ignores common build and cache folders
- GUI interface for selecting folders
- Safe filename handling

## How it works
The script walks through the selected project directory, collects all files, and outputs:
- Project metadata
- Directory structure
- Contents of each readable file

Binary and unsupported files are skipped. :contentReference[oaicite:0]{index=0}

## Usage
Run:
python packer.py

Steps:
1. Select source folder
2. Select destination folder
3. Enter output file name

## Output
Generates a single .txt file containing:
- Project tree
- All readable source code
- File paths and metadata

## Notes
- Designed for code sharing and debugging
- Does not modify any files
- Safe to use on any project directory
