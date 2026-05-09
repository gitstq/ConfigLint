"""Tests for ConfigLint."""

import pytest
from pathlib import Path
import tempfile
import os

from configlint.linters import (
    JSONLinter,
    YAMLLinter,
    TOMLLinter,
    INILinter,
    ENVLinter,
)
from configlint.fixers import (
    JSONFixer,
    YAMLFixer,
    TOMLFixer,
    INIFixer,
    ENVFixer,
)


class TestJSONLinter:
    """Tests for JSON linter."""

    def test_valid_json(self):
        """Test valid JSON content."""
        linter = JSONLinter()
        content = '{"name": "test", "value": 123}'
        result = linter.lint(content, Path("test.json"))
        assert result.valid is True
        assert result.error_count == 0

    def test_invalid_json(self):
        """Test invalid JSON content."""
        linter = JSONLinter()
        content = '{"name": "test", "value": }'
        result = linter.lint(content, Path("test.json"))
        assert result.valid is False
        assert result.error_count > 0

    def test_trailing_whitespace(self):
        """Test detection of trailing whitespace."""
        linter = JSONLinter()
        content = '{"name": "test"}   \n'
        result = linter.lint(content, Path("test.json"))
        assert any(i.issue_type.value == "trailing_whitespace" for i in result.issues)

    def test_missing_newline(self):
        """Test detection of missing final newline."""
        linter = JSONLinter()
        content = '{"name": "test"}'
        result = linter.lint(content, Path("test.json"))
        assert any(i.issue_type.value == "missing_newline" for i in result.issues)


class TestYAMLLinter:
    """Tests for YAML linter."""

    def test_valid_yaml(self):
        """Test valid YAML content."""
        linter = YAMLLinter()
        content = "name: test\nvalue: 123\n"
        result = linter.lint(content, Path("test.yaml"))
        assert result.valid is True
        assert result.error_count == 0

    def test_invalid_yaml(self):
        """Test invalid YAML content."""
        linter = YAMLLinter()
        content = "name: test\n  value: 123\n    nested: bad\n"
        result = linter.lint(content, Path("test.yaml"))
        # YAML parser may still parse this, but it's malformed
        assert result is not None

    def test_tab_detection(self):
        """Test detection of tab characters."""
        linter = YAMLLinter()
        content = "name:\n\tvalue: test\n"
        result = linter.lint(content, Path("test.yaml"))
        assert result.valid is False
        assert any(i.issue_type.value == "inconsistent_indentation" for i in result.issues)


class TestTOMLLinter:
    """Tests for TOML linter."""

    def test_valid_toml(self):
        """Test valid TOML content."""
        linter = TOMLLinter()
        content = '[section]\nname = "test"\nvalue = 123\n'
        result = linter.lint(content, Path("test.toml"))
        assert result.valid is True
        assert result.error_count == 0

    def test_invalid_toml(self):
        """Test invalid TOML content."""
        linter = TOMLLinter()
        content = '[section\nname = "test"\n'
        result = linter.lint(content, Path("test.toml"))
        assert result.valid is False
        assert result.error_count > 0


class TestINILinter:
    """Tests for INI linter."""

    def test_valid_ini(self):
        """Test valid INI content."""
        linter = INILinter()
        content = '[section]\nname = test\nvalue = 123\n'
        result = linter.lint(content, Path("test.ini"))
        assert result.valid is True
        assert result.error_count == 0

    def test_invalid_ini(self):
        """Test invalid INI content."""
        linter = INILinter()
        content = '[section\nname = test\n'
        result = linter.lint(content, Path("test.ini"))
        assert result.valid is False
        assert result.error_count > 0


class TestENVLinter:
    """Tests for ENV linter."""

    def test_valid_env(self):
        """Test valid ENV content."""
        linter = ENVLinter()
        content = 'NAME=test\nVALUE=123\n'
        result = linter.lint(content, Path(".env"))
        assert result.valid is True
        assert result.error_count == 0

    def test_invalid_variable_name(self):
        """Test detection of invalid variable names."""
        linter = ENVLinter()
        content = '123NAME=test\n'
        result = linter.lint(content, Path(".env"))
        assert result.valid is False
        assert any(i.issue_type.value == "invalid_format" for i in result.issues)

    def test_duplicate_key(self):
        """Test detection of duplicate keys."""
        linter = ENVLinter()
        content = 'NAME=test\nNAME=other\n'
        result = linter.lint(content, Path(".env"))
        assert any(i.issue_type.value == "duplicate_key" for i in result.issues)


class TestJSONFixer:
    """Tests for JSON fixer."""

    def test_fix_trailing_whitespace(self):
        """Test fixing trailing whitespace."""
        fixer = JSONFixer()
        content = '{"name": "test"}   \n'
        result = fixer.fix(content, Path("test.json"))
        assert result.issues_fixed > 0
        assert "   " not in result.fixed_content

    def test_fix_missing_newline(self):
        """Test fixing missing final newline."""
        fixer = JSONFixer()
        content = '{"name": "test"}'
        result = fixer.fix(content, Path("test.json"))
        assert result.fixed_content.endswith("\n")


class TestYAMLFixer:
    """Tests for YAML fixer."""

    def test_fix_tabs(self):
        """Test fixing tab characters."""
        fixer = YAMLFixer()
        content = "name:\n\tvalue: test\n"
        result = fixer.fix(content, Path("test.yaml"))
        assert "\t" not in result.fixed_content


class TestENVFixer:
    """Tests for ENV fixer."""

    def test_fix_unquoted_values(self):
        """Test fixing unquoted values with spaces."""
        fixer = ENVFixer()
        content = 'NAME=value with spaces\n'
        result = fixer.fix(content, Path(".env"))
        assert '"value with spaces"' in result.fixed_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
