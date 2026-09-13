---
name: ansys-submodeling-dpf
description: ANSYS DPF 高速結果場提取與局部子模型（Submodeling）自動化分析技能。涵蓋形函數空間座標插值、MAPDL 併發求解池與聖維南切面連續性驗證。
Use when:
  - 需使用 PyAnsys DPF (ansys.dpf.core) 高速讀取大型 RST/CAS 結果檔之位移場與等效應力場。
  - 需將粗網格全域模型位移透過有限元形函數 (on_coordinates) 插值至細緻子模型切面邊界。
  - 需透過 LocalMapdlPool 併發多進程求解多個局部細緻子模型。
  - 需依據聖維南原理 (Saint-Venant's Principle) 評估切面應力連續性誤差 (平均 <= 5%, 局部 <= 10%)。
  - 限制: 需安裝 ansys-dpf-core 與 ansys-mapdl-core。
  - 觸發關鍵字 (繁中/En): 子模型分析, Submodeling, DPF結果提取, on_coordinates, 形函數插值, LocalMapdlPool, 聖維南檢驗, 切面連續性.
---

# ANSYS DPF 高速結果場提取與子模型自動化主控手冊

本技能提供基於 ANSYS DPF 與 PyMAPDL 的先進子模型（Submodeling / Cut-Boundary Interpolation）自動化技術規範。

---

## 一、子模型核心分析 SOP

```mermaid
flowchart LR
    A[1. 全域模型求解<br>取得 global.rst] --> B[2. DPF 空間座標插值<br>on_coordinates 算子]
    B --> C[3. 施加切面約束<br>UX / UY / UZ]
    C --> D[4. MAPDL 求解子模型<br>可選併發求解池]
    D --> E[5. 聖維南連續性驗證<br>切面應力誤差 <= 10%]
```

1. **全域場提取**：以 DPF DataSources 記憶體直接映射串流讀取位移與應力場。
2. **形函數插值**：藉由單元形函數精準內插位移至子模型切面節點（保持力學連續性）。
3. **子模型求解**：導入切面邊界條件，於 MAPDL 或併發池 (`LocalMapdlPool`) 完成局部求解。
4. **邊界連續性檢核**：計算全域與子模型在切面邊界上的應力斷差，嚴格落實聖維南檢核。

---

## 二、模組路由表 (Module Router)

深入操作手冊與實作範例請參閱 `reference/` 與 `scripts/`：

| 分析主題 | 專精文件 | 核心內容 |
| :--- | :--- | :--- |
| **DPF 場提取與形函數插值** | [`reference/dpf_interpolation.md`](reference/dpf_interpolation.md) | 位移/應力算子、`on_coordinates` 向量場映射 |
| **MAPDL 併發求解池** | [`reference/mapdl_pool.md`](reference/mapdl_pool.md) | `LocalMapdlPool` 平行求解多個局部區域 |
| **聖維南連續性誤差驗證** | [`reference/saint_venant_validation.md`](reference/saint_venant_validation.md) | 切面相對誤差計算與自動判定放行標準 |
| **端到端完整管線腳本** | [`scripts/run_submodeling_pipeline.py`](scripts/run_submodeling_pipeline.py) | 提取 $\rightarrow$ 插值 $\rightarrow$ 求解 $\rightarrow$ 驗證全流程腳本 |

---

## 三、絕對禁止事項 (Don'ts)

> [!CAUTION]
> 1. **嚴禁在應力梯度劇烈處建立子模型切面**：
>    切面必須遠離幾何突變、載荷集中點與塑性區，確保切面應力誤差 $\le 10\%$，否則違反聖維南原理。
> 2. **嚴禁使用最近鄰（KNN）幾何距離替代有限元形函數插值**：
>    單純空間距離加權未考慮單元形函數彎曲與剪切連續性，會引發嚴重的人為虛假剛度。
