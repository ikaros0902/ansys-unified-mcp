# -*- coding: utf-8 -*-
"""Meta-Router Tools for dynamic domain tool discovery and execution.

Provides universal meta-tools:
- ans_list_domain_tools: Discovers available tools in any physics domain along with
  their 4-key annotations and JSON parameter schemas.
- ans_call_domain_tool: Dynamically dispatches tool calls across domains on demand,
  wrapping outputs into standardized response envelopes.

Core Value:
Bypasses the static tools/list caching limitation of mainstream MCP clients
(such as Antigravity, Claude Desktop, and Kiro CLI) on connection handshake.
Allows agents running in a lightweight core profile to invoke all 160+ tools
across any domain without client disconnects or renegotiations.

All comments and docstrings in this module strictly use ASCII English.
"""

from __future__ import annotations

import asyncio
import importlib
import inspect
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Sequence, Set

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ansys_unified_mcp.schemas.common_envelope import (
    create_error_envelope,
    create_response_envelope,
)
from ansys_unified_mcp.schemas.domain_inputs import (
    ChemkinReactionKineticsInput,
    HFSSAdaptiveMeshInput,
    LumericalSlabWaveguideInput,
    MarineAqwaHeaveInput,
    MaxwellSetupInput,
    MotorCADEfficiencyInput,
    OpticsSimulationInput,
    SoundPsychoacousticsInput,
)
from ansys_unified_mcp.schemas.tool_annotations import (
    ToolAnnotations,
    create_tool_annotations,
    validate_flat_pydantic,
)
from ansys_unified_mcp.shared import (
    TOOL_REGISTRY,
    aliased_tool,
    get_canonical_name,
    get_tool_function,
    mcp,
)

logger = logging.getLogger("ansys-unified-mcp.meta_router")

# Mapping of physics domain identifiers to their corresponding Python modules
DOMAIN_MODULE_MAP: dict[str, list[str]] = {
    "structural": [
        "ansys_unified_mcp.products.mechanical.tools",
        "ansys_unified_mcp.products.dyna.tools",
        "ansys_unified_mcp.products.dpf.tools",
    ],
    "fluids": [
        "ansys_unified_mcp.products.fluent.tools",
        "ansys_unified_mcp.products.workbench.tools",
    ],
    "geometry": [
        "ansys_unified_mcp.products.geometry.tools",
    ],
    "workbench": [
        "ansys_unified_mcp.products.workbench.tools",
    ],
    "coupling": [
        "ansys_unified_mcp.products.workbench.tools",
        "ansys_unified_mcp.tools.intent_tools",
    ],
    "optimization": [
        "ansys_unified_mcp.products.optislang.tools",
        "ansys_unified_mcp.tools.intent_tools",
    ],
    "thermal": [
        "ansys_unified_mcp.products.mechanical.tools",
        "ansys_unified_mcp.products.workbench.tools",
        "ansys_unified_mcp.tools.intent_tools",
    ],
    "materials": [
        "ansys_unified_mcp.products.mechanical.tools",
    ],
    "multibody": [
        "ansys_unified_mcp.products.mechanical.tools",
    ],
    "common": [
        "ansys_unified_mcp.tools.connection_tools",
        "ansys_unified_mcp.tools.docs_tools",
        "ansys_unified_mcp.tools.apikb_tools",
        "ansys_unified_mcp.tools.sentinel_tools",
        "ansys_unified_mcp.tools.session_manager_tools",
    ],
    "workflow": [
        "ansys_unified_mcp.tools.intent_tools",
    ],
    "electromagnetics": [],
    "optics": [],
    "sound": [
        "ansys_unified_mcp.tools.sound_tools",
    ],
    "aqwa": [],
    "lumerical": [],
    "chemkin": [],
    "motorcad": [],
}

# Domain metadata catalog across 14 physics disciplines and infrastructure services
DOMAIN_CATALOG: dict[str, dict[str, Any]] = {
    "structural": {
        "domain_id": "structural",
        "name": "Structural Mechanics",
        "description": "ANSYS Mechanical, LS-DYNA, and MAPDL finite element analysis.",
        "solvers": ["mechanical", "lsdyna", "mapdl", "dpf"],
        "maturity_levels": [0, 1, 2, 3, 4, 5, 6, 7],
    },
    "fluids": {
        "domain_id": "fluids",
        "name": "Computational Fluid Dynamics",
        "description": "ANSYS Fluent and CFX Navier-Stokes fluid and thermal flow.",
        "solvers": ["fluent", "cfx"],
        "maturity_levels": [0, 1, 2, 3, 4, 5, 6, 7],
    },
    "electromagnetics": {
        "domain_id": "electromagnetics",
        "name": "Electromagnetics (HF & LF)",
        "description": "ANSYS HFSS high-frequency wave propagation and Maxwell low-frequency EM.",
        "solvers": ["hfss", "maxwell", "q3d"],
        "maturity_levels": [0, 1, 2, 3, 4, 5, 6, 7],
    },
    "optics": {
        "domain_id": "optics",
        "name": "Optics & Ray Tracing",
        "description": "ANSYS Speos and Zemax optical ray tracing, illumination, and photometry.",
        "solvers": ["speos", "zemax"],
        "maturity_levels": [0, 1, 2, 3, 4, 5, 6, 7],
    },
    "multibody": {
        "domain_id": "multibody",
        "name": "Multibody Dynamics",
        "description": "Rigid body kinematics, joints, contact constraints, and vibration.",
        "solvers": ["mechanical_rigid", "motion"],
        "maturity_levels": [0, 1, 2, 3, 4, 5, 6, 7],
    },
    "thermal": {
        "domain_id": "thermal",
        "name": "Thermal Analysis",
        "description": "Steady-state and transient heat conduction, convection, and radiation.",
        "solvers": ["mechanical_thermal", "fluent"],
        "maturity_levels": [0, 1, 2, 3, 4, 5, 6, 7],
    },
    "coupling": {
        "domain_id": "coupling",
        "name": "System Coupling & Multiphysics",
        "description": "Conjugate heat transfer (CHT) and fluid-structure interaction (FSI).",
        "solvers": ["system_coupling", "workbench"],
        "maturity_levels": [0, 1, 2, 3, 4, 5, 6, 7],
    },
    "materials": {
        "domain_id": "materials",
        "name": "Materials & Composites",
        "description": "Composite layup definition (ACP) and material constitutive behavior.",
        "solvers": ["acp", "granta"],
        "maturity_levels": [0, 1, 2, 3, 4, 5, 6, 7],
    },
    "geometry": {
        "domain_id": "geometry",
        "name": "Geometry Modeling & Defeaturing",
        "description": "SpaceClaim and PyAnsys Geometry 3D modeling and CAD preparation.",
        "solvers": ["spaceclaim", "geometry"],
        "maturity_levels": [0, 1, 2, 3, 4, 5, 6, 7],
    },
    "optimization": {
        "domain_id": "optimization",
        "name": "Process Optimization & Surrogate",
        "description": "optiSLang MOP surrogate modeling and parameter optimization.",
        "solvers": ["optislang"],
        "maturity_levels": [0, 1, 2, 3, 4, 5, 6, 7],
    },
    "sound": {
        "domain_id": "sound",
        "name": "Acoustics & Psychoacoustics",
        "description": "Ansys Sound acoustic propagation, spherical decay, and Zwicker loudness.",
        "solvers": ["ansys_sound", "mechanical_acoustic"],
        "maturity_levels": [0, 1, 2, 3, 4, 5, 6, 7],
    },
    "aqwa": {
        "domain_id": "aqwa",
        "name": "Marine Hydrodynamics",
        "description": "Ansys AQWA wave diffraction, radiation, RAO, and floating body heave.",
        "solvers": ["aqwa"],
        "maturity_levels": [0, 1, 2, 3, 4, 5, 6, 7],
    },
    "lumerical": {
        "domain_id": "lumerical",
        "name": "Wave Optics & Photonics",
        "description": "Ansys Lumerical FDTD, MODE waveguide solver, and photonic circuits.",
        "solvers": ["lumerical_fdtd", "lumerical_mode"],
        "maturity_levels": [0, 1, 2, 3, 4, 5, 6, 7],
    },
    "chemkin": {
        "domain_id": "chemkin",
        "name": "Chemical Reaction Kinetics",
        "description": "Ansys Chemkin-Pro 0D/1D reactor kinetics and Arrhenius mechanisms.",
        "solvers": ["chemkin_pro"],
        "maturity_levels": [0, 1, 2, 3, 4, 5, 6, 7],
    },
    "motorcad": {
        "domain_id": "motorcad",
        "name": "Electric Machine Design",
        "description": "Ansys Motor-CAD PMSM electromechanical efficiency and loss maps.",
        "solvers": ["motor_cad"],
        "maturity_levels": [0, 1, 2, 3, 4, 5, 6, 7],
    },
    "workbench": {
        "domain_id": "workbench",
        "name": "Workbench Integration",
        "description": "Ansys Workbench project schematic management and journaling.",
        "solvers": ["workbench"],
        "maturity_levels": [0, 1, 2, 3, 4, 5, 6, 7],
    },
    "common": {
        "domain_id": "common",
        "name": "System & Session Utilities",
        "description": "Session lifecycle, diagnostics, and documentation search.",
        "solvers": ["core"],
        "maturity_levels": [0],
    },
    "workflow": {
        "domain_id": "workflow",
        "name": "Automated Workflows",
        "description": "End-to-end multi-step simulation pipelines.",
        "solvers": ["orchestrator"],
        "maturity_levels": [0, 1, 2, 3, 4, 5, 6, 7],
    },
}

# Mapping of physics domain identifiers to their router tools
DOMAIN_ROUTER_TOOL_MAP: dict[str, list[str]] = {
    "structural": [
        "mechanical_connect",
        "mechanical_launch",
        "mechanical_disconnect",
        "mechanical_check_connection",
        "mechanical_get_model_info",
        "mechanical_list_materials",
        "mechanical_assign_material",
        "mechanical_set_mesh_element_size",
        "mechanical_generate_mesh",
        "mechanical_get_mesh_statistics",
        "mechanical_add_fixed_support",
        "mechanical_add_force",
        "mechanical_add_pressure",
        "mechanical_list_boundary_conditions",
        "mechanical_solve_analysis",
        "mechanical_get_solve_status",
        "mechanical_add_total_deformation",
        "mechanical_setup_and_solve_static_structural",
        "mechanical_setup_and_solve_modal",
        "dyna_solve",
        "dpf_extract_structural_results",
    ],
    "fluids": [
        "fluent_launch",
        "fluent_read_case",
        "fluent_read_mesh",
        "fluent_set_solver",
        "fluent_set_boundary",
        "fluent_set_material",
        "fluent_initialize",
        "fluent_iterate",
        "fluent_get_residuals",
        "fluent_save",
        "fluent_exit",
        "run_fluent_journal",
    ],
    "geometry": [
        "geometry_launch",
        "geometry_create_design",
        "geometry_create_block",
        "geometry_create_cylinder",
        "geometry_create_sphere",
        "geometry_sketch_and_extrude",
        "geometry_create_enclosure",
        "geometry_simplify_ram",
        "geometry_simplify_heatsink",
        "spaceclaim_run_script",
    ],
    "workbench": [
        "start_workbench_bridge",
        "stop_workbench_bridge",
        "check_workbench_connection",
        "execute_workbench_script",
        "open_project",
        "save_project",
        "update_project",
        "create_workbench_analysis_system_live",
        "workbench_run_journal",
    ],
    "coupling": [
        "create_thermal_bar_demo_live",
        "create_and_run_thermal_bar_demo",
        "workflow_run_thermal_warpage",
    ],
    "optimization": [
        "optislang_connect",
        "optislang_get_version",
        "optislang_run_script",
        "optislang_start_project",
        "optislang_disconnect",
        "optislang_setup_mop",
        "workflow_train_surrogate_model",
    ],
    "thermal": [
        "create_steady_state_thermal_system_live",
        "create_transient_thermal_system_live",
        "workflow_run_thermal_warpage",
    ],
    "materials": [
        "mechanical_list_materials",
        "mechanical_assign_material",
        "mechanical_assign_materials_from_bom",
    ],
    "multibody": [
        "mechanical_create_joints_from_groups",
        "mechanical_list_point_masses",
    ],
    "electromagnetics": [
        "hfss_setup_adaptive_mesh",
        "maxwell_setup_solver",
    ],
    "optics": [
        "optics_ray_trace_simulation",
    ],
    "sound": [
        "sound_compute_loudness_zwicker",
        "sound_monopole_propagation",
    ],
    "aqwa": [
        "aqwa_heave_natural_frequency",
        "aqwa_hydrodynamic_diffraction",
    ],
    "lumerical": [
        "lumerical_solve_slab_waveguide_modes",
        "lumerical_fdtd_sweep",
    ],
    "chemkin": [
        "chemkin_solve_arrhenius_kinetics",
        "chemkin_load_mechanism",
    ],
    "motorcad": [
        "motorcad_pmsm_efficiency_map",
        "motorcad_solve_electromagnetic",
    ],
    "common": [
        "ans_session_diagnose",
        "ans_session_connect",
        "ans_session_launch",
        "ans_session_status",
        "ans_session_disconnect",
        "ans_session_set_workspace",
        "check_ansys_installation",
        "search_ansys_docs",
        "get_ansys_doc_chunk",
    ],
    "workflow": [
        "workflow_run_drop_test",
        "workflow_run_shock_analysis",
        "workflow_run_random_vibration",
        "workflow_run_thermal_warpage",
        "workflow_train_surrogate_model",
    ],
}

# Synonyms for domain normalization
DOMAIN_SYNONYMS: dict[str, str] = {
    "cfd": "fluids",
    "fluid": "fluids",
    "structure": "structural",
    "structures": "structural",
    "mechanical": "structural",
    "fem": "structural",
    "fea": "structural",
    "cad": "geometry",
    "spaceclaim": "geometry",
    "dyna": "structural",
    "lsdyna": "structural",
    "explicit": "structural",
    "dpf": "structural",
    "postprocessing": "structural",
    "optislang": "optimization",
    "optim": "optimization",
    "multiphysics": "coupling",
    "wb": "workbench",
    "em": "electromagnetics",
    "electromagnetic": "electromagnetics",
    "hfss": "electromagnetics",
    "maxwell": "electromagnetics",
    "speos": "optics",
    "zemax": "optics",
    "optical": "optics",
    "heat": "thermal",
    "temperature": "thermal",
    "joints": "multibody",
    "rigid_dynamics": "multibody",
    "material": "materials",
    "acoustic": "sound",
    "acoustics": "sound",
    "psychoacoustics": "sound",
    "marine": "aqwa",
    "hydrodynamic": "aqwa",
    "hydrodynamics": "aqwa",
    "wave_optics": "lumerical",
    "wave-optics": "lumerical",
    "photonics": "lumerical",
    "fdtd": "lumerical",
    "kinetics": "chemkin",
    "combustion": "chemkin",
    "chemistry": "chemkin",
    "motor_cad": "motorcad",
    "motor-cad": "motorcad",
    "electric_machine": "motorcad",
    "electric_machines": "motorcad",
}

# Domain schema virtual tools for domains in staging
VIRTUAL_DOMAIN_TOOLS: dict[str, list[dict[str, Any]]] = {
    "electromagnetics": [
        {
            "name": "hfss_setup_adaptive_mesh",
            "description": "Configure adaptive mesh refinement setup in ANSYS HFSS.",
            "annotations": ToolAnnotations.external(destructive=False, idempotent=True).to_dict(),
            "parameters": HFSSAdaptiveMeshInput.model_json_schema(),
            "schema_model": HFSSAdaptiveMeshInput,
        },
        {
            "name": "maxwell_setup_solver",
            "description": "Configure electromagnetic solver setup in ANSYS Maxwell.",
            "annotations": ToolAnnotations.external(destructive=False, idempotent=True).to_dict(),
            "parameters": MaxwellSetupInput.model_json_schema(),
            "schema_model": MaxwellSetupInput,
        },
    ],
    "optics": [
        {
            "name": "optics_ray_trace_simulation",
            "description": "Run optical Monte Carlo ray tracing simulation in ANSYS Speos / Zemax.",
            "annotations": ToolAnnotations.external(destructive=False, idempotent=True).to_dict(),
            "parameters": OpticsSimulationInput.model_json_schema(),
            "schema_model": OpticsSimulationInput,
        },
    ],
    "sound": [
        {
            "name": "sound_compute_loudness_zwicker",
            "description": "Compute ISO 532-1 Zwicker psychoacoustic loudness and phon levels.",
            "annotations": ToolAnnotations.external(destructive=False, idempotent=True).to_dict(),
            "parameters": SoundPsychoacousticsInput.model_json_schema(),
            "schema_model": SoundPsychoacousticsInput,
        },
        {
            "name": "sound_monopole_propagation",
            "description": "Calculate spherical monopole wave propagation with 6 dB decay per distance doubling.",
            "annotations": ToolAnnotations.external(destructive=False, idempotent=True).to_dict(),
            "parameters": SoundPsychoacousticsInput.model_json_schema(),
            "schema_model": SoundPsychoacousticsInput,
        },
    ],
    "aqwa": [
        {
            "name": "aqwa_heave_natural_frequency",
            "description": "Calculate marine vessel heave hydrodynamic natural frequency and period.",
            "annotations": ToolAnnotations.external(destructive=False, idempotent=True).to_dict(),
            "parameters": MarineAqwaHeaveInput.model_json_schema(),
            "schema_model": MarineAqwaHeaveInput,
        },
        {
            "name": "aqwa_hydrodynamic_diffraction",
            "description": "Compute 3D boundary element wave diffraction forces and radiation damping.",
            "annotations": ToolAnnotations.external(destructive=False, idempotent=True).to_dict(),
            "parameters": MarineAqwaHeaveInput.model_json_schema(),
            "schema_model": MarineAqwaHeaveInput,
        },
    ],
    "lumerical": [
        {
            "name": "lumerical_solve_slab_waveguide_modes",
            "description": "Solve symmetric dielectric slab waveguide TE0 mode effective index.",
            "annotations": ToolAnnotations.external(destructive=False, idempotent=True).to_dict(),
            "parameters": LumericalSlabWaveguideInput.model_json_schema(),
            "schema_model": LumericalSlabWaveguideInput,
        },
        {
            "name": "lumerical_fdtd_sweep",
            "description": "Run finite-difference time-domain wavelength parameter sweep in Ansys Lumerical.",
            "annotations": ToolAnnotations.external(destructive=False, idempotent=True).to_dict(),
            "parameters": LumericalSlabWaveguideInput.model_json_schema(),
            "schema_model": LumericalSlabWaveguideInput,
        },
    ],
    "chemkin": [
        {
            "name": "chemkin_solve_arrhenius_kinetics",
            "description": "Solve 0D isothermal homogeneous reactor chemical kinetics with Arrhenius rate law.",
            "annotations": ToolAnnotations.external(destructive=False, idempotent=True).to_dict(),
            "parameters": ChemkinReactionKineticsInput.model_json_schema(),
            "schema_model": ChemkinReactionKineticsInput,
        },
        {
            "name": "chemkin_load_mechanism",
            "description": "Load and parse chemical reaction kinetics mechanism file in Ansys Chemkin.",
            "annotations": ToolAnnotations.external(destructive=False, idempotent=True).to_dict(),
            "parameters": ChemkinReactionKineticsInput.model_json_schema(),
            "schema_model": ChemkinReactionKineticsInput,
        },
    ],
    "motorcad": [
        {
            "name": "motorcad_pmsm_efficiency_map",
            "description": "Calculate PMSM torque constant, back-EMF, copper losses, and electromechanical efficiency.",
            "annotations": ToolAnnotations.external(destructive=False, idempotent=True).to_dict(),
            "parameters": MotorCADEfficiencyInput.model_json_schema(),
            "schema_model": MotorCADEfficiencyInput,
        },
        {
            "name": "motorcad_solve_electromagnetic",
            "description": "Execute electromagnetic finite element analysis and winding analysis in Motor-CAD.",
            "annotations": ToolAnnotations.external(destructive=False, idempotent=True).to_dict(),
            "parameters": MotorCADEfficiencyInput.model_json_schema(),
            "schema_model": MotorCADEfficiencyInput,
        },
    ],
}


def normalize_domain(domain: str) -> str:
    """Normalize domain name using synonym dictionary."""
    clean = (domain or "").strip().lower()
    return DOMAIN_SYNONYMS.get(clean, clean)


def ensure_domain_loaded(domain: str) -> None:
    """Dynamically import product modules for the specified domain on-demand."""
    canonical = normalize_domain(domain)
    if canonical in ("all", "*"):
        for modules in DOMAIN_MODULE_MAP.values():
            for mod in modules:
                try:
                    importlib.import_module(mod)
                except Exception as exc:
                    logger.debug(f"Module {mod} import notice: {exc}")
        return

    modules_to_load = DOMAIN_MODULE_MAP.get(canonical, [])
    for mod in modules_to_load:
        try:
            importlib.import_module(mod)
        except Exception as exc:
            logger.debug(f"Dynamic load for {mod} in domain '{canonical}' notice: {exc}")


def _is_tool_in_domain(name: str, desc: str, module: str, domain: str) -> bool:
    """Determine whether a tool matches a physics domain classification."""
    n = name.lower()
    d = (desc or "").lower()
    m = (module or "").lower()

    if domain in ("all", "*"):
        return True

    if domain == "structural":
        return any(x in m for x in ["mechanical", "dyna", "dpf"]) or any(
            x in n for x in ["mechanical_", "dyna_", "dpf_", "structural", "modal", "stress", "deformation"]
        )

    if domain == "fluids":
        return "fluent" in m or any(x in n for x in ["fluent_", "cfx", "flow"])

    if domain == "geometry":
        return "geometry" in m or any(x in n for x in ["geometry_", "spaceclaim_"])

    if domain == "workbench":
        return "workbench" in m or "workbench_" in n

    if domain == "coupling":
        return "workbench" in m or any(x in n for x in ["workflow_", "link", "coupling", "system"])

    if domain == "optimization":
        return "optislang" in m or any(x in n for x in ["optislang_", "surrogate", "mop"])

    if domain == "thermal":
        return "thermal" in n or "thermal" in d or "heat" in d or "temperature" in d or "warpage" in n

    if domain == "materials":
        return "material" in n or "material" in d or "bom" in n

    if domain == "multibody":
        return "joint" in n or "rigid" in n or "multibody" in d

    if domain == "common":
        return "tools." in m and "intent" not in m and "meta_router" not in m

    if domain == "workflow":
        return "intent" in m or n.startswith("workflow_")

    if domain == "electromagnetics":
        return any(x in n for x in ["hfss", "maxwell", "electromagnetic", "pyaedt"])

    if domain == "optics":
        return any(x in n for x in ["speos", "zemax", "optics", "ray"])

    if domain == "sound":
        return any(x in n for x in ["sound", "acoustic", "loudness", "zwicker", "sone", "decibel"]) or "sound" in d or "acoustic" in d

    if domain == "aqwa":
        return any(x in n for x in ["aqwa", "hydrodynamic", "wave_diffraction", "rao", "marine"]) or "aqwa" in d or "hydrodynamic" in d

    if domain == "lumerical":
        return any(x in n for x in ["lumerical", "waveguide", "fdtd", "mode_solver", "photonic"]) or "lumerical" in d or "waveguide" in d

    if domain == "chemkin":
        return any(x in n for x in ["chemkin", "kinetics", "arrhenius", "combustion", "reaction"]) or "chemkin" in d or "reaction" in d

    if domain == "motorcad":
        return any(x in n for x in ["motorcad", "motor_cad", "pmsm", "electric_machine", "winding"]) or "motorcad" in d or "motor-cad" in d

    return False


# Input schemas for meta tools
class ListDomainToolsInput(BaseModel):
    """Input model for listing tools within a domain."""

    model_config = ConfigDict(extra="forbid")

    domain: str = Field(
        ...,
        description="Target physics domain (e.g. structural, fluids, electromagnetics, optics, sound, aqwa, lumerical, chemkin, motorcad, thermal, multibody, coupling, materials, geometry, optimization, workbench, common, all).",
    )


class CallDomainToolInput(BaseModel):
    """Input model for dynamically invoking a domain tool."""

    model_config = ConfigDict(extra="forbid")

    domain: str = Field(
        ...,
        description="Target physics domain identifier.",
    )
    tool_name: str = Field(
        ...,
        description="Name of the tool to execute (canonical name or registered alias).",
    )
    arguments: Optional[dict[str, Any]] = Field(
        default_factory=dict,
        description="Dictionary of parameters to pass to the tool.",
    )


@aliased_tool(
    name="ans_list_domain_tools",
    annotations=create_tool_annotations(read_only=True, idempotent=True),
    description="Query and list all available tools for a physics domain with descriptions, 4-key annotations, and JSON parameter schemas.",
)
@validate_flat_pydantic(ListDomainToolsInput)
async def ans_list_domain_tools(domain: str) -> dict:
    """Discover available tools in a specific physics domain.

    Parameters:
        domain: Target physics domain name.

    Returns:
        Structured response envelope containing tools with schemas and annotations.
    """
    start_time = time.perf_counter()
    canonical_domain = normalize_domain(domain)

    # 1. Ensure domain product modules are imported on-demand
    ensure_domain_loaded(canonical_domain)

    # 2. Collect tools from FastMCP registry
    raw_tools = await mcp.list_tools()
    matched_tools: list[dict[str, Any]] = []
    seen_names: Set[str] = set()

    for t in raw_tools:
        name = t.name
        if name in seen_names:
            continue

        fn = get_tool_function(name)
        mod = getattr(fn, "__module__", "") if fn else ""
        desc = t.description or ""

        if _is_tool_in_domain(name, desc, mod, canonical_domain):
            seen_names.add(name)

            # Extract 4-key annotations
            ann_dict = {
                "readOnlyHint": False,
                "destructiveHint": False,
                "idempotentHint": False,
                "openWorldHint": False,
            }
            if t.annotations:
                if hasattr(t.annotations, "model_dump"):
                    ann_dump = t.annotations.model_dump()
                    ann_dict = {k: bool(ann_dump.get(k, False)) for k in ann_dict}
                elif isinstance(t.annotations, dict):
                    ann_dict = {k: bool(t.annotations.get(k, False)) for k in ann_dict}

            # Extract parameters JSON schema
            parameters = getattr(t, "parameters", None) or {"type": "object", "properties": {}}

            matched_tools.append({
                "name": name,
                "description": desc,
                "annotations": ann_dict,
                "parameters": parameters,
            })

    # 3. Include virtual staging tools if domain has dedicated models
    virtual_tools = VIRTUAL_DOMAIN_TOOLS.get(canonical_domain, [])
    for vt in virtual_tools:
        if vt["name"] not in seen_names:
            seen_names.add(vt["name"])
            matched_tools.append({
                "name": vt["name"],
                "description": vt["description"],
                "annotations": vt["annotations"],
                "parameters": vt["parameters"],
            })

    elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
    summary = f"Discovered {len(matched_tools)} available tools for domain '{canonical_domain}'."

    return create_response_envelope(
        data={
            "domain": canonical_domain,
            "catalog": DOMAIN_CATALOG.get(canonical_domain, {}),
            "tool_count": len(matched_tools),
            "tools": matched_tools,
        },
        summary=summary,
        execution_time_ms=elapsed_ms,
    )


@aliased_tool(
    name="ans_call_domain_tool",
    annotations=create_tool_annotations(read_only=False, destructive=False, idempotent=False, open_world=True),
    description="Dynamically invoke any tool across physics domains on demand with arguments and structured response envelope wrapping.",
)
@validate_flat_pydantic(CallDomainToolInput)
async def ans_call_domain_tool(domain: str, tool_name: str, arguments: Optional[dict[str, Any]] = None) -> dict:
    """Dynamically invoke a domain tool by name with arguments.

    Parameters:
        domain: Physics domain identifier.
        tool_name: Target tool name or registered alias.
        arguments: Key-value parameters dictionary for the tool.

    Returns:
        Structured response envelope with execution result or ASD-STE100 error details.
    """
    start_time = time.perf_counter()
    canonical_domain = normalize_domain(domain)
    args = arguments if arguments is not None else {}

    # 1. Dynamically ensure domain product modules are loaded
    ensure_domain_loaded(canonical_domain)

    # 2. Resolve canonical tool name
    target_name = get_canonical_name(tool_name)

    # 3. Check for virtual domain schema execution with cross-domain fallback
    virtual_tools = VIRTUAL_DOMAIN_TOOLS.get(canonical_domain, [])
    if not any(vt["name"] == target_name for vt in virtual_tools):
        for other_dom, other_vts in VIRTUAL_DOMAIN_TOOLS.items():
            for vt in other_vts:
                if vt["name"] == target_name:
                    virtual_tools = [vt]
                    canonical_domain = other_dom
                    break
            if virtual_tools:
                break

    for vt in virtual_tools:
        if vt["name"] == target_name:
            schema_model = vt.get("schema_model")
            if schema_model:
                try:
                    validated = schema_model(**args)
                    elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
                    return create_response_envelope(
                        data={
                            "tool": target_name,
                            "domain": canonical_domain,
                            "parameters": validated.model_dump(),
                            "status": "validated_staging",
                        },
                        summary=f"Staging parameters for '{target_name}' validated successfully.",
                        execution_time_ms=elapsed_ms,
                    )
                except ValidationError as exc:
                    elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
                    err_lines = [f"{'.'.join(str(l) for l in e.get('loc', []))}: {e.get('msg', '')}" for e in exc.errors()]
                    return create_error_envelope(
                        status="error",
                        error_code="VALIDATION_ERROR",
                        message=f"Validation failed for '{target_name}': {'; '.join(err_lines)}",
                        recovery_action=f"Verify parameters match schema for {schema_model.__name__}.",
                        execution_time_ms=elapsed_ms,
                    )

    # 4. Resolve registered callable function with cross-domain routing
    fn = get_tool_function(target_name)
    if fn is None:
        for other_dom, tool_list in DOMAIN_ROUTER_TOOL_MAP.items():
            if target_name in tool_list:
                ensure_domain_loaded(other_dom)
                fn = get_tool_function(target_name)
                if fn is not None:
                    canonical_domain = other_dom
                    break

    if fn is None:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        return create_error_envelope(
            status="error",
            error_code="TOOL_NOT_FOUND",
            message=f"Tool '{tool_name}' (canonical: '{target_name}') was not found in domain '{domain}'.",
            recovery_action=f"Call ans_list_domain_tools('{domain}') to inspect available tools.",
            execution_time_ms=elapsed_ms,
        )

    # 5. Invoke target function
    try:
        if inspect.iscoroutinefunction(fn):
            raw_result = await fn(**args)
        else:
            raw_result = fn(**args)
    except TypeError as exc:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        return create_error_envelope(
            status="error",
            error_code="INVALID_ARGUMENTS",
            message=f"Argument mismatch when calling '{tool_name}': {exc}",
            recovery_action=f"Check parameter signatures via ans_list_domain_tools('{domain}').",
            execution_time_ms=elapsed_ms,
        )
    except Exception as exc:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        return create_error_envelope(
            status="error",
            error_code="TOOL_EXECUTION_EXCEPTION",
            message=f"Exception encountered while executing '{tool_name}': {exc}",
            recovery_action=f"Review simulator connectivity and input values for '{tool_name}'.",
            execution_time_ms=elapsed_ms,
        )

    elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

    # 6. Wrap result in standardized response envelope
    if isinstance(raw_result, dict):
        # Handle failure reported by the underlying tool
        if raw_result.get("ok") is False or raw_result.get("status") == "error":
            err_code = raw_result.get("error_code") or "TOOL_EXECUTION_FAILED"
            err_msg = raw_result.get("error") or raw_result.get("message") or "Tool returned failure."
            rec_action = raw_result.get("recovery_action") or (
                raw_result.get("suggested_actions", [None])[0] if raw_result.get("suggested_actions") else None
            )
            extra_meta = {
                k: v for k, v in raw_result.items()
                if k not in ("ok", "status", "error_code", "message", "error", "recovery_action", "suggested_actions")
            }
            return create_error_envelope(
                status="error",
                error_code=err_code,
                message=err_msg,
                recovery_action=rec_action,
                execution_time_ms=elapsed_ms,
                **extra_meta,
            )

        summary = raw_result.get("summary") or f"Tool '{tool_name}' executed successfully."
        file_path = raw_result.get("file_path") or raw_result.get("path")
        sha256 = raw_result.get("sha256")
        return create_response_envelope(
            data=raw_result,
            summary=summary,
            file_path=file_path,
            sha256=sha256,
            execution_time_ms=elapsed_ms,
        )

    return create_response_envelope(
        data=raw_result,
        summary=f"Tool '{tool_name}' executed successfully.",
        execution_time_ms=elapsed_ms,
    )
