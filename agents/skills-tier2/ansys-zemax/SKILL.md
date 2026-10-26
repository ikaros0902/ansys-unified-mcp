---
name: ansys-zemax
description: Plan or review OpticStudio automation through the version-matched ZOS-API and Zemax examples. Use for Zemax optical design and analysis; this skill does not provide a live MCP connector.
---

# Zemax OpticStudio／ZOS-API

API 寫作前確認 OpticStudio 與 ZOS-API release、連線方式（既有 OpticStudio extension 或由 API 建立新 instance）、license 與使用者選擇的 lens file。另存輸入副本再修改，先讀回系統設定，才執行 merit function、ray trace 或 optimization。

比較光學結果時鎖定 wavelength、field、aperture、configuration、analysis settings 及 merit-function operand。記錄 ray／analysis 設定、實際輸入檔及輸出量值，不混用序列與 NSC 的資料範圍。ZOSPy 屬可選 Python 封裝，須依目標版本確認，不能取代 API 文件。

目前本 MCP 無 Zemax／ZOS-API controller；只提供產品文件路由。參考目錄見 [領域來源矩陣](../../../docs/skills/DOMAIN_SOURCE_AND_SUPPORT.md)。


