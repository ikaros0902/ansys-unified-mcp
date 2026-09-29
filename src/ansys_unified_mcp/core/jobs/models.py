"""ANSYS Unified MCP 2.0 - 模擬作業資料模型 (Job Data Models).

定義三位一體標準產出矩陣之 Pydantic 資料結構：
- SimulationSummary: 機器可讀之模擬關鍵結果摘要
- PhysicalMetrics: 結構、振動、衝擊、熱翹曲與顯式動力學核心物理純量指標
- ExecutionMetadata: 作業執行時間、進程 PID、求解器版本與熔斷資訊
"""

from __future__ import annotations

import json
import os
import uuid
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class JobStatusEnum(str, Enum):
    """模擬作業生命週期狀態枚舉。"""
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SOLVED = "SOLVED"
    FAILED = "FAILED"
    ABORTED = "ABORTED"


class VerdictEnum(str, Enum):
    """工程裁決判定枚舉。"""
    PASS = "PASS"
    FAIL = "FAIL"
    INCONCLUSIVE = "INCONCLUSIVE"


class PhysicalMetrics(BaseModel):
    """模擬核心物理純量指標模型。"""
    model_config = ConfigDict(extra="allow")

    # 應力與強度
    max_equivalent_stress_mpa: Optional[float] = Field(
        default=None, description="最大 von-Mises 等效應力 (MPa)"
    )
    material_yield_strength_mpa: Optional[float] = Field(
        default=None, description="材料降伏強度 (MPa)"
    )
    safety_factor: Optional[float] = Field(
        default=None, description="安全係數 (Yield Strength / Max Equivalent Stress)"
    )

    # 變形與翹曲
    max_total_deformation_mm: Optional[float] = Field(
        default=None, description="最大總變形量 (mm)"
    )
    max_warpage_z_um: Optional[float] = Field(
        default=None, description="Z 軸最大翹曲位移 (um)"
    )

    # 動力學與振動
    first_mode_frequency_hz: Optional[float] = Field(
        default=None, description="第一階特徵頻率 (Hz)"
    )
    effective_mass_ratio_x: Optional[float] = Field(
        default=None, description="X 向有效模態質量累積佔比 (0.0~1.0)"
    )
    effective_mass_ratio_y: Optional[float] = Field(
        default=None, description="Y 向有效模態質量累積佔比 (0.0~1.0)"
    )
    effective_mass_ratio_z: Optional[float] = Field(
        default=None, description="Z 向有效模態質量累積佔比 (0.0~1.0)"
    )
    peak_acceleration_g: Optional[float] = Field(
        default=None, description="衝擊加速度峰值 (G)"
    )

    # 顯式動力學健康度
    hourglass_energy_ratio_pct: Optional[float] = Field(
        default=None, description="沙漏能佔總能量百分比 (%)"
    )
    mass_scaling_added_pct: Optional[float] = Field(
        default=None, description="質量縮放增加質量百分比 (%)"
    )
    contact_sliding_energy_joules: Optional[float] = Field(
        default=None, description="接觸滑移能 (J)"
    )

    # 代理模型與收斂歷程
    cop_score: Optional[float] = Field(
        default=None, description="optiSLang MOP 最佳預測係數 CoP (0.0~1.0)"
    )
    final_convergence_residual: Optional[float] = Field(
        default=None, description="最終力平衡收斂殘差"
    )

    @model_validator(mode="after")
    def compute_safety_factor_if_missing(self) -> PhysicalMetrics:
        """若未明確提供 safety_factor 但具備應力與降伏強度，自動計算安全係數。"""
        if self.safety_factor is None:
            if (
                self.material_yield_strength_mpa is not None
                and self.max_equivalent_stress_mpa is not None
                and self.max_equivalent_stress_mpa > 0
            ):
                self.safety_factor = round(
                    self.material_yield_strength_mpa / self.max_equivalent_stress_mpa, 4
                )
        return self


class ExecutionMetadata(BaseModel):
    """求解作業執行細節元資料。"""
    model_config = ConfigDict(extra="allow")

    created_at: str = Field(description="作業建立時間 (ISO 8601 UTC)")
    started_at: Optional[str] = Field(default=None, description="作業開始求解時間")
    finished_at: Optional[str] = Field(default=None, description="作業完成時間")
    duration_seconds: Optional[float] = Field(default=None, description="執行總耗時 (秒)")
    solver_name: str = Field(description="求解器名稱 (MAPDL, LS-DYNA, Fluent, optiSLang)")
    solver_version: str = Field(default="2026 R1", description="求解器版本")
    pid: Optional[int] = Field(default=None, description="底層求解進程 PID")
    exit_code: Optional[int] = Field(default=None, description="進程結束返回碼")
    circuit_breaker_triggered: bool = Field(default=False, description="是否觸發早期發散熔斷")
    circuit_breaker_reason: Optional[str] = Field(default=None, description="熔斷觸發原因說明")


class SimulationSummary(BaseModel):
    """三位一體標準成果產物之 summary.json 根模型。"""
    model_config = ConfigDict(extra="allow")

    job_id: str = Field(description="唯一作業標識符")
    workflow_type: str = Field(description="工作流類型")
    tag: str = Field(default="default", description="作業標籤")
    status: JobStatusEnum = Field(default=JobStatusEnum.QUEUED, description="生命週期狀態")
    verdict: VerdictEnum = Field(default=VerdictEnum.INCONCLUSIVE, description="工程判定結論")
    failure_reasons: List[str] = Field(default_factory=list, description="失敗或熔斷原因列表")
    metrics: PhysicalMetrics = Field(default_factory=PhysicalMetrics, description="物理關鍵指標")
    execution: ExecutionMetadata = Field(description="執行細節元資料")
    artifacts: Dict[str, str] = Field(default_factory=dict, description="產生物相對/絕對路徑對照表")

    def to_json(self, indent: int = 2) -> str:
        """導出符合 Schema 規範之 JSON 字串。"""
        return self.model_dump_json(indent=indent)

    def save(self, file_path: Path | str) -> Path:
        """儲存至指定路徑之 summary.json 檔案（採用原子覆寫防護多線程競爭）。"""
        target = Path(file_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp_target = target.parent / f".tmp_summary_{uuid.uuid4().hex[:8]}.json"
        tmp_target.write_text(self.to_json(indent=2), encoding="utf-8")
        os.replace(tmp_target, target)
        return target

    @classmethod
    def from_json_file(cls, file_path: Path | str) -> SimulationSummary:
        """從 summary.json 檔案反序列化載入。"""
        target = Path(file_path)
        if not target.exists():
            raise FileNotFoundError(f"找不到 summary.json 檔案: {target}")
        data = json.loads(target.read_text(encoding="utf-8"))
        return cls.model_validate(data)
