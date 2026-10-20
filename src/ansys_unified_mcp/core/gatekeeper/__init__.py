"""ANSYS Unified MCP 2.0 - 求解前置安全閘門與自愈處方箋套件 (Gatekeeper Package)."""

from ansys_unified_mcp.core.gatekeeper.gatekeeper import Gatekeeper
from ansys_unified_mcp.core.gatekeeper.prescription import (
    ActionCodeEnum,
    CheckResult,
    PreFlightGatekeeperError,
    PreFlightPrescriptionReport,
    PrescriptionDetail,
    RuleStatusEnum,
    SeverityEnum,
)
from ansys_unified_mcp.core.gatekeeper.rules import BaseGateRule
from ansys_unified_mcp.core.gatekeeper.rules.drop_impact_rules import (
    ContactIntegrityRule,
    CriticalTimeStepRule,
    DropVelocityVectorRule,
)
from ansys_unified_mcp.core.gatekeeper.rules.thermal_rules import (
    NonZeroSecantCTERule,
    ZeroStressReferenceTemperatureRule,
)
from ansys_unified_mcp.core.gatekeeper.rules.unit_consistency import UnitConsistencyRule
from ansys_unified_mcp.core.gatekeeper.rules.vibration_rules import (
    ModalCutoffFrequencyRule,
    ModalEffectiveMassRatioRule,
)
from ansys_unified_mcp.core.gatekeeper.fcstd_parser import (
    validate_fcstd_archive,
    parse_fcstd_metadata,
)
from ansys_unified_mcp.core.gatekeeper.staged_diagnostics import (
    FailureClassEnum,
    StagedDiagnosticReport,
    evaluate_staged_rubric,
    assert_ascii_host_script,
    FREECAD_TO_ANSYS_TYPE_MAP,
    FREECAD_TO_ANSYS_LABEL_MAP,
)

__all__ = [
    "Gatekeeper",
    "PreFlightPrescriptionReport",
    "PreFlightGatekeeperError",
    "CheckResult",
    "PrescriptionDetail",
    "RuleStatusEnum",
    "SeverityEnum",
    "ActionCodeEnum",
    "BaseGateRule",
    "ModalEffectiveMassRatioRule",
    "ModalCutoffFrequencyRule",
    "DropVelocityVectorRule",
    "CriticalTimeStepRule",
    "ContactIntegrityRule",
    "NonZeroSecantCTERule",
    "ZeroStressReferenceTemperatureRule",
    "UnitConsistencyRule",
    "validate_fcstd_archive",
    "parse_fcstd_metadata",
    "FailureClassEnum",
    "StagedDiagnosticReport",
    "evaluate_staged_rubric",
    "assert_ascii_host_script",
    "FREECAD_TO_ANSYS_TYPE_MAP",
    "FREECAD_TO_ANSYS_LABEL_MAP",
]
