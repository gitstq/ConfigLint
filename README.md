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
  <strong>通用配置文件语法检查与自动修复工具</strong><br>
  <em>Universal Configuration File Linter & Auto-Fixer</em>
</p>

<p align="center">
  一款强大的命令行工具，支持 <strong>JSON、YAML、TOML、INI、ENV</strong> 等多种配置格式的语法检查、Schema验证与自动修复
</p>

---

## 🎉 项目介绍

**ConfigLint** 是一款专为开发者打造的配置文件检查与修复工具。在日常开发中，配置文件的语法错误往往难以排查，可能导致应用启动失败或运行异常。ConfigLint 能够帮助您：

- ✅ **快速发现**配置文件中的语法错误
- ✅ **自动修复**常见的格式问题（如尾随空格、缺失换行符）
- ✅ **Schema验证**确保配置结构符合预期
- ✅ **批量处理**整个项目目录

### 💡 灵感来源

本项目灵感来源于开发过程中遇到的配置文件调试痛点。现有工具往往只支持单一格式，缺乏统一的解决方案。ConfigLint 致力于成为配置文件管理的"瑞士军刀"。

### 🌟 自研差异化亮点

| 特性 | ConfigLint | 其他工具 |
|------|-----------|---------|
| 多格式支持 | JSON/YAML/TOML/INI/ENV | 通常仅支持1-2种 |
| 自动修复 | ✅ 支持 | ❌ 大多不支持 |
| Schema验证 | ✅ JSON Schema | 部分支持 |
| 批量处理 | ✅ 递归扫描 | ❌ 单文件 |
| CI/CD集成 | ✅ 友好输出 | 部分支持 |

---

## ✨ 核心特性

### 🔍 多格式支持

| 格式 | 扩展名 | 检查项 |
|------|--------|--------|
| **JSON** | `.json` | 语法检查、Schema验证、尾随空格、缺失换行 |
| **YAML** | `.yaml`, `.yml` | 语法检查、Tab检测、重复键、Schema验证 |
| **TOML** | `.toml` | 语法检查、Schema验证、格式问题 |
| **INI** | `.ini`, `.cfg`, `.conf` | 语法检查、空段检测、格式问题 |
| **ENV** | `.env`, `.env.*` | 变量名验证、重复键、引号建议 |

### 🛠️ 自动修复能力

- 🧹 移除尾随空格
- 📝 添加缺失的文件末尾换行符
- 🔄 转换Tab为空格（YAML）
- 📦 为含特殊字符的值添加引号（ENV）
- 🎨 统一JSON缩进格式

### 📊 丰富的输出格式

- **文本格式**：彩色终端输出，清晰易读
- **JSON格式**：便于CI/CD集成和程序处理

---

## 🚀 快速开始

### 📋 环境要求

- Python 3.10 或更高版本
- pip 包管理器

### 📦 安装

```bash
# 使用 pip 安装
pip install configlint

# 或从源码安装
git clone https://github.com/gitstq/ConfigLint.git
cd ConfigLint
pip install -e .
```

### 🎯 基本使用

```bash
# 检查单个文件
configlint check config.json

# 检查整个目录（递归）
configlint lint ./config/

# 使用 Schema 验证
configlint check config.yaml --schema schema.json

# 自动修复问题（预览模式）
configlint fix config.json --dry-run

# 自动修复并保存
configlint fix config.json --write

# 查看支持的格式
configlint formats
```

---

## 📖 详细使用指南

### 🔍 lint 命令

检查配置文件并报告问题：

```bash
# 基本用法
configlint lint <path>

# 选项
  -r, --recursive     递归搜索目录（默认启用）
  -s, --schema PATH   指定 JSON Schema 文件
  --auto-schema       自动检测 Schema 文件（默认启用）
  -V, --verbose       显示详细输出和建议
  -f, --format TEXT   输出格式：text 或 json
  -e, --exclude       排除模式（可多次使用）
```

**示例：**

```bash
# 检查单个文件
configlint lint config.json

# 检查目录，排除特定路径
configlint lint ./src --exclude "tests/*" --exclude "migrations/*"

# JSON 格式输出（便于 CI/CD）
configlint lint ./config --format json

# 详细模式
configlint lint config.yaml --verbose
```

### 🔧 fix 命令

自动修复配置文件问题：

```bash
# 基本用法
configlint fix <path>

# 选项
  -r, --recursive     递归搜索目录
  -w, --write         写入修改到文件
  -d, --dry-run       预览模式，不修改文件
  -V, --verbose       显示详细输出
  -e, --exclude       排除模式
```

**示例：**

```bash
# 预览修复内容
configlint fix config.json --dry-run --verbose

# 执行修复
configlint fix config.yaml --write

# 批量修复目录
configlint fix ./config --write --recursive
```

### ✅ check 命令

快速检查单个文件：

```bash
configlint check <path> [--schema PATH]
```

### 📋 formats 命令

列出所有支持的配置格式：

```bash
configlint formats
```

---

## 💡 设计思路与迭代规划

### 🏗️ 技术架构

```
ConfigLint
├── linters/          # 格式检查器
│   ├── json_linter.py
│   ├── yaml_linter.py
│   ├── toml_linter.py
│   ├── ini_linter.py
│   └── env_linter.py
├── fixers/           # 自动修复器
│   ├── json_fixer.py
│   ├── yaml_fixer.py
│   └── ...
├── utils/            # 工具函数
│   ├── file_utils.py
│   └── schema_utils.py
└── cli.py            # 命令行入口
```

### 🎯 设计理念

1. **模块化设计**：每种格式独立实现，便于扩展
2. **零配置优先**：开箱即用，无需复杂配置
3. **CI/CD友好**：支持JSON输出，便于集成
4. **安全第一**：使用 `yaml.safe_load` 防止代码注入

### 📅 迭代规划

| 版本 | 计划功能 |
|------|---------|
| v1.1 | 支持 XML、HCL 格式 |
| v1.2 | 配置文件规则自定义 |
| v1.3 | pre-commit hook 集成 |
| v2.0 | 图形化界面（可选） |

---

## 📦 打包与部署指南

### 🐍 PyPI 发布

```bash
# 构建
python -m build

# 上传到 PyPI
twine upload dist/*
```

### 🐳 Docker 部署

```dockerfile
FROM python:3.11-slim
RUN pip install configlint
ENTRYPOINT ["configlint"]
```

```bash
# 使用 Docker
docker build -t configlint .
docker run -v $(pwd):/data configlint lint /data/config
```

### ⚙️ pre-commit 集成

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

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 📝 提交 PR

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'feat: 添加新功能'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 提交 Pull Request

### 🐛 报告问题

请使用 [GitHub Issues](https://github.com/gitstq/ConfigLint/issues) 报告问题，包含：
- 问题描述
- 复现步骤
- 预期行为
- 实际行为
- 环境信息

---

## 📄 开源协议说明

本项目采用 [MIT License](LICENSE) 开源协议。

```
MIT License - 自由使用、修改、分发
仅需保留版权声明和许可证副本
```

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq">gitstq</a>
</p>

<p align="center">
  如果这个项目对你有帮助，请给一个 ⭐ Star！
</p>
