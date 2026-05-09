"""
TOML file linter.
"""

from pathlib import Path
from typing import Any, Optional

from configlint.base import (
    BaseLinter,
    Issue,
    IssueType,
    LintResult,
    Severity,
)

try:
    import tomllib
except ImportError:
    import tomli as tomllib

try:
    import jsonschema
    from jsonschema import ValidationError as JsonSchemaValidationError
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


class TOMLLinter(BaseLinter):
    """Linter for TOML configuration files."""

    def __init__(self):
        super().__init__()
        self.supported_extensions = [".toml"]

    def parse(self, content: str) -> tuple[Any, Optional[str]]:
        """Parse TOML content."""
        try:
            data = tomllib.loads(content)
            return data, None
        except Exception as e:
            # TOML errors can be various types
            error_msg = str(e)
            # Try to extract line number if available
            if "line" in error_msg.lower():
                return None, f"TOML syntax error: {error_msg}"
            return None, f"TOML syntax error: {error_msg}"

    def lint(self, content: str, file_path: Path, schema: Optional[dict] = None) -> LintResult:
        """
        Lint TOML content.

        Checks:
        - Valid TOML syntax
        - Trailing whitespace
        - Missing final newline
        - Duplicate keys (handled by parser)
        - Schema validation
        """
        result = LintResult(file_path=file_path, content=content)

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
        lines = content.split("\n")
        for line_num, line in enumerate(lines, 1):
            if line.rstrip() != line and line.strip():
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
