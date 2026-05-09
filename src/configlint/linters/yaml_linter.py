"""
YAML file linter.
"""

from pathlib import Path
from typing import Any, Optional

import yaml

from configlint.base import (
    BaseLinter,
    Issue,
    IssueType,
    LintResult,
    Severity,
)

try:
    import jsonschema
    from jsonschema import ValidationError as JsonSchemaValidationError
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


class YAMLLinter(BaseLinter):
    """Linter for YAML configuration files."""

    def __init__(self):
        super().__init__()
        self.supported_extensions = [".yaml", ".yml"]

    def parse(self, content: str) -> tuple[Any, Optional[str]]:
        """Parse YAML content."""
        try:
            # Use safe_load to avoid arbitrary code execution
            data = yaml.safe_load(content)
            return data, None
        except yaml.YAMLError as e:
            line = getattr(e, 'problem_mark', None)
            line_num = line.line + 1 if line else 1
            col_num = line.column + 1 if line else 1
            return None, f"YAML syntax error at line {line_num}, column {col_num}: {str(e.problem if hasattr(e, 'problem') else e)}"

    def lint(self, content: str, file_path: Path, schema: Optional[dict] = None) -> LintResult:
        """
        Lint YAML content.

        Checks:
        - Valid YAML syntax
        - Trailing whitespace
        - Tab characters (YAML should use spaces)
        - Inconsistent indentation
        - Duplicate keys
        - Missing final newline
        - Schema validation
        """
        result = LintResult(file_path=file_path, content=content)

        # Check for tab characters first
        lines = content.split("\n")
        for line_num, line in enumerate(lines, 1):
            if "\t" in line:
                result.add_issue(Issue(
                    file_path=file_path,
                    line=line_num,
                    issue_type=IssueType.INCONSISTENT_INDENTATION,
                    severity=Severity.ERROR,
                    message="Tab character detected (YAML requires spaces for indentation)",
                    suggestion="Replace tabs with spaces",
                    fixable=True,
                ))

        # Parse and check syntax
        data, error = self.parse(content)
        if error:
            result.add_issue(Issue(
                file_path=file_path,
                issue_type=IssueType.SYNTAX_ERROR,
                severity=Severity.ERROR,
                message=error,
            ))
            return result

        result.parsed_data = data

        # Check for trailing whitespace
        for line_num, line in enumerate(lines, 1):
            if line.rstrip() != line and line.strip():  # Ignore empty lines
                result.add_issue(Issue(
                    file_path=file_path,
                    line=line_num,
                    issue_type=IssueType.TRAILING_WHITESPACE,
                    severity=Severity.WARNING,
                    message="Trailing whitespace detected",
                    suggestion="Remove trailing whitespace",
                    fixable=True,
                ))

        # Check for missing final newline
        if content and not content.endswith("\n"):
            result.add_issue(Issue(
                file_path=file_path,
                line=len(lines),
                issue_type=IssueType.MISSING_NEWLINE,
                severity=Severity.INFO,
                message="Missing newline at end of file",
                suggestion="Add a newline at the end of the file",
                fixable=True,
            ))

        # Check for duplicate keys (custom loader needed)
        duplicate_issues = self._check_duplicate_keys(content)
        for issue in duplicate_issues:
            result.add_issue(issue)

        # Schema validation
        if schema and HAS_JSONSCHEMA and data is not None:
            try:
                jsonschema.validate(instance=data, schema=schema)
            except JsonSchemaValidationError as e:
                path = ".".join(str(p) for p in e.absolute_path) if e.absolute_path else "root"
                result.add_issue(Issue(
                    file_path=file_path,
                    issue_type=IssueType.SCHEMA_VIOLATION,
                    severity=Severity.ERROR,
                    message=f"Schema validation failed at '{path}': {e.message}",
                    suggestion=e.message,
                ))
        elif schema and not HAS_JSONSCHEMA:
            result.add_issue(Issue(
                file_path=file_path,
                issue_type=IssueType.INVALID_FORMAT,
                severity=Severity.WARNING,
                message="Schema validation requested but jsonschema package not installed",
                suggestion="Install jsonschema: pip install jsonschema",
            ))

        return result

    def _check_duplicate_keys(self, content: str) -> list[Issue]:
        """Check for duplicate keys in YAML mappings."""
        issues = []
        seen_keys = {}  # Track keys per mapping level
        current_mapping_keys = set()
        current_indent = -1

        lines = content.split("\n")
        for line_num, line in enumerate(lines, 1):
            # Skip empty lines and comments
            stripped = line.lstrip()
            if not stripped or stripped.startswith("#"):
                continue

            # Get indentation level
            indent = len(line) - len(stripped)

            # Check if this is a key line
            if ":" in stripped:
                key_part = stripped.split(":")[0].strip()
                if key_part and not key_part.startswith("-") and not key_part.startswith('"'):
                    # Reset tracking on indent change
                    if indent != current_indent:
                        current_indent = indent
                        current_mapping_keys = set()

                    # Check for duplicate
                    if key_part in current_mapping_keys:
                        issues.append(Issue(
                            file_path=Path(""),
                            line=line_num,
                            issue_type=IssueType.DUPLICATE_KEY,
                            severity=Severity.ERROR,
                            message=f"Duplicate key '{key_part}' detected",
                            suggestion=f"Rename or remove duplicate key '{key_part}'",
                            fixable=False,
                        ))
                    else:
                        current_mapping_keys.add(key_part)

        return issues
