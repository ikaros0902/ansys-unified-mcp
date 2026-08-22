---
name: pcb-warpage-analysis
description: PCB 多層疊構熱翹曲（Thermal Warpage）自動化分析專用技能。
Use when:
- The user requests PCB multi-layer stackup thermal warpage simulation, Rule of Mixtures (ROM) composite material calculation (E, CTE, Poisson ratio).
- Building 79-layer (or multi-layer) PCB stackup solid bodies from Excel (e.g. MCP_Test.xlsx) with Share Topology enabled.
- Setting up ANSYS Mechanical MultiZone meshing, 3-2-1 statically determinate support (to prevent rigid body motion without artificial thermal stress), thermal boundary loads, and Z-axis warpage displacement contours.
- Trigger keywords (繁中/En): PCB熱翹曲, PCB疊構, PCB堆疊, ROM材料計算, 3-2-1支承, 熱翹曲分析, PCB翹曲, PCB熱應力, 複合材料ROM.
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
`F:\Ming_python\ansys-unified-mcp\scripts\pcb_warpage_analysis\`
1. `01_build_pcb_geometry.py`
2. `02_calculate_rom_materials.py`
3. `03_setup_mechanical_bc_and_solution.py`
4. `run_full_warpage_workflow.py`
