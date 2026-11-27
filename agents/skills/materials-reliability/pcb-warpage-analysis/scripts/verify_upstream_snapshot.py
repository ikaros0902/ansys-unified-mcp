"""驗證上游 ODB 工作流快照與 UPSTREAM_MANIFEST.json 之二進位 SHA-256 一致性。"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def compute_sha256(file_path: Path) -> str:
    """以二進位串流方式計算檔案的 SHA-256 雜湊值（不受換行轉換影響）。"""
    digest = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_snapshot(manifest_path: Path, upstream_dir: Path | None = None) -> int:
    """比對本機快照檔案與 Manifest（及選用的上游目錄）之 SHA-256。"""
    if not manifest_path.is_file():
        print(f"[ERROR] 找不到 Manifest 檔案: {manifest_path}", file=sys.stderr)
        return 1

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[ERROR] 讀取 Manifest 失敗 ({manifest_path}): {exc}", file=sys.stderr)
        return 1

    entries = manifest.get("files")
    if not isinstance(entries, list):
        print("[ERROR] Manifest 格式錯誤：缺少有效的 'files' 清單。", file=sys.stderr)
        return 1

    if upstream_dir is not None and not upstream_dir.is_dir():
        print(f"[ERROR] 找不到上游目錄: {upstream_dir}", file=sys.stderr)
        return 1

    # UPSTREAM_MANIFEST.json 位於 <SKILL>/scripts/ 下，故上兩層即為 <SKILL> 根目錄
    skill_root = manifest_path.resolve().parent.parent

    checked_count = 0
    skipped_modified = 0
    mismatches: list[str] = []

    for entry in entries:
        dest_rel = entry.get("dest_path")
        source_rel = entry.get("source_path")
        expected_sha = entry.get("sha256")
        is_modified = bool(entry.get("modified", False))

        if not dest_rel or not source_rel or not expected_sha:
            mismatches.append(f"Manifest 項目欄位不完整: {entry}")
            continue

        dest_path = skill_root / dest_rel

        # 僅對未經本地修改 (modified: false) 的檔案執行嚴格 SHA-256 一致性驗證
        if is_modified:
            skipped_modified += 1
            if not dest_path.is_file():
                mismatches.append(f"[MISSING] 本地修改檔案遺失: {dest_rel}")
            continue

        checked_count += 1
        if not dest_path.is_file():
            mismatches.append(f"[MISSING] 目的端檔案不存在: {dest_rel}")
            continue

        dest_sha = compute_sha256(dest_path)
        if dest_sha != expected_sha:
            mismatches.append(
                f"[HASH MISMATCH] {dest_rel}: 實際={dest_sha}, Manifest={expected_sha}"
            )

        if upstream_dir is not None:
            upstream_path = upstream_dir / source_rel
            if not upstream_path.is_file():
                mismatches.append(f"[MISSING UPSTREAM] 上游檔案不存在: {source_rel}")
                continue
            upstream_sha = compute_sha256(upstream_path)
            if upstream_sha != expected_sha:
                mismatches.append(
                    f"[UPSTREAM DRIFT] {source_rel} -> {dest_rel}: "
                    f"上游={upstream_sha}, Manifest={expected_sha}"
                )

    if mismatches:
        print(
            f"[FAIL] 快照驗證失敗：共發現 {len(mismatches)} 筆差異"
            f"（已檢查 {checked_count} 筆未修改檔案，略過 {skipped_modified} 筆已修改檔案）。",
            file=sys.stderr,
        )
        for msg in mismatches:
            print(f"  - {msg}", file=sys.stderr)
        return 1

    upstream_note = f"，且與上游目錄一致 ({upstream_dir})" if upstream_dir is not None else ""
    print(
        f"[PASS] 快照驗證通過：已檢查 {checked_count} 筆 modified=false 檔案"
        f"（略過 {skipped_modified} 筆 modified=true 檔案）{upstream_note}。"
    )
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """解析命令列參數。"""
    default_manifest = Path(__file__).resolve().parent / "UPSTREAM_MANIFEST.json"
    parser = argparse.ArgumentParser(
        description="驗證 pcb-warpage-analysis 內嵌上游快照的二進位 SHA-256 一致性。"
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=default_manifest,
        help="UPSTREAM_MANIFEST.json 路徑（預設為同目錄下的 UPSTREAM_MANIFEST.json）。",
    )
    parser.add_argument(
        "--upstream",
        type=Path,
        default=None,
        help="選填：上游來源目錄路徑，提供時同步比對上游原始檔案雜湊值。",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """程式進入點。"""
    args = parse_args(argv)
    return verify_snapshot(args.manifest, args.upstream)


if __name__ == "__main__":
    raise SystemExit(main())
