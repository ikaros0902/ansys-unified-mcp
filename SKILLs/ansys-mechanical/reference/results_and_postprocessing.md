# ANSYS Mechanical 結果後處理與雲圖導出 (Results & Post-processing) 指南

本手冊提供應力、應變、變形量結果物件新增、極值數值提取、無頭環境高解析度白底雲圖導出以及 DPF 高速結果場資料流式讀取之標準 ACT 程式碼規範。

---

## 一、新增常用結果評估物件

所有後處理結果物件均建立在 `Analysis.Solution` 下：

```python
analysis = Model.Analyses[0]
solution = analysis.Solution

# 1. 總變形量 (Total Deformation)
total_disp = solution.AddTotalDeformation()
total_disp.Name = "總變形量合量"

# 2. 定向位移 (Directional Deformation - 如垂直方向 Y 軸沉陷)
dir_disp_y = solution.AddDirectionalDeformation()
dir_disp_y.Name = "Y軸垂直位移"
dir_disp_y.NormalOrientation = Ansys.Mechanical.DataModel.Enums.NormalOrientationType.YAxis

# 3. 等效應力 (Equivalent von-Mises Stress)
von_mises = solution.AddEquivalentStress()
von_mises.Name = "Von-Mises 等效應力"

# 4. 最大主應力 (Maximum Principal Stress - 脆性材料評估)
max_principal = solution.AddMaximumPrincipalStress()
max_principal.Name = "第一主應力 (拉應力)"

# 5. 安全係數工具 (Stress Tool / Safety Factor)
stress_tool = solution.AddStressTool()
stress_tool.Theory = Ansys.Mechanical.DataModel.Enums.StressToolTheoryType.MaxEquivalentStress
safety_factor = stress_tool.AddSafetyFactor()
safety_factor.Name = "降伏安全係數"
```

---

## 二、結果計算與極值數據提取

```python
# 執行所有結果計算評估
solution.EvaluateAllResults()

# 讀取特定結果之極值數據 (傳回帶有單位的 Quantity 物件)
print("=== 求解極值摘要 ===")
print("最大總變形量: {} ({})".format(total_disp.Maximum.Value, total_disp.Maximum.Unit))
print("最小總變形量: {} ({})".format(total_disp.Minimum.Value, total_disp.Minimum.Unit))
print("最高等效應力: {:.2f} MPa".format(von_mises.Maximum.Value / 1e6))
print("最低安全係數: {:.2f}".format(safety_factor.Minimum.Value))
```

---

## 三、無頭環境高解析度白底雲圖批次導出 (Headless Image Export)

在批次執行或無介面伺服器環境中，可使用 `Graphics.ExportImage` 輸出符合技術報告要求的白底高畫質圖檔：

```python
import os

def export_solution_images(solution, output_dir, width=1920, height=1080):
    """
    批次遍歷 Solution 下所有結果物件並輸出白底等角視圖 PNG。
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    settings = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
    settings.Resolution = GraphicsResolutionType.NormalResolution
    settings.Background = GraphicsBackgroundType.White  # 強制白底排版
    settings.Width = width
    settings.Height = height
    
    for result in solution.Children:
        if hasattr(result, "Activate") and hasattr(result, "PlotData"):
            try:
                # 啟動並在圖形視窗聚焦該結果雲圖
                result.Activate()
                
                # 設定等角視圖並全幅縮放適應畫面
                Graphics.Camera.SetSpecificViewOrientation(ViewOrientationType.Iso)
                Graphics.Camera.SetFit()
                
                # 檔案命名與導出
                clean_name = result.Name.replace(" ", "_").replace("/", "_").replace("=", "_")
                img_path = os.path.join(output_dir, "{}.png".format(clean_name))
                
                Graphics.ExportImage(img_path, GraphicsImageExportFormat.PNG, settings)
                print("成功導出雲圖: {}".format(img_path))
            except Exception as e:
                print("雲圖導出失敗 [{}]: {}".format(result.Name, str(e)))

# 調用範例:
# export_solution_images(solution, "C:/Simulations/ExportedImages")
```

---

## 四、DPF 高速結果場流式讀取 (PyAnsys DPF Core)

當分析模型高達數百萬節點時，透過外部 Python 使用 `ansys-dpf-core` 讀取 RST 結果檔，比 GUI 提取速度快 20~50 倍：

```python
import os
from ansys.dpf import core as dpf

def extract_dpf_results_summary(rst_path):
    """使用 DPF 提取 RST 位移場與應力場極值。"""
    if not os.path.exists(rst_path):
        raise FileNotFoundError("找不到 RST 檔案: {}".format(rst_path))
        
    ds = dpf.DataSources(rst_path)
    model = dpf.Model(ds)
    
    # 提取位移場合量極值
    disp_op = dpf.operators.result.displacement(data_sources=ds)
    norm_op = dpf.operators.math.norm_fc(fields_container=disp_op.outputs.fields_container())
    max_disp = max(norm_op.outputs.fields_container()[0].data)
    
    # 提取節點平均 Von-Mises 應力極值
    vm_op = dpf.operators.result.stress_von_mises(
        data_sources=ds,
        requested_location=dpf.locations.nodal
    )
    max_stress_pa = max(vm_op.outputs.fields_container()[0].data)
    
    print("DPF 提取成功: 最大位移={:.6e} m, 最大應力={:.2f} MPa".format(
        max_disp, max_stress_pa / 1e6
    ))
    return {"max_displacement_m": max_disp, "max_stress_mpa": max_stress_pa / 1e6}
```

---

## 五、MCP 工具對照

| ACT 原生 API | ANSYS MCP 工具 | 用途描述 |
|---|---|---|
| `solution.AddTotalDeformation()` | `add_total_deformation` | 新增總變形量結果物件 |
| `solution.AddEquivalentStress()` | `add_equivalent_stress` | 新增等效 von-Mises 應力結果物件 |
| `solution.EvaluateAllResults()` | `run_mechanical_script` | 觸發所有結果物件重新評估 |
