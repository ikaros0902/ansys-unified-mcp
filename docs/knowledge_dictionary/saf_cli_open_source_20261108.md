# SAF CLI 安裝與環境字典

依 Ansys 開源 SAF 儲存庫的 CLI 安裝指南整理。來源固定在提交 `96d59bd5b1e2b9075ac31cd1159a1f991748ff3a`，未從 `stable` 網址推定 SDK 版號。此頁為繁中改寫，保留指令與環境名稱。原文與授權見下方來源。

## 選擇安裝環境

| 詞項 | 說明 |
| --- | --- |
| SAF CLI | `ansys-saf-cli` 套件提供 `saf` 指令。安裝至基底 Python 可直接使用同一套 CLI。 |
| `.cli` | 官方指南建議用專用 Python 虛擬環境安裝 CLI，便於按專案或版本分開管理。啟用這個環境後即可使用 `saf` 指令。 |
| `.venv` | SAF CLI 為個別 solution 建立的虛擬環境。指南用 `.cli` 名稱區分 CLI 環境與 solution 的 `.venv`。 |

## 專用 CLI 環境的步驟

1. 用 `python -m venv .cli` 建立 CLI 專用環境。
2. 在 Windows PowerShell 執行 `.cli\Scripts\Activate.ps1` 啟用環境。在 Linux 或 macOS 執行 `source .cli/bin/activate`。
3. 在啟用的環境中執行 `pip install ansys-saf-cli`，再用 `saf --version` 檢查安裝。

Windows 的長路徑設定是來源列出的前置條件。上述是文件步驟，本次未安裝套件或執行指令。Python 版本矩陣、企業套件存取及部署行為仍須查各自的來源。

## 來源與授權

- 來源為 `doc/source/getting_started/prerequisites/saf_cli.rst`，Git blob `7033b85dba746435e88f31d213c84ce7b4c27b16`，SHA-256 `fcab4fd04314fd8e2e3f22defcc4e05800123ff30446e13a6f9f80d9925ce6d0`。[釘選原文](https://github.com/ansys/saf/blob/96d59bd5b1e2b9075ac31cd1159a1f991748ff3a/doc/source/getting_started/prerequisites/saf_cli.rst)
- 上游授權為 Apache License 2.0。此繁中版本改寫原文、將 reStructuredText 轉為 Markdown，省略網頁排版指令。適用範圍以該提交的儲存庫檔案為限。[授權原文](https://github.com/ansys/saf/blob/96d59bd5b1e2b9075ac31cd1159a1f991748ff3a/LICENSE)
