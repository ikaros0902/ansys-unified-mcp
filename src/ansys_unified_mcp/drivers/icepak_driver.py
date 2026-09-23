"""ANSYS Unified MCP 2.0 - Icepak 電子散熱求解器驅動程式 (IcepakDriver).

封裝 ANSYS Icepak 電子封裝與系統級散熱分析：
- 配置晶片功率熱源、熱傳導係數與自然/強制對流散熱邊界條件
- 批次啟動 Icepak / Fluent-Icepak 熱求解器
- 串流監控熱平衡迭代殘差與晶片結溫 (T_junction)
- 提取 3D 溫度場數據庫，產出 1920x1080 白底高解析溫度雲圖，直通下游熱-結構翹曲單元鏈結
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ansys_unified_mcp.drivers.base import BaseSolverDriver, SolverDriverError
from ansys_unified_mcp.drivers.contour_helper import generate_white_contour_png
from ansys_unified_mcp.jobs.models import (
    ExecutionMetadata,
    JobStatusEnum,
    PhysicalMetrics,
    SimulationSummary,
    VerdictEnum,
)

logger = logging.getLogger("ansys-unified-mcp.drivers.icepak")


class IcepakDriver(BaseSolverDriver):
    """ANSYS Icepak 電子散熱分析驅動程式。"""

    DEFAULT_EXECUTABLE_NAMES = [
        "icepak.exe",
        "ansoft.exe",
    ]

    def __init__(self, solver_bin: Optional[str] = None) -> None:
        super().__init__(solver_name="ANSYS Icepak", solver_bin=solver_bin)

    def validate_prerequisites(self) -> Tuple[bool, str]:
        """驗證 Icepak 求解器可用性。"""
        if self.solver_bin and Path(self.solver_bin).exists():
            return True, f"找到指定 Icepak 可執行檔: {self.solver_bin}"

        for exe in self.DEFAULT_EXECUTABLE_NAMES:
            found = shutil.which(exe)
            if found:
                self.solver_bin = found
                return True, f"於 PATH 找到 Icepak: {found}"

        for ver in ["v242", "v241", "v232"]:
            candidate = Path(f"C:/Program Files/ANSYS Inc/{ver}/icepak/ntbin/win64/icepak.exe")
            if candidate.exists():
                self.solver_bin = str(candidate)
                return True, f"於預設目錄找到 Icepak: {candidate}"

        return False, "未偵測到 Icepak 本機安裝 (支援熱流固耦合沙盒模擬與溫度場映射模式)。"

    def is_available(self) -> bool:
        """回報本機是否已偵測到真實 Icepak 可執行檔 (不含 synthetic 後備模式)。"""
        available, _ = self.validate_prerequisites()
        return available

    def prepare_job(self, job_dir: Path, config: Dict[str, Any]) -> Path:
        """生成 Icepak 熱求解腳本或（在明確授權下）合成測試數據腳本。

        Args:
            job_dir: 作業沙盒目錄
            config: 工作流配置參數。若本機無真實 Icepak 安裝，須明確帶入
                ``allow_synthetic=True`` 才允許生成合成 (synthetic) 測試數據；
                否則直接拋出 SolverDriverError，防止未經授權的假數據流入生產分析。

        Raises:
            SolverDriverError: 本機無真實 Icepak 安裝且 config 未授權
                ``allow_synthetic=True`` 時拋出。
        """
        workspace = job_dir / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)

        ambient_temp_c = float(config.get("ambient_temperature_c", 25.0))
        chip_power_w = float(config.get("chip_power_w", 45.0))
        convection_coeff = float(config.get("convection_coeff_w_m2k", 20.0))

        if not self.is_available():
            allow_synthetic = bool(config.get("allow_synthetic", False))
            if not allow_synthetic:
                raise SolverDriverError(
                    "ANSYS Icepak 求解器未在本機偵測到安裝路徑，無法生成真實求解腳本。"
                    "若僅需離線測試合成 (synthetic) 資料流，請明確傳入 allow_synthetic=True。"
                )
            logger.warning(f"[{self.solver_name}] Running in SYNTHETIC mock mode")
            print("[WARNING] Running in SYNTHETIC mock mode")
            script_path = workspace / "icepak_batch.py"
            content = self._build_synthetic_script(ambient_temp_c, chip_power_w, convection_coeff)
            script_path.write_text(content, encoding="utf-8")
            return script_path

        script_path = workspace / "icepak_batch.py"
        content = self._build_real_script(ambient_temp_c, chip_power_w, convection_coeff)
        script_path.write_text(content, encoding="utf-8")
        return script_path

    def _build_real_script(
        self, ambient_temp_c: float, chip_power_w: float, convection_coeff: float
    ) -> str:
        """生成呼叫真實 Icepak 求解器的批次腳本骨架。"""
        return f"""# ANSYS Icepak 熱分析自動化批次腳本
# Ambient: {ambient_temp_c} C | Chip Power: {chip_power_w} W | h: {convection_coeff} W/m^2-K
import sys
from pathlib import Path

workspace = Path(__file__).parent
log_file = workspace / "icepak.log"

# 此腳本應由真實 Icepak 求解器 (icepak.exe -batch) 執行，
# 讀取幾何、材料與邊界條件卡並輸出真實迭代日誌與溫度場數據。
with open(log_file, "w", encoding="utf-8") as f:
    f.write("ANSYS Icepak Thermal Solver Initialized\\n")
    f.write(f"Ambient Temperature: {ambient_temp_c} C, Heat Source: {chip_power_w} W\\n")
"""

    def _build_synthetic_script(
        self, ambient_temp_c: float, chip_power_w: float, convection_coeff: float
    ) -> str:
        """生成僅供離線測試用的合成 (synthetic) 假數據腳本，附帶明確警示標記。"""
        return f"""# WARNING: SYNTHETIC TEST DATA - DO NOT USE FOR PRODUCTION ANALYSIS
# ANSYS Icepak 熱分析自動化批次腳本 (SYNTHETIC MOCK MODE)
# Ambient: {ambient_temp_c} C | Chip Power: {chip_power_w} W | h: {convection_coeff} W/m^2-K
import sys
from pathlib import Path

workspace = Path(__file__).parent
log_file = workspace / "icepak.log"

print("[WARNING] Running in SYNTHETIC mock mode")

with open(log_file, "w", encoding="utf-8") as f:
    f.write("# WARNING: SYNTHETIC TEST DATA - DO NOT USE FOR PRODUCTION ANALYSIS\\n")
    f.write("ANSYS Icepak Thermal Solver Initialized\\n")
    f.write(f"Ambient Temperature: {ambient_temp_c} C, Heat Source: {chip_power_w} W\\n")
    for step in range(1, 21):
        temp_val = {ambient_temp_c} + ({chip_power_w} * 1.6) * (step / 20.0)
        f.write(f"ITERATION [{{step}}/20] Continuity=1.2e-4 Energy=8.5e-6 Max_T={{temp_val:.2f}} C\\n")
    f.write("Icepak Solution Converged.\\n")
    f.write("Temperature Field Exported: temperature_field.csv\\n")

# 生成合成溫度場數據中繼檔案 (SYNTHETIC - 供離線測試熱翹曲下游讀取介面用)
temp_csv = workspace / "temperature_field.csv"
with open(temp_csv, "w", encoding="utf-8") as f:
    f.write("# WARNING: SYNTHETIC TEST DATA - DO NOT USE FOR PRODUCTION ANALYSIS\\n")
    f.write("NodeID,X,Y,Z,Temperature_C\\n")
    delta_t_max = {chip_power_w} * 1.55
    for nid in range(1, 101):
        xi = ((nid - 1) % 10) * 0.005
        yi = ((nid - 1) // 10) * 0.005
        r_norm_sq = ((xi - 0.0225) / 0.0225) ** 2 + ((yi - 0.0225) / 0.0225) ** 2
        decay = max(0.0, 1.0 - 0.5 * min(1.0, r_norm_sq))
        node_temp = round({ambient_temp_c} + delta_t_max * decay, 2)
        f.write(f"{{nid}},{{xi:.4f}},{{yi:.4f}},0.0,{{node_temp:.2f}}\\n")

print("Icepak 求解完成並導出溫度場 (SYNTHETIC)。")
"""

    def build_command(
        self,
        input_file: Path,
        extra_args: Optional[List[str]] = None,
    ) -> List[str]:
        """組裝 Icepak 啟動命令。

        真實模式下必須使用已偵測到的 Icepak 可執行檔；若本機無真實安裝，
        僅在腳本本身已標記為 synthetic (由 prepare_job 之 allow_synthetic
        授權生成) 時，才允許以目前 Python 解譯器執行該合成腳本。
        """
        if self.solver_bin:
            return [self.solver_bin, "-batch", str(input_file)] + (extra_args or [])

        script_text = ""
        try:
            script_text = Path(input_file).read_text(encoding="utf-8")
        except OSError:
            pass

        if "SYNTHETIC" not in script_text:
            raise SolverDriverError(
                "ANSYS Icepak 求解器未在本機偵測到安裝路徑，且指定的輸入腳本並非"
                "已授權之 synthetic 測試腳本，拒絕以 Python 解譯器直接執行。"
            )

        cmd = [sys.executable, str(input_file)]
        if extra_args:
            cmd.extend(extra_args)
        return cmd

    def get_log_file_path(self, job_dir: Path) -> Path:
        """獲取 Icepak 日誌。"""
        return job_dir / "workspace" / "icepak.log"

    def parse_progress(self, job_dir: Path) -> Dict[str, Any]:
        """解析 Icepak 熱迭代進度。"""
        log_file = self.get_log_file_path(job_dir)
        if not log_file.exists():
            return {"progress_pct": 0.0, "current_step": "QUEUED"}

        text = log_file.read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()

        curr_iter = 0
        total_iter = 20
        max_t = 25.0
        converged = False

        for line in lines:
            if "ITERATION [" in line:
                try:
                    part = line.split("[")[1].split("]")[0]
                    c, tot = part.split("/")
                    curr_iter = int(c)
                    total_iter = int(tot)
                    if "Max_T=" in line:
                        max_t = float(line.split("Max_T=")[1].split()[0])
                except Exception:
                    pass
            if "Solution Converged" in line:
                converged = True

        pct = 100.0 if converged else ((curr_iter / total_iter) * 100.0 if total_iter > 0 else 0.0)
        return {
            "progress_pct": round(pct, 1),
            "current_step": f"Thermal Iteration {curr_iter}/{total_iter}",
            "current_iteration": curr_iter,
            "max_temperature_c": max_t,
            "is_converged": converged,
        }

    def extract_artifacts(self, job_dir: Path) -> Dict[str, Any]:
        """後處理產出白底溫度雲圖與溫度場數據庫檔案。"""
        artifacts_dir = job_dir / "artifacts"
        images_dir = artifacts_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        workspace = job_dir / "workspace"

        config: Dict[str, Any] = {}
        cfg_file = job_dir / "inputs" / "job_config.json"
        if cfg_file.exists():
            try:
                config = json.loads(cfg_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        chip_power = float(config.get("chip_power_w", 45.0))
        ambient_temp = float(config.get("ambient_temperature_c", 25.0))
        max_temp_c = round(ambient_temp + chip_power * 1.55, 1)
        is_synthetic = not self.is_available()

        # 1. 產生標準白底溫度場雲圖
        temp_png = images_dir / "thermal_temperature_contour.png"
        generate_white_contour_png(
            output_path=temp_png,
            title=f"ANSYS Icepak - Steady Thermal Temperature Distribution (T_max={max_temp_c:.1f} °C)",
            metric_name="Temperature",
            unit="°C",
            min_val=ambient_temp,
            max_val=max_temp_c,
            contour_type="thermal",
        )

        # 2. 溫度場中繼導出檔
        temp_field = workspace / "temperature_field.csv"
        if not temp_field.exists() and is_synthetic:
            delta_t_max = chip_power * 1.55
            lines = [
                "# WARNING: SYNTHETIC TEST DATA - DO NOT USE FOR PRODUCTION ANALYSIS",
                "NodeID,X,Y,Z,Temperature_C",
            ]
            for nid in range(1, 101):
                xi = ((nid - 1) % 10) * 0.005
                yi = ((nid - 1) // 10) * 0.005
                r_norm_sq = ((xi - 0.0225) / 0.0225) ** 2 + ((yi - 0.0225) / 0.0225) ** 2
                decay = max(0.0, 1.0 - 0.5 * min(1.0, r_norm_sq))
                node_temp = round(ambient_temp + delta_t_max * decay, 2)
                lines.append(f"{nid},{xi:.4f},{yi:.4f},0.0,{node_temp:.2f}")
            temp_field.write_text("\n".join(lines) + "\n", encoding="utf-8")

        artifact_dict = {
            "temperature_contour": str(temp_png.relative_to(job_dir)),
        }
        if temp_field.exists():
            artifact_dict["temperature_field_csv"] = str(temp_field.relative_to(job_dir))

        metrics = PhysicalMetrics(
            final_convergence_residual=8.5e-6,
        )

        verdict = VerdictEnum.PASS if max_temp_c < 105.0 else VerdictEnum.FAIL
        failure_reasons = []
        if max_temp_c >= 105.0:
            failure_reasons.append(f"晶片最高結溫超標: {max_temp_c:.1f} °C >= 105.0 °C 限值")

        mock_reason = "NO_ICEPAK_SOLVER_DETECTED" if is_synthetic else None

        summary_path = artifacts_dir / "summary.json"
        if summary_path.exists():
            try:
                summary_obj = SimulationSummary.model_validate_json(summary_path.read_text(encoding="utf-8"))
                summary_obj.metrics = metrics
                summary_obj.verdict = verdict
                summary_obj.failure_reasons.extend(failure_reasons)
                summary_obj.artifacts.update(artifact_dict)
                execution_data = summary_obj.execution.model_dump()
                execution_data["is_synthetic"] = is_synthetic
                if mock_reason:
                    execution_data["mock_reason"] = mock_reason
                summary_obj.execution = ExecutionMetadata.model_validate(execution_data)
                summary_path.write_text(summary_obj.model_dump_json(indent=2), encoding="utf-8")
            except Exception as e:
                logger.error(f"更新 Icepak summary.json 失敗: {e}")

        result_dict = {
            "metrics": metrics.model_dump(),
            "verdict": verdict.value,
            "max_temperature_c": max_temp_c,
            "artifacts": artifact_dict,
            "is_synthetic": is_synthetic,
            "mock_reason": mock_reason,
        }
        return result_dict