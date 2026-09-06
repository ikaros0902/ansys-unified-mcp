"""ANSYS Unified MCP 2.0 - 高階工程工況工作流套件 (Workflows Package).

匯出 Workbench 原生拓撲直通單元鏈結引擎與 5 大高階意圖工作流：
- WorkbenchCellLinkEngine: Workbench RunWB2 Journal 原生單元鏈結引擎 (TransferData)
- run_drop_test: 電子產品落摔衝擊工作流 (LS-DYNA 顯式動力學閉環)
- run_shock_analysis: 衝擊響應與反應譜工作流 (半正弦/梯形波)
- run_random_vibration: 隨機振動工作流 (PSD 頻響與三向有效模態質量 >= 90% 硬性閘門)
- run_thermal_warpage: PCB / 封裝熱翹曲工作流 (熱-結構直通、CTE/T_ref 閘門、3-2-1 靜定支承)
- train_surrogate_model: optiSLang 參數化尋優與 MOP 代理模型工作流 (CoP 評估)
"""

from ansys_unified_mcp.workflows.drop_test import run_drop_test
from ansys_unified_mcp.workflows.random_vibration import run_random_vibration
from ansys_unified_mcp.workflows.shock_analysis import run_shock_analysis
from ansys_unified_mcp.workflows.surrogate_model import train_surrogate_model
from ansys_unified_mcp.workflows.thermal_warpage import run_thermal_warpage
from ansys_unified_mcp.workflows.workbench_links import WorkbenchCellLinkEngine

__all__ = [
    "WorkbenchCellLinkEngine",
    "run_drop_test",
    "run_shock_analysis",
    "run_random_vibration",
    "run_thermal_warpage",
    "train_surrogate_model",
]