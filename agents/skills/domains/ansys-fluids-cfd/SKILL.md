---
name: ansys-fluids-cfd
description: Domain router for computational fluid dynamics (CFD), aerodynamic, multiphase, and turbomachinery simulation. Use when simulating fluid flow, turbulence, pressure drop, mixing, or aerodynamics. DO NOT use for structural solid mechanics.
---

# ANSYS 計算流體力學與空氣動力學主控 (Domain 02)

本技能為 ANSYS 領域路由 核心領域主控路由器，專責解析特定物理需求並將 Agent 零損耗導流至專項 模組技能 專業求解器或子工作流。

## 核心工作流 (Core Workflow)

1. 辨識流動物理形態（不可壓/可壓、層流/湍流、單相/多相、旋轉機械）
2. 路由並載入對應 模組技能 CFD 專業求解器技能（Fluent, CFX, Polyflow/Icing）
3. 檢核流體計算域拓撲、壁面邊界層 y+ 網格精度與流向過渡比
4. 配置流體物理屬性、狀態方程與湍流模型（k-epsilon, SST k-omega, LES）
5. 設定邊界條件（速度/質量入口、靜壓出口、對稱面、旋轉壁面）
6. 提交求解器並監控動量、連續性與能量方程殘差曲線及物理量監控點
7. 提取總壓降、阻力係數、速度場切片、流線雲圖與漩渦結構

## 模組技能 專業子技能路由表 (Sub-Skill Router Table)

| 物理任務與工程場景 | 目標學科模組 | 深入研讀之 模組技能 指針 |
|---|---|---|
| 通用 CFD、外氣動、多相流、燃燒化學反應 | 模組技能 Fluent | `../../fluids-cfd/ansys-fluent/SKILL.md` |
| 葉輪旋轉機械、水泵、風機、渦輪機械 (CCL) | 模組技能 CFX | `../../fluids-cfd/ansys-cfx/SKILL.md` |
| 聚合物擠出成型、吹塑、飛機結冰 (FENSAP-ICE) | 模組技能 Polyflow/Icing | `../../fluids-cfd/ansys-polyflow-icing/SKILL.md` |

## 官方文檔與 APIKB 動態查詢強制令

在生成或修改任何數值模擬腳本之前，**必須**優先透過 MCP 查詢底層確切 API 簽名與參數：
- 使用 `search_ansys_docs(query='...')` 檢索該學科之官方手冊規範
- 使用 `api_search(pattern='...')` 驗證 Python / ACT 符號之完整路徑
- 嚴禁憑空猜測非公開屬性或使用已廢棄之語法

## 關鍵禁止事項 (Critical Don'ts)

- 嚴禁使用粗糙壁面網格搭配低 Reynolds 數壁面解析湍流模型（SST 模型壁面第一層 y+ 不得大於 5）。
- 嚴禁在未監控物理通量守恆（進出口質量守恆誤差 < 0.1%）時單憑殘差下降判定收斂。
- 嚴禁在可壓縮跨音速/超音速流場中使用不可壓縮壓力基求解器。
