# -*- coding: utf-8 -*-
"""驗證 SpaceClaimDriver 與 MechanicalDriver 對 ANSYS 2025 R1 (v251) 及動態 AWP_ROOT 之探測支援。"""

import os
from unittest.mock import patch
from pathlib import Path

from ansys_unified_mcp.products.geometry.driver import SpaceClaimDriver
from ansys_unified_mcp.products.mechanical.driver import MechanicalDriver


def test_spaceclaim_driver_awp_root_detection(tmp_path):
    """驗證 SpaceClaimDriver 能正確透過 AWP_ROOT 環境變數找到 SpaceClaim.exe。"""
    mock_scdm_dir = tmp_path / "scdm"
    mock_scdm_dir.mkdir(parents=True)
    mock_exe = mock_scdm_dir / "SpaceClaim.exe"
    mock_exe.write_text("mock executable")

    with patch.dict(os.environ, {"AWP_ROOT251": str(tmp_path)}):
        driver = SpaceClaimDriver()
        ok, msg = driver.validate_prerequisites()
        assert ok is True
        assert "AWP_ROOT251" in msg
        assert driver.solver_bin == str(mock_exe)


def test_mechanical_driver_awp_root_detection(tmp_path):
    """驗證 MechanicalDriver 能正確透過 AWP_ROOT 環境變數找到 ansys251.exe 或 ansys.exe。"""
    mock_bin_dir = tmp_path / "ansys" / "bin" / "winx64"
    mock_bin_dir.mkdir(parents=True)
    mock_exe = mock_bin_dir / "ansys251.exe"
    mock_exe.write_text("mock executable")

    with patch.dict(os.environ, {"AWP_ROOT251": str(tmp_path)}):
        driver = MechanicalDriver()
        ok, msg = driver.validate_prerequisites()
        assert ok is True
        assert "AWP_ROOT251" in msg
        assert driver.solver_bin == str(mock_exe)
