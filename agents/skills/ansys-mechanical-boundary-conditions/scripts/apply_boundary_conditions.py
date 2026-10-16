# -*- coding: utf-8 -*-
"""
ANSYS Mechanical 邊界條件通用施加腳本 (apply_boundary_conditions.py)

依 bc_mode 參數在 static / thermal / shock 三種模式間切換施加邏輯：
- static  : 結構穩態邊界（Fixed/Displacement/Force/Pressure），交叉引用 ansys-mechanical 既有定義。
- thermal : 熱邊界（Convection/Radiation/HeatFlux/Temperature），本技能新增內容。
- shock   : LS-DYNA 衝擊脈衝邊界（InitialVelocity/Velocity 半正弦速度歷程）。

本腳本設計為「IronPython ACT 環境」執行範本，執行時應在 Mechanical ACT 腳本視窗內，
全域物件 ExtAPI / Model / Quantity / LoadDefineBy 由 ACT 環境自動注入，此處僅示範呼叫序列。
註：ACT/IronPython 內嵌程式碼區塊註解需全英文 ASCII，但本檔屬於一般 Python 參考腳本層級，
故沿用繁體中文註解；若直接貼入 ACT Script Editor，請將下方 # 註解改寫為英文 ASCII。
"""

import math


# 衝擊 G 轉換換算常數：1G = 9806.65 mm/s^2（標準重力加速度）
G_TO_MM_S2 = 9806.65


def compute_half_sine_delta_v(shock_g, pulse_duration_s):
    """
    計算半正弦波衝擊脈衝的總速度變化量 (Delta-V)。

    公式推導見 references/shock_pulse_boundary_conditions.md 第 1 節：
        a(t) = A0 * sin(pi * t / T)
        delta_v = 2 * A0 * T / pi

    參數：
        shock_g: 衝擊峰值加速度 (單位: G)
        pulse_duration_s: 脈衝持續時間 (單位: 秒)

    回傳：
        delta_v_mm_s: 總速度變化量 (單位: mm/s)
    """
    a0_mm_s2 = shock_g * G_TO_MM_S2
    delta_v_mm_s = (2.0 * a0_mm_s2 * pulse_duration_s) / math.pi
    return delta_v_mm_s


def apply_static_boundary(analysis, bc_config):
    """
    靜態結構穩態邊界施加（Fixed/Displacement/Force/Pressure）。

    完整 API 範例已在 ansys-mechanical/references/boundary_conditions_and_loads.md 定義，
    本函式僅做參數路由轉發範例，不重複實作細節。

    參數：
        analysis: Mechanical 分析系統物件 (Model.Analyses[i])
        bc_config: dict，須含 "bc_type" (fixed/displacement/force/pressure) 與 "location_ns"
    """
    bc_type = bc_config.get("bc_type")
    location_ns = bc_config.get("location_ns")

    if bc_type == "fixed":
        fixed_support = analysis.AddFixedSupport()
        fixed_support.Name = bc_config.get("name", "FixedSupport_Auto")
        fixed_support.Location = _get_named_selection(location_ns)
        return fixed_support

    if bc_type == "force":
        force = analysis.AddForce()
        force.Name = bc_config.get("name", "Force_Auto")
        force.Location = _get_named_selection(location_ns)
        force.DefineBy = _load_define_by_components()
        components = bc_config.get("component_values", {"X": 0, "Y": 0, "Z": 0})
        _set_force_components(force, components)
        return force

    if bc_type == "pressure":
        pressure = analysis.AddPressure()
        pressure.Name = bc_config.get("name", "Pressure_Auto")
        pressure.Location = _get_named_selection(location_ns)
        pressure.Magnitude.Output.SetDiscreteValue(0, _quantity(bc_config.get("magnitude", "0 [MPa]")))
        return pressure

    raise ValueError("未支援的 static bc_type: {0}，請改用 ansys-mechanical 既有手冊".format(bc_type))


def apply_thermal_boundary(analysis, bc_config):
    """
    熱邊界施加（Convection/Radiation/HeatFlux/Temperature）。

    詳細 API 範例見 references/thermal_boundary_conditions.md。

    參數：
        analysis: Mechanical 熱分析系統物件
        bc_config: dict，須含 "bc_type" (convection/radiation/heat_flux/temperature) 與 "location_ns"
    """
    bc_type = bc_config.get("bc_type")
    location_ns = bc_config.get("location_ns")

    if bc_type == "convection":
        conv = analysis.AddConvection()
        conv.Name = bc_config.get("name", "Convection_Auto")
        conv.Location = _get_named_selection(location_ns)
        conv.FilmCoefficient.Output.SetDiscreteValue(
            0, _quantity(bc_config.get("htc_value", "15 [W m^-2 C^-1]"))
        )
        conv.AmbientTemperature.Output.SetDiscreteValue(
            0, _quantity(bc_config.get("ambient_temp", "25 [C]"))
        )
        return conv

    if bc_type == "radiation":
        rad = analysis.AddRadiation()
        rad.Name = bc_config.get("name", "Radiation_Auto")
        rad.Location = _get_named_selection(location_ns)
        rad.Emissivity.Output.SetDiscreteValue(
            0, _quantity(bc_config.get("emissivity", "0.85 [m^-1 m^-1]"))
        )
        rad.AmbientTemperature.Output.SetDiscreteValue(
            0, _quantity(bc_config.get("ambient_temp", "25 [C]"))
        )
        return rad

    if bc_type == "heat_flux":
        hf = analysis.AddHeatFlux()
        hf.Name = bc_config.get("name", "HeatFlux_Auto")
        hf.Location = _get_named_selection(location_ns)
        hf.Magnitude.Output.SetDiscreteValue(
            0, _quantity(bc_config.get("magnitude", "0 [W m^-2]"))
        )
        return hf

    if bc_type == "temperature":
        temp = analysis.AddTemperature()
        temp.Name = bc_config.get("name", "Temperature_Auto")
        temp.Location = _get_named_selection(location_ns)
        temp.Magnitude.Output.SetDiscreteValue(
            0, _quantity(bc_config.get("magnitude", "25 [C]"))
        )
        return temp

    raise ValueError("未支援的 thermal bc_type: {0}".format(bc_type))


def apply_shock_boundary(analysis, bc_config):
    """
    LS-DYNA 衝擊脈衝邊界施加（InitialVelocity，半正弦波換算速度）。

    詳細公式推導與速度歷程範例見 references/shock_pulse_boundary_conditions.md。
    求解器 Analysis Settings（Hourglass/TSSFAC/雙精度）請另外呼叫
    shock-analysis-workflow 06-constraint-load 模組設定，本函式僅負責邊界本身。

    參數：
        analysis: LS-DYNA Explicit Dynamics 分析系統物件
        bc_config: dict，須含 "shock_g"、"pulse_duration"、"shock_axis"（如 "-Y"）、"location_ns"
    """
    shock_g = bc_config.get("shock_g")
    pulse_duration = bc_config.get("pulse_duration")
    shock_axis = bc_config.get("shock_axis", "-Y")  # 格式: 符號 + 軸向
    location_ns = bc_config.get("location_ns")

    delta_v_mm_s = compute_half_sine_delta_v(shock_g, pulse_duration)

    sign = shock_axis[0]  # "+" 或 "-"
    axis = shock_axis[1].upper()  # "X" / "Y" / "Z"
    signed_delta_v = delta_v_mm_s if sign == "+" else -delta_v_mm_s

    ini_vel = analysis.AddInitialVelocity()
    ini_vel.Name = bc_config.get("name", "Scr_Initial_vel_{0}".format(shock_axis))
    ini_vel.Location = _get_named_selection(location_ns)
    ini_vel.DefineBy = _load_define_by_components()

    _set_velocity_component(ini_vel, axis, signed_delta_v)

    return ini_vel


def apply_boundary_conditions(analysis, bc_mode, bc_config):
    """
    統一入口：依 bc_mode 路由至對應施加函式。

    參數：
        analysis: Mechanical 分析系統物件
        bc_mode: "static" / "thermal" / "shock"
        bc_config: dict，詳見各子函式說明

    回傳：
        新建立的邊界條件物件
    """
    if bc_mode == "static":
        return apply_static_boundary(analysis, bc_config)
    if bc_mode == "thermal":
        return apply_thermal_boundary(analysis, bc_config)
    if bc_mode == "shock":
        return apply_shock_boundary(analysis, bc_config)
    raise ValueError("未知的 bc_mode: {0}，須為 static/thermal/shock".format(bc_mode))


# --------------------------------------------------------------------------
# ACT 環境輔助函式（實際執行時由 ExtAPI/Quantity 等全域物件提供，此處為介面示意）
# --------------------------------------------------------------------------

def _get_named_selection(name):
    """透過 ExtAPI 取得 Named Selection 物件，實際執行時由 ACT 環境注入 ExtAPI。"""
    return ExtAPI.DataModel.GetObjectsByName(name)[0]  # noqa: F821


def _quantity(value_str):
    """包裝 Quantity 建構，實際執行時由 ACT 環境注入 Quantity。"""
    return Quantity(value_str)  # noqa: F821


def _load_define_by_components():
    """回傳 LoadDefineBy.Components 列舉值，實際執行時由 ACT 環境注入。"""
    return LoadDefineBy.Components  # noqa: F821


def _set_force_components(force_obj, components):
    """依字典設定 Force 三軸分量。"""
    if "X" in components:
        force_obj.XComponent.Output.SetDiscreteValue(0, _quantity("{0} [N]".format(components["X"])))
    if "Y" in components:
        force_obj.YComponent.Output.SetDiscreteValue(0, _quantity("{0} [N]".format(components["Y"])))
    if "Z" in components:
        force_obj.ZComponent.Output.SetDiscreteValue(0, _quantity("{0} [N]".format(components["Z"])))


def _set_velocity_component(vel_obj, axis, value_mm_s):
    """依軸向字串設定 InitialVelocity 單一分量，其餘分量維持預設 0。"""
    quantity_str = "{0} [mm sec^-1]".format(value_mm_s)
    if axis == "X":
        vel_obj.XComponent = _quantity(quantity_str)
    elif axis == "Y":
        vel_obj.YComponent = _quantity(quantity_str)
    elif axis == "Z":
        vel_obj.ZComponent = _quantity(quantity_str)
    else:
        raise ValueError("未知軸向: {0}".format(axis))
