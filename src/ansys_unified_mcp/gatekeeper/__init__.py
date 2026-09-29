"""Backward-compatibility shim for ansys_unified_mcp.gatekeeper -> ansys_unified_mcp.core.gatekeeper."""
from ansys_unified_mcp.core.gatekeeper import *
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
]
