"""
02_calculate_rom_materials.py
--------------------------------------------------------------------------------
APDL Material Property Generation Script for PCB Warpage Analysis (ROM Method)
- Reads Copper, EM-370, and EM-892K2 material CSV files.
- Computes temperature-dependent Rule of Mixtures (ROM) effective properties:
    E_eff(T)   = f_cu * E_cu(T) + (1 - f_cu) * E_sub(T)
    CTE_eff(T) = f_cu * CTE_cu(T) + (1 - f_cu) * CTE_sub(T)
    NU_eff     = f_cu * NU_cu + (1 - f_cu) * NU_sub
- Generates valid APDL macro (apdl_rom_materials.mac).
- CRITICAL APDL SYNTAX RULES:
    1. MP, PRXY, i, nu MUST be defined BEFORE MPTEMP / MPDATA commands.
    2. Ends with FINISH and /SOLU to cleanly return MAPDL to solver mode.
"""

import os
import sys
import pandas as pd
import numpy as np

def generate_rom_apdl_macro(folder_path: str, mac_output_path: str = None):
    excel_path = os.path.join(folder_path, 'MCP_Test.xlsx')
    if mac_output_path is None:
        mac_output_path = os.path.join(folder_path, 'apdl_rom_materials.mac')

    print(f"Loading material CSVs from: {folder_path}")
    copper_df = pd.read_csv(os.path.join(folder_path, 'Copper.csv')).dropna(how='all')
    em370_df = pd.read_csv(os.path.join(folder_path, 'EM-370.csv')).dropna(how='all')
    em892_df = pd.read_csv(os.path.join(folder_path, 'EM-892K2.csv')).dropna(how='all')

    def clean_cols(df):
        df.columns = [c.strip() for c in df.columns]
        return df

    copper_df = clean_cols(copper_df)
    em370_df = clean_cols(em370_df)
    em892_df = clean_cols(em892_df)

    temp_points = np.array([30, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260])

    def interp_prop(df, prop_col):
        return np.interp(temp_points, df['T (C)'].values, df[prop_col].values)

    cu_E = interp_prop(copper_df, 'E (GPa)') * 1e9       # Pa
    cu_CTE = interp_prop(copper_df, 'CTE (ppm)') * 1e-6    # 1/C
    cu_PR = float(copper_df['Poisson'].iloc[0])

    em370_E = interp_prop(em370_df, 'E (GPa)') * 1e9
    em370_CTE = interp_prop(em370_df, 'CTE (ppm)') * 1e-6
    em370_PR = float(em370_df['Poisson'].iloc[0])

    em892_E = interp_prop(em892_df, 'E (GPa)') * 1e9
    em892_CTE = interp_prop(em892_df, 'CTE (ppm)') * 1e-6
    em892_PR = float(em892_df['Poisson'].iloc[0])

    df_stack = pd.read_excel(excel_path, sheet_name='Stackup')
    df_param = pd.read_excel(excel_path, sheet_name='Parameters')

    Ti = float(df_param[df_param['Parameter']=='Ti']['Value'].values[0])  # Initial Temp (30 C)

    apdl_lines = [
        "! ==========================================",
        "! APDL Material Definitions (ROM Method)",
        "! PCB 79 Layers Temperature-Dependent Materials",
        "! ==========================================",
        "/PREP7",
        f"TREF, {Ti}",
        ""
    ]

    for idx, row in df_stack.iterrows():
        layer_id = int(row.iloc[0])
        cu_pct = float(row['Cu (%)'])
        mat_type = str(row['Material']).strip()
        
        f_cu = cu_pct / 100.0
        f_sub = 1.0 - f_cu
        
        if '370' in mat_type:
            sub_E, sub_CTE, sub_PR = em370_E, em370_CTE, em370_PR
        else:
            sub_E, sub_CTE, sub_PR = em892_E, em892_CTE, em892_PR
            
        eff_E = f_cu * cu_E + f_sub * sub_E
        eff_CTE = f_cu * cu_CTE + f_sub * sub_CTE
        eff_PR = f_cu * cu_PR + f_sub * sub_PR
        
        apdl_lines.append(f"! --- Layer {layer_id:02d} ({mat_type}, Cu {cu_pct:.1f}%) ---")
        # Define PRXY BEFORE MPTEMP / MPDATA to avoid deletion warning
        apdl_lines.append(f"MP, PRXY, {layer_id}, {eff_PR:.4f}")
        
        # Temperature points (23 points)
        t_str1 = ", ".join([str(t) for t in temp_points[:6]])
        t_str2 = ", ".join([str(t) for t in temp_points[6:12]])
        t_str3 = ", ".join([str(t) for t in temp_points[12:18]])
        t_str4 = ", ".join([str(t) for t in temp_points[18:]])
        
        # EX (Pa)
        apdl_lines.append(f"MPTEMP, 1, {t_str1}")
        apdl_lines.append(f"MPTEMP, 7, {t_str2}")
        apdl_lines.append(f"MPTEMP, 13, {t_str3}")
        apdl_lines.append(f"MPTEMP, 19, {t_str4}")
        
        e_str1 = ", ".join([f"{v:.6e}" for v in eff_E[:6]])
        e_str2 = ", ".join([f"{v:.6e}" for v in eff_E[6:12]])
        e_str3 = ", ".join([f"{v:.6e}" for v in eff_E[12:18]])
        e_str4 = ", ".join([f"{v:.6e}" for v in eff_E[18:]])
        
        apdl_lines.append(f"MPDATA, EX, {layer_id}, 1, {e_str1}")
        apdl_lines.append(f"MPDATA, EX, {layer_id}, 7, {e_str2}")
        apdl_lines.append(f"MPDATA, EX, {layer_id}, 13, {e_str3}")
        apdl_lines.append(f"MPDATA, EX, {layer_id}, 19, {e_str4}")
        
        # ALPX (1/C)
        apdl_lines.append(f"MPTEMP, 1, {t_str1}")
        apdl_lines.append(f"MPTEMP, 7, {t_str2}")
        apdl_lines.append(f"MPTEMP, 13, {t_str3}")
        apdl_lines.append(f"MPTEMP, 19, {t_str4}")
        
        cte_str1 = ", ".join([f"{v:.6e}" for v in eff_CTE[:6]])
        cte_str2 = ", ".join([f"{v:.6e}" for v in eff_CTE[6:12]])
        cte_str3 = ", ".join([f"{v:.6e}" for v in eff_CTE[12:18]])
        cte_str4 = ", ".join([f"{v:.6e}" for v in eff_CTE[18:]])
        
        apdl_lines.append(f"MPDATA, ALPX, {layer_id}, 1, {cte_str1}")
        apdl_lines.append(f"MPDATA, ALPX, {layer_id}, 7, {cte_str2}")
        apdl_lines.append(f"MPDATA, ALPX, {layer_id}, 13, {cte_str3}")
        apdl_lines.append(f"MPDATA, ALPX, {layer_id}, 19, {cte_str4}")
        apdl_lines.append("")

    # Finish /PREP7 and return to /SOLU mode
    apdl_lines.append("FINISH")
    apdl_lines.append("/SOLU")
    apdl_lines.append("")

    apdl_code = "\n".join(apdl_lines)
    with open(mac_output_path, 'w', encoding='utf-8') as fp:
        fp.write(apdl_code)

    print(f"Successfully generated APDL Macro: {mac_output_path} ({len(apdl_lines)} lines)")
    return mac_output_path

if __name__ == "__main__":
    folder = r'D:\ANSYS_MCP_Connect\PCB_Stackup_material'
    if len(sys.argv) > 1:
        folder = sys.argv[1]
    generate_rom_apdl_macro(folder)
