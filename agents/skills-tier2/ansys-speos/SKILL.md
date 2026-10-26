---
name: ansys-speos
description: Check Ansys Speos client, RPC, and illumination API workflows against the installed Speos product release. Use for Speos illumination and optical simulation; no live MCP connector is provided.
---

# Ansys Speos 與 Illumination

先辨識 Speos 版本與實際宿主（Speos client API、RPC、NX library 或 Lab automation），再讀相符 API 範例；不同宿主不得假設型別可互換。

核對光源光譜、材料、幾何／面向、偵測器、波長範圍及光線追跡設定。結果須附單位、量測區域與 solver 狀態。若 ray tracing 有隨機性，保留 seed 和 ray 數並以重複性評估差異，不以單次彩色圖判斷改善。

目前本 MCP 無 Speos controller。查閱來源及版本標記見 [領域來源矩陣](../../../docs/skills/DOMAIN_SOURCE_AND_SUPPORT.md)。


