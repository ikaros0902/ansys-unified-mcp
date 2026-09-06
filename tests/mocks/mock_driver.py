# -*- coding: utf-8 -*-
"""高保真離線模擬求解器驅動 (MockSolverDriver)

實作 BaseSolverDriver 介面合約，提供純離線、高保真之求解器生命週期模擬。
支援生成虛擬子進程 (FakeProcess)、模擬進度輪詢、優雅中斷，
並於 extract_results 時自動合成 1920x1080 白底 PNG 雲圖、summary.json 與 overview.html。
"""

from __future__ import annotations

import json
import os
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class FakeProcess:
    """模擬 subprocess.Popen 介面之子進程物件。"""

    def __init__(self, pid: int = 12345, returncode: Optional[int] = None) -> None:
        self.pid = pid
        self.returncode = returncode
        self._is_terminated = False
        self._is_killed = False

    def poll(self) -> Optional[int]:
        """輪詢進程狀態，若未終止則回傳 None，若已結束則回傳 exit code。"""
        return self.returncode

    def wait(self, timeout: Optional[float] = None) -> int:
        """等待進程結束。"""
        if self.returncode is None:
            self.returncode = 0
        return self.returncode

    def terminate(self) -> None:
        """優雅發送終止信號 (SIGTERM)。"""
        self._is_terminated = True
        self.returncode = -15  # SIGTERM

    def kill(self) -> None:
        """強制殺死進程 (SIGKILL)。"""
        self._is_killed = True
        self.returncode = -9  # SIGKILL


class BaseSolverDriverContract(ABC):
    """求解器驅動抽象契約基類。"""

    @abstractmethod
    def validate_prerequisites(self) -> Tuple[bool, str]:
        """驗證求解器環境變數、二進位程式碼與授權可用性。"""
        pass

    @abstractmethod
    def prepare_job(self, job_dir: Path, config: Dict[str, Any]) -> Path:
        """在沙盒 workspace 中建立求解輸入腳本，返回主輸入路徑。"""
        pass

    @abstractmethod
    def launch(self, job_dir: Path, input_file: Path) -> Any:
        """啟動求解器子進程。"""
        pass

    @abstractmethod
    def parse_progress(self, job_dir: Path) -> Dict[str, Any]:
        """解析當前計算進度百分比、時間步與殘差。"""
        pass

    @abstractmethod
    def abort(self, proc: Any) -> None:
        """終止求解器進程。"""
        pass

    @abstractmethod
    def extract_results(self, job_dir: Path) -> Dict[str, Any]:
        """提取結果數據並輸出 summary.json 與白底雲圖。"""
        pass


class MockSolverDriver(BaseSolverDriverContract):
    """通用高保真離線虛擬驅動。"""

    def __init__(
        self,
        solver_name: str = "MockSolver",
        solver_version: str = "2026 R1",
        simulated_status: str = "SOLVED",
        simulated_verdict: str = "PASS",
        custom_metrics: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.solver_name = solver_name
        self.solver_version = solver_version
        self.simulated_status = simulated_status
        self.simulated_verdict = simulated_verdict
        self.custom_metrics = custom_metrics or {}
        self.current_process: Optional[FakeProcess] = None

    def validate_prerequisites(self) -> Tuple[bool, str]:
        """離線模式預設驗證通過。"""
        return True, f"{self.solver_name} {self.solver_version} (Mock Mode) environment ready."

    def prepare_job(self, job_dir: Path, config: Dict[str, Any]) -> Path:
        """在 workspace 目錄中寫入仿真執行腳本。"""
        workspace_dir = job_dir / "workspace"
        workspace_dir.mkdir(parents=True, exist_ok=True)

        input_script = workspace_dir / "mock_solve_script.py"
        with open(input_script, "w", encoding="utf-8") as f:
            f.write("# Mock Solver Input Script\n")
            f.write(f"# Config: {json.dumps(config, indent=2)}\n")
            f.write("print('Executing mock simulation...')\n")

        return input_script

    def launch(self, job_dir: Path, input_file: Path) -> FakeProcess:
        """啟動虛擬子進程並生成初始日誌檔案。"""
        workspace_dir = job_dir / "workspace"
        workspace_dir.mkdir(parents=True, exist_ok=True)

        log_path = workspace_dir / "solve.out"
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"*** {self.solver_name} Launched ***\n")
            f.write("INCREMENT 1 SUBSTEP 1 TIME= 0.2000\n")
            f.write("FORCE CONVERGENCE VALUE = 0.0100 CRITERION = 0.0500\n")

        self.current_process = FakeProcess(pid=99999, returncode=None)
        return self.current_process

    def parse_progress(self, job_dir: Path) -> Dict[str, Any]:
        """模擬解析求解日誌進度。"""
        return {
            "progress_pct": 100.0 if self.simulated_status == "SOLVED" else 45.0,
            "current_step": "Substep 5 / 5",
            "converged": self.simulated_status == "SOLVED",
            "physical_health": {
                "hourglass_ratio": 0.015,
                "mass_scaling_pct": 0.002,
                "max_residual": 0.008,
            },
        }

    def abort(self, proc: Any) -> None:
        """優雅終止進程。"""
        if proc is not None and hasattr(proc, "terminate"):
            proc.terminate()
            self.simulated_status = "ABORTED"
            self.simulated_verdict = "FAIL"

    def extract_results(self, job_dir: Path) -> Dict[str, Any]:
        """合成完整的三位一體標準產出 (summary.json, 白底 PNG, overview.html)。"""
        artifacts_dir = job_dir / "artifacts"
        images_dir = artifacts_dir / "images"
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        images_dir.mkdir(parents=True, exist_ok=True)

        # 1. 生成 1920x1080 白底高清雲圖
        stress_img_path = images_dir / "stress_von_mises.png"
        warpage_img_path = images_dir / "warpage_z.png"
        self._generate_white_contour_png(stress_img_path, title="Equivalent (von-Mises) Stress [MPa]")
        self._generate_white_contour_png(warpage_img_path, title="Z-Axis Warpage Displacement [um]")

        # 2. 構建標準 summary.json
        summary_data: Dict[str, Any] = {
            "job_id": job_dir.name,
            "workflow_type": "mock_workflow",
            "tag": "offline_verification",
            "status": self.simulated_status,
            "verdict": self.simulated_verdict,
            "failure_reasons": [] if self.simulated_verdict == "PASS" else ["Simulated failure threshold exceeded"],
            "metrics": {
                "max_equivalent_stress_mpa": self.custom_metrics.get("max_equivalent_stress_mpa", 94.2),
                "material_yield_strength_mpa": self.custom_metrics.get("material_yield_strength_mpa", 180.0),
                "safety_factor": self.custom_metrics.get("safety_factor", 1.91),
                "max_total_deformation_mm": self.custom_metrics.get("max_total_deformation_mm", 0.128),
                "max_warpage_z_um": self.custom_metrics.get("max_warpage_z_um", 128.0),
                "first_mode_frequency_hz": self.custom_metrics.get("first_mode_frequency_hz", 145.5),
                "effective_mass_ratio_x": self.custom_metrics.get("effective_mass_ratio_x", 0.925),
                "effective_mass_ratio_y": self.custom_metrics.get("effective_mass_ratio_y", 0.912),
                "effective_mass_ratio_z": self.custom_metrics.get("effective_mass_ratio_z", 0.940),
                "hourglass_energy_ratio_pct": self.custom_metrics.get("hourglass_energy_ratio_pct", 1.5),
                "mass_scaling_added_pct": self.custom_metrics.get("mass_scaling_added_pct", 0.05),
            },
            "execution": {
                "created_at": "2026-09-06T09:00:00Z",
                "finished_at": "2026-09-06T09:01:30Z",
                "duration_seconds": 90.0,
                "solver_name": self.solver_name,
                "solver_version": self.solver_version,
                "pid": self.current_process.pid if self.current_process else None,
                "exit_code": 0 if self.simulated_status == "SOLVED" else 1,
            },
            "artifacts": {
                "summary_json": str(artifacts_dir / "summary.json"),
                "overview_html": str(artifacts_dir / "overview.html"),
                "stress_contour": str(stress_img_path),
                "warpage_contour": str(warpage_img_path),
            },
        }

        summary_file = artifacts_dir / "summary.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)

        # 3. 輸出自包含免聯網 overview.html
        html_file = artifacts_dir / "overview.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>CAE 模擬分析儀表板 - {job_dir.name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f8fafc; color: #1e293b; margin: 0; padding: 24px; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 16px; }}
        .badge-pass {{ background: #10b981; color: white; padding: 6px 14px; border-radius: 9999px; font-weight: bold; }}
        .badge-fail {{ background: #ef4444; color: white; padding: 6px 14px; border-radius: 9999px; font-weight: bold; }}
        .card-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-top: 24px; }}
        .card {{ background: white; padding: 20px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .metric-val {{ font-size: 28px; font-weight: bold; color: #0f172a; margin-top: 8px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>模擬作業儀表板: {job_dir.name}</h1>
        <span class="{'badge-pass' if self.simulated_verdict == 'PASS' else 'badge-fail'}">{self.simulated_verdict}</span>
    </div>
    <div class="card-grid">
        <div class="card">
            <div>最大等效應力 (von-Mises)</div>
            <div class="metric-val">{summary_data['metrics']['max_equivalent_stress_mpa']} MPa</div>
        </div>
        <div class="card">
            <div>安全係數 (SF)</div>
            <div class="metric-val">{summary_data['metrics']['safety_factor']}</div>
        </div>
        <div class="card">
            <div>最大翹曲變形 (Z)</div>
            <div class="metric-val">{summary_data['metrics']['max_total_deformation_mm']} mm</div>
        </div>
    </div>
</body>
</html>""")

        return summary_data

    @staticmethod
    def _generate_white_contour_png(target_file: Path, title: str) -> None:
        """繪製 1920x1080 純白背景之高解析雲圖 PNG。"""
        if HAS_PIL:
            # 建立 1920x1080 32-bit RGBA 畫布，背景純白 #FFFFFF
            img = Image.new("RGBA", (1920, 1080), (255, 255, 255, 255))
            draw = ImageDraw.Draw(img)

            # 繪製主視圖幾何框與仿 CAE 等值線漸層
            draw.rectangle([(200, 150), (1500, 950)], outline=(180, 190, 205), width=2)

            # 繪製右側 Color Bar (8 個色階區塊)
            colors = [
                (220, 38, 38),   # 紅 (Max)
                (234, 88, 12),   # 橘紅
                (245, 158, 11),  # 橘黃
                (234, 179, 8),   # 黃
                (132, 204, 22),  # 黃綠
                (34, 197, 94),   # 綠
                (14, 165, 233),  # 淺藍
                (59, 130, 246),  # 深藍 (Min)
            ]
            bar_x = 1620
            bar_y_start = 200
            bar_height = 80

            for i, color in enumerate(colors):
                y0 = bar_y_start + i * bar_height
                y1 = y0 + bar_height
                draw.rectangle([(bar_x, y0), (bar_x + 60, y1)], fill=color, outline=(100, 116, 139))

            img.save(target_file, format="PNG")
        else:
            # 若無 PIL 則寫入 1x1 最小合法 PNG 標頭
            minimal_png = (
                b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
                b"\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\xf8\xff\xff"
                b"?\x00\x05\xfe\x02\xfe\xa74e\xd8\x00\x00\x00\x00IEND\xaeB`\x82"
            )
            with open(target_file, "wb") as f:
                f.write(minimal_png)


class MockMechanicalDriver(MockSolverDriver):
    """ANSYS Mechanical 虛擬驅動。"""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(solver_name="ANSYS Mechanical", **kwargs)


class MockLSDynaDriver(MockSolverDriver):
    """LS-DYNA 顯式動力學虛擬驅動。"""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(solver_name="LS-DYNA Explicit", **kwargs)


class MockFluentDriver(MockSolverDriver):
    """ANSYS Fluent 流體力學虛擬驅動。"""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(solver_name="ANSYS Fluent", **kwargs)


class MockOptislangDriver(MockSolverDriver):
    """ANSYS optiSLang 參數優化虛擬驅動。"""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(solver_name="ANSYS optiSLang", **kwargs)
