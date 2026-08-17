# -*- coding: utf-8 -*-
"""
Rule of Mixtures (ROM) Material Calculator & APDL Macro Generator for PCB Stackup.
"""
import os

def calculate_rom_properties(f_cu):
    """
    根據銅含量比例 (f_cu) 與 Rule of Mixtures (ROM) 計算混合物性 EX, ALPX, PRXY
    """
    # 銅與基材 (FR4/EMC) 物性參數
    e_cu = 110000.0   # MPa
    e_sub = 22000.0   # MPa
    alpx_cu = 1.6e-5  # 1/°C
    alpx_sub = 1.4e-5 # 1/°C
    prxy = 0.28

    # 混合律算式 (Rule of Mixtures)
    ex_eff = f_cu * e_cu + (1.0 - f_cu) * e_sub
    alpx_eff = f_cu * alpx_cu + (1.0 - f_cu) * alpx_sub
    return ex_eff, alpx_eff, prxy

def export_apdl_macro(output_path="apdl_rom_materials.mac", num_layers=79):
    """
    輸出遵循 APDL 語法規範的材料設定巨集。
    關鍵規則：MP, PRXY 必須在 MPTEMP / MPDATA (EX, ALPX) 之前宣告。
    """
    lines = [
        "! ========================================================",
        "! APDL ROM Material Definitions for PCB Stackup",
        "! Note: MP, PRXY MUST be declared BEFORE MPTEMP / MPDATA",
        "! ========================================================",
        "/PREP7",
        ""
    ]
    
    for i in range(1, num_layers + 1):
        f_cu = 0.35 if i % 2 == 1 else 0.15  # 示範銅箔比例分佈
        ex_eff, alpx_eff, prxy = calculate_rom_properties(f_cu)
        
        lines.append("! Layer {:02d} Material Definition (f_cu = {:.2f})".format(i, f_cu))
        lines.append("MP, PRXY, {}, {:.4f}".format(i, prxy))  # 1. 優先宣告 PRXY
        lines.append("MP, EX, {}, {:.2f}".format(i, ex_eff))    # 2. 宣告 EX
        lines.append("MP, EY, {}, {:.2f}".format(i, ex_eff))    # 3. 宣告 EY
        lines.append("MP, EZ, {}, {:.2f}".format(i, ex_eff * 0.8)) # EZ
        lines.append("MP, ALPX, {}, {:.4e}".format(i, alpx_eff)) # 4. 宣告 ALPX
        lines.append("MP, ALPY, {}, {:.4e}".format(i, alpx_eff)) # ALPY
        lines.append("")
        
    lines.append("FINISH")
    lines.append("/SOLU")
    lines.append("")
    
    with open(output_path, "w") as f:
        f.write("\n".join(lines))
    print("成功輸出 APDL 材料設定巨集: {}".format(output_path))
    return output_path

if __name__ == "__main__":
    export_apdl_macro()
