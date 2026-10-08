# -*- coding: utf-8 -*-
"""LS-DYNA product facade.

負責以 PyDYNA (ansys-dyna-core) 離線程式化生成 LS-DYNA .k keyword deck。

純離線設計：本模組不連線 LS-DYNA solver 或任何實機，僅使用 PyDYNA 的
Deck/keywords 物件模型在記憶體中組裝卡片並輸出文字，供後續人工或其他
管線送求解器執行。
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

PRODUCT = "dyna"

# 常用 keyword 類別白名單（供 list_keyword_types 工具回傳），避免直接暴露
# kw 模組全部 3000+ 類別造成資訊過載。
_COMMON_KEYWORD_TYPES: tuple[str, ...] = (
    "ControlTermination",
    "ControlEnergy",
    "ControlTimestep",
    "ControlContact",
    "Node",
    "Part",
    "SectionShell",
    "SectionSolid",
    "MatElastic",
    "MatPiecewiseLinearPlasticity",
    "ContactAutomaticSurfaceToSurface",
    "DatabaseBinaryD3Plot",
    "DatabaseGlstat",
    "BoundarySpcNode",
    "LoadNodePoint",
)


class DynaController:
    """封裝 PyDYNA Deck 之離線 keyword deck 生成邏輯。"""

    def _load_pydyna(self):
        """延遲載入 PyDYNA（避免未安裝時拖垮整個 server 啟動）。

        注意：不可用 importlib.import_module 載入 ansys.dyna.core.keywords。
        PyDYNA 的 keywords 套件在首次載入時會於 sys.modules 自我替換為
        完整填充的惰性模組（lazy __getattr__），但 importlib.import_module
        會回傳替換前的舊模組物件（僅 2 個屬性），導致 kw_mod.ControlTermination
        等類別存取拋出 AttributeError。改用一般 import 語句才能取得替換後的
        正確模組物件（3175 個 keyword 類別）。
        """
        import ansys.dyna.core as deck_mod
        import ansys.dyna.core.keywords as kw_mod

        return deck_mod, kw_mod

    def create_keyword_deck(
        self,
        endtim: float,
        hourglass_control: bool = False,
    ) -> dict:
        """生成基礎 LS-DYNA keyword deck 文字。

        Args:
            endtim: *CONTROL_TERMINATION 的終止時間 (endtim)。
            hourglass_control: True 時額外附加 *CONTROL_ENERGY 卡片，
                啟用沙漏能與滑移能追蹤（hgen/slnten 設為 2，供後續
                能量守恆與沙漏能比例檢核使用）。

        Returns:
            成功：{"ok": True, "deck_text": "...", "cards": [...]}
            失敗：{"ok": False, "error": "..."}
        """
        try:
            deck_mod, kw_mod = self._load_pydyna()
        except ImportError as exc:
            return {"ok": False, "error": f"PyDYNA (ansys-dyna-core) 未安裝: {exc}"}

        try:
            dk = deck_mod.Deck()
            dk.append(kw_mod.ControlTermination(endtim=endtim))

            cards = ["*CONTROL_TERMINATION"]
            if hourglass_control:
                # hgen=2：啟用沙漏能計算；slnten=2：啟用滑移介面能計算，
                # 供後續能量守恆誤差與沙漏能比例門禁檢核。
                dk.append(kw_mod.ControlEnergy(hgen=2, slnten=2))
                cards.append("*CONTROL_ENERGY")

            deck_text = dk.write()
            return {"ok": True, "deck_text": deck_text, "cards": cards, "endtim": endtim}
        except Exception as exc:  # noqa: BLE001 - PyDYNA 內部例外一律優雅回傳
            return {"ok": False, "error": str(exc)}

    def export_keyword_file(
        self,
        output_path: str,
        endtim: float,
        hourglass_control: bool = False,
    ) -> dict:
        """生成基礎 keyword deck 並寫出為 .k 檔。

        Args:
            output_path: 輸出 .k 檔絕對路徑（父目錄不存在時自動建立）。
            endtim: *CONTROL_TERMINATION 的終止時間 (endtim)。
            hourglass_control: 同 create_keyword_deck。

        Returns:
            成功：{"ok": True, "file_path": "...", "cards": [...]}
            失敗：{"ok": False, "error": "..."}
        """
        result = self.create_keyword_deck(endtim=endtim, hourglass_control=hourglass_control)
        if not result.get("ok"):
            return result

        try:
            dest = Path(output_path)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(result["deck_text"], encoding="utf-8")
            return {
                "ok": True,
                "file_path": str(dest),
                "cards": result["cards"],
                "endtim": endtim,
            }
        except Exception as exc:  # noqa: BLE001 - 檔案系統例外一律優雅回傳
            return {"ok": False, "error": str(exc)}

    @staticmethod
    def find_dyna_solver() -> Optional[Path]:
        """自動偵測本機 LS-DYNA 求解器 (優先尋找 lsdyna_dp.exe 或 lsdyna.exe)。"""
        import os
        for env_var in sorted([k for k in os.environ if k.startswith("AWP_ROOT")], reverse=True):
            root = Path(os.environ[env_var])
            bin_dir = root / "ansys" / "bin" / "winx64"
            for candidate in ("lsdyna_dp.exe", "lsdyna_sp.exe", "lsdyna.exe"):
                p = bin_dir / candidate
                if p.is_file():
                    return p
        for ver in ("v251", "v242", "v232"):
            base = Path(f"C:/Program Files/ANSYS Inc/{ver}/ansys/bin/winx64")
            for candidate in ("lsdyna_dp.exe", "lsdyna_sp.exe", "lsdyna.exe"):
                p = base / candidate
                if p.is_file():
                    return p
        return None

    @staticmethod
    def find_prepost() -> Optional[Path]:
        """自動偵測本機 LS-PrePost 執行檔。"""
        import os
        for env_var in sorted([k for k in os.environ if k.startswith("AWP_ROOT")], reverse=True):
            root = Path(os.environ[env_var])
            bin_dir = root / "ansys" / "bin" / "winx64"
            if bin_dir.is_dir():
                for match in bin_dir.glob("**/lsprepost*.exe"):
                    if match.is_file():
                        return match
        for ver in ("v251", "v242", "v232"):
            bin_dir = Path(f"C:/Program Files/ANSYS Inc/{ver}/ansys/bin/winx64")
            if bin_dir.is_dir():
                for match in bin_dir.glob("**/lsprepost*.exe"):
                    if match.is_file():
                        return match
        return None

    def solve_keyword(
        self,
        k_file_path: str,
        ncpu: int = 4,
        memory: str = "100m",
        working_dir: str = "",
        dry_run: bool = False,
        timeout: float = 300.0,
    ) -> dict:
        """調度本機 LS-DYNA 求解器執行計算。"""
        k_path = Path(k_file_path)
        if not dry_run and not k_path.is_file():
            return {"ok": False, "error": f"Keyword 檔案不存在: {k_file_path}"}

        solver_exe = self.find_dyna_solver()
        if not dry_run and solver_exe is None:
            return {"ok": False, "error": "未偵測到本機 LS-DYNA 求解器 (lsdyna_dp.exe)。"}

        work_dir = Path(working_dir) if working_dir else k_path.parent
        cmd = [
            str(solver_exe) if solver_exe else "lsdyna_dp.exe",
            f"i={k_path.name if working_dir else str(k_path.resolve())}",
            f"ncpu={ncpu}",
            f"memory={memory}",
        ]

        if dry_run:
            return {
                "ok": True,
                "dry_run": True,
                "command": cmd,
                "solver_executable": str(solver_exe) if solver_exe else "lsdyna_dp.exe",
                "working_dir": str(work_dir),
                "k_file": str(k_path),
            }

        try:
            import subprocess
            proc = subprocess.run(
                cmd,
                cwd=str(work_dir),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return {
                "ok": proc.returncode == 0,
                "return_code": proc.returncode,
                "stdout": proc.stdout[-2000:] if proc.stdout else "",
                "stderr": proc.stderr[-2000:] if proc.stderr else "",
                "working_dir": str(work_dir),
                "command": cmd,
            }
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": f"LS-DYNA 求解超時 ({timeout} 秒)"}
        except Exception as exc:
            return {"ok": False, "error": f"執行求解器失敗: {exc}"}

    def run_prepost(
        self,
        cfile_path: str = "",
        script_content: str = "",
        working_dir: str = "",
        dry_run: bool = False,
        timeout: float = 120.0,
    ) -> dict:
        """以無頭批次模式執行 LS-PrePost SCL/cfile 命令腳本。"""
        prepost_exe = self.find_prepost()
        if not dry_run and prepost_exe is None:
            return {"ok": False, "error": "未偵測到本機 LS-PrePost 執行檔 (lsprepost.exe)。"}

        work_dir = Path(working_dir) if working_dir else Path.cwd()
        actual_cfile = None
        if script_content:
            import tempfile
            tf = tempfile.NamedTemporaryFile("w", suffix=".cfile", delete=False, encoding="utf-8")
            tf.write(script_content)
            tf.close()
            actual_cfile = tf.name
        elif cfile_path:
            actual_cfile = cfile_path

        if not actual_cfile and not dry_run:
            return {"ok": False, "error": "必須指定 cfile_path 或 script_content。"}

        cmd = [
            str(prepost_exe) if prepost_exe else "lsprepost.exe",
            "-n",
            "-c",
            str(actual_cfile or "mock.cfile"),
        ]

        if dry_run:
            return {
                "ok": True,
                "dry_run": True,
                "command": cmd,
                "prepost_executable": str(prepost_exe) if prepost_exe else "lsprepost.exe",
                "cfile": actual_cfile,
            }

        try:
            import subprocess
            proc = subprocess.run(
                cmd,
                cwd=str(work_dir),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return {
                "ok": proc.returncode == 0,
                "return_code": proc.returncode,
                "stdout": proc.stdout[-2000:] if proc.stdout else "",
                "stderr": proc.stderr[-2000:] if proc.stderr else "",
                "cfile": actual_cfile,
            }
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": f"LS-PrePost 執行超時 ({timeout} 秒)"}
        except Exception as exc:
            return {"ok": False, "error": f"執行 LS-PrePost 失敗: {exc}"}


    def list_keyword_types(self) -> dict:
        """回傳常用 LS-DYNA keyword 類別名稱清單（白名單篩選，非 kw 模組全集）。

        Returns:
            {"ok": True, "keyword_types": [...]}
        """
        return {"ok": True, "keyword_types": list(_COMMON_KEYWORD_TYPES)}


controller = DynaController()


