"""
JSON file fixer.
"""

import json
from pathlib import Path
from typing import Optional

from configlint.base import (
    BaseFixer,
    FixResult,
    Issue,
    IssueType,
)


class JSONFixer(BaseFixer):
    """Fixer for JSON configuration files."""

    def __init__(self):
        super().__init__()
        self.supported_extensions = [".json"]

    def fix(self, content: str, file_path: Path, issues: Optional[list[Issue]] = None) -> FixResult:
        """
        Fix JSON content.

        Fixes:
        - Trailing whitespace
        - Missing final newline
        - Formatting (indentation)
        """
        original_content = content
        fixed_content = content
        issues_fixed = 0
        issues_remaining = []

        # Fix trailing whitespace
        lines = fixed_content.split("\n")
        fixed_lines = []
        for line in lines:
            if line.rstrip() != line:
                fixed_lines.append(line.rstrip())
                issues_fixed += 1
            else:
                fixed_lines.append(line)
        fixed_content = "\n".join(fixed_lines)

        # Fix missing final newline
        if fixed_content and not fixed_content.endswith("\n"):
            fixed_content += "\n"
            issues_fixed += 1

        # Try to parse and reformat for consistent indentation
        try:
            data = json.loads(fixed_content)
            # Reformat with consistent indentation
            fixed_content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        except json.JSONDecodeError:
            # Can't fix syntax errors
            if issues:
                for issue in issues:
                    if issue.issue_type == IssueType.SYNTAX_ERROR:
                        issues_remaining.append(issue)

        return FixResult(
            file_path=file_path,
            original_content=original_content,
            fixed_content=fixed_content,
            issues_fixed=issues_fixed,
            issues_remaining=issues_remaining,
            success=len(issues_remaining) == 0,
            message=f"Fixed {issues_fixed} issues" if issues_fixed > 0 else "No fixable issues found",
        )
