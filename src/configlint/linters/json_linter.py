"""
JSON file linter.
"""

import json
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
    import jsonschema
    from jsonschema import ValidationError as JsonSchemaValidationError
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


class JSONLinter(BaseLinter):
    """Linter for JSON configuration files."""

    def __init__(self):
        super().__init__()
        self.supported_extensions = [".json"]

    def parse(self, content: str) -> tuple[Any, Optional[str]]:
        """Parse JSON content."""
        try:
            data = json.loads(content)
            return data, None
        except json.JSONDecodeError as e:
            return None, f"JSON syntax error at line {e.lineno}, column {e.colno}: {e.msg}"

    def lint(self, content: str, file_path: Path, schema: Optional[dict] = None) -> LintResult:
        """
        Lint JSON content.

        Checks:
        - Valid JSON syntax
        - Trailing whitespace in strings
        - Duplicate keys (not detectable in standard JSON parser)
        - Schema validation (if schema provided)
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

        # Check for trailing whitespace in content
        lines = content.split("\n")
        for line_num, line in enumerate(lines, 1):
            if line.rstrip() != line:
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
