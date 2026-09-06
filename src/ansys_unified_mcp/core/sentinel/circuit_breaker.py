"""ANSYS Unified MCP 2.0 - 早期物理發散熔斷器 (CircuitBreaker).

實時監控求解物理健康指標，一旦偵測到物理不穩定或數值發散立即執行早期熔斷：
- 沙漏能比例 (Hourglass / Total Energy 或 Internal Energy) > 5% 且持續超標 (去抖動或單次 >15%)
- 質量縮放比例 (Added Mass / Initial Mass) > 5% 破壞動態真實性
- 殘差或物理量出現 NaN / Inf
- 負滑移能 (Sliding Energy < 0 且絕對值 > 10% 總能) 接觸穿透鎖死
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class BreakerVerdict:
    """熔斷判定裁決結果。"""

    triggered: bool = False
    rule_id: Optional[str] = None
    reason: Optional[str] = None
    diagnosis: Optional[str] = None
    action_code: Optional[str] = None
    suggested_fix: Optional[str] = None
    metrics_snapshot: Dict[str, Any] = field(default_factory=dict)


class CircuitBreaker:
    """模擬作業物理健康守護與發散熔斷器。"""

    DEFAULT_HOURGLASS_THRESHOLD_PCT = 5.0
    DEFAULT_MASS_SCALING_THRESHOLD_PCT = 5.0
    DEFAULT_NEGATIVE_SLIDING_RATIO = 0.10  # 10%
    MAX_RESIDUAL_EXPLOSION = 1e10

    def __init__(
        self,
        hourglass_threshold_pct: float = DEFAULT_HOURGLASS_THRESHOLD_PCT,
        mass_scaling_threshold_pct: float = DEFAULT_MASS_SCALING_THRESHOLD_PCT,
        sliding_ratio_threshold: float = DEFAULT_NEGATIVE_SLIDING_RATIO,
        debounce_count: int = 3,
    ) -> None:
        """初始化熔斷器。

        Args:
            hourglass_threshold_pct: 沙漏能佔比上限百分比 (%)
            mass_scaling_threshold_pct: 質量縮放上限百分比 (%)
            sliding_ratio_threshold: 負滑移能佔總能量比例上限
            debounce_count: 沙漏能去抖動容忍次數 (防初始接觸震盪誤殺)
        """
        self.hourglass_threshold_pct = hourglass_threshold_pct
        self.mass_scaling_threshold_pct = mass_scaling_threshold_pct
        self.sliding_ratio_threshold = sliding_ratio_threshold
        self.debounce_count = debounce_count

        self._hourglass_over_count = 0
        self._consecutive_growth_count = 0
        self._last_residual = 0.0

    def reset(self) -> None:
        """重置內部計數器。"""
        self._hourglass_over_count = 0
        self._consecutive_growth_count = 0
        self._last_residual = 0.0

    def evaluate_lsdyna(
        self,
        hourglass_energy: float,
        internal_energy: float,
        total_energy: float,
        sliding_energy: float = 0.0,
        added_mass_pct: float = 0.0,
        has_nan_inf: bool = False,
        current_time: float = 0.0,
    ) -> BreakerVerdict:
        """評估 LS-DYNA 顯式分析物理健康度。"""
        ref_energy = total_energy if total_energy > 0 else max(internal_energy, 1e-12)
        hg_ratio_pct = (hourglass_energy / ref_energy) * 100.0

        ref_total = max(total_energy, 1e-12)

        snapshot = {
            "hourglass_energy": hourglass_energy,
            "internal_energy": internal_energy,
            "total_energy": total_energy,
            "sliding_energy": sliding_energy,
            "added_mass_pct": added_mass_pct,
            "current_time": current_time,
            "hourglass_ratio_pct": round(hg_ratio_pct, 4),
        }

        # 1. 數值異常 (NaN / Inf) 立即熔斷
        if (
            has_nan_inf
            or math.isnan(hourglass_energy)
            or math.isinf(hourglass_energy)
            or math.isnan(internal_energy)
            or math.isinf(internal_energy)
            or math.isnan(total_energy)
            or math.isinf(total_energy)
        ):
            return BreakerVerdict(
                triggered=True,
                rule_id="CB-DYNA-001",
                reason="LS-DYNA 能量數值出現 NaN / Inf 嚴重發散",
                diagnosis="求解器在更新節點坐標或應力張量時出現浮點除以零或溢位，網格可能已完全崩潰或時間步過大。",
                action_code="REDUCE_TIMESTEP_OR_CHECK_CONTACT",
                suggested_fix="檢查幾何干涉、縮小 *CONTROL_TIMESTEP 的 TSSFAC 係數至 0.67，或啟用網格自適應細化。",
                metrics_snapshot=snapshot,
            )

        # 2. 質量縮放超標熔斷 (Added Mass > 5%)
        if added_mass_pct > self.mass_scaling_threshold_pct:
            return BreakerVerdict(
                triggered=True,
                rule_id="CB-DYNA-002",
                reason=f"質量縮放比例達到 {added_mass_pct:.2f}%，超過安全上限 {self.mass_scaling_threshold_pct}%",
                diagnosis="為追求求解步長引入了過多虛擬數值質量，嚴重破壞動態響應慣性矩，所得衝擊載荷與應力已失真。",
                action_code="TUNE_MASS_SCALING_DT2MS",
                suggested_fix="檢視最小網格尺寸單元並將 DT2MS 數值調小，或對微小過渡圓角進行幾何去特徵化 (Defeaturing)。",
                metrics_snapshot=snapshot,
            )

        # 3. 沙漏能失控檢測 (Hourglass Energy Ratio > 5%)
        if hg_ratio_pct > self.hourglass_threshold_pct:
            self._hourglass_over_count += 1
            if self._hourglass_over_count >= self.debounce_count or hg_ratio_pct > 15.0:
                return BreakerVerdict(
                    triggered=True,
                    rule_id="CB-DYNA-003",
                    reason=f"沙漏能佔比達到 {hg_ratio_pct:.2f}%，連續 {self._hourglass_over_count} 次超標 (門檻: {self.hourglass_threshold_pct}%)",
                    diagnosis="單積分點單元發生零能畸變模式，沙漏能佔比過高導致結構剛度虛假弱化或非物理變形。",
                    action_code="UPGRADE_HOURGLASS_CONTROL",
                    suggested_fix="在 *CONTROL_HOURGLASS 中改用 Flanagan-Belytschko 剛度型沙漏 (IHQ=4 或 5)，或將關鍵零件改為完全積分單元 (ELFORM=2)。",
                    metrics_snapshot=snapshot,
                )
        else:
            self._hourglass_over_count = max(0, self._hourglass_over_count - 1)

        # 4. 負滑移能檢測 (Negative Sliding Energy < -10% Total Energy)
        if sliding_energy < 0:
            neg_ratio = abs(sliding_energy) / ref_total
            snapshot["negative_sliding_ratio"] = round(neg_ratio, 4)
            if neg_ratio > self.sliding_ratio_threshold:
                return BreakerVerdict(
                    triggered=True,
                    rule_id="CB-DYNA-004",
                    reason=f"接觸滑移能呈顯著負值 ({sliding_energy:.3e} J)，佔總能 {neg_ratio*100:.1f}%，超過 10% 門檻",
                    diagnosis="接觸對發生穿透節點鎖死、初始干涉反彈或網格尺寸跨度過大，數值接觸力向系統注入虛假非物理能量。",
                    action_code="RESOLVE_CONTACT_PENETRATION",
                    suggested_fix="在 *CONTROL_CONTACT 中設置 IGNORE=1 忽略微小初始穿透，並啟用 SOFT=2 (Segment-based contact)。",
                    metrics_snapshot=snapshot,
                )

        return BreakerVerdict(triggered=False, metrics_snapshot=snapshot)

    def evaluate_mechanical(
        self,
        force_residual: Optional[float],
        criterion: Optional[float] = None,
        has_distortion: bool = False,
        has_nan_inf: bool = False,
        substep: int = 1,
    ) -> BreakerVerdict:
        """評估 Mechanical / MAPDL 結構求解健康度。"""
        snapshot = {
            "force_residual": force_residual,
            "criterion": criterion,
            "has_distortion": has_distortion,
            "substep": substep,
        }

        if has_nan_inf:
            return BreakerVerdict(
                triggered=True,
                rule_id="CB-MECH-001",
                reason="Mechanical 殘差或方程求解出現 NaN / Inf 數值崩潰",
                diagnosis="剛度矩陣奇異或位移增量過大導致浮點溢位，可能缺少充分位移拘束產生剛體運動。",
                action_code="CHECK_BOUNDARY_CONSTRAINTS",
                suggested_fix="檢核支承條件與接觸初始狀態，確認結構無未拘束自由度，並開啟弱彈簧 (Weak Springs)。",
                metrics_snapshot=snapshot,
            )

        if force_residual is not None:
            if math.isnan(force_residual) or math.isinf(force_residual):
                return BreakerVerdict(
                    triggered=True,
                    rule_id="CB-MECH-001",
                    reason="力平衡殘差為 NaN 或 Inf",
                    diagnosis="非線性迭代數值發散。",
                    action_code="ENABLE_AUTO_TIMESTEPPING",
                    suggested_fix="開啟自動時間步 (Auto Time Stepping) 並增加初始子步數 (Substeps >= 20)。",
                    metrics_snapshot=snapshot,
                )

            if force_residual > self.MAX_RESIDUAL_EXPLOSION:
                return BreakerVerdict(
                    triggered=True,
                    rule_id="CB-MECH-002",
                    reason=f"力平衡殘差暴衝至 {force_residual:.2e}，超過上限 {self.MAX_RESIDUAL_EXPLOSION:.0e}",
                    diagnosis="材料塑性硬化截斷或幾何大變形極度畸變引發數值雪崩。",
                    action_code="REDUCE_LOAD_INCREMENT",
                    suggested_fix="開啟 Large Deflection，並將載荷加載步細分為更多子步。",
                    metrics_snapshot=snapshot,
                )

        if has_distortion:
            is_over = False
            if force_residual is not None:
                if criterion is not None and force_residual > criterion:
                    is_over = True
                elif force_residual > 100.0:
                    is_over = True
            if is_over:
                return BreakerVerdict(
                    triggered=True,
                    rule_id="CB-MECH-003",
                    reason="單元嚴重畸變 (Highly Distorted) 伴隨力平衡殘差未收斂",
                    diagnosis="局部應力集中導致單元過度壓縮翻轉 (Negative Jacobian)。",
                    action_code="REFINE_MESH_LOCALLY",
                    suggested_fix="在應力集中與大變形區域局部細化網格，或將低階單元切換為具備中節點的高階二次單元。",
                    metrics_snapshot=snapshot,
                )

        return BreakerVerdict(triggered=False, metrics_snapshot=snapshot)

    def evaluate_fluent(
        self,
        residuals: Dict[str, float],
        has_nan_inf: bool = False,
        is_diverged: bool = False,
        reversed_flow_faces: int = 0,
        iteration: int = 0,
    ) -> BreakerVerdict:
        """評估 Fluent CFD 求解健康度。"""
        snapshot = {
            "residuals": residuals,
            "has_nan_inf": has_nan_inf,
            "reversed_flow_faces": reversed_flow_faces,
            "iteration": iteration,
        }

        if has_nan_inf:
            return BreakerVerdict(
                triggered=True,
                rule_id="CB-CFD-001",
                reason="Fluent 殘差或速度/壓力方程出現 NaN / Inf 浮點崩潰",
                diagnosis="壓力-速度耦合方程在求解過程中數值溢位，通常源於不良網格歪斜率或超大鬆弛因子。",
                action_code="LOWER_UNDER_RELAXATION_FACTORS",
                suggested_fix="降低壓力與動量欠鬆弛因子，並執行網格品質改善。",
                metrics_snapshot=snapshot,
            )

        if is_diverged:
            return BreakerVerdict(
                triggered=True,
                rule_id="CB-CFD-002",
                reason="Fluent 連續性或動量方程殘差呈指數暴增發散",
                diagnosis="邊界條件不匹配或流場激波引起數值不穩定。",
                action_code="INITIALIZE_WITH_FMG_OR_HYBRID",
                suggested_fix="使用 Hybrid Initialization 初始化流場，並啟用 Coupled 求解器。",
                metrics_snapshot=snapshot,
            )

        for name, val in residuals.items():
            if val > 1e8:
                return BreakerVerdict(
                    triggered=True,
                    rule_id="CB-CFD-003",
                    reason=f"Fluent 方程 [{name}] 殘差超過 10^8 發散臨界值 ({val:.2e})",
                    diagnosis=f"物理場 [{name}] 方程迭代未收斂且誤差擴散。",
                    action_code="CHECK_INLET_OUTLET_CONDITIONS",
                    suggested_fix="檢查入口流速與出口背壓邊界，確認無質量不守恆衝突。",
                    metrics_snapshot=snapshot,
                )

        return BreakerVerdict(triggered=False, metrics_snapshot=snapshot)
