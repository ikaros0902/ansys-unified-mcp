# ANSYS Mechanical 求解器設定與控制 (Analysis Setup) 指南

本手冊提供 ANSYS Mechanical 求解控制、大變形非線性開關、載荷副步（Substeps）自動步進控制、Newton-Raphson 收斂微調以及模態特徵值求解設定之標準 ACT 程式碼規範。

---

## 一、Analysis Settings 物件取得與基礎設定

求解控制參數集中於各分析系統的第一個子節點 `Analysis Settings`：

```python
analysis = Model.Analyses[0]
settings = analysis.Children[0]  # 或 ExtAPI.DataModel.GetObjectsByType(Ansys.ACT.Automation.Mechanical.AnalysisSettings)[0]
```

---

## 二、非線性靜態求解控制 (Nonlinear Controls)

當模型包含幾何大變形、狀態非線性（接觸開閉/滑移）或材料非線性（彈塑性/超彈性）時，必須配置非線性步進參數：

```python
# 1. 大變形效應開關 (Large Deflection)
# 若結構存在薄板彎曲、大撓度、轉動或屈曲預兆，必須開啟 True
settings.LargeDeflection = True

# 2. 多載荷步與自動副步控制 (Automatic Time Stepping)
settings.NumberOfSteps = 1  # 總步數
settings.AutomaticTimeStepping = Ansys.Mechanical.DataModel.Enums.AutomaticTimeStepping.On

# 設定時間副步細分 (以 Substeps 或 Time 形式):
# - 推薦非線性初始設定：初始副步 20、最小副步 10、最大副步 100
settings.DefineBy = Ansys.Mechanical.DataModel.Enums.TimeStepDefineByType.Substeps
settings.InitialSubsteps = 20
settings.MinimumSubsteps = 10
settings.MaximumSubsteps = 100

# 3. Newton-Raphson 迭代與線搜尋控制 (Line Search)
# 線搜尋 (Line Search) 能防止非線性迭代跳步發散
settings.NewtonRaphsonType = Ansys.Mechanical.DataModel.Enums.NewtonRaphsonType.Full
settings.LineSearch = Ansys.Mechanical.DataModel.Enums.LineSearchType.On

# 4. 數值穩定化 (Stabilization)
# 適用於薄殼挫曲、局部翻轉或接觸即將閉合前的輕微剛度奇異
settings.Stabilization = Ansys.Mechanical.DataModel.Enums.StabilizationType.Constant
settings.EnergyDissipationRatio = 0.001  # 控制阻尼耗能比 <= 0.1% 以免影響真實解
```

---

## 三、模態分析求解器設定 (Modal Analysis Controls)

模態分析用於提取無阻尼/小阻尼自由振動頻率與固有振型：

```python
modal_analysis = Model.Analyses[0]
modal_settings = modal_analysis.Children[0]

# 1. 指定提取固有頻率階數 (Max Modes to Find)
modal_settings.MaxModesToFind = 10  # 提取前 10 階模態

# 2. 搜尋頻率區間限制 (可選)
modal_settings.LimitSearchToRange = True
modal_settings.RangeMinimum = Quantity("10 [Hz]")
modal_settings.RangeMaximum = Quantity("5000 [Hz]")

# 3. 求解器演算法 (Block Lanczos 為實體結構最高效率演算法)
modal_settings.SolverType = Ansys.Mechanical.DataModel.Enums.SolverType.Direct

# 4. 預應力模態設定 (Pre-Stress Modal)
# 若模態系統連接上游 Static Structural，可開啟載荷硬化效應
```

---

## 四、求解結果儲存控制 (Output Controls)

為避免大型模型 RST 檔案膨脹，需合理配置結果輸出頻率與項目：

```python
# 儲存頻率控制：
# - StoreResultsAt: AllPoints (儲存所有副步，便於檢視歷程曲線)
# - StoreResultsAt: Last (僅儲存最後一刻，節省硬碟空間)
settings.StoreResultsAt = Ansys.Mechanical.DataModel.Enums.TimePointsOptions.AllPoints

# 輸出應變、應力與接觸數據
settings.GeneralMiscellaneous = True
settings.ContactData = True
```

---

## 五、執行求解與同步監控

在腳本中啟動求解運算，並可指定同步等待直到運算完成：

```python
print("開始求解分析系統 [{}]...".format(analysis.Name))

# analysis.Solve(True) 參數 True 代表同步阻塞等待，直到求解結束或報錯
analysis.Solve(True)

# 檢查求解狀態
solution = analysis.Solution
print("求解運算結束！狀態: {}".format(solution.Status))
```

---

## 六、MCP 工具對照

| ACT 原生 API | ANSYS MCP 工具 | 用途描述 |
|---|---|---|
| `analysis.Solve(True)` | `solve_analysis` | 啟動指定分析系統的求解運算 |
| `analysis.Solution.Status` | `get_solve_status` | 查詢求解進度與狀態 |
