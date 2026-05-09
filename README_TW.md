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
  <strong>通用設定檔語法檢查與自動修復工具</strong><br>
  <em>Universal Configuration File Linter & Auto-Fixer</em>
</p>

<p align="center">
  一款強大的命令列工具，支援 <strong>JSON、YAML、TOML、INI、ENV</strong> 等多種設定格式的語法檢查、Schema驗證與自動修復
</p>

---

## 🎉 專案介紹

**ConfigLint** 是一款專為開發者打造的設定檔檢查與修復工具。在日常開發中，設定檔的語法錯誤往往難以排查，可能導致應用程式啟動失敗或執行異常。ConfigLint 能夠幫助您：

- ✅ **快速發現**設定檔中的語法錯誤
- ✅ **自動修復**常見的格式問題（如尾隨空白、缺少換行符）
- ✅ **Schema驗證**確保設定結構符合預期
- ✅ **批次處理**整個專案目錄

### 💡 靈感來源

本專案靈感來自於開發過程中遇到的設定檔除錯痛點。現有工具往往只支援單一格式，缺乏統一的解決方案。ConfigLint 致力於成為設定檔管理的「瑞士刀」。

### 🌟 自研差異化亮點

| 特性 | ConfigLint | 其他工具 |
|------|-----------|---------|
| 多格式支援 | JSON/YAML/TOML/INI/ENV | 通常僅支援1-2種 |
| 自動修復 | ✅ 支援 | ❌ 大多不支援 |
| Schema驗證 | ✅ JSON Schema | 部分支援 |
| 批次處理 | ✅ 遞迴掃描 | ❌ 單一檔案 |
| CI/CD整合 | ✅ 友善輸出 | 部分支援 |

---

## ✨ 核心特性

### 🔍 多格式支援

| 格式 | 副檔名 | 檢查項 |
|------|--------|--------|
| **JSON** | `.json` | 語法檢查、Schema驗證、尾隨空白、缺少換行 |
| **YAML** | `.yaml`, `.yml` | 語法檢查、Tab檢測、重複鍵、Schema驗證 |
| **TOML** | `.toml` | 語法檢查、Schema驗證、格式問題 |
| **INI** | `.ini`, `.cfg`, `.conf` | 語法檢查、空段檢測、格式問題 |
| **ENV** | `.env`, `.env.*` | 變數名驗證、重複鍵、引號建議 |

### 🛠️ 自動修復能力

- 🧹 移除尾隨空白
- 📝 新增缺少的檔案結尾換行符
- 🔄 轉換Tab為空白（YAML）
- 📦 為含特殊字元的值新增引號（ENV）
- 🎨 統一JSON縮排格式

### 📊 豐富的輸出格式

- **文字格式**：彩色終端輸出，清晰易讀
- **JSON格式**：便於CI/CD整合和程式處理

---

## 🚀 快速開始

### 📋 環境要求

- Python 3.10 或更高版本
- pip 套件管理器

### 📦 安裝

```bash
# 使用 pip 安裝
pip install configlint

# 或從原始碼安裝
git clone https://github.com/gitstq/ConfigLint.git
cd ConfigLint
pip install -e .
```

### 🎯 基本使用

```bash
# 檢查單一檔案
configlint check config.json

# 檢查整個目錄（遞迴）
configlint lint ./config/

# 使用 Schema 驗證
configlint check config.yaml --schema schema.json

# 自動修復問題（預覽模式）
configlint fix config.json --dry-run

# 自動修復並儲存
configlint fix config.json --write

# 查看支援的格式
configlint formats
```

---

## 📖 詳細使用指南

### 🔍 lint 命令

檢查設定檔並報告問題：

```bash
# 基本用法
configlint lint <path>

# 選項
  -r, --recursive     遞迴搜尋目錄（預設啟用）
  -s, --schema PATH   指定 JSON Schema 檔案
  --auto-schema       自動偵測 Schema 檔案（預設啟用）
  -V, --verbose       顯示詳細輸出和建議
  -f, --format TEXT   輸出格式：text 或 json
  -e, --exclude       排除模式（可多次使用）
```

**範例：**

```bash
# 檢查單一檔案
configlint lint config.json

# 檢查目錄，排除特定路徑
configlint lint ./src --exclude "tests/*" --exclude "migrations/*"

# JSON 格式輸出（便於 CI/CD）
configlint lint ./config --format json

# 詳細模式
configlint lint config.yaml --verbose
```

### 🔧 fix 命令

自動修復設定檔問題：

```bash
# 基本用法
configlint fix <path>

# 選項
  -r, --recursive     遞迴搜尋目錄
  -w, --write         寫入修改到檔案
  -d, --dry-run       預覽模式，不修改檔案
  -V, --verbose       顯示詳細輸出
  -e, --exclude       排除模式
```

**範例：**

```bash
# 預覽修復內容
configlint fix config.json --dry-run --verbose

# 執行修復
configlint fix config.yaml --write

# 批次修復目錄
configlint fix ./config --write --recursive
```

### ✅ check 命令

快速檢查單一檔案：

```bash
configlint check <path> [--schema PATH]
```

### 📋 formats 命令

列出所有支援的設定格式：

```bash
configlint formats
```

---

## 💡 設計思路與迭代規劃

### 🏗️ 技術架構

```
ConfigLint
├── linters/          # 格式檢查器
│   ├── json_linter.py
│   ├── yaml_linter.py
│   ├── toml_linter.py
│   ├── ini_linter.py
│   └── env_linter.py
├── fixers/           # 自動修復器
│   ├── json_fixer.py
│   ├── yaml_fixer.py
│   └── ...
├── utils/            # 工具函式
│   ├── file_utils.py
│   └── schema_utils.py
└── cli.py            # 命令列入口
```

### 🎯 設計理念

1. **模組化設計**：每種格式獨立實作，便於擴展
2. **零設定優先**：開箱即用，無需複雜設定
3. **CI/CD友善**：支援JSON輸出，便於整合
4. **安全第一**：使用 `yaml.safe_load` 防止程式碼注入

### 📅 迭代規劃

| 版本 | 計劃功能 |
|------|---------|
| v1.1 | 支援 XML、HCL 格式 |
| v1.2 | 設定檔規則自訂 |
| v1.3 | pre-commit hook 整合 |
| v2.0 | 圖形化介面（選用） |

---

## 📦 打包與部署指南

### 🐍 PyPI 發布

```bash
# 建置
python -m build

# 上傳到 PyPI
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

### ⚙️ pre-commit 整合

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

## 🤝 貢獻指南

我們歡迎所有形式的貢獻！

### 📝 提交 PR

1. Fork 本儲存庫
2. 建立功能分支：`git checkout -b feature/amazing-feature`
3. 提交變更：`git commit -m 'feat: 新增新功能'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 提交 Pull Request

### 🐛 回報問題

請使用 [GitHub Issues](https://github.com/gitstq/ConfigLint/issues) 回報問題，包含：
- 問題描述
- 重現步驟
- 預期行為
- 實際行為
- 環境資訊

---

## 📄 開源授權說明

本專案採用 [MIT License](LICENSE) 開源授權。

```
MIT License - 自由使用、修改、散布
僅需保留版權聲明和授權條款副本
```

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq">gitstq</a>
</p>

<p align="center">
  如果這個專案對你有幫助，請給一個 ⭐ Star！
</p>
