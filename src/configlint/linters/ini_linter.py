"""
INI file linter.
"""

import configparser
from pathlib import Path
from typing import Any, Optional

from configlint.base import (
    BaseLinter,
    Issue,
    IssueType,
    LintResult,
    Severity,
)


class INILinter(BaseLinter):
    """Linter for INI configuration files."""

    def __init__(self):
        super().__init__()
        self.supported_extensions = [".ini", ".cfg", ".conf"]

    def parse(self, content: str) -> tuple[Any, Optional[str]]:
        """Parse INI content."""
        try:
            config = configparser.ConfigParser()
            config.read_string(content)
            # Convert to dict for consistency
            data = {}
            for section in config.sections():
                data[section] = dict(config[section])
            # Also include DEFAULT section if it has values
            if config.defaults():
                data["DEFAULT"] = dict(config.defaults())
            return data, None
        except configparser.Error as e:
            return None, f"INI syntax error: {str(e)}"

    def lint(self, content: str, file_path: Path, schema: Optional[dict] = None) -> LintResult:
        """
        Lint INI content.

        Checks:
        - Valid INI syntax
        - Trailing whitespace
        - Missing final newline
        - Duplicate keys (handled by parser)
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

        # Check for empty sections
        if data:
            for section, values in data.items():
                if not values:
                    result.add_issue(Issue(
                        file_path=file_path,
                        issue_type=IssueType.INVALID_FORMAT,
                        severity=Severity.WARNING,
                        message=f"Empty section '[{section}]' has no keys",
                        suggestion=f"Add keys to section '[{section}]' or remove it",
                        fixable=False,
                    ))

        return result
