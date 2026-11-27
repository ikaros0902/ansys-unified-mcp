# -*- coding: utf-8 -*-
"""BGA-shadow 與全板 Z 軸位移平面擬合（Leveling）之薄層包裝與獨立 CLI。

本模組為 Track 1（無 ODB++ ROM）與 Track 2（有 ODB++ Trace Mapping）共用的
後處理入口，延遲動態載入同層 `odb_workflow/1_Scripts/level_bga_shadow.py`，
不依賴 `ansys_unified_mcp` 套件。

注意：在處理 `--help` 與無參數 usage 分支前嚴禁匯入 `numpy`，確保於未安裝科學計算
套件的精簡 Python 環境中亦可正常執行 CLI 說明檢查。
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

_UPSTREAM_SCRIPT = (
    Path(__file__).resolve().parent / "odb_workflow" / "1_Scripts" / "level_bga_shadow.py"
)
_UPSTREAM_MODULE_NAME = "level_bga_shadow"
_UPSTREAM_CACHE: ModuleType | None = None

# ANSYS MAPDL /UNITS 指令對應之長度單位（僅允許已知公制系統）
_MAPDL_UNITS_TO_XY: dict[str, str] = {
    "MPA": "mm",
    "NMM": "mm",
    "SI": "m",
    "MKS": "m",
    "UMKS": "um",
}
_UNSUPPORTED_MAPDL_UNITS = {"CGS", "BIN", "BFT"}
_MIN_BOARD_SPAN_MM = 1e-3
_MAX_BOARD_SPAN_MM = 5000.0


def _load_upstream_leveling() -> ModuleType:
    """延遲動態載入上游 `odb_workflow/1_Scripts/level_bga_shadow.py`。

    若同路徑模組先前已透過其他測試或呼叫載入 `sys.modules["level_bga_shadow"]`，
    則直接複用該模組實例，確保 `InputError` 例外型別完全一致。
    """
    global _UPSTREAM_CACHE
    if _UPSTREAM_CACHE is not None:
        return _UPSTREAM_CACHE

    if not _UPSTREAM_SCRIPT.is_file():
        raise FileNotFoundError(f"找不到上游 Leveling 腳本: {_UPSTREAM_SCRIPT}")

    existing = sys.modules.get(_UPSTREAM_MODULE_NAME)
    if existing is not None:
        existing_file = getattr(existing, "__file__", None)
        if existing_file and Path(existing_file).resolve() == _UPSTREAM_SCRIPT.resolve():
            _UPSTREAM_CACHE = existing
            return existing

    spec = importlib.util.spec_from_file_location(_UPSTREAM_MODULE_NAME, _UPSTREAM_SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"無法建立模組規格以載入: {_UPSTREAM_SCRIPT}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[_UPSTREAM_MODULE_NAME] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(_UPSTREAM_MODULE_NAME, None)
        raise

    _UPSTREAM_CACHE = module
    return module


def get_input_error_class() -> type[Exception]:
    """回傳上游 `level_bga_shadow.InputError` 例外類別。"""
    return _load_upstream_leveling().InputError


def compute_leveled_warpage(
    x_mm: Any,
    y_mm: Any,
    uz_mm: Any,
    *,
    method: str = "OLS",
    mode: str = "detrend",
    flip_z: bool = False,
) -> dict[str, Any]:
    """計算去傾（Leveling）後之 PCB Z 軸翹曲量、方向性形態與傾斜角。

    Args:
        x_mm: 節點 X 座標（mm），一維序列或陣列。
        y_mm: 節點 Y 座標（mm），一維序列或陣列。
        uz_mm: 節點 Z 軸位移（mm），一維序列或陣列。
        method: 平面擬合方法（`"OLS"`、`"RANSAC"`、`"Huber"` 或 `"Tukey"`）。
        mode: 平面移除方式（`"detrend"` 或 `"rotate"`）。
        flip_z: 若為 `True`，於擬合前將 `uz_mm` 乘以 `-1`。

    Returns:
        包含 `warpage_um`、`warpage_mil`、`shape`（`"Smile"` / `"Cry"` / `"Undetermined"`）、
        `tilt_deg`、`z_leveled_mm` 與 `warnings` 之字典。

    Raises:
        InputError: 當輸入維度/長度不合法、含非有限值、`N < 3`、點集共線
            （設計矩陣 `[x, y, 1]` 秩 `< 3`）或方法/模式參數無效時拋出。
    """
    import numpy as np

    upstream = _load_upstream_leveling()
    input_error = upstream.InputError

    try:
        x = np.asarray(x_mm, dtype=float)
        y = np.asarray(y_mm, dtype=float)
        uz = np.asarray(uz_mm, dtype=float)
    except (TypeError, ValueError) as exc:
        raise input_error(f"輸入座標或位移無法轉換為浮點數陣列: {exc}") from exc

    if x.ndim != 1 or y.ndim != 1 or uz.ndim != 1:
        raise input_error(
            f"輸入必須為一維陣列，目前維度為 x={x.ndim}D, y={y.ndim}D, uz={uz.ndim}D"
        )

    if x.size == 0 or not (x.size == y.size == uz.size):
        raise input_error(
            f"輸入長度必須一致且非空，目前長度為 x={x.size}, y={y.size}, uz={uz.size}"
        )

    if not (np.all(np.isfinite(x)) and np.all(np.isfinite(y)) and np.all(np.isfinite(uz))):
        raise input_error("輸入陣列包含 NaN 或無限大數值，無法執行平面擬合")

    n_nodes = int(x.size)
    if n_nodes < 3:
        raise input_error(f"節點數不足以擬合平面：至少需 3 點，目前僅有 {n_nodes} 點")

    # 以平均座標置中後檢驗設計矩陣秩（與 [x, y, 1] 理論秩等價），避免大板座標偏移造成病態判定
    design_matrix = np.column_stack([x - x.mean(), y - y.mean(), np.ones(n_nodes, dtype=float)])
    if int(np.linalg.matrix_rank(design_matrix)) < 3:
        raise input_error("輸入點集共線或退化（設計矩陣秩 < 3），無法決定唯一擬合平面")

    warnings: list[str] = []
    if n_nodes < upstream.MIN_NODES:
        warnings.append(
            f"節點數僅 {n_nodes} 點，少於建議最小值 MIN_NODES={upstream.MIN_NODES}，翹曲結果僅供參考。"
        )

    uz_eff = -uz if flip_z else uz.copy()
    xo, yo, z_leveled_mm, info = upstream.level(x, y, uz_eff, method=method, mode=mode)
    shape_res = upstream.warpage_shape(xo, yo, z_leveled_mm)

    warpage_mm = float(shape_res["warpage_mm"])
    warpage_um = warpage_mm * 1000.0
    warpage_mil = warpage_mm * float(upstream.MIL_PER_MM)

    return {
        "warpage_um": float(warpage_um),
        "warpage_mil": float(warpage_mil),
        "shape": str(shape_res["shape"]),
        "tilt_deg": float(info["tilt_deg"]),
        "z_leveled_mm": np.asarray(z_leveled_mm, dtype=float),
        "warnings": warnings,
    }


def _scan_dat_units_directives(dat_path: Path) -> list[str]:
    """掃描 MAPDL `ds.dat` 檔中的 `/UNITS` 指令標記。"""
    found: list[str] = []
    units_re = re.compile(r"^\s*/units\s*,\s*([A-Za-z0-9_]+)", re.IGNORECASE)
    with dat_path.open("r", encoding="latin-1", errors="replace") as handle:
        for line in handle:
            match = units_re.match(line)
            if match:
                found.append(match.group(1).upper())
    return found


def _run_direct_cli(args: argparse.Namespace) -> int:
    """執行單組 Mechanical 匯出結果檔與 `ds.dat` 之直接平面擬合流程。"""
    import numpy as np

    upstream = _load_upstream_leveling()
    input_error = upstream.InputError

    try:
        z_unit = str(args.z_unit).lower()
        xy_unit = str(args.xy_unit).lower()
        if z_unit not in upstream.UNIT_TO_MM or xy_unit not in upstream.UNIT_TO_MM:
            raise input_error("z_unit 與 xy_unit 僅支援 m、mm、um")

        res_path = Path(args.result).resolve()
        dat_path = Path(args.dat).resolve()
        nodes, vals, col_header, head_unit = upstream.read_displacement(
            res_path, args.value_column
        )

        # CLI 直接處理匯出檔時，檔頭必須具備明確單位且與 z_unit 完全一致
        if not head_unit:
            raise input_error(
                f"{res_path.name}: 欄位 '{col_header}' 缺少明確單位標記，請確認匯出檔頭單位後重試"
            )
        if head_unit != z_unit:
            raise input_error(
                f"{res_path.name}: 欄位 '{col_header}' 單位為 '{head_unit}'，與指定的 z_unit='{z_unit}' 不符"
            )

        xyz_map, dat_consistent_units = upstream.read_nblock(
            dat_path, {int(n) for n in nodes}
        )
        if dat_consistent_units:
            mapped_consistent = _MAPDL_UNITS_TO_XY.get(dat_consistent_units.upper())
            if mapped_consistent and mapped_consistent != xy_unit:
                raise input_error(
                    f"{dat_path.name}: 檔案宣告 consistent {dat_consistent_units} units，與 xy_unit='{xy_unit}' 不符"
                )

        for directive in _scan_dat_units_directives(dat_path):
            if directive in _UNSUPPORTED_MAPDL_UNITS:
                raise input_error(
                    f"{dat_path.name}: /UNITS,{directive} 非公制 mm/m/um 系統，無法與 xy_unit='{xy_unit}' 對齊"
                )
            mapped_dir = _MAPDL_UNITS_TO_XY.get(directive)
            if mapped_dir and mapped_dir != xy_unit:
                raise input_error(
                    f"{dat_path.name}: /UNITS,{directive} 對應 '{mapped_dir}'，與 xy_unit='{xy_unit}' 不符"
                )

        keep = np.array([int(n) in xyz_map for n in nodes], dtype=bool)
        if not keep.any():
            raise input_error(
                f"{res_path.name} 與 {dat_path.name} 無任何共同節點，兩者可能非同一次求解產物"
            )

        warnings: list[str] = []
        if not keep.all():
            dropped = int((~keep).sum())
            warnings.append(
                f"{dropped}/{len(nodes)} 個節點未出現於 {dat_path.name} 的 NBLOCK 中並已略過。"
            )

        nodes_kept = nodes[keep]
        vals_kept = vals[keep]
        coords_mm = np.array([xyz_map[int(n)] for n in nodes_kept], dtype=float) * upstream.UNIT_TO_MM[xy_unit]
        uz_mm = vals_kept * upstream.UNIT_TO_MM[z_unit]

        span_x = float(np.ptp(coords_mm[:, 0]))
        span_y = float(np.ptp(coords_mm[:, 1]))
        max_span = max(span_x, span_y)
        if max_span < _MIN_BOARD_SPAN_MM or max_span > _MAX_BOARD_SPAN_MM:
            raise input_error(
                f"節點外框尺寸 ({span_x:.4g} x {span_y:.4g} mm) 超出合理物理範圍 "
                f"[{_MIN_BOARD_SPAN_MM}, {_MAX_BOARD_SPAN_MM}] mm，請檢查 xy_unit='{xy_unit}' 是否正確"
            )

        res = compute_leveled_warpage(
            coords_mm[:, 0],
            coords_mm[:, 1],
            uz_mm,
            method=args.method,
            mode=args.mode,
            flip_z=bool(args.flip_z),
        )
        all_warnings = warnings + res["warnings"]
        scope_label = (
            "Full-Board Leveled" if args.scope == "full-board" else "BGA-Shadow Leveled"
        )

        if args.json:
            payload = {
                "scope": scope_label,
                "nodes": int(len(nodes_kept)),
                "warpage_um": res["warpage_um"],
                "warpage_mil": res["warpage_mil"],
                "shape": res["shape"],
                "tilt_deg": res["tilt_deg"],
                "warnings": all_warnings,
            }
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(
                f"RESULT [{scope_label}]: nodes={len(nodes_kept)}, "
                f"warpage={res['warpage_um']:.3f} um ({res['warpage_mil']:.4f} mil), "
                f"shape={res['shape']}, tilt={res['tilt_deg']:.5f} deg"
            )
            for msg in all_warnings:
                print(f"WARNING: {msg}")

        if all_warnings and not args.accept_warnings:
            return upstream.EXIT_WARN
        return upstream.EXIT_OK
    except input_error as exc:
        print(f"INPUT ERROR: {exc}")
        return upstream.EXIT_INPUT
    except (OSError, ValueError) as exc:
        print(f"INPUT ERROR: {type(exc).__name__}: {exc}")
        return upstream.EXIT_INPUT


def build_parser() -> argparse.ArgumentParser:
    """建立命令列參數解析器。"""
    parser = argparse.ArgumentParser(
        prog="level_wrapper.py",
        description=(
            "PCB 熱翹曲 Z 軸位移平面擬合（Leveling）薄層包裝 CLI。"
            "支援透過專案 JSON 委派上游批次流程，或直接對單組匯出位移與 ds.dat 執行計算。"
        ),
    )
    parser.add_argument(
        "project_json",
        nargs="?",
        help="專案設定 JSON 路徑（委派給上游 level_bga_shadow.py 執行）。",
    )
    parser.add_argument("--case", default=None, help="搭配 project_json 使用，僅執行指定案例名稱。")
    parser.add_argument("--result", default=None, help="直接模式：Mechanical 匯出 Z 位移文字/CSV 檔路徑。")
    parser.add_argument("--dat", default=None, help="直接模式：Mechanical 求解器 ds.dat 路徑。")
    parser.add_argument(
        "--z-unit",
        default="mm",
        choices=("mm", "m", "um"),
        help="直接模式之匯出 Z 位移單位（預設 mm，須與檔頭單位一致）。",
    )
    parser.add_argument(
        "--xy-unit",
        default="mm",
        choices=("mm", "m", "um"),
        help="直接模式之 ds.dat 節點座標單位（預設 mm）。",
    )
    parser.add_argument("--value-column", default=None, help="指定匯出檔中的 Z 位移欄位名稱。")
    parser.add_argument(
        "--method",
        default="OLS",
        choices=("OLS", "RANSAC", "Huber", "Tukey"),
        help="平面擬合演算法（預設 OLS）。",
    )
    parser.add_argument(
        "--mode",
        default="detrend",
        choices=("detrend", "rotate"),
        help="平面移除模式（預設 detrend）。",
    )
    parser.add_argument("--flip-z", action="store_true", help="擬合前將 Z 位移乘以 -1。")
    parser.add_argument(
        "--scope",
        default="bga-shadow",
        choices=("bga-shadow", "full-board"),
        help="報告範圍標註（bga-shadow 或 full-board）。",
    )
    parser.add_argument("--accept-warnings", action="store_true", help="允許存在警告時仍回傳 Exit Code 0。")
    parser.add_argument("--json", action="store_true", help="直接模式以 JSON 格式輸出結果。")
    return parser


def main(argv: list[str] | None = None) -> int:
    """命令列進入點。無參數或 `--help` 時於匯入 `numpy` 前直接印出說明並回傳 0。"""
    args_list = sys.argv[1:] if argv is None else list(argv)
    parser = build_parser()

    if not args_list:
        parser.print_help()
        return 0

    args = parser.parse_args(args_list)

    if args.project_json:
        upstream = _load_upstream_leveling()
        return int(upstream.run(Path(args.project_json), only_case=args.case))

    if args.result or args.dat:
        if not (args.result and args.dat):
            print("INPUT ERROR: 直接模式必須同時提供 --result 與 --dat。", file=sys.stderr)
            return 3
        return _run_direct_cli(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
