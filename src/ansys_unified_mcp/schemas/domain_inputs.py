# -*- coding: utf-8 -*-
"""Pydantic input models for specific physics domains.

All domain models strictly configure extra='forbid' to guarantee strict validation,
prevent silent parameter errors, and support schema reflection.
All comments and docstrings in this module strictly use ASCII English.
"""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


# -----------------------------------------------------------------------------
# Electromagnetics Domain (HFSS / Maxwell)
# -----------------------------------------------------------------------------

class HFSSAdaptiveMeshInput(BaseModel):
    """Input parameters for HFSS adaptive mesh refinement setup."""

    model_config = ConfigDict(extra="forbid")

    freq_ghz: float = Field(
        ...,
        gt=0.0,
        description="Adaptive solution frequency in GHz.",
    )
    max_delta_s: float = Field(
        default=0.02,
        gt=0.0,
        description="Target S-parameter convergence delta limit.",
    )
    max_passes: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of adaptive refinement passes.",
    )
    min_passes: int = Field(
        default=1,
        ge=1,
        description="Minimum number of adaptive passes to execute.",
    )
    min_converged_passes: int = Field(
        default=1,
        ge=1,
        description="Number of consecutive passes required below max_delta_s.",
    )


class MaxwellSetupInput(BaseModel):
    """Input parameters for Maxwell solver configuration."""

    model_config = ConfigDict(extra="forbid")

    setup_name: str = Field(
        default="Setup1",
        description="Name of the Maxwell solver setup.",
    )
    solve_type: str = Field(
        default="Magnetostatic",
        description="Formulation type (Magnetostatic, Transient, EddyCurrent).",
    )
    percent_error: float = Field(
        default=1.0,
        ge=0.01,
        le=100.0,
        description="Target percentage error convergence limit.",
    )
    max_passes: int = Field(
        default=15,
        ge=1,
        description="Maximum adaptive refinement passes.",
    )


# -----------------------------------------------------------------------------
# Fluids Domain (Fluent / CFX)
# -----------------------------------------------------------------------------

class FluentBoundaryConditionInput(BaseModel):
    """Input parameters for Fluent boundary condition setup."""

    model_config = ConfigDict(extra="forbid")

    zone_name: str = Field(
        ...,
        description="Target boundary zone identifier.",
    )
    bc_type: str = Field(
        default="velocity-inlet",
        description="Boundary type (velocity-inlet, pressure-outlet, wall, symmetry).",
    )
    velocity_magnitude: float = Field(
        default=1.0,
        ge=0.0,
        description="Inlet velocity magnitude in m/s.",
    )
    temperature_k: float = Field(
        default=300.0,
        gt=0.0,
        description="Fluid temperature in Kelvin.",
    )
    turbulent_intensity: float = Field(
        default=0.05,
        ge=0.0,
        le=1.0,
        description="Turbulence intensity fraction (0.0 to 1.0).",
    )


class FluentSolverSettingsInput(BaseModel):
    """Input parameters for Fluent solver formulation and iterations."""

    model_config = ConfigDict(extra="forbid")

    solver_type: str = Field(
        default="pressure-based",
        description="Solver formulation (pressure-based or density-based).",
    )
    time_dependence: str = Field(
        default="steady",
        description="Time formulation (steady or transient).",
    )
    turbulence_model: str = Field(
        default="k-omega-sst",
        description="Turbulence model formulation (k-omega-sst, k-epsilon, laminar).",
    )
    num_iterations: int = Field(
        default=100,
        ge=1,
        description="Total solver iterations to execute.",
    )


# -----------------------------------------------------------------------------
# Structural Domain (Mechanical / MAPDL)
# -----------------------------------------------------------------------------

class MechanicalMeshInput(BaseModel):
    """Input parameters for Mechanical global mesh configuration."""

    model_config = ConfigDict(extra="forbid")

    element_size: float = Field(
        ...,
        gt=0.0,
        description="Global element mesh size in meters.",
    )
    mesh_metric: str = Field(
        default="Skewness",
        description="Mesh quality metric (Skewness, AspectRatio, OrthogonalQuality).",
    )
    growth_rate: float = Field(
        default=1.2,
        ge=1.0,
        le=3.0,
        description="Mesh size transition growth rate.",
    )


class MechanicalBoundaryConditionInput(BaseModel):
    """Input parameters for Mechanical structural load or restraint."""

    model_config = ConfigDict(extra="forbid")

    named_selection: str = Field(
        ...,
        description="Target Named Selection or boundary scope.",
    )
    bc_type: str = Field(
        ...,
        description="Boundary condition type (FixedSupport, Force, Pressure, Displacement).",
    )
    magnitude: float = Field(
        default=0.0,
        description="Load or displacement magnitude value.",
    )
    unit: str = Field(
        default="N",
        description="Engineering unit for magnitude (e.g. N, Pa, mm).",
    )


class StaticStructuralSolveInput(BaseModel):
    """Input parameters for Static Structural analysis execution."""

    model_config = ConfigDict(extra="forbid")

    analysis_name: str = Field(
        default="Static Structural",
        description="Target structural analysis system name.",
    )
    large_deflection: bool = Field(
        default=False,
        description="Enable non-linear large deflection geometric effects.",
    )
    num_modes: int = Field(
        default=6,
        ge=1,
        description="Number of modal modes if coupled with prestressed modal.",
    )


# -----------------------------------------------------------------------------
# Thermal Domain
# -----------------------------------------------------------------------------

class SteadyThermalSolveInput(BaseModel):
    """Input parameters for Steady-State Thermal analysis."""

    model_config = ConfigDict(extra="forbid")

    ambient_temperature: float = Field(
        default=22.0,
        description="Ambient reference temperature in Celsius.",
    )
    convection_coefficient: float = Field(
        default=10.0,
        ge=0.0,
        description="Convective heat transfer coefficient in W/(m^2*K).",
    )
    heat_flux: float = Field(
        default=0.0,
        ge=0.0,
        description="Applied surface heat flux in W/m^2.",
    )


# -----------------------------------------------------------------------------
# Geometry Domain (SpaceClaim / PyAnsys Geometry)
# -----------------------------------------------------------------------------

class GeometryCreateBlockInput(BaseModel):
    """Input parameters for creating a 3D rectangular block."""

    model_config = ConfigDict(extra="forbid")

    x_length: float = Field(
        ...,
        gt=0.0,
        description="Block dimension along X axis in millimeters.",
    )
    y_length: float = Field(
        ...,
        gt=0.0,
        description="Block dimension along Y axis in millimeters.",
    )
    z_length: float = Field(
        ...,
        gt=0.0,
        description="Block dimension along Z axis in millimeters.",
    )
    name: str = Field(
        default="Block",
        description="Body name for created block.",
    )


class GeometryCreateCylinderInput(BaseModel):
    """Input parameters for creating a 3D cylinder."""

    model_config = ConfigDict(extra="forbid")

    radius: float = Field(
        ...,
        gt=0.0,
        description="Cylinder radius in millimeters.",
    )
    length: float = Field(
        ...,
        gt=0.0,
        description="Cylinder axial length in millimeters.",
    )
    name: str = Field(
        default="Cylinder",
        description="Body name for created cylinder.",
    )


# -----------------------------------------------------------------------------
# Explicit Dynamics Domain (LS-DYNA)
# -----------------------------------------------------------------------------

class LSDynaDropTestInput(BaseModel):
    """Input parameters for transient drop impact test simulation."""

    model_config = ConfigDict(extra="forbid")

    drop_height_mm: float = Field(
        ...,
        gt=0.0,
        description="Drop height in millimeters.",
    )
    impact_angle_deg: float = Field(
        default=0.0,
        description="Orientation angle at impact in degrees.",
    )
    termination_time_ms: float = Field(
        default=5.0,
        gt=0.0,
        description="Simulation termination time in milliseconds.",
    )


# -----------------------------------------------------------------------------
# Multibody Domain (Rigid Dynamics / Kinematic Joints)
# -----------------------------------------------------------------------------

class MultibodyJointInput(BaseModel):
    """Input parameters for defining a kinematic joint between bodies."""

    model_config = ConfigDict(extra="forbid")

    joint_type: str = Field(
        default="Revolute",
        description="Kinematic joint type (Revolute, Prismatic, Fixed, Spherical).",
    )
    reference_body: str = Field(
        ...,
        description="Reference body name or Named Selection.",
    )
    mobile_body: str = Field(
        ...,
        description="Mobile body name or Named Selection.",
    )


# -----------------------------------------------------------------------------
# Materials Domain
# -----------------------------------------------------------------------------

class MaterialAssignmentInput(BaseModel):
    """Input parameters for assigning engineering material to a body."""

    model_config = ConfigDict(extra="forbid")

    part_name: str = Field(
        ...,
        description="Target body or component name.",
    )
    material_name: str = Field(
        ...,
        description="Material identifier in engineering database.",
    )


# -----------------------------------------------------------------------------
# Optimization Domain (optiSLang)
# -----------------------------------------------------------------------------

class OptislangMOPInput(BaseModel):
    """Input parameters for Metamodel of Optimal Prognosis (MOP)."""

    model_config = ConfigDict(extra="forbid")

    design_variables: List[str] = Field(
        ...,
        min_length=1,
        description="List of design parameter names to vary.",
    )
    responses: List[str] = Field(
        ...,
        min_length=1,
        description="List of target response variable names to evaluate.",
    )
    max_samples: int = Field(
        default=100,
        ge=10,
        description="Maximum sample designs for surrogate generation.",
    )


# -----------------------------------------------------------------------------
# Optics Domain (Speos / Zemax)
# -----------------------------------------------------------------------------

class OpticsSimulationInput(BaseModel):
    """Input parameters for optical ray tracing simulation."""

    model_config = ConfigDict(extra="forbid")

    source_type: str = Field(
        default="luminaire",
        description="Optical source definition type.",
    )
    ray_count: int = Field(
        default=1000000,
        ge=1000,
        description="Monte Carlo ray count for tracing.",
    )
    wavelength_nm: float = Field(
        default=550.0,
        gt=0.0,
        description="Primary optical wavelength in nanometers.",
    )


# -----------------------------------------------------------------------------
# Sound & Acoustics Domain (Ansys Sound / NVH)
# -----------------------------------------------------------------------------

class SoundPsychoacousticsInput(BaseModel):
    """Input parameters for Zwicker psychoacoustics and acoustic propagation."""

    model_config = ConfigDict(extra="forbid")

    frequency_hz: float = Field(
        default=1000.0,
        gt=0.0,
        description="Acoustic tone frequency in Hz.",
    )
    spl_db: float = Field(
        default=40.0,
        ge=0.0,
        description="Sound pressure level at reference distance in dB.",
    )
    distance_m: float = Field(
        default=1.0,
        gt=0.0,
        description="Radial observation distance in meters.",
    )


# -----------------------------------------------------------------------------
# Marine Hydrodynamics Domain (AQWA)
# -----------------------------------------------------------------------------

class MarineAqwaHeaveInput(BaseModel):
    """Input parameters for marine vessel heave hydrodynamics simulation."""

    model_config = ConfigDict(extra="forbid")

    length: float = Field(
        default=20.0,
        gt=0.0,
        description="Vessel total length in meters.",
    )
    beam: float = Field(
        default=10.0,
        gt=0.0,
        description="Vessel beam width in meters.",
    )
    draft: float = Field(
        default=2.0,
        gt=0.0,
        description="Vessel draft depth in meters.",
    )
    water_density: float = Field(
        default=1025.0,
        gt=0.0,
        description="Seawater density in kg/m^3.",
    )


# -----------------------------------------------------------------------------
# Wave Optics & Photonics Domain (Lumerical FDTD / MODE)
# -----------------------------------------------------------------------------

class LumericalSlabWaveguideInput(BaseModel):
    """Input parameters for photonic slab waveguide eigenmode simulation."""

    model_config = ConfigDict(extra="forbid")

    core_index: float = Field(
        default=1.50,
        gt=1.0,
        description="Refractive index of waveguide core layer.",
    )
    cladding_index: float = Field(
        default=1.45,
        gt=1.0,
        description="Refractive index of cladding layer.",
    )
    core_half_thickness_um: float = Field(
        default=1.0,
        gt=0.0,
        description="Waveguide core half-thickness in micrometers.",
    )
    wavelength_um: float = Field(
        default=1.55,
        gt=0.0,
        description="Vacuum operating wavelength in micrometers.",
    )


# -----------------------------------------------------------------------------
# Reaction Kinetics Domain (Chemkin-Pro)
# -----------------------------------------------------------------------------

class ChemkinReactionKineticsInput(BaseModel):
    """Input parameters for 0D chemical reaction kinetics simulation."""

    model_config = ConfigDict(extra="forbid")

    a0_pre_exponential: float = Field(
        default=1.0e6,
        gt=0.0,
        description="Arrhenius pre-exponential factor A0 in 1/s.",
    )
    ea_activation_energy_j_mol: float = Field(
        default=50000.0,
        ge=0.0,
        description="Reaction activation energy in J/mol.",
    )
    temperature_k: float = Field(
        default=500.0,
        gt=0.0,
        description="Reaction temperature in Kelvin.",
    )
    ca0_initial_concentration: float = Field(
        default=1.0,
        gt=0.0,
        description="Initial reactant A concentration in mol/m^3.",
    )


# -----------------------------------------------------------------------------
# Electric Machine Domain (Motor-CAD)
# -----------------------------------------------------------------------------

class MotorCADEfficiencyInput(BaseModel):
    """Input parameters for PMSM motor electromechanical efficiency simulation."""

    model_config = ConfigDict(extra="forbid")

    pole_pairs: int = Field(
        default=4,
        ge=1,
        description="Number of magnetic pole pairs.",
    )
    flux_linkage_wb: float = Field(
        default=0.05,
        gt=0.0,
        description="Permanent magnet flux linkage in Weber.",
    )
    stator_resistance_ohm: float = Field(
        default=0.10,
        gt=0.0,
        description="Stator winding phase resistance in Ohms.",
    )
    omega_m_rad_s: float = Field(
        default=300.0,
        gt=0.0,
        description="Rotor mechanical angular velocity in rad/s.",
    )
    target_torque_nm: float = Field(
        default=15.0,
        gt=0.0,
        description="Target electromagnetic output torque in Nm.",
    )

