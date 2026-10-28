"""
API 知識層 (API Knowledge Base) 配置與路徑定義。
"""

from pathlib import Path
import json
import hashlib
from datetime import datetime, timezone
import re

REPO_ROOT = Path(__file__).resolve().parents[4]
DOCS_DIR = REPO_ROOT / "docs" / "api_inventory"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

# SQLite 資料庫存放路徑 (與 docsearch 一致存於 Documentation_clean)
DB_DIR = REPO_ROOT / "Documentation_clean"
DB_PATH = DB_DIR / "api_kb.sqlite"

# 來源 JSON 檔案清單
APIKB_INDEX_VERSION = "2"

SOURCES = {
    "mechanical": DOCS_DIR / "mechanical_api.json",
    "spaceclaim": DOCS_DIR / "spaceclaim_api.json",
    "spaceclaim_core_rea": DOCS_DIR / "spaceclaim_core_rea_api.json",
    "optislang": DOCS_DIR / "optislang_api.json",
    "optislang_core": DOCS_DIR / "optislang_core_api.json",
    "lsdyna": DOCS_DIR / "lsdyna_api.json",
    "mapdl": DOCS_DIR / "mapdl_api.json",
    "dpf": DOCS_DIR / "dpf_api.json",
    "fluent": DOCS_DIR / "fluent_api.json",
    "primemesh": DOCS_DIR / "primemesh_api.json",
    "sound": DOCS_DIR / "sound_api.json",
    "pydyna": DOCS_DIR / "pydyna_api.json",
    "mechanical_core": DOCS_DIR / "mechanical_core_api.json",
    "geometry_core": DOCS_DIR / "geometry_core_api.json",
    "workbench": DOCS_DIR / "workbench_api.json",
    "workbench_protocol": DOCS_DIR / "workbench_protocol_api.json",
    "mechanical_protocol": DOCS_DIR / "mechanical_protocol_api.json",
    "geometry_protocol": DOCS_DIR / "geometry_protocol_api.json",
    "fluent_protocol": DOCS_DIR / "fluent_protocol_api.json",
    "mapdl_protocol": DOCS_DIR / "mapdl_protocol_api.json",
    "primemesh_protocol": DOCS_DIR / "primemesh_protocol_api.json",
    "discovery_protocol": DOCS_DIR / "discovery_protocol_api.json",
    "dbu_protocol": DOCS_DIR / "dbu_protocol_api.json",
    "result_explorer_protocol": DOCS_DIR / "result_explorer_protocol_api.json",
    "platform_instance_management_protocol": DOCS_DIR / "platform_instance_management_protocol_api.json",
    "filetransfer_protocol": DOCS_DIR / "filetransfer_protocol_api.json",
    "rsm_jobmanagement_rea": DOCS_DIR / "rsm_jobmanagement_rea_api.json",
    "acp_core_rea": DOCS_DIR / "acp_core_rea_api.json",
    "autodyn_rea": DOCS_DIR / "autodyn_rea_api.json",
    "designxplorer_rea": DOCS_DIR / "designxplorer_rea_api.json",
    "engineeringdata_rea": DOCS_DIR / "engineeringdata_rea_api.json",
    "engineeringdata_core_rea": DOCS_DIR / "engineeringdata_core_rea_api.json",
    "engineeringdata_dataprovider_rea": DOCS_DIR / "engineeringdata_dataprovider_rea_api.json",
    "designmodeler_core_rea": DOCS_DIR / "designmodeler_core_rea_api.json",
    "materialdesigner_core_rea": DOCS_DIR / "materialdesigner_core_rea_api.json",
    "mechanical_interfaces_rea": DOCS_DIR / "mechanical_interfaces_rea_api.json",
    "mechanical_datamodel_rea": DOCS_DIR / "mechanical_datamodel_rea_api.json",
    "discovery_collaboration_rea": DOCS_DIR / "discovery_collaboration_rea_api.json",
    "discovery_gateway_rea": DOCS_DIR / "discovery_gateway_rea_api.json",
    "discovery_geometry_rea": DOCS_DIR / "discovery_geometry_rea_api.json",
    "discovery_onscale_rea": DOCS_DIR / "discovery_onscale_rea_api.json",
    "discovery_physics_rea": DOCS_DIR / "discovery_physics_rea_api.json",
    "discovery_project_rea": DOCS_DIR / "discovery_project_rea_api.json",
    "discovery_results_rea": DOCS_DIR / "discovery_results_rea_api.json",
    "maxwell_addin_rea": DOCS_DIR / "maxwell_addin_rea_api.json",
    "q3d_addin_rea": DOCS_DIR / "q3d_addin_rea_api.json",
    "icepak_ansoft_addin_rea": DOCS_DIR / "icepak_ansoft_addin_rea_api.json",
    "granta_mi_rea": DOCS_DIR / "granta_mi_rea_api.json",
    "materialdesigner_rea": DOCS_DIR / "materialdesigner_rea_api.json",
    "turbosystem_ccd_rea": DOCS_DIR / "turbosystem_ccd_rea_api.json",
    "turbosystem_ccm_rea": DOCS_DIR / "turbosystem_ccm_rea_api.json",
    "turbosystem_afd_core_rea": DOCS_DIR / "turbosystem_afd_core_rea_api.json",
    "turbosystem_ccd_core_rea": DOCS_DIR / "turbosystem_ccd_core_rea_api.json",
    "turbosystem_cpd_core_rea": DOCS_DIR / "turbosystem_cpd_core_rea_api.json",
    "turbosystem_rtd_core_rea": DOCS_DIR / "turbosystem_rtd_core_rea_api.json",
    "units_rea": DOCS_DIR / "units_rea_api.json",
    "vista_tf_rea": DOCS_DIR / "vista_tf_rea_api.json",
    "act_core_rea": DOCS_DIR / "act_core_rea_api.json",
    "api_discovery_rea": DOCS_DIR / "api_discovery_rea_api.json",
    "api_geometry_rea": DOCS_DIR / "api_geometry_rea_api.json",
    "act_interfaces_rea": DOCS_DIR / "act_interfaces_rea_api.json",
    "lsdyna_interfaces_rea": DOCS_DIR / "lsdyna_interfaces_rea_api.json",
    "ansysem_coredotnet_rea": DOCS_DIR / "ansysem_coredotnet_rea_api.json",
    "additive_rea": DOCS_DIR / "additive_rea_api.json",
    "aqwa_addin_rea": DOCS_DIR / "aqwa_addin_rea_api.json",
    "aqwa_remote_itf_rea": DOCS_DIR / "aqwa_remote_itf_rea_api.json",
    "cfx_addin_rea": DOCS_DIR / "cfx_addin_rea_api.json",
    "cfx_cadapi_native": DOCS_DIR / "cfx_cadapi_native_exports_api.json",
    "cfx_acmo_native": DOCS_DIR / "cfx_acmo_native_exports_api.json",
    "dpf_mechanicalresults_native": DOCS_DIR / "dpf_mechanicalresults_native_exports_api.json",
    "dpf_engineeringdata_native": DOCS_DIR / "dpf_engineeringdata_native_exports_api.json",
    "dpf_abaqus_native": DOCS_DIR / "dpf_abaqus_native_exports_api.json",
    "dpf_cgns_native": DOCS_DIR / "dpf_cgns_native_exports_api.json",
    "dpf_compression_native": DOCS_DIR / "dpf_compression_native_exports_api.json",
    "dpf_femutils_native": DOCS_DIR / "dpf_femutils_native_exports_api.json",
    "dpf_flowdiagram_native": DOCS_DIR / "dpf_flowdiagram_native_exports_api.json",
    "dpf_grpc_native": DOCS_DIR / "dpf_grpc_native_exports_api.json",
    "dpf_hdf5_native": DOCS_DIR / "dpf_hdf5_native_exports_api.json",
    "dpf_livepost_native": DOCS_DIR / "dpf_livepost_native_exports_api.json",
    "dpf_lsdynahgp_native": DOCS_DIR / "dpf_lsdynahgp_native_exports_api.json",
    "dpf_math_native": DOCS_DIR / "dpf_math_native_exports_api.json",
    "dpf_mechanical_native": DOCS_DIR / "dpf_mechanical_native_exports_api.json",
    "dpf_native_native": DOCS_DIR / "dpf_native_native_exports_api.json",
    "dpf_pythonpluginwrapper_native": DOCS_DIR / "dpf_pythonpluginwrapper_native_exports_api.json",
    "dpf_rbd_native": DOCS_DIR / "dpf_rbd_native_exports_api.json",
    "dpf_vtk_native": DOCS_DIR / "dpf_vtk_native_exports_api.json",
    "dpf_autodyn_native": DOCS_DIR / "dpf_autodyn_native_exports_api.json",
    "dpf_cff_native": DOCS_DIR / "dpf_cff_native_exports_api.json",
    "dpf_multiphysicsmapper_native": DOCS_DIR / "dpf_multiphysicsmapper_native_exports_api.json",
    "dpf_prime_native": DOCS_DIR / "dpf_prime_native_exports_api.json",
    "dpf_datamodel_native": DOCS_DIR / "dpf_datamodel_native_exports_api.json",
    "dpf_systemcouplingmapping_native": DOCS_DIR / "dpf_systemcouplingmapping_native_exports_api.json",
    "lumerical_interopapi_native": DOCS_DIR / "lumerical_interopapi_native_exports_api.json",
    "lumerical_interopapi_remote_native": DOCS_DIR / "lumerical_interopapi_remote_native_exports_api.json",
    "lumerical_lumapi_native": DOCS_DIR / "lumerical_lumapi_native_exports_api.json",
    "fluent_addin_rea": DOCS_DIR / "fluent_addin_rea_api.json",
    "icepak_addin_rea": DOCS_DIR / "icepak_addin_rea_api.json",
    "meshing_addin_rea": DOCS_DIR / "meshing_addin_rea_api.json",
    "polyflow_addin_rea": DOCS_DIR / "polyflow_addin_rea_api.json",
    "sherlock_addin_rea": DOCS_DIR / "sherlock_addin_rea_api.json",
    "sherlock_core": DOCS_DIR / "sherlock_core_api.json",
    "rocky": DOCS_DIR / "rocky_api.json",
    "cfx": DOCS_DIR / "cfx_api.json",
    "speos": DOCS_DIR / "speos_api.json",
    "speos_protocol": DOCS_DIR / "speos_protocol_api.json",
    "siwave_libironpythoncmd_rea": DOCS_DIR / "siwave_libironpythoncmd_rea_api.json",
    "hfss_addin_rea": DOCS_DIR / "hfss_addin_rea_api.json",
    "apip_wrapper_native": DOCS_DIR / "apip_wrapper_native_exports_api.json",
    "rom_api_native": DOCS_DIR / "rom_api_native_exports_api.json",
    "system_coupling_rpc_native": DOCS_DIR / "system_coupling_rpc_native_exports_api.json",
    "system_coupling_participant_native": DOCS_DIR / "system_coupling_participant_native_exports_api.json",
    "speos_apip_wrapper_native": DOCS_DIR / "speos_apip_wrapper_native_exports_api.json",
    "zemax_zosapi_rea": DOCS_DIR / "zemax_zosapi_rea_api.json",
    "zemax_zosapi_interfaces_rea": DOCS_DIR / "zemax_zosapi_interfaces_rea_api.json",
    "designer_addin_rea": DOCS_DIR / "designer_addin_rea_api.json",
    "mechanical_ansoft_addin_rea": DOCS_DIR / "mechanical_ansoft_addin_rea_api.json",
    "motion_api_rea": DOCS_DIR / "motion_api_rea_api.json",
    "simplorer_addin_rea": DOCS_DIR / "simplorer_addin_rea_api.json",
}

# 每個快照提供可追溯版本；新增版本時以獨立檔案登錄，避免覆蓋舊版。
INTERFACES = {
    "mechanical": "Mechanical ACT object model",
    "spaceclaim": "SpaceClaim embedded scripting API",
    "spaceclaim_core_rea": "SpaceClaim Core API v251 REA managed metadata",
    "optislang": "PyOptiSLang and scripting API",
    "optislang_core": "PyOptiSLang 1.6.0 Optislang client",
    "lsdyna": "LS-DYNA keyword and LS-PrePost APIs",
    "mapdl": "PyMAPDL documented Python client API",
    "dpf": "PyDPF-Core 0.16.1 core data classes",
    "fluent": "PyFluent 0.42.1 launcher functions",
    "primemesh": "PyPrimeMesh 0.10.5 Client and launch_prime",
    "sound": "PyAnsys Sound 0.3.0 SoundComposer and Track",
    "pydyna": "PyDyna 0.12.1 Deck class",
    "mechanical_core": "PyMechanical 0.13.2 Mechanical client and launch/connect functions",
    "geometry_core": "PyAnsys Geometry 0.17.1 Modeler and launch_modeler",
    "workbench": "PyWorkbench ansys-workbench-core 0.14.0 direct module exports",
    "sherlock_core": "PyAnsys Sherlock SDK 2.1.4 static AST declarations",
    "rocky": "PyAnsys Rocky SDK 0.6.2 static AST declarations",
    "cfx": "PyAnsys CFX SDK 0.3.0; metadata requires licensed local CFX and states 2025 R2 SP3+; direct AST only, dynamic flobject/TUI omitted",
    "speos": "PyAnsys Speos SDK 0.9.2 client; support/version examples conflict in package metadata",
    "speos_protocol": "PyAnsys Speos gRPC/protobuf schema from ansys-api-speos 0.16.3",
    "workbench_protocol": "Workbench gRPC protocol schema from ansys-api-workbench 0.4.0",
    "mechanical_protocol": "Mechanical gRPC protocol schema from ansys-api-mechanical 0.1.4",
    "geometry_protocol": "Geometry gRPC protocol schema from ansys-api-geometry 0.4.92",
    "fluent_protocol": "Fluent gRPC protocol schema from ansys-api-fluent 0.6.0",
    "mapdl_protocol": "MAPDL gRPC protocol schema from ansys-api-mapdl 0.6.0",
    "primemesh_protocol": "PrimeMesh gRPC protocol schema from ansys-api-meshing-prime 0.2.0",
    "discovery_protocol": "Discovery gRPC protocol schema from ansys-api-discovery 1.2.12",
    "dbu_protocol": "DBU Service gRPC protocol schema from ansys-api-dbu 0.3.29; product mapping unverified",
    "result_explorer_protocol": "Result Explorer gRPC protocol schema from ansys-api-result-explorer 0.1.1; product mapping unverified",
    "platform_instance_management_protocol": "Shared platform instance management gRPC schema; not mapped to one product",
    "filetransfer_protocol": "Shared file-transfer tool gRPC schema; not mapped to one product",
    "autodyn_rea": "AUTODYN v251 REA managed metadata; support status unverified",
    "designxplorer_rea": "DesignXplorer v251 REA managed metadata; support status unverified",
    "engineeringdata_rea": "Engineering Data v251 REA managed metadata; support status unverified",
    "mechanical_interfaces_rea": "Mechanical Interfaces v251 REA managed metadata; support status unverified",
    "mechanical_datamodel_rea": "Mechanical DataModel v251 REA managed metadata; support status unverified",
    "discovery_collaboration_rea": "Discovery Collaboration API v251 REA managed metadata; support status unverified",
    "discovery_gateway_rea": "Discovery Gateway API v251 REA managed metadata; support status unverified",
    "discovery_geometry_rea": "Discovery Geometry API v251 REA managed metadata; support status unverified",
    "discovery_onscale_rea": "Discovery OnScale API v251 REA managed metadata; support status unverified",
    "discovery_physics_rea": "Discovery Physics API v251 REA managed metadata; support status unverified",
    "discovery_project_rea": "Discovery Project API v251 REA managed metadata; support status unverified",
    "discovery_results_rea": "Discovery Results API v251 REA managed metadata; support status unverified",
    "maxwell_addin_rea": "Maxwell Ansoft add-in v251 REA metadata; support status unverified",
    "q3d_addin_rea": "Q3D Extractor Ansoft add-in v251 REA metadata; support status unverified",
    "icepak_ansoft_addin_rea": "Icepak Ansoft add-in v251 REA metadata; support status unverified",
    "granta_mi_rea": "Granta MI v251 REA managed metadata; support status unverified",
    "materialdesigner_rea": "Material Designer v251 REA managed metadata; support status unverified",
    "turbosystem_ccd_rea": "TurboSystem CCD interface v251 REA metadata; support status unverified",
    "turbosystem_ccm_rea": "TurboSystem CCM interface v251 REA metadata; support status unverified",
    "units_rea": "ANSYS Units DataModel v251 REA metadata; support status unverified",
    "vista_tf_rea": "Vista TF DataModel v251 REA metadata; support status unverified",
    "act_core_rea": "ACT Core v251 REA managed metadata; support status unverified",
    "api_discovery_rea": "API Server Discovery v251 REA metadata; product mapping unverified",
    "api_geometry_rea": "API Server Geometry v251 REA metadata; product mapping unverified",
    "act_interfaces_rea": "ACT Interfaces v251 REA managed metadata; support status unverified",
    "lsdyna_interfaces_rea": "LS-DYNA ACT Interfaces v251 REA metadata; product mapping unverified",
    "ansysem_coredotnet_rea": "AnsysEM CoreDotNet v251 REA metadata; product mapping unverified",
    "additive_rea": "Ansys Additive v251 REA metadata; product mapping unverified",
    "aqwa_addin_rea": "AQWA Core add-in v251 REA metadata; support status unverified",
    "cfx_addin_rea": "CFX Core add-in v251 REA metadata; support status unverified",
    "cfx_cadapi_native": "CFX CadApi v251 native PE exports; signatures unavailable",
    "cfx_acmo_native": "CFX Acmo v251 native PE exports; signatures unavailable",
    "dpf_mechanicalresults_native": "DPF Mechanical Results v251 native export; signature unavailable",
    "dpf_engineeringdata_native": "DPF Engineering Data v251 native export; signature unavailable",
    "dpf_abaqus_native": "DPF Abaqus reader v251 native exports; signatures unverified",
    "dpf_cgns_native": "DPF CGNS reader v251 native exports; signatures unverified",
    "dpf_compression_native": "DPF compression component v251 native exports; signatures unverified",
    "dpf_femutils_native": "DPF FEM utilities v251 native exports; signatures unverified",
    "dpf_flowdiagram_native": "DPF FlowDiagram component v251 native exports; signatures unverified",
    "dpf_grpc_native": "DPF gRPC component v251 native exports; signatures unverified",
    "dpf_hdf5_native": "DPF HDF5 component v251 native exports; signatures unverified",
    "dpf_livepost_native": "DPF LivePost component v251 native exports; signatures unverified",
    "dpf_lsdynahgp_native": "DPF LS-DYNA HGP component v251 native exports; signatures unverified",
    "dpf_math_native": "DPF math component v251 native exports; signatures unverified",
    "dpf_mechanical_native": "DPF Mechanical component v251 native exports; signatures unverified",
    "dpf_native_native": "DPF native component v251 native exports; signatures unverified",
    "dpf_pythonpluginwrapper_native": "DPF Python plugin wrapper v251 native exports; signatures unverified",
    "dpf_rbd_native": "DPF rigid-body dynamics component v251 native exports; signatures unverified",
    "dpf_vtk_native": "DPF VTK component v251 native exports; signatures unverified",
    "dpf_autodyn_native": "DPF AUTODYN plugin v251 native exports; signatures unverified",
    "dpf_cff_native": "DPF CFF plugin v251 native exports; signatures unverified",
    "dpf_multiphysicsmapper_native": "DPF multiphysics mapper plugin v251 native exports; signatures unverified",
    "dpf_prime_native": "DPF Prime plugin v251 native exports; signatures unverified",
    "dpf_datamodel_native": "DPF simulation data model plugin v251 native exports; signatures unverified",
    "dpf_systemcouplingmapping_native": "DPF System Coupling mapping plugin v251 native exports; signatures unverified",
    "lumerical_interopapi_native": "Lumerical Python interop API v251 native exports; signatures unverified",
    "lumerical_interopapi_remote_native": "Lumerical remote Python interop API v251 native exports; signatures unverified",
    "lumerical_lumapi_native": "Lumerical Tcl API v251 native exports; signatures unverified",
    "fluent_addin_rea": "Fluent add-in v251 REA metadata; support status unverified",
    "icepak_addin_rea": "Icepak Core add-in v251 REA metadata; support status unverified",
    "meshing_addin_rea": "Meshing Core add-in v251 REA metadata; support status unverified",
    "polyflow_addin_rea": "Polyflow add-in v251 REA metadata; support status unverified",
    "sherlock_addin_rea": "Sherlock add-in v251 REA metadata; support status unverified",
    "hfss_addin_rea": "HFSS Ansoft add-in v251 REA metadata; support status unverified",
    "apip_wrapper_native": "AnsysEM APIP wrapper native PE exports; product mapping unverified",
    "rom_api_native": "ROM v251 native PE exports; official API support unverified",
    "system_coupling_rpc_native": "System Coupling ANSRPC wrapper native PE exports; product API mapping unverified",
    "system_coupling_participant_native": "System Coupling participant v251 native PE exports; support status unverified",
    "speos_apip_wrapper_native": "Speos APIP wrapper native exports; product API support unverified",
    "zemax_zosapi_rea": "Zemax OpticStudio ZOSAPI v251 REA metadata; support status unverified",
    "zemax_zosapi_interfaces_rea": "Zemax OpticStudio ZOSAPI interfaces v251 REA metadata; support status unverified",
    "designer_addin_rea": "Designer Ansoft add-in v251 REA metadata; product mapping unverified",
    "mechanical_ansoft_addin_rea": "Mechanical Ansoft add-in v251 REA metadata; product mapping unverified",
    "simplorer_addin_rea": "Simplorer Ansoft add-in v251 REA metadata; product mapping unverified",
}


def source_snapshots() -> list[tuple[str, Path]]:
    """回傳既有來源及同產品額外快照；保留 SOURCES 的舊字典介面。"""
    snapshots = []
    for product, primary in SOURCES.items():
        candidates = [primary, *sorted(DOCS_DIR.glob(f"{product}_api_v*.json"))]
        seen = set()
        for candidate in candidates:
            if candidate.is_file() and candidate.resolve() not in seen:
                snapshots.append((product, candidate))
                seen.add(candidate.resolve())
    return snapshots


def source_metadata(product: str, path: Path) -> dict:
    """由 API JSON 建立 snapshot 與可選 artifact 來源紀錄。"""
    raw = path.read_bytes()
    try:
        data = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError):
        data = {}
    version = str(data.get("version", "unknown"))
    if version == "unknown":
        filename_release = re.search(r"v(?:251|252|261)", path.stem, re.I)
        if filename_release:
            version = filename_release.group(0).lower()
    sdk_version = ""
    if product == "optislang":
        sdk_version = version
        version = "unknown (product release not recorded)"
    elif product in {"mapdl", "dpf", "fluent", "primemesh", "sound", "pydyna", "mechanical_core", "geometry_core", "optislang_core", "workbench", "sherlock_core", "rocky", "cfx", "speos", "speos_protocol", "workbench_protocol", "mechanical_protocol", "geometry_protocol", "fluent_protocol", "mapdl_protocol", "primemesh_protocol", "discovery_protocol", "dbu_protocol", "result_explorer_protocol", "platform_instance_management_protocol", "filetransfer_protocol"}:
        sdk_version = str(data.get("sdk_version", ""))
        version = "unknown (product release not recorded)"
    sources = data.get("sources")
    assembly = sources.get("assembly", {}) if isinstance(sources, dict) else {}
    try:
        source_path = path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        source_path = path.resolve().as_posix()
    return {
        "product": product,
        "release": version,
        "interface": INTERFACES.get(product, "unknown"),
        "source_path": source_path,
        "sdk_version": sdk_version,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "artifact_sha256": str(assembly.get("sha256", "")),
        "rea_evidence_id": str(assembly.get("rea_evidence_id", "")),
        "ingested_at": datetime.now(timezone.utc).isoformat(),
    }


# 高頻通用方法白名單（出現於超過此數量類別時，標記為 is_inherited 且降低搜尋權重）
INHERITED_THRESHOLD = 50
COMMON_INHERITED_NAMES = {
    "Equals",
    "GetHashCode",
    "GetType",
    "ToString",
    "MemberwiseClone",
    "ReferenceEquals",
    "GetObjectData",
    "CopyTo",
    "GetChildren",
    "IsPropertyVisible",
    "IsPropertyEditable",
    "__init__",
    "__repr__",
    "__str__",
}
