# -*- coding: utf-8 -*-
"""
check_fluent_mesh.py
--------------------------------------------------------------------------------
ANSYS Fluent 網格品質與邊界層 y+ 預檢獨立工具。
本工具提供兩大核心工程檢驗能力：
1. 邊界層首層網格高度 (y1) 與 y+ 理論工程估算器：
   - 依據平板/管流湍流邊界層理論計算雷諾數、摩擦速度與所需首層高度；
   - 嚴格校核分區：黏性底層 (y+ <= 1)、對數律區 (30 < y+ < 300) 或紅燈攔截緩衝層禁區 (5 < y+ < 30)。
2. Fluent 網格品質驗收與門檻評估：
   - 最小正交品質 (Orthogonal Quality >= 0.15 放行)
   - 最大歪斜度 (Skewness <= 0.85 放行)
   - 負體積單元判定 (致命紅線 = 0)
--------------------------------------------------------------------------------
"""

import math
import sys
import argparse
from typing import Dict, Any, Tuple


def calculate_boundary_layer_y1(
    velocity: float,
    length: float,
    density: float = 1.225,
    viscosity: float = 1.7894e-05,
    target_y_plus: float = 1.0
) -> Dict[str, Any]:
    """
    計算滿足目標 y+ 所需之近壁面第一層網格高度 y1

    參數：
        velocity: 主流特徵速度 (m/s)
        length: 特徵長度或管徑 (m)
        density: 流體密度 (kg/m^3)，預設空氣 1.225
        viscosity: 動力黏度 (Pa*s)，預設空氣 1.7894e-5
        target_y_plus: 目標 y+ 值 (預設 1.0)

    返回：
        包含雷諾數、摩擦速度、首層高度與工程分區評估的字典
    """
    if velocity <= 0 or length <= 0 or density <= 0 or viscosity <= 0:
        raise ValueError("流體物性、速度與特徵長度必須大於零。")

    # 1. 雷諾數計算
    reynolds = (density * velocity * length) / viscosity

    # 2. 壁面摩擦係數估算 (湍流平板邊界層經驗公式)
    if reynolds < 2300:
        # 層流公式
        cf = 1.328 / math.sqrt(max(reynolds, 1.0))
        flow_regime = "層流 (Laminar)"
    else:
        # 湍流公式
        cf = 0.0592 * (reynolds ** -0.2)
        flow_regime = "湍流 (Turbulent)"

    # 3. 壁面剪切應力 tau_w 與摩擦速度 u_tau
    tau_w = 0.5 * cf * density * (velocity ** 2)
    u_tau = math.sqrt(tau_w / density)

    # 4. 所需首層網格厚度 y1
    y1 = (target_y_plus * viscosity) / (density * u_tau)

    # 5. y+ 分區專家判定
    if target_y_plus <= 1.0:
        regime_judge = "黏性底層 (Viscous Sublayer): 滿足高精度熱傳、分離與摩擦力解析要求。"
        status = "PASS"
    elif target_y_plus < 5.0:
        regime_judge = "黏性底層邊界容限 (y+ < 5): 可接受，但高熱通量下建議進一步加密至 y+ <= 1。"
        status = "ACCEPTABLE"
    elif 5.0 <= target_y_plus <= 30.0:
        regime_judge = "【⚠️ 緩衝層禁區 (5 < y+ < 30)】: 壁面函數失效且阻尼未完全建立，將產生嚴重數值失真！"
        status = "CRITICAL_VIOLATION"
    elif 30.0 < target_y_plus <= 300.0:
        regime_judge = "對數律區 (Log-law Region): 滿足高雷諾數標準壁面函數適用範圍。"
        status = "PASS"
    else:
        regime_judge = "核心流區 (y+ > 300): 超出壁面函數有效對數律區，網格過粗。"
        status = "OVER_COARSE"

    return {
        "reynolds": reynolds,
        "flow_regime": flow_regime,
        "friction_coeff": cf,
        "wall_shear_stress": tau_w,
        "friction_velocity": u_tau,
        "target_y_plus": target_y_plus,
        "y1_meters": y1,
        "y1_mm": y1 * 1000.0,
        "status": status,
        "regime_judgment": regime_judge
    }


def evaluate_mesh_quality(
    min_ortho_quality: float,
    max_skewness: float,
    has_negative_volume: bool = False
) -> Tuple[bool, str]:
    """
    評估 Fluent 網格品質是否符合林明志標準規範

    驗收門檻：
    - 負體積單元: 致命禁忌 (必須為 False)
    - 最小正交品質 (Min Orthogonal Quality): >= 0.15 放行 (>= 0.20 優良)
    - 最大歪斜度 (Max Skewness): <= 0.85 放行 (<= 0.80 優良)
    """
    if has_negative_volume:
        return False, "[FATAL] 網格存在負體積單元 (Negative Volume Cells)，有限體積求解器將立即發散！"

    if min_ortho_quality < 0.15:
        return False, f"[FAIL] 最小正交品質 ({min_ortho_quality:.4f}) 低於工程放行紅線 0.15，數值易震盪發散。"

    if max_skewness > 0.85:
        return False, f"[FAIL] 最大歪斜度 ({max_skewness:.4f}) 高於工程放行紅線 0.85，梯度計算精度不足。"

    # 品質分級回報
    quality_grade = "優良 (Excellent)" if (min_ortho_quality >= 0.20 and max_skewness <= 0.80) else "合格 (Acceptable)"
    detail = (
        f"[PASS] 網格品質判定為 {quality_grade}。\n"
        f"       - 最小正交品質: {min_ortho_quality:.4f} (門檻 >= 0.15)\n"
        f"       - 最大歪斜度:   {max_skewness:.4f} (門檻 <= 0.85)\n"
        f"       - 負體積單元:   無"
    )
    return True, detail


def rescale_first_layer_height(y1_current: float, yplus_current: float, target_yplus: float = 1.0) -> float:
    """依據求解器測得之實際 y+ 線性自愈反算目標首層高度"""
    if yplus_current <= 0 or y1_current <= 0:
        raise ValueError("首層高度與 y+ 必須大於零")
    return y1_current * (target_yplus / yplus_current)


def print_y_plus_report(res: Dict[str, Any]):
    """輸出格式化 y+ 評估報告"""
    print("================================================================================")
    print("  ANSYS Fluent 邊界層 y+ 與首層網格高度 (y1) 評估報告")
    print("================================================================================")
    print(f"[*] 雷諾數 (Re):           {res['reynolds']:.2e} ({res['flow_regime']})")
    print(f"[*] 壁面摩擦係數 (Cf):     {res['friction_coeff']:.6f}")
    print(f"[*] 摩擦速度 (u_tau):      {res['friction_velocity']:.4f} m/s")
    print(f"[*] 壁面剪切應力 (tau_w):  {res['wall_shear_stress']:.4f} Pa")
    print(f"[*] 目標 y+ 數值:          {res['target_y_plus']:.2f}")
    print(f"[*] 理論首層高度 (y1):     {res['y1_meters']:.6e} m ({res['y1_mm']:.4f} mm)")
    print("--------------------------------------------------------------------------------")
    print(f"[*] 判定狀態:              [{res['status']}]")
    print(f"[*] 專家評估:              {res['regime_judgment']}")
    print("================================================================================")


def main():
    parser = argparse.ArgumentParser(description="Fluent 網格品質與邊界層 y+ 預檢工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # 子命令 1: y+ 計算
    yplus_parser = subparsers.add_parser("yplus", help="計算目標 y+ 之首層網格高度")
    yplus_parser.add_argument("-u", "--velocity", type=float, required=True, help="主流流速 (m/s)")
    yplus_parser.add_argument("-l", "--length", type=float, required=True, help="特徵長度或管徑 (m)")
    yplus_parser.add_argument("-rho", "--density", type=float, default=1.225, help="密度 (kg/m^3)")
    yplus_parser.add_argument("-mu", "--viscosity", type=float, default=1.7894e-05, help="黏度 (Pa*s)")
    yplus_parser.add_argument("-y", "--yplus", type=float, default=1.0, help="目標 y+ (預設 1.0)")

    # 子命令 2: 網格品質評估
    mesh_parser = subparsers.add_parser("check", help="檢驗網格正交品質與歪斜度")
    mesh_parser.add_argument("--ortho", type=float, required=True, help="最小正交品質 (Min Orthogonal Quality)")
    mesh_parser.add_argument("--skew", type=float, required=True, help="最大歪斜度 (Max Skewness)")
    mesh_parser.add_argument("--negative-volume", action="store_true", help="是否含有負體積")

    # 子命令 3: y+ 反向自愈重劃 (Action Item 2)
    rescale_parser = subparsers.add_parser("rescale", help="依據實測 y+ 反向自愈縮放計算目標首層高度")
    rescale_parser.add_argument("-y1", "--y1-current", type=float, required=True, help="目前首層網格高度 y1 (m 或 mm)")
    rescale_parser.add_argument("-y", "--yplus-current", type=float, required=True, help="求解器測得之實際 y+")
    rescale_parser.add_argument("--target-y", type=float, default=1.0, help="目標 y+ (預設 1.0)")

    args = parser.parse_args()

    if args.command == "yplus":
        res = calculate_boundary_layer_y1(
            velocity=args.velocity,
            length=args.length,
            density=args.density,
            viscosity=args.viscosity,
            target_y_plus=args.yplus
        )
        print_y_plus_report(res)
        if res["status"] == "CRITICAL_VIOLATION":
            sys.exit(1)
        sys.exit(0)

    elif args.command == "check":
        passed, msg = evaluate_mesh_quality(args.ortho, args.skew, args.negative_volume)
        print(msg)
        sys.exit(0 if passed else 1)

    elif args.command == "rescale":
        try:
            target_y1 = rescale_first_layer_height(
                y1_current=args.y1_current,
                yplus_current=args.yplus_current,
                target_yplus=args.target_y
            )
            print("================================================================================")
            print("  ANSYS Fluent 邊界層 y+ 反向自愈重劃計算報告")
            print("================================================================================")
            print(f"[*] 現有首層網格高度 (y1_current):    {args.y1_current:.6e}")
            print(f"[*] 求解器測得實際 y+ (yplus_current): {args.yplus_current:.2f}")
            print(f"[*] 目標 y+ 數值 (target_y):          {args.target_y:.2f}")
            print(f"[*] 自愈目標首層高度 (target_y1):     {target_y1:.6e}")
            print("================================================================================")
            sys.exit(0)
        except Exception as e:
            print(f"[ERROR] 反向自愈計算失敗: {e}")
            sys.exit(1)

    else:
        # 預設自檢展示
        print("[*] 執行內建標準混合彎管 (Mixing Elbow) 邊界層與網格品質驗算示範:")
        # 混合彎管主入口: U = 0.4 m/s, D = 0.1016 m, 水流密度 1000, 黏度 0.001
        res_water = calculate_boundary_layer_y1(
            velocity=0.4,
            length=0.1016,
            density=998.2,
            viscosity=0.001003,
            target_y_plus=1.0
        )
        print_y_plus_report(res_water)

        print("\n[*] 執行網格品質放行門檻校核示範:")
        passed, msg = evaluate_mesh_quality(min_ortho_quality=0.28, max_skewness=0.72)
        print(msg)
        sys.exit(0)


if __name__ == "__main__":
    main()
