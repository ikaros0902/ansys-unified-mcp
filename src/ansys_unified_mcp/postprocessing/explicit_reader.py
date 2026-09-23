"""ANSYS Unified MCP 2.0 - LS-DYNA 顯式動力學結果讀取器 (LSDynaExplicitReader).

專責讀取與評估 LS-DYNA 落摔衝擊 (Drop Test) 與衝擊響應 (Shock Analysis) 關鍵指標：
1. 終態檢核 (SOLVED, FAILED, ABORTED)
2. 檢查 d3plot 二進位結果場檔案存在性
3. 讀取並解析 glstat 能量平衡 (動能、內能、沙漏能、總能量與能量平衡比)
4. 計算沙漏能佔比 (hourglass_energy / internal_energy) 並驗證 < 5% 門檻
5. 讀取並解析 matter.out (或 d3hsp) 質量縮放百分比 (added mass percentage)
"""

from __future__ import annotations

import logging
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Union

from ansys_unified_mcp.postprocessing.base import (
    BaseResultReader,
    JobNotReadyError,
    PostprocessingError,
)

logger = logging.getLogger(__name__)


class LSDynaExplicitReader(BaseResultReader):
    """LS-DYNA 顯式動力學日誌與結果讀取器。"""

    RE_TIME_DT = re.compile(
        r"time\s*=\s*([\d\.E\+\-]+)\s+dt\s*=\s*([\d\.E\+\-]+)", re.IGNORECASE
    )
    RE_KINETIC = re.compile(r"kinetic\s+energy\s*=\s*([\d\.E\+\-]+)", re.IGNORECASE)
    RE_INTERNAL = re.compile(r"internal\s+energy\s*=\s*([\d\.E\+\-]+)", re.IGNORECASE)
    RE_HOURGLASS = re.compile(r"hourglass\s+energy\s*=\s*([\d\.E\+\-]+)", re.IGNORECASE)
    RE_TOTAL_ENERGY = re.compile(r"total\s+energy\s*=\s*([\d\.E\+\-]+)", re.IGNORECASE)
    RE_SLIDING = re.compile(
        r"(sliding\s+interface\s+energy|sliding\s+energy)\s*=\s*([\d\.E\+\-]+)",
        re.IGNORECASE,
    )
    RE_MASS_SCALING = re.compile(
        r"added\s+mass\s*=\s*[\d\.E\+\-]+\s*\(ratio\s*=\s*([\d\.E\+\-]+)\s*%\)",
        re.IGNORECASE,
    )
    RE_MASS_SCALING_D3HSP = re.compile(
        r"added\s+mass\s+percentage\s*=\s*([\d\.E\+\-]+)", re.IGNORECASE
    )

    def locate_file(self, job_dir: Path, filename_pattern: str) -> Optional[Path]:
        """在作業目錄及其子目錄中搜尋指定檔名。"""
        # 先找直屬目錄
        for p in job_dir.glob(filename_pattern):
            if p.is_file():
                return p
        # 再遞迴尋找
        for p in job_dir.rglob(filename_pattern):
            if p.is_file():
                return p
        return None

    def check_d3plot_exists(self, job_dir: Path) -> bool:
        """確認 d3plot 或 d3plot01 等結果場檔案是否存在。"""
        for p in job_dir.rglob("*"):
            if p.is_file() and p.name.lower().startswith("d3plot"):
                return True
        return False

    def parse_glstat(self, glstat_path: Path) -> Dict[str, float]:
        """解析 glstat 檔案提取最終時間步之能量數值。"""
        text = glstat_path.read_text(encoding="utf-8", errors="replace")
        
        ke, ie, hg, te, sl = 0.0, 0.0, 0.0, 0.0, 0.0
        added_mass = 0.0

        for line in text.splitlines():
            line_str = line.strip()
            if not line_str:
                continue

            m = self.RE_KINETIC.search(line_str)
            if m:
                try:
                    ke = float(m.group(1))
                except ValueError:
                    pass

            m = self.RE_INTERNAL.search(line_str)
            if m:
                try:
                    ie = float(m.group(1))
                except ValueError:
                    pass

            m = self.RE_HOURGLASS.search(line_str)
            if m:
                try:
                    hg = float(m.group(1))
                except ValueError:
                    pass

            m = self.RE_TOTAL_ENERGY.search(line_str)
            if m:
                try:
                    te = float(m.group(1))
                except ValueError:
                    pass

            m = self.RE_SLIDING.search(line_str)
            if m:
                try:
                    sl = float(m.group(2))
                except ValueError:
                    pass

            m = self.RE_MASS_SCALING.search(line_str)
            if m:
                try:
                    added_mass = float(m.group(1))
                except ValueError:
                    pass

        # 計算能量平衡與沙漏能比例
        hg_ratio = (hg / ie) if ie > 1e-12 else 0.0
        balance_ratio = ((ke + ie + hg + sl) / te) if abs(te) > 1e-12 else 1.0

        return {
            "kinetic_energy": ke,
            "internal_energy": ie,
            "hourglass_energy": hg,
            "total_energy": te,
            "sliding_energy": sl,
            "energy_balance": balance_ratio,
            "hourglass_ratio": hg_ratio,
            "hourglass_ratio_pct": hg_ratio * 100.0,
            "added_mass_pct_from_glstat": added_mass,
        }

    def parse_matter_out(self, matter_path: Path) -> float:
        """解析 matter.out 提取質量縮放增加百分比。"""
        text = matter_path.read_text(encoding="utf-8", errors="replace")
        added_mass = 0.0
        for line in text.splitlines():
            m1 = self.RE_MASS_SCALING.search(line)
            if m1:
                try:
                    added_mass = float(m1.group(1))
                except ValueError:
                    pass
            m2 = self.RE_MASS_SCALING_D3HSP.search(line)
            if m2:
                try:
                    added_mass = float(m2.group(1))
                except ValueError:
                    pass
        return added_mass

    def _synthetic_fallback(self) -> Dict[str, Any]:
        """提供顯式動力學之合成標準結果指標。"""
        return {
            "is_synthetic": True,
            "mock_reason": "NO_EXPLICIT_FILES_DETECTED",
            "d3plot_exists": True,
            "kinetic_energy": 120.5,
            "internal_energy": 550.0,
            "hourglass_energy": 12.0,
            "total_energy": 682.5,
            "energy_balance": 1.0,
            "hourglass_ratio": 12.0 / 550.0,
            "hourglass_ratio_pct": (12.0 / 550.0) * 100.0,
            "hourglass_acceptable": True,
            "mass_scaling_added_pct": 0.15,
        }

    def read_results(
        self,
        job_dir: Union[Path, str],
        allow_synthetic: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """讀取 LS-DYNA 顯式分析結果 (glstat, matter.out, d3plot)。

        Args:
            job_dir: 作業目錄。
            allow_synthetic: 若為 True，缺少檔案時回傳合成指標；若為 False，嚴格拋出例外。
            **kwargs: 可選指定 job_status 或 assert_healthy。

        Returns:
            Dict[str, Any]: 包含能量平衡、沙漏能比例、質量縮放等指標之字典。

        Raises:
            JobNotReadyError: 作業尚未完成。
            PostprocessingError: 找不到必要日誌或解析失敗。
        """
        job_path = Path(job_dir).resolve()
        job_status = kwargs.get("job_status")

        # 1. 檢驗終態閘門
        self.validate_terminal_state(job_path, job_status=job_status)

        # 2. 檢驗 d3plot 存在性
        d3plot_exists = self.check_d3plot_exists(job_path)

        # 3. 搜尋 glstat 檔案
        glstat_path = self.locate_file(job_path, "glstat*")
        if glstat_path is None or not glstat_path.exists():
            if allow_synthetic:
                logger.info("未找到 glstat 檔案，回傳合成指標 (allow_synthetic=True)")
                return self._synthetic_fallback()
            raise PostprocessingError(
                f"在作業目錄 '{job_path}' 中找不到 glstat 能量日誌檔案。"
            )

        # 4. 解析 glstat
        energy_data = self.parse_glstat(glstat_path)

        # 5. 搜尋並解析 matter.out
        mass_scaling_pct = energy_data.get("added_mass_pct_from_glstat", 0.0)
        matter_path = self.locate_file(job_path, "matter.out*")
        if matter_path is not None and matter_path.exists():
            parsed_ms = self.parse_matter_out(matter_path)
            if parsed_ms > 0:
                mass_scaling_pct = parsed_ms

        hg_ratio = energy_data["hourglass_ratio"]
        hg_ratio_pct = energy_data["hourglass_ratio_pct"]
        is_acceptable = bool(hg_ratio < 0.05)

        # 若使用者指定嚴格檢驗健康度且沙漏能超標，拋出 PostprocessingError
        if kwargs.get("assert_healthy", False) and not is_acceptable:
            raise PostprocessingError(
                f"LS-DYNA 沙漏能比例 {hg_ratio_pct:.2f}% 超出 5% 安全門檻。"
            )

        return {
            "is_synthetic": False,
            "d3plot_exists": d3plot_exists,
            "kinetic_energy": energy_data["kinetic_energy"],
            "internal_energy": energy_data["internal_energy"],
            "hourglass_energy": energy_data["hourglass_energy"],
            "total_energy": energy_data["total_energy"],
            "sliding_energy": energy_data["sliding_energy"],
            "energy_balance": energy_data["energy_balance"],
            "hourglass_ratio": hg_ratio,
            "hourglass_ratio_pct": hg_ratio_pct,
            "hourglass_acceptable": is_acceptable,
            "mass_scaling_added_pct": mass_scaling_pct,
            "glstat_path": str(glstat_path),
        }
