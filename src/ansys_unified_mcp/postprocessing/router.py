"""ANSYS Unified MCP 2.0 - 後處理路由分發器 (PostprocessingRouter).

根據模擬工況類型 (workflow_type) 動態派發適配之後處理讀取器：
- 隱式結構 (Static/Transient)、模態 (Modal)、隨機振動 (Random Vibration)、熱翹曲 (Thermal Warpage) -> DPFSandboxReader (.rst)
- 顯式動力學落摔衝擊 (Drop Test)、衝擊響應 (Shock Analysis) -> LSDynaExplicitReader (glstat/d3plot)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Set, Union

from ansys_unified_mcp.postprocessing.base import BaseResultReader
from ansys_unified_mcp.postprocessing.dpf_reader import DPFSandboxReader
from ansys_unified_mcp.postprocessing.explicit_reader import LSDynaExplicitReader

logger = logging.getLogger(__name__)


class PostprocessingRouter:
    """後處理結果讀取路由分發器。"""

    EXPLICIT_WORKFLOWS: Set[str] = {
        "drop_test",
        "shock_analysis",
        "shock",
        "lsdyna",
        "lsdyna_explicit",
        "explicit",
        "explicit_dynamics",
    }

    IMPLICIT_WORKFLOWS: Set[str] = {
        "static_structural",
        "transient_structural",
        "modal",
        "modal_analysis",
        "random_vibration",
        "thermal_warpage",
        "steady_state_thermal",
        "transient_thermal",
        "implicit",
        "structural",
    }

    def __init__(
        self,
        dpf_reader: Optional[BaseResultReader] = None,
        explicit_reader: Optional[BaseResultReader] = None,
    ) -> None:
        """初始化後處理路由器，支援自訂讀取器實例注入。"""
        self.dpf_reader = dpf_reader or DPFSandboxReader()
        self.explicit_reader = explicit_reader or LSDynaExplicitReader()

    def get_reader(self, workflow_type: str) -> BaseResultReader:
        """依據工作流名稱獲取專屬之結果讀取器。

        Args:
            workflow_type: 工況類型名稱（不區分大小寫）。

        Returns:
            BaseResultReader: DPFSandboxReader 或 LSDynaExplicitReader 實例。
        """
        wf_norm = str(workflow_type).lower().strip().replace("-", "_")

        # 優先比對顯式動力學
        if wf_norm in self.EXPLICIT_WORKFLOWS:
            return self.explicit_reader
        for exp_kw in ("drop", "shock", "lsdyna", "explicit"):
            if exp_kw in wf_norm:
                return self.explicit_reader

        # 其餘隱式、模態、振動、熱翹曲皆路由至 DPF
        return self.dpf_reader

    route = get_reader  # 別名相容

    def read_results(
        self,
        workflow_type: str,
        job_dir: Union[Path, str],
        allow_synthetic: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """自動路由並執行結果讀取。

        Args:
            workflow_type: 工況類型名稱。
            job_dir: 作業沙盒目錄。
            allow_synthetic: 是否允許合成指標回退。
            **kwargs: 傳遞予具體讀取器之額外參數。

        Returns:
            Dict[str, Any]: 讀取之結果指標字典。
        """
        reader = self.get_reader(workflow_type)
        return reader.read_results(job_dir, allow_synthetic=allow_synthetic, **kwargs)

    route_and_read = read_results  # 別名相容
