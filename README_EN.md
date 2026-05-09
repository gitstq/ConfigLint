<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Status-Stable-brightgreen.svg" alt="Status">
</p>

<p align="center">
  <a href="README.md">简体中文</a> |
  <a href="README_EN.md">English</a> |
  <a href="README_TW.md">繁體中文</a>
</p>

<h1 align="center">🔍 ConfigLint</h1>

<p align="center">
  <strong>Universal Configuration File Linter & Auto-Fixer</strong>
</p>

<p align="center">
  A powerful CLI tool for linting and fixing configuration files in <strong>JSON, YAML, TOML, INI, ENV</strong> formats with schema validation support
</p>

---

## 🎉 Introduction

**ConfigLint** is a developer-focused configuration file linting and fixing tool. Configuration file syntax errors are often difficult to debug and can cause application startup failures or runtime issues. ConfigLint helps you:

- ✅ **Quickly detect** syntax errors in configuration files
- ✅ **Automatically fix** common formatting issues (trailing whitespace, missing newlines)
- ✅ **Validate schemas** to ensure configuration structure meets expectations
- ✅ **Batch process** entire project directories

### 💡 Inspiration

This project was inspired by the pain points encountered during development when debugging configuration files. Existing tools often support only a single format, lacking a unified solution. ConfigLint aims to be the "Swiss Army knife" for configuration file management.

### 🌟 Key Differentiators

| Feature | ConfigLint | Other Tools |
|---------|-----------|-------------|
| Multi-format Support | JSON/YAML/TOML/INI/ENV | Usually 1-2 formats |
| Auto-fix | ✅ Supported | ❌ Most don't support |
| Schema Validation | ✅ JSON Schema | Partial support |
| Batch Processing | ✅ Recursive scan | ❌ Single file |
| CI/CD Integration | ✅ Friendly output | Partial support |

---

## ✨ Core Features

### 🔍 Multi-Format Support

| Format | Extensions | Checks |
|--------|------------|--------|
| **JSON** | `.json` | Syntax check, Schema validation, Trailing whitespace, Missing newline |
| **YAML** | `.yaml`, `.yml` | Syntax check, Tab detection, Duplicate keys, Schema validation |
| **TOML** | `.toml` | Syntax check, Schema validation, Format issues |
| **INI** | `.ini`, `.cfg`, `.conf` | Syntax check, Empty section detection, Format issues |
| **ENV** | `.env`, `.env.*` | Variable name validation, Duplicate keys, Quote suggestions |

### 🛠️ Auto-Fix Capabilities

- 🧹 Remove trailing whitespace
- 📝 Add missing final newlines
- 🔄 Convert tabs to spaces (YAML)
- 📦 Add quotes to values with special characters (ENV)
- 🎨 Unify JSON indentation

### 📊 Rich Output Formats

- **Text format**: Colorful terminal output, easy to read
- **JSON format**: Easy CI/CD integration and programmatic processing

---

## 🚀 Quick Start

### 📋 Requirements

- Python 3.10 or higher
- pip package manager

### 📦 Installation

```bash
# Install via pip
pip install configlint

# Or install from source
git clone https://github.com/gitstq/ConfigLint.git
cd ConfigLint
pip install -e .
```

### 🎯 Basic Usage

```bash
# Check a single file
configlint check config.json

# Check entire directory (recursive)
configlint lint ./config/

# Validate with schema
configlint check config.yaml --schema schema.json

# Auto-fix issues (preview mode)
configlint fix config.json --dry-run

# Auto-fix and save
configlint fix config.json --write

# View supported formats
configlint formats
```

---

## 📖 Detailed Usage Guide

### 🔍 lint Command

Check configuration files and report issues:

```bash
# Basic usage
configlint lint <path>

# Options
  -r, --recursive     Recursively search directories (default: enabled)
  -s, --schema PATH   Specify JSON Schema file
  --auto-schema       Auto-detect schema files (default: enabled)
  -V, --verbose       Show detailed output with suggestions
  -f, --format TEXT   Output format: text or json
  -e, --exclude       Exclude patterns (can be used multiple times)
```

**Examples:**

```bash
# Check a single file
configlint lint config.json

# Check directory, exclude specific paths
configlint lint ./src --exclude "tests/*" --exclude "migrations/*"

# JSON format output (for CI/CD)
configlint lint ./config --format json

# Verbose mode
configlint lint config.yaml --verbose
```

### 🔧 fix Command

Automatically fix configuration file issues:

```bash
# Basic usage
configlint fix <path>

# Options
  -r, --recursive     Recursively search directories
  -w, --write         Write changes to files
  -d, --dry-run       Preview mode, don't modify files
  -V, --verbose       Show detailed output
  -e, --exclude       Exclude patterns
```

**Examples:**

```bash
# Preview fixes
configlint fix config.json --dry-run --verbose

# Apply fixes
configlint fix config.yaml --write

# Batch fix directory
configlint fix ./config --write --recursive
```

### ✅ check Command

Quick check for a single file:

```bash
configlint check <path> [--schema PATH]
```

### 📋 formats Command

List all supported configuration formats:

```bash
configlint formats
```

---

## 💡 Design Philosophy & Roadmap

### 🏗️ Technical Architecture

```
ConfigLint
├── linters/          # Format-specific linters
│   ├── json_linter.py
│   ├── yaml_linter.py
│   ├── toml_linter.py
│   ├── ini_linter.py
│   └── env_linter.py
├── fixers/           # Auto-fixers
│   ├── json_fixer.py
│   ├── yaml_fixer.py
│   └── ...
├── utils/            # Utility functions
│   ├── file_utils.py
│   └── schema_utils.py
└── cli.py            # CLI entry point
```

### 🎯 Design Principles

1. **Modular Design**: Each format implemented independently for easy extension
2. **Zero-Config First**: Works out of the box, no complex setup needed
3. **CI/CD Friendly**: JSON output support for easy integration
4. **Security First**: Uses `yaml.safe_load` to prevent code injection

### 📅 Roadmap

| Version | Planned Features |
|---------|-----------------|
| v1.1 | XML, HCL format support |
| v1.2 | Custom configuration rules |
| v1.3 | pre-commit hook integration |
| v2.0 | Optional GUI interface |

---

## 📦 Packaging & Deployment

### 🐍 PyPI Release

```bash
# Build
python -m build

# Upload to PyPI
twine upload dist/*
```

### 🐳 Docker Deployment

```dockerfile
FROM python:3.11-slim
RUN pip install configlint
ENTRYPOINT ["configlint"]
```

```bash
# Use with Docker
docker build -t configlint .
docker run -v $(pwd):/data configlint lint /data/config
```

### ⚙️ pre-commit Integration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: configlint
        name: ConfigLint
        entry: configlint lint
        language: system
        types: [file]
        files: \.(json|yaml|yml|toml|ini|env)$
```

---

## 🤝 Contributing

We welcome all forms of contribution!

### 📝 Submitting a PR

1. Fork this repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'feat: add new feature'`
4. Push the branch: `git push origin feature/amazing-feature`
5. Submit a Pull Request

### 🐛 Reporting Issues

Please use [GitHub Issues](https://github.com/gitstq/ConfigLint/issues) to report problems, including:
- Problem description
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment information

---

## 📄 License

This project is released under the [MIT License](LICENSE).

```
MIT License - Free to use, modify, and distribute
Only requires retaining copyright notice and license copy
```

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq">gitstq</a>
</p>

<p align="center">
  If this project helps you, please give it a ⭐ Star!
</p>
