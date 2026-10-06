# -*- coding: utf-8 -*-
"""SpaceClaim 伺服器端 IronPython 腳本資源（以 .ironpy 檔存放）。

這些腳本透過 Modeler.run_script_file 送到 SpaceClaim 伺服器端（IronPython）執行，
在那裡才有 argsDict / GetRootPart / Selection / ViewHelper 等情境全域。故以 .ironpy
副檔名存放：CPython 不會嘗試匯入、靜態檢查器也不會對那些僅存在於 SpaceClaim 的
全域誤報。載入時以 UTF-8 逐位元讀回，內容與先前內嵌字串完全一致。
"""
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent


def load_script(stem: str) -> str:
    """讀取 <stem>.ironpy 的原始內容（逐位元，UTF-8）。"""
    return (_SCRIPT_DIR / (stem + ".ironpy")).read_text(encoding="utf-8")
