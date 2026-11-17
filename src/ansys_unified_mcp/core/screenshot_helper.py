# -*- coding: utf-8 -*-
"""跨模組統一截圖路徑解析與 FastMCP 影像內容封裝工具。"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional

from ansys_unified_mcp.core.paths import resolve_runtime_dir

_SCREENSHOT_MAX_EDGE = 1568


def resolve_screenshot_path(
    file_path: str = "",
    default_name: str = "screenshot.png",
) -> Path:
    """解析截圖輸出絕對路徑，自動補上 .png 副檔名與建立父目錄。"""
    raw = (file_path or "").strip() or default_name
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = resolve_runtime_dir() / "screenshots" / candidate
    if not candidate.suffix:
        candidate = candidate.with_suffix(".png")
    candidate = candidate.resolve()
    candidate.parent.mkdir(parents=True, exist_ok=True)
    return candidate


def screenshot_image_content(
    path: str | Path,
    max_edge: int = _SCREENSHOT_MAX_EDGE,
) -> tuple[Any, Optional[str]]:
    """讀取本機截圖檔並轉為 MCP ImageContent；必要時等比例縮圖。回傳 (content, note)。"""
    from fastmcp.utilities.types import Image

    str_path = str(path)
    try:
        from PIL import Image as PILImage
    except ImportError:
        PILImage = None

    if PILImage is None:
        ext = os.path.splitext(str_path)[1].lower().lstrip(".")
        if ext not in ("png", "jpg", "jpeg", "gif"):
            return None, f"未安裝 Pillow，無法將 .{ext} 轉為可回傳的影像"
        return Image(path=str_path).to_image_content(), None

    import io

    with PILImage.open(str_path) as im:
        im.load()
        note = None
        if max(im.size) > max_edge:
            orig = im.size
            im.thumbnail((max_edge, max_edge))
            note = f"回傳影像已由 {orig[0]}x{orig[1]} 縮為 {im.size[0]}x{im.size[1]}（檔案為原尺寸）"
        buf = io.BytesIO()
        im.convert("RGB").save(buf, format="PNG")
    return Image(data=buf.getvalue(), format="png").to_image_content(), note


def finalize_screenshot_response(
    env: dict[str, Any],
    return_image: bool = True,
    as_tool_result: bool = False,
) -> Any:
    """依規範處理截圖回傳信封與可選的 FastMCP ToolResult 影像附加。"""
    out = dict(env)
    path_val = out.get("file_path")
    if out.get("ok") and path_val and os.path.isfile(str(path_val)) and return_image:
        try:
            img, note = screenshot_image_content(str(path_val))
            out["image_returned"] = img is not None
            if note:
                out.setdefault("warnings", []).append(note)
            if as_tool_result and img is not None:
                from fastmcp.tools.base import ToolResult
                from mcp.types import TextContent

                return ToolResult(
                    content=[
                        TextContent(type="text", text=json.dumps(out, ensure_ascii=False)),
                        img,
                    ],
                    structured_content=out,
                    is_error=False,
                )
        except Exception as exc:
            out.setdefault("warnings", []).append(f"影像讀取失敗: {exc}")
            out.setdefault("image_returned", False)
    else:
        out.setdefault("image_returned", False)
    return out
