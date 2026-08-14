# PCB 多層熱翹曲分析工作流程

依據 pcb-warpage-analysis 專業技能執行：
1. 讀取或確認 PCB 疊構參數（層數、總厚度、殘銅率、熱膨脹係數 CTE）。
2. 透過 SpaceClaim API 建立實體幾何與 Named Selection 邊界標記。
3. 計算並套用 Rule of Mixtures (ROM) 複合材料參數。
4. 施加 3-2-1 靜定無拘束支撐與回焊溫度載荷（如 260°C）。
5. 執行求解並輸出 Z 方向熱翹曲位移（Warpage Z-Displacement）分析圖表。
