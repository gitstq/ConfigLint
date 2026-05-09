"""
ENV (dotenv) file linter.
"""

import re
from pathlib import Path
from typing import Any, Optional

from configlint.base import (
    BaseLinter,
    Issue,
    IssueType,
    LintResult,
    Severity,
)


class ENVLinter(BaseLinter):
    """Linter for .env (dotenv) configuration files."""

    # Pattern for valid env variable names
    VAR_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

    def __init__(self):
        super().__init__()
        self.supported_extensions = [".env"]
        # Also support files named .env or .env.*
        self.supported_names = [".env"]

    def supports_file(self, file_path: Path) -> bool:
        """Check if this linter supports the given file."""
        if file_path.suffix.lower() in self.supported_extensions:
            return True
        # Check for .env files or .env.* patterns
        name = file_path.name
        if name == ".env" or name.startswith(".env."):
            return True
        return False

    def parse(self, content: str) -> tuple[Any, Optional[str]]:
        """Parse ENV content."""
        try:
            data = {}
            lines = content.split("\n")
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue
                # Parse KEY=VALUE
                if "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip()
                    # Remove quotes if present
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    data[key] = value
            return data, None
        except Exception as e:
            return None, f"ENV parsing error: {str(e)}"

    def lint(self, content: str, file_path: Path, schema: Optional[dict] = None) -> LintResult:
        """
        Lint ENV content.

        Checks:
        - Valid KEY=VALUE format
        - Valid variable names (alphanumeric + underscore, can't start with number)
        - Trailing whitespace
        - Missing final newline
        - Duplicate keys
        - Unquoted values with special characters
        """
        result = LintResult(file_path=file_path, content=content)

        lines = content.split("\n")
        seen_keys = {}

        for line_num, line in enumerate(lines, 1):
            original_line = line

            # Check for trailing whitespace
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

            line = line.strip()

            # Skip empty lines and comments
            if not line:
                continue
            if line.startswith("#"):
                # Check for inline comments without space
                if "#" in line[1:] and not any(c in line for c in ["="]):
                    pass  # This is fine for pure comment lines
                continue

            # Check for valid KEY=VALUE format
            if "=" not in line:
                result.add_issue(Issue(
                    file_path=file_path,
                    line=line_num,
                    issue_type=IssueType.SYNTAX_ERROR,
                    severity=Severity.ERROR,
                    message="Invalid format: missing '=' separator",
                    suggestion="Use KEY=VALUE format",
                    fixable=False,
                ))
                continue

            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()

            # Check for empty key
            if not key:
                result.add_issue(Issue(
                    file_path=file_path,
                    line=line_num,
                    issue_type=IssueType.SYNTAX_ERROR,
                    severity=Severity.ERROR,
                    message="Empty key before '='",
                    suggestion="Provide a valid variable name",
                    fixable=False,
                ))
                continue

            # Check for valid variable name
            if not self.VAR_NAME_PATTERN.match(key):
                result.add_issue(Issue(
                    file_path=file_path,
                    line=line_num,
                    issue_type=IssueType.INVALID_FORMAT,
                    severity=Severity.ERROR,
                    message=f"Invalid variable name '{key}' (must start with letter or underscore, contain only alphanumeric and underscore)",
                    suggestion=f"Rename '{key}' to follow naming conventions",
                    fixable=False,
                ))

            # Check for duplicate keys
            if key in seen_keys:
                result.add_issue(Issue(
                    file_path=file_path,
                    line=line_num,
                    issue_type=IssueType.DUPLICATE_KEY,
                    severity=Severity.WARNING,
                    message=f"Duplicate key '{key}' (first defined at line {seen_keys[key]})",
                    suggestion=f"Remove or rename duplicate key '{key}'",
                    fixable=False,
                ))
            else:
                seen_keys[key] = line_num

            # Check for unquoted values with spaces or special characters
            if value and not (value.startswith('"') or value.startswith("'")):
                if " " in value or "#" in value:
                    result.add_issue(Issue(
                        file_path=file_path,
                        line=line_num,
                        issue_type=IssueType.INVALID_FORMAT,
                        severity=Severity.WARNING,
                        message=f"Value '{value}' contains spaces or special characters and should be quoted",
                        suggestion=f"Quote the value: {key}=\"{value}\"",
                        fixable=True,
                    ))

        # Parse and store data
        data, _ = self.parse(content)
        result.parsed_data = data

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

        return result
