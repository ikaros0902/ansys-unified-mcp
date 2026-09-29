from typing import Any, Dict

from ansys_unified_mcp.core.gatekeeper.evidence import verify_manifest
from ansys_unified_mcp.core.gatekeeper.prescription import (
    ActionCodeEnum,
    CheckResult,
    PrescriptionDetail,
    RuleStatusEnum,
    SeverityEnum,
)
from ansys_unified_mcp.core.gatekeeper.rules import BaseGateRule


class EvidenceIntegrityRule(BaseGateRule):
    """資料完整性證據檢核規則 (Evidence Integrity Rule)。
    
    確保在工作流各階段傳遞的實體檔案 (例如 CAD 到 Mesh, Mesh 到 Solve)
    並未在傳遞過程中被竄改或遺失。
    """
    
    rule_id = "GATE-EVI-001"
    rule_name = "證據清單完整性檢核"
    severity = SeverityEnum.FATAL
    
    def check(self, context: Dict[str, Any]) -> CheckResult:
        if "evidence_manifest" not in context:
            # 若無 evidence_manifest 則略過檢核 (視為 PASSED)
            return CheckResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                status=RuleStatusEnum.PASSED,
                severity=SeverityEnum.INFO,
                diagnosis="未提供 evidence_manifest，略過檔案完整性檢核。",
                prescription=None,
            )
            
        manifest = context["evidence_manifest"]
        is_valid = verify_manifest(manifest)
        
        if is_valid:
            return CheckResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                status=RuleStatusEnum.PASSED,
                severity=SeverityEnum.INFO,
                observed_value={"file_path": manifest.get("file_path"), "valid": True},
                diagnosis=f"證據檔案完整性檢核通過: {manifest.get('file_path')}",
                prescription=None,
            )
        else:
            return CheckResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                status=RuleStatusEnum.BLOCKED,
                severity=SeverityEnum.FATAL,
                observed_value={"file_path": manifest.get("file_path"), "valid": False},
                diagnosis=f"證據檔案遺失或 Hash 驗證失敗: {manifest.get('file_path')}",
                prescription=PrescriptionDetail(
                    action_code=ActionCodeEnum.GENERIC_REMEDIATION.value,
                    suggested_fix="請確認檔案未被意外刪除或修改，或重新生成前置階段的證據清單。",
                    code_snippet="# 重新產生檔案與對應的 evidence_manifest\nmanifest = create_manifest(file_path, semantic_ids)",
                )
            )
