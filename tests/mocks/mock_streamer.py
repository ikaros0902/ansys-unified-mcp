# -*- coding: utf-8 -*-
"""高保真求解器日誌串流產生器 (MockLogStreamer)

模擬 ANSYS Mechanical (.solve.out)、LS-DYNA (glstat) 與 Fluent (fluent.log)
之即時求解日誌輸出，支援正常收斂模式與異常發散/沙漏能超標模式。
"""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Generator, List, Optional, Union


class MockLogStreamer:
    """求解器日誌串流產生器，支援生成靜態文字或以後台執行緒模擬即時檔案串流。"""

    def __init__(self) -> None:
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def stop(self) -> None:
        """終止目前正在進行的串流執行緒。"""
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    # --------------------------------------------------------------------------
    # 1. ANSYS Mechanical (.solve.out) 日誌生成
    # --------------------------------------------------------------------------
    @staticmethod
    def generate_mechanical_solve_out(
        mode: str = "converged",
        total_substeps: int = 5,
    ) -> List[str]:
        """生成 ANSYS Mechanical / MAPDL 求解日誌片段。

        Args:
            mode: 'converged' (正常收斂) 或 'divergence' (發散/未收斂/NaN)
            total_substeps: 總子步數
        """
        lines: List[str] = [
            "***** ANSYS MECHANICAL SOLVER OUTPUT STREAM *****\n",
            "  Job launched at 2026-09-06 09:00:00\n",
            "  EQUILIBRIUM ITERATION CONTROLS ACTIVATED\n",
        ]

        time_val = 0.0
        dt = 1.0 / max(total_substeps, 1)

        for substep in range(1, total_substeps + 1):
            time_val += dt
            lines.append(f"INCREMENT     1 SUBSTEP     {substep} TIME=  {time_val:0.4f}\n")
            lines.append(f"C U M U L A T I V E   I T E R A T I O N =     {substep * 2}\n")

            if mode == "converged" or substep < total_substeps:
                # 正常步進收斂歷程
                lines.append(f"FORCE CONVERGENCE VALUE =  {0.08 / substep:0.6f}  CRITERION=  0.050000\n")
                lines.append(f"FORCE CONVERGENCE VALUE =  {0.02 / substep:0.6f}  CRITERION=  0.050000\n")
                lines.append(f"  >>> SUBSTEP {substep} CONVERGED AT TIME {time_val:0.4f} <<<\n")
            else:
                # 發散模式：殘差單調暴增並產生 NaN 或未收斂警告
                lines.append("FORCE CONVERGENCE VALUE =  128.450000  CRITERION=  0.050000\n")
                lines.append("FORCE CONVERGENCE VALUE =  99999.9999  CRITERION=  0.050000\n")
                lines.append("FORCE CONVERGENCE VALUE =  NaN  CRITERION=  0.050000\n")
                lines.append(" *** ERROR *** Substep not converged: Element 402 has become highly distorted.\n")
                lines.append("Negative jacobian detected in solid element calculation.\n")
                break

        if mode == "converged":
            lines.append("  SOLUTION FINISHED AT TIME = 1.0000\n")
            lines.append(" *** MECHANICAL SOLUTION COMPLETED SUCCESSFULLY ***\n")

        return lines

    # --------------------------------------------------------------------------
    # 2. LS-DYNA (glstat) 能量日誌生成
    # --------------------------------------------------------------------------
    @staticmethod
    def generate_lsdyna_glstat(
        mode: str = "normal",
        total_steps: int = 15,
    ) -> List[str]:
        """生成 LS-DYNA 能量平衡日誌 (glstat) 片段。

        Args:
            mode: 'normal' (健康能量平衡，沙漏比 < 5%) 或
                  'hourglass_exceeded' (沙漏能飆升 > 5%，觸發早期熔斷)
            total_steps: 模擬時間步數
        """
        lines: List[str] = [
            "*** LS-DYNA GLOBAL STATISTICS (glstat) ***\n",
            "Units: mm, tonne, s, N, MPa, mJ\n",
        ]

        t = 0.0
        dt = 0.00025

        for step in range(1, total_steps + 1):
            t += dt
            lines.append(f"time = {t:0.6E} dt = {dt:0.6E}\n")

            if mode == "hourglass_exceeded" and step >= 10:
                # 沙漏能暴增模式：E_hg = 62.0, E_total = 932.0 => 6.65% > 5%
                kinetic = 350.0 - (step - 10) * 10.0
                internal = 520.0 + (step - 10) * 5.0
                hourglass = 62.0 + (step - 10) * 3.0
                total = kinetic + internal + hourglass
                added_mass_pct = 0.012
            else:
                # 正常模式：沙漏能比率維持在 1.2% ~ 1.8%
                kinetic = max(500.0 - step * 25.0, 50.0)
                internal = step * 25.0
                hourglass = total_steps * 0.4 + step * 0.1  # 約 6.0 ~ 7.5 J
                total = kinetic + internal + hourglass
                added_mass_pct = 0.002

            lines.append(f"kinetic energy = {kinetic:0.4E}\n")
            lines.append(f"internal energy = {internal:0.4E}\n")
            lines.append(f"hourglass energy = {hourglass:0.4E}\n")
            lines.append(f"total energy = {total:0.4E}\n")
            lines.append("sliding interface energy = 0.0000E+00\n")
            lines.append(f"added mass = 1.2000E-07 (ratio = {added_mass_pct:0.3f} %)\n")
            lines.append("\n")

        return lines

    # --------------------------------------------------------------------------
    # 3. ANSYS Fluent (fluent.log) 日誌生成
    # --------------------------------------------------------------------------
    @staticmethod
    def generate_fluent_log(
        mode: str = "converged",
        total_iterations: int = 20,
    ) -> List[str]:
        """生成 ANSYS Fluent 殘差求解日誌。

        Args:
            mode: 'converged' (收斂) 或 'divergence' / 'reversed_flow' (發散/逆流)
            total_iterations: 迭代步數
        """
        lines: List[str] = [
            "  iter  continuity   x-velocity   y-velocity            k        omega     time/iter\n"
        ]

        for it in range(1, total_iterations + 1):
            if mode == "converged" or it < total_iterations // 2:
                # 殘差平穩下降
                c = 1.0 / (it * 10.0)
                u = 0.2 / (it * 5.0)
                v = 0.3 / (it * 5.0)
                k = 0.5 / (it * 8.0)
                w = 0.8 / (it * 8.0)
                lines.append(f"  {it:4d}  {c:0.4e}   {u:0.4e}   {v:0.4e}   {k:0.4e}   {w:0.4e}  0:00:01   10\n")
            else:
                # 發散或逆流模式
                if mode == "reversed_flow":
                    lines.append(f"  {it:4d}  1.5240e-01   8.9123e-02   9.1234e-02   3.1234e-01   5.9123e-01  0:00:01   10\n")
                    lines.append("reversed flow in 25 faces on pressure-outlet 4.\n")
                else:
                    lines.append(f"  {it:4d}         nan   1.8912e+02   3.9123e+02          inf          inf  0:00:01   10\n")
                    lines.append("divergence detected in AMG solver: continuity\n")
                    break

        if mode == "converged":
            lines.append("  solution is converged.\n")

        return lines

    # --------------------------------------------------------------------------
    # 4. 即時檔案串流引擎
    # --------------------------------------------------------------------------
    def stream_to_file(
        self,
        target_path: Union[str, Path],
        lines: List[str],
        interval_sec: float = 0.01,
    ) -> threading.Thread:
        """啟動後台線程，依序將日誌行按設定間隔寫入指定檔案，支援即時 flush。

        Args:
            target_path: 目標日誌輸出路徑
            lines: 欲寫入之日誌文本行清單
            interval_sec: 每行寫入之間隔時間 (秒)
        Returns:
            執行串流之 Thread 物件
        """
        self._stop_event.clear()
        target_file = Path(target_path)
        target_file.parent.mkdir(parents=True, exist_ok=True)

        def _worker() -> None:
            with open(target_file, "w", encoding="utf-8") as f:
                for line in lines:
                    if self._stop_event.is_set():
                        break
                    f.write(line)
                    f.flush()
                    time.sleep(interval_sec)

        self._thread = threading.Thread(target=_worker, daemon=True)
        self._thread.start()
        return self._thread

    def write_static_log(
        self,
        target_path: Union[str, Path],
        log_type: str = "solve_out",
        mode: str = "converged",
    ) -> Path:
        """同步一次性寫入完整的日誌靜態檔（方便單元測試直接使用）。

        Args:
            target_path: 輸出檔案路徑
            log_type: 'solve_out' | 'glstat' | 'fluent'
            mode: 求解狀態模式 ('converged', 'divergence', 'normal', 'hourglass_exceeded')
        """
        target_file = Path(target_path)
        target_file.parent.mkdir(parents=True, exist_ok=True)

        if log_type == "solve_out":
            lines = self.generate_mechanical_solve_out(mode=mode)
        elif log_type == "glstat":
            lines = self.generate_lsdyna_glstat(mode=mode)
        elif log_type == "fluent":
            lines = self.generate_fluent_log(mode=mode)
        else:
            raise ValueError(f"不支援的 log_type: {log_type}")

        with open(target_file, "w", encoding="utf-8") as f:
            f.writelines(lines)

        return target_file
