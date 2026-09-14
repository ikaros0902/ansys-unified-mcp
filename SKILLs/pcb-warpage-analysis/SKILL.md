---
name: pcb-warpage-analysis
description: PCB 多層疊構熱翹曲（Thermal Warpage）自動化分析專用技能。涵蓋 ROM 複合材料巨集、SpaceClaim 疊構建模與 3-2-1 靜定支承熱應力求解。
Use when:
  - 需進行 PCB 多層疊構熱翹曲模擬或 Rule of Mixtures (ROM) 等效材料常數推算。
  - 需自動化建立多層 PCB 實體幾何（啟用 Share Topology）並施加 3-2-1 靜定無熱應力支承。
  - 限制: 需配合疊構參數表與 ANSYS Mechanical 環境。
  - 觸發關鍵字 (繁中/En): PCB熱翹曲, PCB疊構, ROM材料計算, 3-2-1支承, PCB翹曲.
---

# PCB Multi-Layer Thermal Warpage Analysis Skill

本技能專門處理 PCB 多層板熱翹曲（Z 軸變形）自動化分析工作流（ANSYS SpaceClaim 疊構建模 + ROM 複合材料巨集 + Mechanical 3-2-1 靜定支承熱應力求解）。

---

## 工作流架構

```mermaid
flowchart TD
    A[MCP_Test.xlsx 疊構參數] --> B[01_build_pcb_geometry.py 疊構建模]
    A --> C[02_calculate_rom_materials.py ROM 材料計算]
    B --> D[SpaceClaim: 79 Solid Bodies + Share Topology]
    C --> E[APDL Macro: apdl_rom_materials.mac]
    D --> F[03_setup_mechanical_bc_and_solution.py]
    E --> F
    F --> G[ANSYS Mechanical: MultiZone 網格 + 3-2-1 支承 + 220°C 熱載荷]
    G --> H[求解輸出 Z 軸翹曲變形雲圖]
```

## 核心腳本目錄
本技能目錄內建腳本 `./scripts/`（或專案根目錄 `scripts/pcb_warpage_analysis/`）：
1. `01_build_pcb_geometry.py`：SpaceClaim / Discovery 疊構幾何建模
2. `02_calculate_rom_materials.py`：ROM 等效材料計算與 APDL Macro 輸出
3. `03_setup_mechanical_bc_and_solution.py`：Mechanical 邊界條件設定與求解
4. `run_full_warpage_workflow.py`：全自動化閉環批次執行腳本
