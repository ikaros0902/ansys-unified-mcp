# -*- coding: utf-8 -*-
"""一次性腳本：連線已開啟的 SpaceClaim，整排簡化 RAM+socket。

直接呼叫底層 sim_impl.call_tool，不經由 MCP 客戶端。
用法:
    .\.venv\Scripts\python.exe scripts\run_ram_simplify_batch.py \
        --motherboard JVPCB1074973E --ram DIMM_DDR5_EGS --socket J33
"""
import argparse
import asyncio
import sys

from ansys_unified_mcp.products.geometry import call_dispatch as sim_impl


def _text(res):
    try:
        return "\n".join(c.text for c in res)
    except Exception:
        return str(res)


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--motherboard", required=True)
    ap.add_argument("--ram", required=True)
    ap.add_argument("--socket", required=True)
    ap.add_argument("--result-prefix", default="RAM_simplified")
    ap.add_argument("--ns-prefix", default="ram_bottom")
    ap.add_argument("--tol-mm", type=float, default=2.0)
    ap.add_argument("--component-name", default="RAM_simplified")
    ap.add_argument("--no-move", action="store_true", help="不要移入新 component")
    ap.add_argument("--no-hide", action="store_true", help="不要抑制原始 body")
    ap.add_argument("--dry-run", action="store_true", help="只連線並列出 body，不執行簡化")
    args = ap.parse_args()

    # 1) 連線（自動掃描 50051-50055 連上已開的 SpaceClaim）
    _log = open("ram_result_utf8.log", "w", encoding="utf-8")

    def emit(*parts):
        line = " ".join(str(p) for p in parts)
        print(line)
        _log.write(line + "\n")
        _log.flush()

    emit("[1/3] 連線 SpaceClaim ...")
    launch = await sim_impl.call_tool("geometry_launch", {})
    launch_msg = _text(launch)
    emit(launch_msg)
    if "已連線" not in launch_msg and "connected" not in launch_msg.lower():
        emit("連線失敗，中止。")
        return 2

    # 2) 列出 body，核對名稱
    emit("\n[2/3] 列出當前設計 body ...")
    try:
        bodies = _text(await sim_impl.call_tool("geometry_list_bodies", {}))
    except Exception as exc:  # noqa: BLE001
        import traceback
        emit("list_bodies 失敗：", exc)
        emit(traceback.format_exc())
        emit("提示：若顯示 'No active design'，表示 SpaceClaim 已連線但沒有開啟任何設計文件。")
        return 4
    emit(bodies)

    for label, nm in (("motherboard", args.motherboard), ("ram", args.ram), ("socket", args.socket)):
        if nm not in bodies:
            emit(f"\n⚠️  找不到 {label} body 名稱 '{nm}'（未出現在上面的清單中）。")
            if not args.dry_run:
                return 3

    if args.dry_run:
        emit("\n[dry-run] 僅列出 body，不執行簡化。")
        return 0

    # 3) 整排批次簡化
    emit("\n[3/3] 執行 geometry_simplify_ram_batch ...")
    out = _text(await sim_impl.call_tool("geometry_simplify_ram_batch", {
        "motherboard": args.motherboard,
        "ram": args.ram,
        "socket": args.socket,
        "result_prefix": args.result_prefix,
        "ns_prefix": args.ns_prefix,
        "tol_mm": args.tol_mm,
        "move_to_component": not args.no_move,
        "component_name": args.component_name,
        "hide_source": not args.no_hide,
    }))
    emit(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
