"""ANSYS Unified MCP 2.0 - 物理安全閘門檢核規則基類與介面 (Gate Rules)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Set

from ansys_unified_mcp.gatekeeper.prescription import CheckResult, SeverityEnum


class BaseGateRule(ABC):
    """物理安全閘門檢驗規則抽象基類。"""

    rule_id: str
    rule_name: str
    severity: SeverityEnum = SeverityEnum.FATAL
    target_workflows: Set[str] = set()

    def applies_to(self, workflow_type: str) -> bool:
        """判定此規則是否適用於指定的工作流類型。若為空集合則表示適用於所有工況。"""
        if not self.target_workflows:
            return True
        return workflow_type.lower() in {w.lower() for w in self.target_workflows}

    @abstractmethod
    def check(self, context: Dict[str, Any]) -> CheckResult:
        """執行物理檢核並回傳 CheckResult。"""
        pass
