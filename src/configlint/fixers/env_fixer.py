"""
ENV (dotenv) file fixer.
"""

from pathlib import Path
from typing import Optional

from configlint.base import (
    BaseFixer,
    FixResult,
    Issue,
    IssueType,
)


class ENVFixer(BaseFixer):
    """Fixer for .env (dotenv) configuration files."""

    def __init__(self):
        super().__init__()
        self.supported_extensions = [".env"]

    def supports_file(self, file_path: Path) -> bool:
        """Check if this fixer supports the given file."""
        name = file_path.name
        if file_path.suffix.lower() in self.supported_extensions:
            return True
        if name == ".env" or name.startswith(".env."):
            return True
        return False

    def fix(self, content: str, file_path: Path, issues: Optional[list[Issue]] = None) -> FixResult:
        """
        Fix ENV content.

        Fixes:
        - Trailing whitespace
        - Missing final newline
        - Unquoted values with spaces (adds quotes)
        """
        original_content = content
        fixed_content = content
        issues_fixed = 0
        issues_remaining = []

        # Fix trailing whitespace
        lines = fixed_content.split("\n")
        fixed_lines = []
        for line in lines:
            original_line = line
            line = line.rstrip()

            # Check if this is a KEY=VALUE line that needs quoting
            if "=" in line and not line.strip().startswith("#"):
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()

                # Add quotes if value has spaces and isn't already quoted
                if value and " " in value:
                    if not (value.startswith('"') and value.endswith('"')) and \
                       not (value.startswith("'") and value.endswith("'")):
                        value = f'"{value}"'
                        line = f"{key}={value}"
                        issues_fixed += 1

            if original_line.rstrip() != original_line:
                issues_fixed += 1

            fixed_lines.append(line)

        fixed_content = "\n".join(fixed_lines)

        # Fix missing final newline
        if fixed_content and not fixed_content.endswith("\n"):
            fixed_content += "\n"
            issues_fixed += 1

        return FixResult(
            file_path=file_path,
            original_content=original_content,
            fixed_content=fixed_content,
            issues_fixed=issues_fixed,
            issues_remaining=issues_remaining,
            success=True,
            message=f"Fixed {issues_fixed} issues" if issues_fixed > 0 else "No fixable issues found",
        )
