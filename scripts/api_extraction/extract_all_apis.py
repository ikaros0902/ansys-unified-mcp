"""
ANSYS API 快照批次萃取總控腳本
依序萃取 SpaceClaim、Mechanical、optiSLang、LS-DYNA、PyMAPDL、PyDPF-Core、PyFluent、PyPrimeMesh、PyAnsys Sound 與 PyDyna 與 PyMechanical client 與 PyAnsys Geometry 與 PyOptiSLang 1.6.0、PyWorkbench 0.14.0 public module、PyAnsys Sherlock 2.1.4、PyAnsys Rocky 0.6.2、PyAnsys CFX 0.3.0、PyAnsys Speos 0.9.2 與 product gRPC/protobuf schemas 範圍內的 API。
"""

import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

# 加入當前 scripts 目錄
scripts_dir = Path(__file__).resolve().parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from extract_spaceclaim_api import extract_spaceclaim
from extract_mechanical_api import extract_mechanical
from extract_optislang_api import extract_optislang
from extract_optislang_core_api import extract_optislang_core_api
from extract_lsdyna_api import extract_lsdyna
from extract_mapdl_api import extract_mapdl_api
from extract_dpf_api import extract_dpf_api
from extract_fluent_api import extract_fluent_api
from extract_primemesh_api import extract_primemesh_api
from extract_sound_api import extract_sound_api
from extract_pydyna_api import extract_pydyna_api
from extract_mechanical_core_api import extract_mechanical_core_api
from extract_geometry_core_api import extract_geometry_core_api
from extract_workbench_api import extract_workbench_api
from extract_workbench_protocol_api import extract_workbench_protocol_api
from extract_product_protocol_apis import extract_product_protocol_apis


def main():
    if "--native-pe-exports" in sys.argv:
        written = build_native_export_snapshots()
        from ansys_unified_mcp.analytics.apikb.build import build_database

        result = build_database(force=True)
        print(f"Native PE export snapshots: {len(written)}; APIKB: {result.get('statistics')}")
        return
    if "--rea-metadata" in sys.argv:
        build_rea_metadata_snapshots()
        from render_rea_source_index import main as render_rea_source_index

        render_rea_source_index()
        from ansys_unified_mcp.analytics.apikb.build import build_database

        result = build_database(force=True)
        print(f"REA metadata snapshots indexed: {result.get('statistics')}")
        return

    print("=" * 60)
    print("開始執行 ANSYS API 快照批次萃取...")
    print("=" * 60)
    start_total = time.time()

    from extract_sherlock_api import extract_cfx_api, extract_rocky_api, extract_sherlock_api, extract_speos_api

    extraction_steps = (
        (
            "SpaceClaim",
            "[1/20] 萃取 SpaceClaim API (SpaceClaim.Api.V251.Scripting.dll)...",
            extract_spaceclaim,
        ),
        (
            "Mechanical",
            "[2/20] 萃取 Mechanical ACT & DataModel API (ansys-mechanical-stubs)...",
            extract_mechanical,
        ),
        (
            "optiSLang",
            "[3/20] 萃取 optiSLang API (ansys.optislang.core & scripting)...",
            extract_optislang,
        ),
        (
            "PyOptiSLang core",
            "[4/20] 萃取 PyOptiSLang 1.6.0 Optislang client API...",
            extract_optislang_core_api,
        ),
        (
            "LS-DYNA",
            "[5/20] 萃取 LS-DYNA & LS-PrePost API (Python, SCL, Keywords)...",
            extract_lsdyna,
        ),
        ("PyMAPDL", "[6/20] 萃取 PyMAPDL 文件覆蓋的 Python API...", extract_mapdl_api),
        ("PyDPF-Core", "[7/20] 萃取 PyDPF-Core 0.16.1 核心資料類別...", extract_dpf_api),
        ("PyFluent", "[8/20] 萃取 PyFluent 0.42.1 launcher API...", extract_fluent_api),
        ("PyPrimeMesh", "[9/20] 萃取 PyPrimeMesh 0.10.5 Client API...", extract_primemesh_api),
        ("PyAnsys Sound", "[10/20] 萃取 PyAnsys Sound 0.3.0 SoundComposer 與 Track...", extract_sound_api),
        ("PyDyna", "[11/20] 萃取 PyDyna 0.12.1 Deck API...", extract_pydyna_api),
        ("PyMechanical", "[12/20] 萃取 PyMechanical 0.13.2 client API...", extract_mechanical_core_api),
        ("PyAnsys Geometry", "[13/20] 萃取 PyAnsys Geometry 0.17.1 Modeler API...", extract_geometry_core_api),
        ("PyWorkbench", "[14/20] 萃取 PyWorkbench 0.14.0 public module exports...", extract_workbench_api),
        ("Workbench protocol", "[15/20] 萃取 ansys-api-workbench 0.4.0 gRPC schema...", extract_workbench_protocol_api),
        ("PyAnsys product protocols", "[16/20] 萃取 Mechanical/Geometry/Fluent/MAPDL/PrimeMesh/Discovery schemas...", extract_product_protocol_apis),
        ("PyAnsys Sherlock", "[17/20] 靜態擷取 Sherlock SDK 2.1.4 原始碼...", extract_sherlock_api),
        ("PyAnsys Rocky", "[18/20] 靜態擷取 Rocky SDK 0.6.2 原始碼...", extract_rocky_api),
        ("PyAnsys CFX", "[19/20] 靜態擷取 CFX SDK 0.3.0 原始碼...", extract_cfx_api),
        ("PyAnsys Speos", "[20/20] 靜態擷取 Speos SDK 0.9.2 原始碼...", extract_speos_api),
    )
    for name, message, extractor in extraction_steps:
        print(f"\n{message}")
        t0 = time.time()
        result = extractor()
        statistics = result.get("statistics") if isinstance(result, dict) else None
        if not isinstance(statistics, dict) or not any(
            isinstance(count, int) and count > 0
            for key, count in statistics.items()
            if key != "total_modules"
        ):
            raise RuntimeError(f"{name} API 擷取失敗，沒有有效 API 項目。")
        print(f"{name} 萃取耗時: {time.time() - t0:.2f} 秒")

    from render_protocol_dictionaries import main as render_protocol_dictionaries
    from render_rea_source_index import main as render_rea_source_index
    from render_sdk_dictionaries import main as render_sdk_dictionaries

    render_protocol_dictionaries()
    render_rea_source_index()
    render_sdk_dictionaries()

    print("\n[21/21] 建置 API 知識層 SQLite 索引庫 (api_kb.sqlite)...")
    t0 = time.time()
    try:
        from ansys_unified_mcp.analytics.apikb.build import build_database

        kb_res = build_database(force=True)
    except Exception as exc:
        print(f"API 知識庫建置失敗: {exc}")
        raise
    if not kb_res:
        raise RuntimeError("API 知識庫建置失敗，沒有回傳有效結果。")
    print(f"API 知識庫建置完成，耗時: {time.time() - t0:.2f} 秒，統計: {kb_res.get('statistics')}")

    print("\n" + "=" * 60)
    print(
        f"[SUCCESS] 全部 API 快照抽取與知識庫建置完畢！總耗時: {time.time() - start_total:.2f} 秒"
    )
    print(
        f"目錄位置: {(Path(__file__).resolve().parent.parent.parent / 'docs' / 'api_inventory').resolve()}"
    )
    print("=" * 60)


def _rea_payload(source: dict) -> dict:
    """支援 REA 直接輸出與 MCP data envelope。"""
    return source.get("data", source)



def build_native_export_snapshots() -> list[Path]:
    """Extract native PE exports as unverified API candidates."""
    import ctypes
    import re
    import shutil
    import subprocess

    readobj = os.environ.get("LLVM_READOBJ") or shutil.which("llvm-readobj")
    if not readobj:
        raise FileNotFoundError("llvm-readobj is required. Set LLVM_READOBJ or add it to PATH.")
    awp_value = os.environ.get("AWP_ROOT251")
    if not awp_value:
        raise RuntimeError("Set AWP_ROOT251 to the ANSYS 2025 R1 installation root.")
    awp_root = Path(awp_value)
    if not awp_root.is_dir():
        raise FileNotFoundError(f"ANSYS 2025 R1 installation root does not exist: {awp_root}")
    output_root = Path(__file__).resolve().parents[2] / "docs" / "api_inventory"
    targets = (
        (
            "apip_wrapper_native",
            "apip_wrapper_native_exports_api.json",
            "AnsysEM/ApipWrapper.dll",
            "AnsysEM APIP wrapper native exports; product mapping unverified",
        ),
        (
            "cfx_cadapi_native",
            "cfx_cadapi_native_exports_api.json",
            "CFX/lib/winnt-amd64/Ans.CFX.CadApi.dll",
            "CFX CadApi native exports; support status unverified",
        ),
        (
            "cfx_acmo_native",
            "cfx_acmo_native_exports_api.json",
            "CFX/lib/winnt-amd64/Ans.CFX.Acmo.dll",
            "CFX Acmo native exports; support status unverified",
        ),
        (
            "dpf_mechanicalresults_native",
            "dpf_mechanicalresults_native_exports_api.json",
            "dpf/bin/winx64/Ans.Dpf.MechanicalResults.dll",
            "DPF Mechanical Results plugin native export; support status unverified",
        ),
        (
            "dpf_engineeringdata_native",
            "dpf_engineeringdata_native_exports_api.json",
            "dpf/bin/winx64/Ans.Dpf.EngineeringData.dll",
            "DPF Engineering Data native export; support status unverified",
        ),
        (
            "dpf_abaqus_native",
            "dpf_abaqus_native_exports_api.json",
            "dpf/bin/winx64/Ans.Dpf.Abaqus.dll",
            "DPF Abaqus reader; support status unverified",
        ),
        (
            "dpf_cgns_native",
            "dpf_cgns_native_exports_api.json",
            "dpf/bin/winx64/Ans.Dpf.Cgns.dll",
            "DPF CGNS reader; support status unverified",
        ),
        (
            "dpf_compression_native",
            "dpf_compression_native_exports_api.json",
            "dpf/bin/winx64/Ans.Dpf.Compression.dll",
            "DPF compression component; support status unverified",
        ),
        (
            "dpf_femutils_native",
            "dpf_femutils_native_exports_api.json",
            "dpf/bin/winx64/Ans.Dpf.FEMutils.dll",
            "DPF FEM utilities; support status unverified",
        ),
        (
            "dpf_flowdiagram_native",
            "dpf_flowdiagram_native_exports_api.json",
            "dpf/bin/winx64/Ans.Dpf.FlowDiagram.dll",
            "DPF FlowDiagram component; support status unverified",
        ),
        (
            "dpf_grpc_native",
            "dpf_grpc_native_exports_api.json",
            "dpf/bin/winx64/Ans.Dpf.Grpc.dll",
            "DPF gRPC component; support status unverified",
        ),
        (
            "dpf_hdf5_native",
            "dpf_hdf5_native_exports_api.json",
            "dpf/bin/winx64/Ans.Dpf.Hdf5.dll",
            "DPF HDF5 component; support status unverified",
        ),
        (
            "dpf_livepost_native",
            "dpf_livepost_native_exports_api.json",
            "dpf/bin/winx64/Ans.Dpf.LivePost.dll",
            "DPF LivePost component; support status unverified",
        ),
        (
            "dpf_lsdynahgp_native",
            "dpf_lsdynahgp_native_exports_api.json",
            "dpf/bin/winx64/Ans.Dpf.LSDYNAHGP.dll",
            "DPF LS-DYNA HGP component; support status unverified",
        ),
        (
            "dpf_math_native",
            "dpf_math_native_exports_api.json",
            "dpf/bin/winx64/Ans.Dpf.Math.dll",
            "DPF math component; support status unverified",
        ),
        (
            "dpf_mechanical_native",
            "dpf_mechanical_native_exports_api.json",
            "dpf/bin/winx64/Ans.Dpf.Mechanical.dll",
            "DPF Mechanical component; support status unverified",
        ),
        (
            "dpf_native_native",
            "dpf_native_native_exports_api.json",
            "dpf/bin/winx64/Ans.Dpf.Native.dll",
            "DPF native component; support status unverified",
        ),
        (
            "dpf_pythonpluginwrapper_native",
            "dpf_pythonpluginwrapper_native_exports_api.json",
            "dpf/bin/winx64/Ans.Dpf.PythonPluginWrapper.dll",
            "DPF Python plugin wrapper; support status unverified",
        ),
        (
            "dpf_rbd_native",
            "dpf_rbd_native_exports_api.json",
            "dpf/bin/winx64/Ans.Dpf.Rbd.dll",
            "DPF rigid-body dynamics component; support status unverified",
        ),
        (
            "dpf_vtk_native",
            "dpf_vtk_native_exports_api.json",
            "dpf/bin/winx64/Ans.Dpf.Vtk.dll",
            "DPF VTK component; support status unverified",
        ),
        (
            "dpf_autodyn_native",
            "dpf_autodyn_native_exports_api.json",
            "dpf/plugins/dpf_autodyn/Ans.DPF.Autodyn.dll",
            "DPF AUTODYN plugin; support status unverified",
        ),
        (
            "dpf_cff_native",
            "dpf_cff_native_exports_api.json",
            "dpf/plugins/dpf_cff/Ans.Dpf.CFF.dll",
            "DPF CFF plugin; support status unverified",
        ),
        (
            "dpf_multiphysicsmapper_native",
            "dpf_multiphysicsmapper_native_exports_api.json",
            "dpf/plugins/dpf_multiphysicsmapper/Ans.Dpf.MultiphysicsMapper.dll",
            "DPF multiphysics mapper plugin; support status unverified",
        ),
        (
            "dpf_prime_native",
            "dpf_prime_native_exports_api.json",
            "dpf/plugins/dpf_prime/Ans.Dpf.Prime.dll",
            "DPF Prime plugin; support status unverified",
        ),
        (
            "dpf_datamodel_native",
            "dpf_datamodel_native_exports_api.json",
            "dpf/plugins/dpf_simulationdatamodel/Ans.Dpf.DataModel.dll",
            "DPF simulation data model plugin; support status unverified",
        ),
        (
            "dpf_systemcouplingmapping_native",
            "dpf_systemcouplingmapping_native_exports_api.json",
            "dpf/plugins/dpf_sysc/Ans.Dpf.SystemCouplingMapping.dll",
            "DPF System Coupling mapping plugin; support status unverified",
        ),
        (
            "lumerical_interopapi_native",
            "lumerical_interopapi_native_exports_api.json",
            "Lumerical/api/python/interopapi.dll",
            "Lumerical Python interop API; support status unverified",
        ),
        (
            "lumerical_interopapi_remote_native",
            "lumerical_interopapi_remote_native_exports_api.json",
            "Lumerical/api/python/interopapi-remote.dll",
            "Lumerical remote Python interop API; support status unverified",
        ),
        (
            "lumerical_lumapi_native",
            "lumerical_lumapi_native_exports_api.json",
            "Lumerical/api/tcl/lumapi.dll",
            "Lumerical Tcl API; support status unverified",
        ),
        (
            "rom_api_native",
            "rom_api_native_exports_api.json",
            "Addins/ROM/bin/Win64/Rom.Api.dll",
            "ROM native exports; official support status unverified",
        ),
        (
            "system_coupling_rpc_native",
            "system_coupling_rpc_native_exports_api.json",
            "SystemCoupling/runTime/winx64/bin/SysC.AnsRpc.Wrapper.dll",
            "System Coupling ANSRPC wrapper native exports; product API mapping unverified",
        ),
        (
            "system_coupling_participant_native",
            "system_coupling_participant_native_exports_api.json",
            "SystemCoupling/runTime/winx64/bin/SysC.SystemCouplingParticipant.dll",
            "System Coupling participant native exports; support status unverified",
        ),
        (
            "speos_apip_wrapper_native",
            "speos_apip_wrapper_native_exports_api.json",
            "Optical Products/Speos/bin/ApipWrapper.dll",
            "Speos APIP wrapper native exports; product API support unverified",
        ),
    )
    try:
        dbghelp = ctypes.WinDLL("dbghelp")
        undecorate = dbghelp.UnDecorateSymbolName
        undecorate.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint32, ctypes.c_uint32]
        undecorate.restype = ctypes.c_uint32
    except (AttributeError, OSError):
        undecorate = None

    def demangle(name: str) -> str:
        if undecorate is None or not name.startswith("?"):
            return ""
        try:
            source = name.encode("ascii")
        except UnicodeEncodeError:
            return ""
        buffer = ctypes.create_string_buffer(4096)
        if not undecorate(source, buffer, len(buffer), 0):
            return ""
        return buffer.value.decode("ascii", errors="replace")

    version_text = subprocess.run(
        [readobj, "--version"], check=True, capture_output=True, text=True, encoding="utf-8",
        errors="replace",
    ).stdout
    version_match = re.search(r"LLVM version ([^\s]+)", version_text)
    tool_version = version_match.group(1) if version_match else "unknown"
    written = []

    for product, filename, relative_binary, interface in targets:
        binary = awp_root / Path(relative_binary)
        if not binary.is_file():
            raise FileNotFoundError(f"Required v251 binary is missing: {binary}")
        binary_hash = hashlib.sha256(binary.read_bytes()).hexdigest()
        output_path = output_root / filename
        exports_text = subprocess.run(
            [readobj, "--coff-exports", str(binary)], check=True, capture_output=True,
            text=True, encoding="utf-8", errors="replace",
        ).stdout
        exports = []
        for block in re.findall(r"Export\s*\{(.*?)\}", exports_text, flags=re.S):
            ordinal_match = re.search(r"Ordinal:\s*(\d+)", block)
            rva_match = re.search(r"RVA:\s*(0x[0-9A-Fa-f]+)", block)
            name_match = re.search(r"Name:\s*([^\r\n]+)", block)
            if not ordinal_match or not rva_match:
                continue
            raw_name = name_match.group(1).strip() if name_match else ""
            signature = demangle(raw_name) if raw_name else ""
            if not raw_name:
                raw_name = f"ordinal_{ordinal_match.group(1)}"
            note = (
                f"PE export. Ordinal: {ordinal_match.group(1)}. RVA: {rva_match.group(1)}. "
                "This static symbol does not prove official support or runtime behavior."
            )
            if signature:
                note += f" Decoded symbol: {signature}."
            else:
                note += " This export name does not encode a function signature."
            exports.append(
                {"name": raw_name, "signature": signature, "doc": note}
            )
        if not exports:
            raise RuntimeError(f"No named or ordinal PE exports were read from {binary.name}.")
        names = [item["name"] for item in exports]
        if len(names) != len(set(names)):
            raise RuntimeError(f"Duplicate export names prevent stable indexing for {binary.name}.")

        snapshot = {
            "module": "NativeExports",
            "version": "v251",
            "interface": interface,
            "scope": (
                "This snapshot lists PE export names from llvm-readobj. An export name does not prove "
                "API support. A signature appears only when the MSVC symbol name contains type data. "
                "The extractor does not read function bodies or run the DLL."
            ),
            "sources": {
                "assembly": {
                    "path": f"$env:AWP_ROOT251/{relative_binary.replace(chr(92), '/')}",
                    "sha256": binary_hash,
                    "byte_length": binary.stat().st_size,
                },
                "analysis": {"tool": "llvm-readobj", "version": tool_version, "operation": "--coff-exports"},
            },
            "modules": {
                "NativeExports": {"doc": interface, "classes": {}, "functions": exports}
            },
            "statistics": {
                "total_modules": 1,
                "total_functions": len(exports),
                "demangled_signatures": sum(bool(item["signature"]) for item in exports),
            },
        }
        if output_path.exists():
            old = json.loads(output_path.read_text(encoding="utf-8"))
            old_hash = old.get("sources", {}).get("assembly", {}).get("sha256")
            if old_hash != binary_hash:
                raise FileExistsError(f"Refusing to replace a snapshot for a different binary: {output_path}")
        output_root.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=f"{output_path.stem}.", suffix=".tmp", dir=output_root)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
                json.dump(snapshot, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, output_path)
        except BaseException:
            Path(temp_name).unlink(missing_ok=True)
            raise
        written.append(output_path)
    return written


def build_rea_metadata_snapshots() -> list[Path]:
    """將本機 REA v251 managed metadata 轉為 APIKB 可索引的候選快照。"""
    repo_root = Path(__file__).resolve().parents[2]
    evidence_root = repo_root / ".audit" / "repo-restructure" / "rea-managed-v251"
    output_root = repo_root / "docs" / "api_inventory"
    components = (
        (
            "Ans.Rsm.JobManagement.json",
            "rsm_jobmanagement_rea_api.json",
            "rsm_jobmanagement_rea",
            "Remote Solve Manager JobManagement v251 REA metadata; product mapping and support status unverified",
        ),
        (
            "Ans.EngineeringData.Core.json",
            "engineeringdata_core_rea_api.json",
            "engineeringdata_core_rea",
            "Engineering Data Core v251 REA metadata; support status unverified",
        ),
        (
            "Ans.EngineeringData.DataProvider.json",
            "engineeringdata_dataprovider_rea_api.json",
            "engineeringdata_dataprovider_rea",
            "Engineering Data DataProvider v251 REA metadata; support status unverified",
        ),
        (
            "Ans.DesignModeler.Core.json",
            "designmodeler_core_rea_api.json",
            "designmodeler_core_rea",
            "DesignModeler Core v251 REA metadata; support status unverified",
        ),
        (
            "Ans.MaterialDesigner.Core.json",
            "materialdesigner_core_rea_api.json",
            "materialdesigner_core_rea",
            "Material Designer Core v251 REA metadata; support status unverified",
        ),
        (
            "ACP.Core.json",
            "acp_core_rea_api.json",
            "acp_core_rea",
            "ACP v251 core add-in REA metadata; support status unverified",
        ),
        (
            "MotionAPI.json",
            "motion_api_rea_api.json",
            "motion_api_rea",
            "ANSYS Motion v251 MotionAPI REA metadata; support status unverified",
        ),
        (
            "Ansys.Ansoft.SIwave.LibIronPythonCmd.json",
            "siwave_libironpythoncmd_rea_api.json",
            "siwave_libironpythoncmd_rea",
            "AnsysEM SIwave IronPython command library v251 REA candidate; support status unverified",
        ),
        (
            "Ans.AUTODYN.DataModel.json",
            "autodyn_rea_api.json",
            "autodyn_rea",
            "AUTODYN v251 REA managed metadata; support status unverified",
        ),
        (
            "Ans.DesignXplorer.PublicAPIs.json",
            "designxplorer_rea_api.json",
            "designxplorer_rea",
            "DesignXplorer v251 REA managed metadata; support status unverified",
        ),
        (
            "Ans.EngineeringData.DataModel.json",
            "engineeringdata_rea_api.json",
            "engineeringdata_rea",
            "Engineering Data v251 REA managed metadata; support status unverified",
        ),
        (
            "Ansys.Mechanical.Interfaces.json",
            "mechanical_interfaces_rea_api.json",
            "mechanical_interfaces_rea",
            "Mechanical Interfaces v251 REA managed metadata; support status unverified",
        ),
        (
            "Ansys.Mechanical.DataModel.json",
            "mechanical_datamodel_rea_api.json",
            "mechanical_datamodel_rea",
            "Mechanical DataModel v251 REA managed metadata; support status unverified",
        ),
        (
            "Ansys.Collaboration.Api.json",
            "discovery_collaboration_rea_api.json",
            "discovery_collaboration_rea",
            "Discovery Collaboration API v251 REA managed metadata; support status unverified",
        ),
        (
            "Ansys.Gateway.Api.json",
            "discovery_gateway_rea_api.json",
            "discovery_gateway_rea",
            "Discovery Gateway API v251 REA managed metadata; support status unverified",
        ),
        (
            "Ansys.Geometry.Api.json",
            "discovery_geometry_rea_api.json",
            "discovery_geometry_rea",
            "Discovery Geometry API v251 REA managed metadata; support status unverified",
        ),
        (
            "Ansys.OnScale.Api.json",
            "discovery_onscale_rea_api.json",
            "discovery_onscale_rea",
            "Discovery OnScale API v251 REA managed metadata; support status unverified",
        ),
        (
            "Ansys.Physics.Api.json",
            "discovery_physics_rea_api.json",
            "discovery_physics_rea",
            "Discovery Physics API v251 REA managed metadata; support status unverified",
        ),
        (
            "Ansys.Project.Api.json",
            "discovery_project_rea_api.json",
            "discovery_project_rea",
            "Discovery Project API v251 REA managed metadata; support status unverified",
        ),
        (
            "Ansys.Results.Api.json",
            "discovery_results_rea_api.json",
            "discovery_results_rea",
            "Discovery Results API v251 REA managed metadata; support status unverified",
        ),
        (
            "Ans.Ansoft.MaxwellAddinPlugin.json",
            "maxwell_addin_rea_api.json",
            "maxwell_addin_rea",
            "Maxwell Ansoft add-in v251 REA metadata; support status unverified",
        ),
        (
            "Ans.Ansoft.Q3DExtractorAddinPlugin.json",
            "q3d_addin_rea_api.json",
            "q3d_addin_rea",
            "Q3D Extractor Ansoft add-in v251 REA metadata; support status unverified",
        ),
        (
            "Ans.Ansoft.IcepakAddinPlugin.json",
            "icepak_ansoft_addin_rea_api.json",
            "icepak_ansoft_addin_rea",
            "Icepak Ansoft add-in v251 REA metadata; support status unverified",
        ),
        (
            "Ansys.Apip.Client.json",
            "granta_mi_rea_api.json",
            "granta_mi_rea",
            "Granta MI v251 REA managed metadata; support status unverified",
        ),
        (
            "Ans.MaterialDesigner.Wrapper.json",
            "materialdesigner_rea_api.json",
            "materialdesigner_rea",
            "Material Designer v251 REA managed metadata; support status unverified",
        ),
        (
            "Ans.TurboSystem.CCDInterface.json",
            "turbosystem_ccd_rea_api.json",
            "turbosystem_ccd_rea",
            "TurboSystem CCD interface v251 REA metadata; support status unverified",
        ),
        (
            "Ans.TurboSystem.CCMInterface.json",
            "turbosystem_ccm_rea_api.json",
            "turbosystem_ccm_rea",
            "TurboSystem CCM interface v251 REA metadata; support status unverified",
        ),
        (
            "Ans.TurboSystem.AFDCore.json",
            "turbosystem_afd_core_rea_api.json",
            "turbosystem_afd_core_rea",
            "TurboSystem AFDCore v251 REA metadata; support status unverified",
        ),
        (
            "Ans.TurboSystem.CCDCore.json",
            "turbosystem_ccd_core_rea_api.json",
            "turbosystem_ccd_core_rea",
            "TurboSystem CCDCore v251 REA metadata; support status unverified",
        ),
        (
            "Ans.TurboSystem.CPDCore.json",
            "turbosystem_cpd_core_rea_api.json",
            "turbosystem_cpd_core_rea",
            "TurboSystem CPDCore v251 REA metadata; support status unverified",
        ),
        (
            "Ans.TurboSystem.RTDCore.json",
            "turbosystem_rtd_core_rea_api.json",
            "turbosystem_rtd_core_rea",
            "TurboSystem RTDCore v251 REA metadata; support status unverified",
        ),
        (
            "Ans.Units.DataModel.json",
            "units_rea_api.json",
            "units_rea",
            "ANSYS Units DataModel v251 REA metadata; support status unverified",
        ),
        (
            "Ans.VistaTF.DataModel.json",
            "vista_tf_rea_api.json",
            "vista_tf_rea",
            "Vista TF DataModel v251 REA metadata; support status unverified",
        ),
        (
            "Ansys.ACT.Core.json",
            "act_core_rea_api.json",
            "act_core_rea",
            "ACT Core v251 REA managed metadata; support status unverified",
        ),
        (
            "Infrastructure.ApiDiscoveryV251.json",
            "api_discovery_rea_api.json",
            "api_discovery_rea",
            "API Server Discovery v251 REA metadata; product mapping unverified",
        ),
        (
            "Infrastructure.ApiGeometryV251.json",
            "api_geometry_rea_api.json",
            "api_geometry_rea",
            "API Server Geometry v251 REA metadata; product mapping unverified",
        ),
        (
            "Ansys.ACT.Interfaces.json",
            "act_interfaces_rea_api.json",
            "act_interfaces_rea",
            "ACT Interfaces v251 REA metadata; support status unverified",
        ),
        (
            "Ansys.ACTLSDYNA.Interfaces.json",
            "lsdyna_interfaces_rea_api.json",
            "lsdyna_interfaces_rea",
            "LS-DYNA ACT Interfaces v251 REA metadata; product mapping unverified",
        ),
        (
            "Ansys.Ansoft.CoreDotNet.json",
            "ansysem_coredotnet_rea_api.json",
            "ansysem_coredotnet_rea",
            "AnsysEM CoreDotNet v251 REA metadata; product mapping unverified",
        ),
        (
            "Ansys.Api.Additive.json",
            "additive_rea_api.json",
            "additive_rea",
            "Ansys Additive v251 REA metadata; product mapping unverified",
        ),
        (
            "SpaceClaim.Api.V251.json",
            "spaceclaim_core_rea_api.json",
            "spaceclaim_core_rea",
            "SpaceClaim Core API v251 REA metadata; support status unverified",
        ),
        (
            "Ans.AQWA.Core.json",
            "aqwa_addin_rea_api.json",
            "aqwa_addin_rea",
            "AQWA Core add-in v251 REA metadata; support status unverified",
        ),
        (
            "Ans.AQWA.RemoteItf.json",
            "aqwa_remote_itf_rea_api.json",
            "aqwa_remote_itf_rea",
            "AQWA RemoteItf v251 REA metadata; support status unverified",
        ),
        (
            "Ans.CFX.CFXCore.json",
            "cfx_addin_rea_api.json",
            "cfx_addin_rea",
            "CFX Core add-in v251 REA metadata; support status unverified",
        ),
        (
            "Ans.Fluent.json",
            "fluent_addin_rea_api.json",
            "fluent_addin_rea",
            "Fluent add-in v251 REA metadata; support status unverified",
        ),
        (
            "Ans.Icepak.Core.json",
            "icepak_addin_rea_api.json",
            "icepak_addin_rea",
            "Icepak Core add-in v251 REA metadata; support status unverified",
        ),
        (
            "Ans.Meshing.Core.json",
            "meshing_addin_rea_api.json",
            "meshing_addin_rea",
            "Meshing Core add-in v251 REA metadata; support status unverified",
        ),
        (
            "Ans.Polyflow.json",
            "polyflow_addin_rea_api.json",
            "polyflow_addin_rea",
            "Polyflow add-in v251 REA metadata; support status unverified",
        ),
        (
            "Ans.Sherlock.Addin.json",
            "sherlock_addin_rea_api.json",
            "sherlock_addin_rea",
            "Sherlock add-in v251 REA metadata; support status unverified",
        ),
        (
            "Ans.Ansoft.HFSSAddinPlugin.json",
            "hfss_addin_rea_api.json",
            "hfss_addin_rea",
            "HFSS Ansoft add-in v251 REA metadata; support status unverified",
        ),
        (
            "Ans.Ansoft.DesignerAddinPlugin.json",
            "designer_addin_rea_api.json",
            "designer_addin_rea",
            "Designer Ansoft add-in v251 REA metadata; product mapping unverified",
        ),
        (
            "Ans.Ansoft.MechanicalAddinPlugin.json",
            "mechanical_ansoft_addin_rea_api.json",
            "mechanical_ansoft_addin_rea",
            "Mechanical Ansoft add-in v251 REA metadata; product mapping unverified",
        ),
        (
            "Ans.Ansoft.SimplorerAddinPlugin.json",
            "simplorer_addin_rea_api.json",
            "simplorer_addin_rea",
            "Simplorer Ansoft add-in v251 REA metadata; product mapping unverified",
        ),
        (
            "ZOSAPI.json",
            "zemax_zosapi_rea_api.json",
            "zemax_zosapi_rea",
            "Zemax OpticStudio ZOSAPI v251 REA metadata; support status unverified",
        ),
        (
            "ZOSAPI_Interfaces.json",
            "zemax_zosapi_interfaces_rea_api.json",
            "zemax_zosapi_interfaces_rea",
            "Zemax OpticStudio ZOSAPI interfaces v251 REA metadata; support status unverified",
        ),
    )
    type_visibility = {
        0: "not-public",
        1: "public",
        2: "nested-public",
        3: "nested-private",
        4: "nested-family",
        5: "nested-assembly",
        6: "nested-family-and-assembly",
        7: "nested-family-or-assembly",
    }
    method_access = {
        0: "compiler-controlled",
        1: "private",
        2: "family-and-assembly",
        3: "assembly",
        4: "family",
        5: "family-or-assembly",
        6: "public",
    }
    written = []

    for input_name, output_name, product, interface in components:
        input_path = evidence_root / input_name
        if not input_path.is_file():
            raise FileNotFoundError(f"REA evidence file is missing: {input_path}")
        source = json.loads(input_path.read_text(encoding="utf-8"))
        source_payload = _rea_payload(source)
        normalized = source_payload.get("normalized_result")
        if not isinstance(normalized, dict) or normalized.get("metadata", {}).get("status") != "complete":
            raise ValueError(f"REA metadata is incomplete: {input_path}")
        artifact = normalized.get("artifact")
        module = normalized.get("module")
        types = normalized.get("types")
        methods = normalized.get("methods")
        if not isinstance(artifact, dict) or not isinstance(module, dict):
            raise ValueError(f"REA artifact identity is incomplete: {input_path}")
        if not isinstance(types, list) or not isinstance(methods, list) or not types or not methods:
            raise ValueError(f"REA metadata has no type or method rows: {input_path}")

        modules = {}
        type_records = {}
        for type_record in types:
            if not isinstance(type_record, dict) or type_record.get("name") == "<Module>":
                continue
            namespace = type_record.get("namespace") or "global"
            name = type_record.get("name")
            if not isinstance(name, str) or not name:
                continue
            flags = type_record.get("flags")
            flags = flags if isinstance(flags, int) else -1
            visibility = type_visibility.get(flags & 0x7, "unknown") if flags >= 0 else "unknown"
            kind = "interface" if flags >= 0 and flags & 0x20 else "type"
            class_key = name
            classes = modules.setdefault(
                namespace,
                {"doc": "Namespace from REA metadata.", "classes": {}, "functions": []},
            )["classes"]
            if class_key in classes:
                class_key = f"{name}__{type_record.get('token', 'unknown')}"
            class_info = {
                "name": class_key,
                "doc": (
                    f"REA TypeDef; kind={kind}; visibility={visibility}; flags={flags}. "
                    "Static metadata only. Product support status is unverified."
                ),
                "methods": [],
                "properties": [],
            }
            classes[class_key] = class_info
            type_records[type_record.get("token")] = class_info

        for method in methods:
            if not isinstance(method, dict):
                continue
            class_info = type_records.get(method.get("declaring_type_token"))
            if class_info is None:
                continue
            flags = method.get("flags")
            flags = flags if isinstance(flags, int) else -1
            access = method_access.get(flags & 0x7, "unknown") if flags >= 0 else "unknown"
            signature_data = method.get("signature")
            if not isinstance(signature_data, dict):
                signature_data = {}
            parameter_types = signature_data.get("parameter_types")
            parameter_count = signature_data.get("parameter_count")
            if (
                signature_data.get("parse_status") == "decoded"
                and isinstance(parameter_types, list)
                and parameter_count == len(parameter_types)
            ):
                signature = (
                    f"({', '.join(str(value) for value in parameter_types)}) "
                    f"-> {signature_data.get('return_type') or 'unknown'}"
                )
            else:
                signature = f"<unresolved signature sha256={signature_data.get('raw_sha256', 'unknown')}>"
            class_info["methods"].append(
                {
                    "name": method.get("name") or "<unnamed>",
                    "signature": signature,
                    "doc": (
                        f"REA MethodDef; access={access}; flags={flags}; "
                        f"static={bool(flags >= 0 and flags & 0x10)}; "
                        f"special_name={bool(flags >= 0 and flags & 0x800)}. "
                        "Parameter names and some class type references are unresolved. "
                        "Static metadata only. Product support status is unverified."
                    ),
                }
            )

        snapshot = {
            "module": module.get("name") or input_name.removesuffix(".json"),
            "version": "2025 R1 (v251)",
            "source": "REA CLI inspect-managed-members 6.0.0",
            "interface": interface,
            "scope": (
                "This snapshot lists managed TypeDef and MethodDef rows. It can include "
                "non-public members. Type visibility flags are recorded in class docs. "
                "Some signatures contain unresolved class:<rid> values. It is not a "
                "complete or supported public API declaration."
            ),
            "sources": {
                "assembly": {
                    "file": Path(str(artifact.get("path", input_name))).name,
                    "sha256": artifact.get("sha256"),
                    "bytes": artifact.get("byte_length"),
                    "mvid": module.get("mvid"),
                    "rea_evidence_id": source_payload.get("evidence_id"),
                }
            },
            "modules": modules,
            "statistics": {
                "total_modules": len(modules),
                "total_classes": len(type_records),
                "total_methods": len(methods),
                "total_properties": 0,
                "total_functions": 0,
            },
        }
        output_path = output_root / output_name
        if output_path.exists():
            previous = json.loads(output_path.read_text(encoding="utf-8"))
            previous_evidence = previous.get("sources", {}).get("assembly", {}).get("rea_evidence_id")
            if previous_evidence != source_payload.get("evidence_id"):
                raise FileExistsError(f"Refusing to replace unrelated snapshot: {output_path}")
            print(f"Preserved unchanged REA snapshot: {output_path.name}")
            written.append(output_path)
            continue
        fd, temp_name = tempfile.mkstemp(
            prefix=f"{output_path.stem}.", suffix=".tmp", dir=output_root
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
                json.dump(snapshot, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
            os.replace(temp_name, output_path)
        except Exception:
            Path(temp_name).unlink(missing_ok=True)
            raise
        written.append(output_path)

    return written


if __name__ == "__main__":
    main()
