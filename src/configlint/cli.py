#!/usr/bin/env python3
"""
ConfigLint CLI - Universal Configuration File Linter & Auto-Fixer
通用配置文件语法检查与自动修复工具
"""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax

from configlint import __version__
from configlint.base import FixResult, Issue, LintResult, Severity
from configlint.linters import (
    ENVLinter,
    INILinter,
    JSONLinter,
    TOMLLinter,
    YAMLLinter,
)
from configlint.fixers import (
    ENVFixer,
    INIFixer,
    JSONFixer,
    TOMLFixer,
    YAMLFixer,
)
from configlint.utils import (
    detect_schema_file,
    find_config_files,
    get_file_type,
    load_schema,
    read_file,
    write_file,
)


console = Console()

# Linter and fixer registry
LINTERS = {
    "json": JSONLinter(),
    "yaml": YAMLLinter(),
    "toml": TOMLLinter(),
    "ini": INILinter(),
    "env": ENVLinter(),
}

FIXERS = {
    "json": JSONFixer(),
    "yaml": YAMLFixer(),
    "toml": TOMLFixer(),
    "ini": INIFixer(),
    "env": ENVFixer(),
}


def get_linter_for_file(file_path: Path):
    """Get the appropriate linter for a file."""
    file_type = get_file_type(file_path)
    if file_type and file_type in LINTERS:
        return LINTERS[file_type]
    return None


def get_fixer_for_file(file_path: Path):
    """Get the appropriate fixer for a file."""
    file_type = get_file_type(file_path)
    if file_type and file_type in FIXERS:
        return FIXERS[file_type]
    return None


def format_issue(issue: Issue, show_suggestion: bool = True) -> str:
    """Format an issue for display."""
    parts = []

    # Location
    location = str(issue.file_path)
    if issue.line is not None:
        location += f":{issue.line}"
        if issue.column is not None:
            location += f":{issue.column}"

    # Severity with color
    severity_colors = {
        Severity.ERROR: "red",
        Severity.WARNING: "yellow",
        Severity.INFO: "blue",
    }
    severity_str = f"[{severity_colors.get(issue.severity, 'white')}]{issue.severity.value.upper()}[/{severity_colors.get(issue.severity, 'white')}]"

    parts.append(f"{location} {severity_str} {issue.message}")

    if show_suggestion and issue.suggestion:
        parts.append(f"  💡 Suggestion: {issue.suggestion}")

    return "\n".join(parts)


def print_results(results: list[LintResult], verbose: bool = False) -> None:
    """Print lint results in a formatted way."""
    total_errors = sum(r.error_count for r in results)
    total_warnings = sum(r.warning_count for r in results)
    total_infos = sum(r.info_count for r in results)
    total_files = len(results)
    files_with_issues = sum(1 for r in results if r.issues)

    # Summary table
    table = Table(title="📊 Lint Summary", show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", justify="right")

    table.add_row("Files Checked", str(total_files))
    table.add_row("Files with Issues", str(files_with_issues))
    table.add_row("Errors", f"[red]{total_errors}[/red]")
    table.add_row("Warnings", f"[yellow]{total_warnings}[/yellow]")
    table.add_row("Info", f"[blue]{total_infos}[/blue]")

    console.print(table)

    # Print issues if any
    if files_with_issues > 0:
        console.print()
        console.print("[bold]Issues Found:[/bold]")
        console.print()

        for result in results:
            if result.issues:
                for issue in result.issues:
                    console.print(format_issue(issue, show_suggestion=verbose))
                    if verbose:
                        console.print()


@click.group(invoke_without_command=True)
@click.option("--version", "-v", is_flag=True, help="Show version and exit")
@click.pass_context
def main(ctx: click.Context, version: bool) -> None:
    """
    🔍 ConfigLint - Universal Configuration File Linter & Auto-Fixer

    A powerful CLI tool for linting and fixing configuration files
    in JSON, YAML, TOML, INI, and ENV formats.

    \b
    Examples:
      configlint lint config.json
      configlint lint ./config/ --recursive
      configlint fix config.yaml --write
      configlint check .env
    """
    if version:
        console.print(f"[bold cyan]ConfigLint[/bold cyan] version {__version__}")
        sys.exit(0)

    if ctx.invoked_subcommand is None:
        # Show help when no subcommand is provided
        click.echo(ctx.get_help())


@main.command()
@click.argument("path", type=click.Path(exists=True), required=False, default=".")
@click.option("--recursive", "-r", is_flag=True, default=True, help="Search directories recursively")
@click.option("--schema", "-s", type=click.Path(exists=True), help="JSON Schema file for validation")
@click.option("--auto-schema", is_flag=True, default=True, help="Auto-detect schema files")
@click.option("--verbose", "-V", is_flag=True, help="Show detailed output with suggestions")
@click.option("--format", "-f", "output_format", type=click.Choice(["text", "json"]), default="text", help="Output format")
@click.option("--exclude", "-e", multiple=True, help="Patterns to exclude (can be used multiple times)")
def lint(
    path: str,
    recursive: bool,
    schema: Optional[str],
    auto_schema: bool,
    verbose: bool,
    output_format: str,
    exclude: tuple,
) -> None:
    """
    🔍 Lint configuration files for syntax errors and issues.

    \b
    Examples:
      configlint lint config.json
      configlint lint ./config/ --recursive
      configlint lint config.yaml --schema schema.json
    """
    path_obj = Path(path)
    schema_data = None

    # Load explicit schema if provided
    if schema:
        schema_data = load_schema(Path(schema))
        if not schema_data:
            console.print(f"[red]Error: Could not load schema from {schema}[/red]")
            sys.exit(1)

    # Find all config files
    files = list(find_config_files(path_obj, recursive=recursive, exclude=list(exclude)))

    if not files:
        console.print("[yellow]No configuration files found[/yellow]")
        sys.exit(0)

    results: list[LintResult] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Linting files...", total=len(files))

        for file_path in files:
            progress.update(task, description=f"Linting {file_path.name}...")

            linter = get_linter_for_file(file_path)
            if not linter:
                continue

            content = read_file(file_path)

            # Try to auto-detect schema
            file_schema = schema_data
            if auto_schema and not schema_data:
                schema_path = detect_schema_file(file_path)
                if schema_path:
                    file_schema = load_schema(schema_path)

            result = linter.lint(content, file_path, schema=file_schema)
            results.append(result)
            progress.advance(task)

    # Output results
    if output_format == "json":
        import json as json_module
        output = {
            "files_checked": len(results),
            "total_errors": sum(r.error_count for r in results),
            "total_warnings": sum(r.warning_count for r in results),
            "total_infos": sum(r.info_count for r in results),
            "results": [
                {
                    "file": str(r.file_path),
                    "valid": r.valid,
                    "issues": [
                        {
                            "line": i.line,
                            "column": i.column,
                            "severity": i.severity.value,
                            "type": i.issue_type.value,
                            "message": i.message,
                            "suggestion": i.suggestion,
                            "fixable": i.fixable,
                        }
                        for i in r.issues
                    ],
                }
                for r in results
            ],
        }
        console.print(json_module.dumps(output, indent=2))
    else:
        print_results(results, verbose=verbose)

    # Exit with error code if there are errors
    total_errors = sum(r.error_count for r in results)
    if total_errors > 0:
        sys.exit(1)


@main.command()
@click.argument("path", type=click.Path(exists=True), required=False, default=".")
@click.option("--recursive", "-r", is_flag=True, default=True, help="Search directories recursively")
@click.option("--write", "-w", "write_changes", is_flag=True, help="Write changes to files")
@click.option("--dry-run", "-d", is_flag=True, help="Show what would be changed without modifying files")
@click.option("--verbose", "-V", is_flag=True, help="Show detailed output")
@click.option("--exclude", "-e", multiple=True, help="Patterns to exclude")
def fix(
    path: str,
    recursive: bool,
    write_changes: bool,
    dry_run: bool,
    verbose: bool,
    exclude: tuple,
) -> None:
    """
    🔧 Fix configuration files automatically.

    \b
    Examples:
      configlint fix config.json --dry-run
      configlint fix ./config/ --write
      configlint fix config.yaml -w -V
    """
    if dry_run:
        write_changes = False

    path_obj = Path(path)
    files = list(find_config_files(path_obj, recursive=recursive, exclude=list(exclude)))

    if not files:
        console.print("[yellow]No configuration files found[/yellow]")
        sys.exit(0)

    total_fixed = 0
    fix_results: list[FixResult] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Fixing files...", total=len(files))

        for file_path in files:
            progress.update(task, description=f"Fixing {file_path.name}...")

            linter = get_linter_for_file(file_path)
            fixer = get_fixer_for_file(file_path)

            if not linter or not fixer:
                continue

            content = read_file(file_path)
            result = linter.lint(content, file_path)

            if result.issues:
                fix_result = fixer.fix(content, file_path, result.issues)
                fix_results.append(fix_result)

                if fix_result.issues_fixed > 0:
                    total_fixed += fix_result.issues_fixed

                    if write_changes:
                        write_file(file_path, fix_result.fixed_content)
                        if verbose:
                            console.print(f"[green]✓ Fixed {fix_result.issues_fixed} issues in {file_path}[/green]")
                    elif dry_run:
                        if verbose:
                            console.print(f"[cyan]Would fix {fix_result.issues_fixed} issues in {file_path}[/cyan]")
                            if verbose:
                                # Show diff
                                console.print("\n[bold]Original:[/bold]")
                                console.print(Panel(Syntax(content, "text", line_numbers=True)))
                                console.print("\n[bold]Fixed:[/bold]")
                                console.print(Panel(Syntax(fix_result.fixed_content, "text", line_numbers=True)))

            progress.advance(task)

    # Summary
    console.print()
    if total_fixed > 0:
        if write_changes:
            console.print(f"[green]✅ Fixed {total_fixed} issues in {len(fix_results)} files[/green]")
        elif dry_run:
            console.print(f"[cyan]Would fix {total_fixed} issues in {len(fix_results)} files (dry run)[/cyan]")
        else:
            console.print(f"[yellow]Found {total_fixed} fixable issues. Use --write to apply changes.[/yellow]")
    else:
        console.print("[green]✅ No fixable issues found[/green]")


@main.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--schema", "-s", type=click.Path(exists=True), help="JSON Schema file for validation")
def check(path: str, schema: Optional[str]) -> None:
    """
    ✅ Quick check a single configuration file.

    \b
    Examples:
      configlint check config.json
      configlint check config.yaml --schema schema.json
    """
    path_obj = Path(path)
    file_type = get_file_type(path_obj)

    if not file_type:
        console.print(f"[red]Error: Unsupported file type for {path}[/red]")
        sys.exit(1)

    linter = get_linter_for_file(path_obj)
    if not linter:
        console.print(f"[red]Error: No linter available for {path}[/red]")
        sys.exit(1)

    content = read_file(path_obj)
    schema_data = None

    if schema:
        schema_data = load_schema(Path(schema))
        if not schema_data:
            console.print(f"[red]Error: Could not load schema from {schema}[/red]")
            sys.exit(1)
    else:
        # Try auto-detect
        schema_path = detect_schema_file(path_obj)
        if schema_path:
            schema_data = load_schema(schema_path)
            if schema_data:
                console.print(f"[dim]Using schema: {schema_path}[/dim]")

    result = linter.lint(content, path_obj, schema=schema_data)

    if result.valid:
        console.print(f"[green]✅ {path} is valid![/green]")
        if result.info_count > 0:
            console.print(f"[blue]ℹ️  {result.info_count} info messages[/blue]")
    else:
        console.print(f"[red]❌ {path} has {result.error_count} error(s)[/red]")
        for issue in result.issues:
            console.print(format_issue(issue))
        sys.exit(1)


@main.command()
def formats() -> None:
    """
    📋 List supported configuration file formats.
    """
    table = Table(title="📋 Supported Formats", show_header=True, header_style="bold cyan")
    table.add_column("Format", style="cyan")
    table.add_column("Extensions", style="green")
    table.add_column("Features", style="yellow")

    format_info = [
        ("JSON", ".json", "Syntax check, Schema validation, Auto-fix"),
        ("YAML", ".yaml, .yml", "Syntax check, Schema validation, Tab detection, Auto-fix"),
        ("TOML", ".toml", "Syntax check, Schema validation, Auto-fix"),
        ("INI", ".ini, .cfg, .conf", "Syntax check, Empty section detection, Auto-fix"),
        ("ENV", ".env, .env.*", "Syntax check, Variable name validation, Duplicate detection, Auto-fix"),
    ]

    for fmt, exts, features in format_info:
        table.add_row(fmt, exts, features)

    console.print(table)


if __name__ == "__main__":
    main()
