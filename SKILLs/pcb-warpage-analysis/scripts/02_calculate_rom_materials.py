# -*- coding: utf-8 -*-
"""
PCB 複合材料混合定律 (Rule of Mixtures, ROM) 計算與 APDL 巨集生成器
依據各層銅箔比例 (f_Cu) 計算有效彈性模數、熱膨脹係數 (CTE) 與泊松比，並輸出 APDL 指令檔。
"""
import os

def calculate_rom_properties(f_cu, e_cu=110000.0, e_sub=22000.0, cte_cu=1.7e-5, cte_sub=1.4e-5, nu_cu=0.34, nu_sub=0.18):
    """
    計算等效混合材料性質 (Rule of Mixtures)
    """
    e_eff = f_cu * e_cu + (1.0 - f_cu) * e_sub
    cte_eff = f_cu * cte_cu + (1.0 - f_cu) * cte_sub
    nu_eff = f_cu * nu_cu + (1.0 - f_cu) * nu_sub
    return e_eff, cte_eff, nu_eff

def generate_apdl_rom_macro(output_path, layer_f_cu_list):
    """
    生成合法語法的 APDL 巨集 (apdl_rom_materials.mac)
    注意：MP, PRXY 必須在 MPTEMP 與 MPDATA (EX/ALPX) 之前宣告！
    巨集結尾必須包含 FINISH 與 /SOLU 離開 /PREP7 模式。
    """
    lines = ["/PREP7", "! APDL ROM Materials Macro Auto-generated\n"]
    
    for mat_id, f_cu in enumerate(layer_f_cu_list, start=1):
        e_eff, cte_eff, nu_eff = calculate_rom_properties(f_cu)
        
        # 1. 必須先宣告 PRXY Constant
        lines.append("MP, PRXY, {}, {:.4f}".format(mat_id, nu_eff))
        
        # 2. 宣告溫度點與 EX, ALPX
        lines.append("MPTEMP, 1, 20.0, 150.0, 260.0")
        lines.append("MPDATA, EX, {}, 1, {:.2f}, {:.2f}, {:.2f}".format(mat_id, e_eff, e_eff * 0.9, e_eff * 0.8))
        lines.append("MPDATA, ALPX, {}, 1, {:.6e}, {:.6e}, {:.6e}".format(mat_id, cte_eff, cte_eff * 1.05, cte_eff * 1.1))
        lines.append("")

    # 3. 必須包含 FINISH 與 /SOLU Clean Exit
    lines.append("FINISH")
    lines.append("/SOLU")
    lines.append("! APDL Macro Complete")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        
    print("成功生成 APDL ROM 巨集：{}".format(output_path))
    return output_path

if __name__ == "__main__":
    sample_f_cu = [0.8, 0.2, 0.5, 0.1, 0.9]
    generate_apdl_rom_macro("apdl_rom_materials.mac", sample_f_cu)
