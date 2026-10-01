---
name: pcb-warpage-analysis
description: PCB 多層疊構熱翹曲（Thermal Warpage）自動化分析專用技能。涵蓋 ROM 複合材料巨集、SpaceClaim 疊構建模、3-2-1 靜定支承熱應力求解與最佳相機構圖規範。
Use when:
  - 需進行 PCB 多層疊構熱翹曲模擬或 Rule of Mixtures (ROM) 等效材料常數推算。
  - 需自動化建立多層 PCB 實體幾何（啟用 Share Topology）並施加 3-2-1 靜定無熱應力支承。
  - 限制: 需配合疊構參數表與 ANSYS Mechanical 環境。
  - 觸發關鍵字 (繁中/En): PCB熱翹曲, PCB疊構, ROM材料計算, 3-2-1支承, PCB翹曲.
---

# PCB Multi-Layer Thermal Warpage Analysis Skill

本技能專門處理 PCB 多層板熱翹曲（Z 軸變形）自動化分析工作流（ANSYS SpaceClaim 疊構建模 + ROM 複合材料巨集 + Mechanical 3-2-1 靜定支承熱應力求解 + 最佳相機構圖雲圖導出）。

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
    G --> H[求解輸出 Z 軸翹曲變形雲圖 (最佳視角截圖)]
```

---

## 核心後處理規範 (Post-Processing Best Practices)

1. **嚴格聚焦 Z 軸方向位移 (Z-Directional Deformation Only)**：
   - 熱翹曲的核心指標為出平面撓度（Out-of-Plane Deflection, $U_z$）。
   - **嚴格禁用 / 移除 `Total Deformation`**：因三維總合向量疊加了面內熱膨脹位移（In-plane Expansion, $U_x, U_y$），會混淆真實翹曲拱度與淨翹曲量評估。
   - 必備監視項目：
     - `Z_Displacement_PCB_All_Layers`（全板穿透厚度方向）
     - `Z_Displacement_L01_Top_Face`（頂層外表面外凸值）
     - `Z_Displacement_L79_Bottom_Face`（底層支承面外凸值）

2. **相機構圖與視角最佳化規範 (Camera Framing & Sizing Standards)**：
   - 截圖時禁止使用隨機或未校正之視角，避免邊緣裁切或圖例遮擋。
   - **標準視角 A（2D 正投影俯視圖）**：
     - 視角設定：`cam.SetSpecificViewOrientation(ViewOrientationType.Front)`（朝向 XY 板面）。
     - 邊距調整：`cam.SetFit()` 搭配 `cam.Zoom(0.85)`，確保板面置中，左上圖例與下方標尺無任何重疊遮擋。
   - **標準視角 B（3D 擬真透視等角圖）**：
     - 視角設定：由 Front View 旋轉 `cam.Rotate(-28, CameraAxisType.ScreenX)` 與 `cam.Rotate(-25, CameraAxisType.ScreenY)`。
     - 邊距調整：`cam.SetFit()` 搭配 `cam.Zoom(0.82)`，完整呈現板厚實體層疊與出平面圓弧翹曲曲率。

---

## 核心腳本目錄
本技能目錄內建腳本 `./scripts/`（或專案根目錄 `scripts/pcb_warpage_analysis/`）：
1. `01_build_pcb_geometry.py`：SpaceClaim / Discovery 疊構幾何建模（支援 Share Topology）
2. `02_calculate_rom_materials.py`：ROM 等效材料計算與 APDL Macro 輸出
3. `03_setup_mechanical_bc_and_solution.py`：Mechanical 邊界條件設定、Z 軸專屬求解與相機構圖匯出函式
4. `run_full_warpage_workflow.py`：全自動化閉環批次執行腳本
