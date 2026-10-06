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

    def list_keyword_types(self) -> dict:
        """回傳常用 LS-DYNA keyword 類別名稱清單（白名單篩選，非 kw 模組全集）。

        Returns:
            {"ok": True, "keyword_types": [...]}
        """
        return {"ok": True, "keyword_types": list(_COMMON_KEYWORD_TYPES)}


controller = DynaController()
