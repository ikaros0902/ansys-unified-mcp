# -*- coding: utf-8 -*-
"""check_file_policy 政策檢查腳本的單元測試。

驗證三種檢查的核心邏輯（ascii / abs-path / skill-lines），全部在 tmp_path 造樣本，
不觸碰真實專案檔案，符合測試隔離原則。
"""

import importlib.util
from pathlib import Path

# 以檔案路徑動態載入 scripts/maintenance/check_file_policy.py（非套件模組）
_MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "maintenance"
    / "check_file_policy.py"
)
_spec = importlib.util.spec_from_file_location("check_file_policy", _MODULE_PATH)
cfp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cfp)


# ===== ascii 檢查：ANSYS 內嵌腳本註解必須純 ASCII =====

def test_ascii_flags_non_ascii_comment(tmp_path: Path):
    f = tmp_path / "listener.py"
    # 第 2 行為含繁中的註解，應被標記
    f.write_text("x = 1\n# 這是中文註解\ny = 2\n", encoding="utf-8")
    violations = cfp.check_ascii(f)
    assert len(violations) == 1
    assert violations[0][0] == 2  # 行號


def test_ascii_passes_pure_ascii(tmp_path: Path):
    f = tmp_path / "listener.py"
    f.write_text("x = 1  # pure ascii comment\ny = 2\n", encoding="utf-8")
    assert cfp.check_ascii(f) == []


# ===== abs-path 檢查：不得硬編碼機器專屬絕對路徑 =====

def test_abs_path_flags_windows_user_path(tmp_path: Path):
    f = tmp_path / "config.py"
    f.write_text('P = "C:/Users/someone/data.pmdb"\n', encoding="utf-8")
    violations = cfp.check_abs_path(f)
    assert len(violations) == 1
    assert violations[0][0] == 1


def test_abs_path_flags_drive_root(tmp_path: Path):
    f = tmp_path / "config.py"
    f.write_text('# ok line\nP = r"D:\\Ikaros\\model.scdoc"\n', encoding="utf-8")
    violations = cfp.check_abs_path(f)
    assert len(violations) == 1
    assert violations[0][0] == 2


def test_abs_path_passes_relative(tmp_path: Path):
    f = tmp_path / "config.py"
    f.write_text('P = "data/model.scdoc"\nQ = "./out.rst"\n', encoding="utf-8")
    assert cfp.check_abs_path(f) == []


# ===== skill-lines 檢查：SKILL.md 不得超過 150 行 =====

def test_skill_lines_flags_oversized(tmp_path: Path):
    f = tmp_path / "SKILL.md"
    f.write_text("\n".join(f"line {i}" for i in range(151)), encoding="utf-8")
    violations = cfp.check_skill_lines(f, limit=150)
    assert len(violations) == 1


def test_skill_lines_passes_within_limit(tmp_path: Path):
    f = tmp_path / "SKILL.md"
    f.write_text("\n".join(f"line {i}" for i in range(150)), encoding="utf-8")
    assert cfp.check_skill_lines(f, limit=150) == []
