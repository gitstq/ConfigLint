"""
Schema utility functions.
"""

import json
from pathlib import Path
from typing import Any, Optional

import yaml


def load_schema(schema_path: Path) -> Optional[dict]:
    """
    Load a JSON Schema from a file.

    Supports JSON and YAML formats.

    Args:
        schema_path: Path to the schema file

    Returns:
        Schema as dictionary or None if loading fails
    """
    if not schema_path.exists():
        return None

    content = schema_path.read_text(encoding="utf-8")

    # Try JSON first
    if schema_path.suffix.lower() == ".json":
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return None

    # Try YAML
    if schema_path.suffix.lower() in [".yaml", ".yml"]:
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError:
            return None

    # Try both formats
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    try:
        return yaml.safe_load(content)
    except yaml.YAMLError:
        pass

    return None


def detect_schema_file(config_path: Path) -> Optional[Path]:
    """
    Try to detect a schema file for the given config file.

    Looks for:
    - {config_name}.schema.json
    - {config_name}.schema.yaml
    - schema.json in the same directory
    - .schema/{config_name}.json

    Args:
        config_path: Path to the configuration file

    Returns:
        Path to schema file or None if not found
    """
    config_dir = config_path.parent
    config_stem = config_path.stem

    # Common schema file patterns
    schema_patterns = [
        config_dir / f"{config_stem}.schema.json",
        config_dir / f"{config_stem}.schema.yaml",
        config_dir / f"{config_stem}.schema.yml",
        config_dir / "schema.json",
        config_dir / ".schema" / f"{config_stem}.json",
        config_dir / ".schema" / f"{config_stem}.yaml",
    ]

    for schema_path in schema_patterns:
        if schema_path.exists():
            return schema_path

    return None
