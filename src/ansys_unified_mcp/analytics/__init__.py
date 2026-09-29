"""ANSYS Unified MCP 2.0 - 分析、後處理、報告與檢索子系統 (Analytics Subsystem).

涵蓋四大核心分析與報告職責：
- postprocessing: 有限元結果場提取與顯式日誌解析管線 (DPF / Explicit)
- reporting: 自包含 HTML 視覺化儀表板與向量 SVG 圖表合成
- docsearch: 本地 SQLite FTS5 文件檢索與 API 參照
"""

from __future__ import annotations
