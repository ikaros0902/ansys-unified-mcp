# -*- coding: utf-8 -*-
"""DPF product facade.

負責 ANSYS DPF (Data Processing Framework) 之 .rst 結果檔解析。

物理範圍切分：DPF 專注於 Mechanical 產出的隱式結構、模態、隨機振動與熱分析之
.rst 結果檔；LS-DYNA 顯式落摔結果走既有的 d3plot/glstat 專用解析管線，
不在此混雜（見 ansys_unified_mcp.drivers 中 LS-DYNA 相關實作）。

檔案鎖硬規則 (File Lock Guard)：DPF 只在作業終結後 (TERMINAL) 對檔案操作。
為防止與求解器爭搶檔案鎖，extract_structural_results 預設以「Sandbox 副本
模式 (sandbox_copy)」將 .rst 複製至獨立暫存目錄後才開啟讀取，讀取完成後
清理暫存副本。
"""

from __future__ import annotations

import logging
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Optional

logger = logging.getLogger("ansys-unified-mcp.dpf")

PRODUCT = "dpf"


class DPFController:
    """負責 DPF Model 開啟、指標抽取與沙盒防檔案鎖邏輯。"""

    def _make_sandbox_copy(self, source: Path) -> Path:
        """將來源檔複製至獨立暫存目錄，回傳副本路徑。"""
        sandbox_dir = Path(tempfile.gettempdir()) / "ansys_mcp_dpf_sandbox" / uuid.uuid4().hex
        sandbox_dir.mkdir(parents=True, exist_ok=True)
        dest = sandbox_dir / source.name
        shutil.copy2(source, dest)
        return dest

    def _cleanup_sandbox_copy(self, sandbox_path: Path) -> None:
        """清理沙盒副本所在的暫存目錄（盡力而為，不拋出例外）。"""
        try:
            shutil.rmtree(sandbox_path.parent, ignore_errors=True)
        except Exception:  # noqa: BLE001 - 清理失敗不應影響主流程結果
            pass

    def _resolve_read_path(
        self, rst_path: Path, copy_to_sandbox: bool, output_dir: Optional[Path]
    ) -> tuple[Path, Optional[Path]]:
        """決定實際讀取路徑。回傳 (read_path, sandbox_path_to_cleanup)。"""
        if not copy_to_sandbox:
            return rst_path, None
        if output_dir is not None:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            sandbox_dir = Path(tempfile.mkdtemp(prefix="ansys_mcp_dpf_", dir=output_dir))
            dest = sandbox_dir / rst_path.name
            shutil.copy2(rst_path, dest)
            return dest, dest
        sandbox_path = self._make_sandbox_copy(rst_path)
        return sandbox_path, sandbox_path

    def extract_structural_results(
        self,
        rst_path: str | Path,
        copy_to_sandbox: bool = True,
        output_dir: Optional[Path] = None,
    ) -> dict:
        """從 .rst 結果檔抽取關鍵結構化指標。

        Args:
            rst_path: .rst 結果檔路徑。
            copy_to_sandbox: True 時先複製至獨立暫存目錄再讀取，避免與求解器
                爭搶檔案鎖（預設 True，符合檔案鎖硬規則）。
            output_dir: 指定沙盒副本存放目錄；未指定則使用系統暫存目錄下的
                隨機子目錄。

        Returns:
            成功：{"ok": True, "metrics": {...}, "time_freq_sets": [...]}
            失敗：{"ok": False, "error": "..."}
        """
        source = Path(rst_path)
        if not source.exists():
            return {"ok": False, "error": f"RST file not found: {source}"}

        try:
            import importlib
            dpf = importlib.import_module("ansys.dpf.core")
        except ImportError:
            return {"ok": False, "error": "ansys-dpf-core not installed."}

        read_path, sandbox_path = self._resolve_read_path(source, copy_to_sandbox, output_dir)

        from ansys_unified_mcp.analytics.postprocessing.dpf_summary import extract_summary, release_streams

        model = None
        try:
            model = dpf.Model(str(read_path))
            mesh = model.metadata.meshed_region
            summary = extract_summary(model, dpf)
            return {
                "ok": True,
                "metrics": {
                    "num_nodes": int(mesh.nodes.n_nodes),
                    "num_elements": int(mesh.elements.n_elements),
                    "max_deformation": summary["displacement"]["total_max"],
                    "max_equivalent_stress": summary["stress_von_mises"]["max"],
                },
                "time_freq_sets": summary["time_freq_sets"],
                "results": summary,
            }
        except Exception as exc:  # noqa: BLE001 - 任何 DPF 解析例外一律優雅回傳
            return {"ok": False, "error": str(exc)}
        finally:
            release_streams(model)
            if sandbox_path is not None:
                self._cleanup_sandbox_copy(sandbox_path)

    def get_model_summary(self, rst_path: str | Path) -> dict:
        """回傳 .rst 結果檔的模型摘要（分析類型、單元/節點數、可用結果清單）。"""
        source = Path(rst_path)
        if not source.exists():
            return {"ok": False, "error": f"RST file not found: {source}"}

        try:
            import importlib
            dpf = importlib.import_module("ansys.dpf.core")
        except ImportError:
            return {"ok": False, "error": "ansys-dpf-core not installed."}

        from ansys_unified_mcp.analytics.postprocessing.dpf_summary import release_streams

        read_path, sandbox_path = self._resolve_read_path(source, True, None)
        model = None
        try:
            model = dpf.Model(str(read_path))
            mesh = model.metadata.meshed_region
            return {
                "ok": True,
                "summary": {
                    "num_nodes": int(mesh.nodes.n_nodes),
                    "num_elements": int(mesh.elements.n_elements),
                    "result_info": str(model.metadata.result_info),
                },
            }
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc)}
        finally:
            release_streams(model)
            if sandbox_path is not None:
                self._cleanup_sandbox_copy(sandbox_path)


controller = DPFController()
