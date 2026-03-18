"""
date_folders.py

A cross-platform module for creating nested year/month/day folder structures
based on the current date.
"""

import os
from datetime import datetime
from pathlib import Path


def create_date_folders(root_path, date=None):
    """
    Create nested year/month/day folders from a given root path.

    Args:
        root_path (str or Path): The root directory where folders will be created
        date (datetime, optional): Date to use for folder structure.
                                   Defaults to current date if not provided.

    Returns:
        Path: The full path to the created day folder

    Raises:
        ValueError: If root_path is empty or None
        PermissionError: If lacking permissions to create directories
        OSError: If directory creation fails for other reasons

    """
    if not root_path:
        raise ValueError("root_path cannot be empty or None")

    # Convert to Path object for cross-platform compatibility
    root = Path(root_path)

    # Use provided date or get current date
    if date is None:
        date = datetime.now()

    # Format date components with zero-padding
    year = f"{date.year:04d}"
    month = f"{date.month:02d}"
    day = f"{date.day:02d}"

    # Construct the full path
    full_path = root / year / month / day

    # Create directories (parents=True creates intermediate dirs, exist_ok=True won't error if exists)
    full_path.mkdir(parents=True, exist_ok=True)

    return full_path


def main():
    """
    Main function for command-line usage.
    Prompts user for root path and creates date folders.
    """
    print("Date Folder Creator")
    print("=" * 50)

    # Get root path from user
    root_path = input("Enter the root path for folder creation: ").strip()

    if not root_path:
        print("Error: Path cannot be empty!")
        return

    try:
        # Create the folders
        created_path = create_date_folders(root_path)
        print(f"\n✓ Successfully created folder structure:")
        print(f"  {created_path}")
        print(f"\nFolder structure:")
        print(f"  {root_path}/")
        print(f"  └── {datetime.now().year}/")
        print(f"      └── {datetime.now().month:02d}/")
        print(f"          └── {datetime.now().day:02d}/")

    except PermissionError:
        print(f"\n✗ Error: Permission denied. Cannot create folders at '{root_path}'")
    except FileNotFoundError:
        print(f"\n✗ Error: The path '{root_path}' does not exist or is invalid")
    except Exception as e:
        print(f"\n✗ Error: {type(e).__name__}: {e}")
    return created_path


if __name__ == "__main__":
    main()
