# -*- coding: utf-8 -*-
# [!IMPORTANT] 此檔案是對外部使用者的官方安裝入口，請勿因重構衝動刪除。
#
# docs/deployment/DEPLOYMENT_SOP.md 的方案 A（Claude Desktop）與方案 B（Antigravity）
# 皆明確教學新使用者將其 AI 客戶端設定檔指向本檔案（而非 `python -m ansys_unified_mcp.__main__`）。
# 本機這份專案自己的 pyproject.toml [project.scripts] 與 mcp_config.json 確實未經過此檔案，
# 但那只代表「本機開發環境不依賴它」，不代表「可安全刪除」——刪除會讓依照 DEPLOYMENT_SOP.md
# 安裝的外部使用者設定檔直接失效。
#
# 此檔案本身也不是 Phase 2 計畫文件所指的「巨石伺服器」問題：巨石問題（單一 FastMCP 一次性
# 載入全部工具）來自 __main__.py 的 ANSYS_MCP_PROFILE 預設值為 "all"，與此入口腳本是否存在
# 無關。若要刪除此檔案，必須同步改寫 DEPLOYMENT_SOP.md 兩個方案的設定範例，並驗證改用
# `-m ansys_unified_mcp.__main__` 啟動時，src 目錄仍會被正確加入 sys.path（本檔案目前
# 做了這件事，見下方 sys.path.insert）。
import os
import sys
from pathlib import Path

# 自動將專案 src 目錄加入 sys.path，保證無論以何種方式啟動均能載入 ansys_unified_mcp
src_dir = Path(__file__).resolve().parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import runpy

if __name__ == "__main__":
    # 執行實際的 ANSYS MCP 伺服器主程式
    runpy.run_module("ansys_unified_mcp.__main__", run_name="__main__")
