---
name: ansys-geometry-meshing
description: Domain router for CAD preparation, defeaturing, mid-surfacing, and mesh generation. Use for SpaceClaim geometry cleanup, BGA array geometry, defeaturing, PrimeMesh, or DPF. DO NOT use for solver numerical setup or post-processing.
---

# ANSYS 幾何前處理、去特徵與網格劃分主控 (Domain 09)

本技能為 ANSYS 領域路由 核心領域主控路由器，專責解析特定物理需求並將 Agent 零損耗導流至專項 模組技能 專業求解器或子工作流。

## 核心工作流 (Core Workflow)

1. 導入原始工程 CAD 幾何（STEP, Parasolid, IGES, SCDOC）
2. 幾何拓撲缺陷診斷（自相交面、微小碎邊面、非流形幾何檢查）
3. 執行幾何簡化（特徵去除、小孔/倒角修復、薄壁件抽取中面 Midsurface）
4. 建立共享共形拓撲（Share Topology）或組裝包圍盒 (Enclosure)
5. 路由並載入對應 模組技能 幾何或網格劃分技能（SpaceClaim, Ansys Mesh）
6. 施加網格局部尺寸控制、邊界層膨脹層（Inflation）與幾何自適應劃分
7. 驗證網格品質指標（正交度 > 0.15, 畸變率 < 0.85, 長寬比 < 20）

## 模組技能 專業子技能路由表 (Sub-Skill Router Table)

| 物理任務與工程場景 | 目標學科模組 | 深入研讀之 模組技能 指針 |
|---|---|---|
| CAD 幾何前處理、模型簡化、去特徵、抽取中面、SpaceClaim API | 模組技能 SpaceClaim | `../../geometry-meshing/ansys-spaceclaim/SKILL.md` |
| 結構與流體網格劃分、邊界層膨脹層、六面體/多面體核心網格 | 模組技能 Ansys Mesh | `../../geometry-meshing/ansys-mesh/SKILL.md` |
| BGA 錫球、焊盤與陣列 CAD 建模 | 模組技能 SpaceClaim | `../../geometry-meshing/ansys-spaceclaim/SKILL.md`（`geometry_create_bga_array`；尺寸參數為 mm） |
| 大數據量網格後處理、截面提取與場數據操作 (DPF) | 模組技能 DPF | `../../structural-mechanics/ansys-submodeling-dpf/SKILL.md` |

## 官方文檔與 APIKB 動態查詢強制令

在生成或修改任何數值模擬腳本之前，**必須**優先透過 MCP 查詢底層確切 API 簽名與參數：
- 使用 `search_ansys_docs(query='...')` 檢索該學科之官方手冊規範
- 使用 `api_search(query='...', product='spaceclaim')` 驗證 Python / ACT 符號之完整路徑
- 嚴禁憑空猜測非公開屬性或使用已廢棄之語法

## 關鍵禁止事項 (Critical Don'ts)

- 嚴禁在流體/熱傳多體裝配體中未共享拓撲即進行網格劃分（導致界面不共形）。
- 嚴禁放行包含負體積單元或正交度低於 0.05 的劣質網格進入求解器。
- 嚴禁在薄壁鈑金結構中強行使用粗糙實體四面體單元（應抽取中面使用殼單元）。
