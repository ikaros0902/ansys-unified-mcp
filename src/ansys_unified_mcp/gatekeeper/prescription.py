"""ANSYS Unified MCP 2.0 - 前置安全閘門結構化自愈處方箋 (Pre-Flight Prescription Schema).

依據 PreFlightPrescriptionReport JSON Schema 定義阻斷檢驗結果、
診斷說明與可執行修復代碼段 (Code Snippets)。
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class RuleStatusEnum(str, Enum):
    """檢核項目狀態枚舉。"""
    PASSED = "PASSED"
    BLOCKED = "BLOCKED"
    WARNING = "WARNING"


class SeverityEnum(str, Enum):
    """嚴重度等級枚舉。"""
    FATAL = "FATAL"
    WARNING = "WARNING"
    INFO = "INFO"


class ActionCodeEnum(str, Enum):
    """標準化自愈處方箋動作代碼。"""
    INCREASE_MODES_AND_CUTOFF = "INCREASE_MODES_AND_CUTOFF"
    EXTEND_FREQUENCY_RANGE = "EXTEND_FREQUENCY_RANGE"
    INVERT_VELOCITY_OR_NORMAL = "INVERT_VELOCITY_OR_NORMAL"
    CONFIGURE_MASS_SCALING = "CONFIGURE_MASS_SCALING"
    DEFINE_RIGIDWALL_OR_CONTACT = "DEFINE_RIGIDWALL_OR_CONTACT"
    ASSIGN_TEMPERATURE_DEPENDENT_CTE = "ASSIGN_TEMPERATURE_DEPENDENT_CTE"
    SPECIFY_REFERENCE_TEMPERATURE = "SPECIFY_REFERENCE_TEMPERATURE"
    CONVERT_TO_CONSISTENT_UNIT_SYSTEM = "CONVERT_TO_CONSISTENT_UNIT_SYSTEM"
    GENERIC_REMEDIATION = "GENERIC_REMEDIATION"


class PrescriptionDetail(BaseModel):
    """結構化自愈處方細節。"""
    model_config = ConfigDict(extra="allow")

    action_code: str = Field(description="標準化修復動作代號")
    suggested_fix: str = Field(description="具體工程修復指導建議")
    code_snippet: str = Field(description="直接可用的修復腳本或參數設定代碼段")


class CheckResult(BaseModel):
    """單一物理規則檢驗結果。"""
    model_config = ConfigDict(extra="allow")

    rule_id: str = Field(description="規則編號 (如 GATE-VIB-001)")
    rule_name: str = Field(description="規則可讀名稱")
    status: RuleStatusEnum = Field(description="檢驗狀態 (PASSED, BLOCKED, WARNING)")
    severity: SeverityEnum = Field(description="嚴重度等級 (FATAL, WARNING, INFO)")
    observed_value: Dict[str, Any] = Field(default_factory=dict, description="觀測到的參數數值")
    required_threshold: Dict[str, Any] = Field(default_factory=dict, description="期望物理門檻值")
    diagnosis: str = Field(description="診斷分析說明")
    prescription: Optional[PrescriptionDetail] = Field(
        default=None, description="自愈處方箋 (若通過則為 None)"
    )


class PreFlightPrescriptionReport(BaseModel):
    """前置安全閘門綜合處方箋報告 (對齊 spec_report.md Schema)。"""
    model_config = ConfigDict(extra="allow")

    gatekeeper: str = Field(default="pre_flight_sentinel", description="閘門守護者識別名稱")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="核驗時間戳記 (ISO 8601 UTC)",
    )
    passed: bool = Field(description="是否全員放行允許送算")
    blocking_issues_count: int = Field(default=0, description="致命阻斷項目總數")
    warnings_count: int = Field(default=0, description="警告項目總數")
    checks: List[CheckResult] = Field(default_factory=list, description="各規則檢核明細列表")

    def to_json(self, indent: int = 2) -> str:
        """導出標準 JSON 格式字串。"""
        return self.model_dump_json(indent=indent)

    def to_dict(self) -> Dict[str, Any]:
        """導出 Python 原始字典結構。"""
        return self.model_dump()

    def summary_markdown(self) -> str:
        """產出高資訊密度 Markdown 格式報告供 AI 或終端呈現。"""
        status_badge = "🟢 PASS (允許送算)" if self.passed else "🔴 BLOCKED (嚴禁送算)"
        lines = [
            f"### 🛡️ 前置物理安全閘門核驗報告: {status_badge}",
            f"- **核驗時間**: `{self.timestamp}`",
            f"- **致命阻斷 (FATAL)**: `{self.blocking_issues_count}` 項",
            f"- **工程警告 (WARNING)**: `{self.warnings_count}` 項",
            "",
            "#### 檢驗項目明細：",
        ]
        for check in self.checks:
            icon = "✅" if check.status == RuleStatusEnum.PASSED else ("❌" if check.status == RuleStatusEnum.BLOCKED else "⚠️")
            lines.append(f"- {icon} **[{check.rule_id}] {check.rule_name}**: {check.status.value} ({check.severity.value})")
            lines.append(f"  - **診斷**: {check.diagnosis}")
            if check.prescription:
                lines.append(f"  - **自愈建議**: {check.prescription.suggested_fix}")
                lines.append(f"  - **修復代碼**:\n```python\n{check.prescription.code_snippet}\n```")
        return "\n".join(lines)


class PreFlightGatekeeperError(Exception):
    """前置物理安全閘門阻斷例外。

    當存在 FATAL 阻斷項目且調用端啟用嚴格阻斷模式時拋出，
    包含完整之結構化處方箋報告。
    """

    def __init__(self, report: PreFlightPrescriptionReport) -> None:
        self.report = report
        blocked_rules = [
            f"{c.rule_id} ({c.rule_name})"
            for c in report.checks
            if c.status == RuleStatusEnum.BLOCKED and c.severity == SeverityEnum.FATAL
        ]
        msg = (
            f"Pre-Flight 物理安全閘門攔截：共發現 {report.blocking_issues_count} 個致命阻斷項目，未達物理標準嚴禁送算！\n"
            f"阻斷規則: {', '.join(blocked_rules)}\n"
            f"請參閱 report 屬性獲取詳細自愈處方箋與修正代碼。"
        )
        super().__init__(msg)
