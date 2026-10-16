# 網格 Sizing 策略與品質工作流 (`sizing_strategy_and_quality_workflow.md`)

本手冊補充「怎麼選第一版網格策略、怎麼量化檢查品質」，與 `metrics_and_quality_standards.md`（指標數值門檻）、`mesh_methods_and_geometry_healing.md`（劃分方法與幾何修復）互補，不重複定義門檻數值。

---

## 一、Adaptive Sizing 當第一版網格

`Adaptive Sizing` 是通用自動化策略，`Resolution` 從 1（粗）到 7（細），`Defeature Size` 由演算法自動計算，適合當探索性的第一版網格，不保證是最適合特定模型的控制方式。

`Transition`（Fast / Slow）影響元素數量級：Slow（平滑過渡）比 Fast（快速過渡）可能讓節點與元素數量翻倍以上，需要在精度與計算成本之間取捨。先用 Fast 看分布，確認需要再切 Slow 精算。

## 二、Sizing Function：依幾何特徵自動加密

- **Curvature**：依曲率法向角決定邊與面的尺寸，適合圓孔、圓角等曲面特徵。
- **Proximity**：在窄縫、薄壁處確保跨間隙至少有指定數量的元素，避免薄壁方向網格過粗。
- 兩者的尺寸過渡都受 `Growth Rate` 控制（數值門檻見 `local_controls_and_washers.md`）。

## 三、Edge Sizing 的 Hard/Bias 覆蓋陷阱

`Soft`/`Hard` 行為的定義見 `local_controls_and_washers.md` 第一節，本節只補充該文件未提到的陷阱：

> [!WARNING]
> Hard 或帶 Bias 的邊，在與鄰近網格交界處可能出現突兀的尺寸跳躍，而且會覆蓋 `Max Face Size` 的全域設定。局部 Hard 設定前先確認鄰接面是否也需要對應調整，避免交界處產生畸變單元。

## 四、網格品質要量化檢查，不能只用眼睛看

量化檢查流程（搭配 `metrics_and_quality_standards.md` 的數值門檻）：

1. **Error Limits** 設為 `Aggressive Mechanical` 時，單元品質低於門檻會讓網格生成直接失敗（而不是生成後再警告），適合在前處理階段強制擋掉劣質網格。
2. 可設定 `Target Element Quality`，讓 tet mesher 主動改善最差的單元，而不是被動接受演算法預設結果。
3. `Mesh Metric` 直方圖可以點選特定區間，定位差單元的位置；`Display Style` 設為 `Element Quality` 可直接用顏色看出分布。
4. `Quality Worksheet` 可一次檢查 Aspect Ratio、Jacobian Ratio、Max Corner Angle 等多項指標；對失敗元素可右鍵選 `Show Contours`，或建立 Named Selection 方便後續追蹤與局部加密。

## 五、幾何前處理決定網格上限

很多網格品質問題其實出在幾何本身，不是網格設定：

- **Feature Detection + Feature Suppress**：例如用「Solid Fillet 半徑小於某閾值」的條件批次抓出小圓角並抑制，避免小特徵把全域網格尺寸拉得過細（進而拖垮 LS-DYNA CFL 步長，見 `ansys-lsdyna/references/mass_scaling_rules.md`）。
- **Virtual Topology**：合併碎面、碎邊，讓 mesher 不必受原始 CAD 切面邊界限制，是 `mesh_methods_and_geometry_healing.md` 中 Virtual Topology 的操作動機補充。

## 六、方法選擇的經驗法則

結構簡單、可掃掠的區段適合用 Sweep/Hex；複雜有機區域交給 Tet 或自動方法。把模型先分區、各區用適合的方法，通常比單一方法套用整個模型更有效率（方法細節見 `mesh_methods_and_geometry_healing.md`）。

## 七、網格收斂與下游資料品質（交叉引用）

`Resolution` 與 `Transition` 可當作網格收斂研究的控制參數，用來系統性比較結果對網格密度的敏感度；若要訓練 surrogate / 代理模型，資料篩選門檻屬 `ansys-optislang` 的職責範圍（見 `ansys-optislang/references/mop_metamodel.md`），本檔不展開。
