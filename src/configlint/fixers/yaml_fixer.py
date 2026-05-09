"""
YAML file fixer.
"""

from pathlib import Path
from typing import Optional

import yaml

from configlint.base import (
    BaseFixer,
    FixResult,
    Issue,
    IssueType,
)


class YAMLFixer(BaseFixer):
    """Fixer for YAML configuration files."""

    def __init__(self):
        super().__init__()
        self.supported_extensions = [".yaml", ".yml"]

    def fix(self, content: str, file_path: Path, issues: Optional[list[Issue]] = None) -> FixResult:
        """
        Fix YAML content.

        Fixes:
        - Trailing whitespace
        - Missing final newline
        - Tab characters (convert to spaces)
        """
        original_content = content
        fixed_content = content
        issues_fixed = 0
        issues_remaining = []

        # Fix tab characters
        if "\t" in fixed_content:
            fixed_content = fixed_content.replace("\t", "  ")
            issues_fixed += fixed_content.count("  ") - original_content.count("  ")

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

        # Check if the result is still valid YAML
        try:
            yaml.safe_load(fixed_content)
        except yaml.YAMLError:
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
