---
name: act-extension-development
description: ANSYS ACT 擴充外掛開發、IronPython 限制、FileSystemWatcher 事件監聽與 Wizard API 自動化技能。
Use when:
  - 需開發或除錯 ANSYS ACT 外掛、XML 配置或 IronPython 2.7 腳本。
  - 需透過 FileSystemWatcher 實裝 Workbench 非同步檔案 IPC 監聽。
  - 需程式化調用既有加密之 ACT Wizard (`.wbex`)。
  - 觸發關鍵字 (繁中/En): ACT外掛, ACT開發, FileSystemWatcher, ACT Wizard, IronPython限制.
---

# ANSYS ACT 擴充外掛開發主控手冊

本技能提供 ANSYS ACT 外掛開發實務規範，涵蓋 IronPython 2.7 底層限制、跨環境（Workbench vs. Mechanical）通訊架構與 ACT Wizard 程式化調用。

---

## 一、核心開發 SOP

```mermaid
flowchart LR
    A[1. 定義 XML 介面與回呼] --> B[2. IronPython 腳本實作]
    B --> C[3. 避開 exec 閉包陷阱]
    C --> D[4. FileSystemWatcher 非同步通訊]
    D --> E[5. WPF Dispatcher 安全執行]
```

1. **環境隔離**：確認外掛運行於 Workbench（Project Schematic）或 Mechanical（Model Window），選用對應 API 上下文。
2. **IronPython 語法防禦**：避免在動態 `exec` 中使用閉包，類別與函式採頂層定義。
3. **IPC 通訊**：採用 .NET `FileSystemWatcher` 搭配 WPF Dispatcher，實現 0% CPU 佔用的安全非同步事件監聽。

---

## 二、模組路由表 (Module Router)

深入知識規劃外置於 `reference/`；下列手冊**尚未建立**，故以純文字列示，待實際撰寫後再恢復為連結。

| 主題分類 | 參考文件 | 狀態 | 核心內容 |
| :--- | :--- | :--- | :--- |
| **IronPython 2.7 陷阱** | `reference/ironpython_quirks.md` | 待建立 | `exec` 閉包限制、`__name__` 差異、`clr` 重複載入防護 |
| **非同步檔案監聽** | `reference/filesystemwatcher_pattern.md` | 待建立 | `FileSystemWatcher`、WPF Dispatcher 與去重鎖 |
| **Wizard 程式化呼叫** | `reference/wizard_api.md` | 待建立 | `ExtensionManager` 操作加密 `.wbex` 與 Component 刷新 |

> 實作參考可暫先查閱 `scripts/` 下的可執行範例。

---

## 三、絕對禁止事項 (Don'ts)

> [!CAUTION]
> 1. **嚴禁在 ACT 內嵌腳本與 XML 中撰寫中文註解**：
>    IronPython 2.7 對非 ASCII 字元處理脆弱，中文註解極易引發編碼崩潰。
> 2. **嚴禁在 FileSystemWatcher 背景執行緒直接呼叫 ExtAPI**：
>    跨執行緒調用 ANSYS COM/UI 物件會導致死鎖或記憶體存取違規，必須透過 WPF Dispatcher。
