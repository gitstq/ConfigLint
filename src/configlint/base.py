"""
Base classes for linters and fixers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class Severity(Enum):
    """Issue severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class IssueType(Enum):
    """Types of configuration issues."""
    SYNTAX_ERROR = "syntax_error"
    INVALID_FORMAT = "invalid_format"
    SCHEMA_VIOLATION = "schema_violation"
    DUPLICATE_KEY = "duplicate_key"
    TRAILING_WHITESPACE = "trailing_whitespace"
    MISSING_NEWLINE = "missing_newline"
    INCONSISTENT_INDENTATION = "inconsistent_indentation"
    INVALID_VALUE = "invalid_value"
    MISSING_REQUIRED_KEY = "missing_required_key"
    DEPRECATED_KEY = "deprecated_key"


@dataclass
class Issue:
    """Represents a single configuration issue."""
    file_path: Path
    line: Optional[int] = None
    column: Optional[int] = None
    issue_type: IssueType = IssueType.SYNTAX_ERROR
    severity: Severity = Severity.ERROR
    message: str = ""
    suggestion: Optional[str] = None
    fixable: bool = False

    def __str__(self) -> str:
        location = ""
        if self.line is not None:
            location = f":{self.line}"
            if self.column is not None:
                location += f":{self.column}"
        return f"{self.file_path}{location} [{self.severity.value}] {self.message}"


@dataclass
class LintResult:
    """Result of linting a file or directory."""
    file_path: Path
    issues: list[Issue] = field(default_factory=list)
    valid: bool = True
    content: Optional[str] = None
    parsed_data: Optional[Any] = None

    def add_issue(self, issue: Issue) -> None:
        """Add an issue to the result."""
        self.issues.append(issue)
        if issue.severity == Severity.ERROR:
            self.valid = False

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.WARNING)

    @property
    def info_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.INFO)


@dataclass
class FixResult:
    """Result of fixing a file."""
    file_path: Path
    original_content: str
    fixed_content: str
    issues_fixed: int = 0
    issues_remaining: list[Issue] = field(default_factory=list)
    success: bool = True
    message: str = ""


class BaseLinter(ABC):
    """Abstract base class for format-specific linters."""

    def __init__(self):
        self.supported_extensions: list[str] = []

    @abstractmethod
    def lint(self, content: str, file_path: Path, schema: Optional[dict] = None) -> LintResult:
        """
        Lint the given content.

        Args:
            content: The file content to lint
            file_path: Path to the file (for error reporting)
            schema: Optional JSON Schema for validation

        Returns:
            LintResult with any issues found
        """
        pass

    @abstractmethod
    def parse(self, content: str) -> tuple[Any, Optional[str]]:
        """
        Parse the content and return data or error message.

        Args:
            content: The file content to parse

        Returns:
            Tuple of (parsed_data, error_message)
        """
        pass

    def supports_file(self, file_path: Path) -> bool:
        """Check if this linter supports the given file."""
        return file_path.suffix.lower() in self.supported_extensions


class BaseFixer(ABC):
    """Abstract base class for format-specific fixers."""

    def __init__(self):
        self.supported_extensions: list[str] = []

    @abstractmethod
    def fix(self, content: str, file_path: Path, issues: Optional[list[Issue]] = None) -> FixResult:
        """
        Fix the given content.

        Args:
            content: The file content to fix
            file_path: Path to the file
            issues: Optional list of specific issues to fix

        Returns:
            FixResult with the fixed content
        """
        pass

    def supports_file(self, file_path: Path) -> bool:
        """Check if this fixer supports the given file."""
        return file_path.suffix.lower() in self.supported_extensions
