"""
File utility functions.
"""

import json
from pathlib import Path
from typing import Generator, Optional

import yaml

try:
    import tomllib
except ImportError:
    import tomli as tomllib


# Supported file extensions and their types
FILE_TYPES = {
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".ini": "ini",
    ".cfg": "ini",
    ".conf": "ini",
    ".env": "env",
}

# Files that should be treated as env files by name
ENV_FILE_NAMES = [".env"]


def get_file_type(file_path: Path) -> Optional[str]:
    """
    Determine the file type based on extension or name.

    Args:
        file_path: Path to the file

    Returns:
        File type string or None if not supported
    """
    # Check by extension first
    ext = file_path.suffix.lower()
    if ext in FILE_TYPES:
        return FILE_TYPES[ext]

    # Check by name for .env files
    name = file_path.name
    if name in ENV_FILE_NAMES or name.startswith(".env."):
        return "env"

    return None


def find_config_files(
    path: Path,
    recursive: bool = True,
    extensions: Optional[list[str]] = None,
    exclude: Optional[list[str]] = None,
) -> Generator[Path, None, None]:
    """
    Find all configuration files in a directory.

    Args:
        path: Directory path to search
        recursive: Whether to search recursively
        extensions: List of extensions to include (None = all supported)
        exclude: List of patterns to exclude

    Yields:
        Path objects for each found file
    """
    if extensions is None:
        extensions = list(FILE_TYPES.keys()) + [".env"]

    exclude = exclude or []
    exclude_patterns = [".git", "node_modules", "__pycache__", ".venv", "venv", "build", "dist"]

    if path.is_file():
        if get_file_type(path) and not any(p in str(path) for p in exclude_patterns):
            yield path
        return

    if recursive:
        pattern = "**/*"
    else:
        pattern = "*"

    for file_path in path.glob(pattern):
        if not file_path.is_file():
            continue

        # Skip excluded patterns
        if any(p in str(file_path) for p in exclude_patterns):
            continue
        if any(p in str(file_path) for p in exclude):
            continue

        # Check if it's a supported file type
        if get_file_type(file_path):
            yield file_path


def read_file(file_path: Path) -> str:
    """
    Read file content with proper encoding handling.

    Args:
        file_path: Path to the file

    Returns:
        File content as string
    """
    # Try UTF-8 first, then fall back to latin-1
    encodings = ["utf-8", "latin-1"]

    for encoding in encodings:
        try:
            return file_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue

    # If all else fails, read as binary and decode with errors ignored
    return file_path.read_bytes().decode("utf-8", errors="ignore")


def write_file(file_path: Path, content: str) -> None:
    """
    Write content to file.

    Args:
        file_path: Path to the file
        content: Content to write
    """
    file_path.write_text(content, encoding="utf-8")
