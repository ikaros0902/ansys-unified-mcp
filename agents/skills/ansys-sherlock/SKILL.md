---
name: ansys-sherlock
description: Find and interpret version-matched Ansys Sherlock documentation and API references for PCB reliability workflows. Use for Sherlock reliability analysis; this knowledge skill does not establish a live MCP connector.
---

# Ansys Sherlock 文件與 API 路由

Sherlock 的 PCB 可靠度模型、材料／製程輸入和結果解讀屬於獨立產品範圍。先確認產品版本、可用介面與輸入檔，再查對應 API；不要把 Mechanical 或 optiSLang 的物件模型假設成 Sherlock API。

## 查證流程

1. 以 `D:\Ikaros\ACT_Test\3.documents\Sherlock\api_reference\sherlock-apis-2026-r1\` 的 `sherlock-reference.md` 與 `index.md` 查型別／方法，確認來源頁中的完整名稱。
2. 找到 API 條目後再查看使用者任務所需的 Sherlock workflow guide／sample；只有 stub 或目錄時標註資訊不足。
3. 記錄 build、API 版本、使用宿主、輸入檔和輸出結果；先唯讀檢查材料／stackup／載入，再取得明確授權才修改或執行可靠度分析。
4. 不因 API 文件存在而宣稱 MCP 連線可用。MCP 尚無 Sherlock product controller；本 skill 僅提供文件路由和支援界線。

## 來源限制

本機已盤點的 API 文件版本為 2026 R1；其內容不構成 v251／v252 相容證明。版本未明或文件條目未提供簽名時，將結果標為未知／部分核對。

完整來源清單見 [領域來源矩陣](../../../docs/skills/DOMAIN_SOURCE_AND_SUPPORT.md)。


