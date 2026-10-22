---
name: ansys-optical-engineering
description: Route ANSYS Speos/Illumination, Zemax OpticStudio, and Lumerical optical design tasks to the product-specific API and physical result references. Use for optical simulations; this skill does not provide a live connector.
---

# 光學工程產品路由

先辨識產品與物理問題，再載入該產品 references。Speos、Zemax／OpticStudio、Lumerical 對光源、材料、量測器、頻譜、結果量值及自動化介面有不同定義；不可混用 API。

## 產品分流

| 任務 | 路由 |
|---|---|
| 系統照明、光線追跡、照度／輝度或照明設備 | [`ansys-speos`](../ansys-speos/SKILL.md) |
| OpticStudio 序列／非序列系統、ZOS-API、容差或最佳化 | [`ansys-zemax`](../ansys-zemax/SKILL.md) |
| FDTD／MODE／INTERCONNECT 等光子模擬 | [`ansys-lumerical`](../ansys-lumerical/SKILL.md) |

## 通用檢核

先記錄波長與單位、光源／monitor、材料與色散模型、邊界、網格、隨機 ray count／seed（若適用）、輸入檔 hash 及產品版本。比較結果時固定 FoV／視場、分析區域和量測定義；不以畫面顏色或不同 monitor 定義的數值做等價判定。

本 MCP 尚未註冊以上光學產品 controller；skill 僅供文件／API 對照，不宣稱可啟動 GUI、連線或求解。來源狀態見 [領域來源矩陣](../../../docs/skills/DOMAIN_SOURCE_AND_SUPPORT.md)。


