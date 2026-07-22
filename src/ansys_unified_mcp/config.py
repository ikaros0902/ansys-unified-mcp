import os
import winreg
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class AnsysConfig:
    version: str
    root_path: Path
    workbench_exe: Path
    mechanical_exe: Path
    fluent_exe: Path
    cfx_solve_exe: Path
    cfx_pre_exe: Path
    mapdl_exe: Path
    lsdyna_exe: Path

def _find_ansys_registry() -> Dict[str, str]:
    """掃描 Windows 登錄檔尋找所有已安裝的 ANSYS 版本。"""
    versions = {}
    try:
        # ANSYS 通常將安裝路徑寫在 HKLM\SOFTWARE\ANSYS, Inc.\ANSYS
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\ANSYS, Inc.\ANSYS")
        for i in range(100):
            try:
                ver = winreg.EnumKey(key, i)
                sub_key = winreg.OpenKey(key, ver)
                # 某些版本直接存在這裡，或者在安裝路徑中
                install_dir, _ = winreg.QueryValueEx(sub_key, "InstallDir")
                versions[ver] = install_dir
            except EnvironmentError:
                break
    except EnvironmentError:
        pass
    return versions

def get_config() -> AnsysConfig:
    """獲取 ANSYS 系統設定，自動推導各模組路徑。"""
    ansys_root = os.environ.get("ANSYS_ROOT")
    version = "251" # 預設 v251
    root_path = None

    if ansys_root and Path(ansys_root).exists():
        root_path = Path(ansys_root)
        # 嘗試從路徑名推導版本，例如 v251
        name = root_path.name
        if name.startswith("v") and name[1:].isdigit():
            version = name[1:]
    else:
        # 自動從登錄檔偵測
        registry_versions = _find_ansys_registry()
        if registry_versions:
            # 取最新版本
            version = max(registry_versions.keys())
            root_path = Path(registry_versions[version])
        else:
            # Fallback 猜測
            fallback = Path(rf"C:\Program Files\ANSYS Inc\v{version}")
            if fallback.exists():
                root_path = fallback

    if not root_path or not root_path.exists():
        raise RuntimeError(f"找不到 ANSYS 安裝路徑。請確保已安裝 ANSYS 或設定 ANSYS_ROOT 環境變數。")

    # 推導各模組執行檔相對路徑 (基於標準安裝結構)
    wb_exe = root_path / "Framework" / "bin" / "Win64" / "RunWB2.exe"
    mech_exe = root_path / "aisol" / "bin" / "winx64" / "AnsysWBU.exe"
    fluent_exe = root_path / "fluent" / "ntbin" / "win64" / "fluent.exe"
    cfx_solve = root_path / "CFX" / "bin" / "cfx5solve.exe"
    cfx_pre = root_path / "CFX" / "bin" / "cfx5pre.exe"
    mapdl_exe = root_path / "ansys" / "bin" / "winx64" / "ANSYS.exe"
    lsdyna_exe = root_path / "ansys" / "bin" / "winx64" / "lsdyna.exe" # 依實際安裝可能不同

    # 寫回環境變數供相依套件使用
    os.environ["AWP_ROOT" + version] = str(root_path)

    return AnsysConfig(
        version=version,
        root_path=root_path,
        workbench_exe=wb_exe,
        mechanical_exe=mech_exe,
        fluent_exe=fluent_exe,
        cfx_solve_exe=cfx_solve,
        cfx_pre_exe=cfx_pre,
        mapdl_exe=mapdl_exe,
        lsdyna_exe=lsdyna_exe
    )

config = get_config()
