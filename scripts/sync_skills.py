# -*- coding: utf-8 -*-
"""
sync_skills.py
--------------------------------------------------------------------------------
僅同步純淨 ANSYS CAE 相關技能至本專案目錄。
"""
import os
import shutil

src_skills = r"C:\Users\Ming\AppData\Local\hermes\skills"
dst_skills_1 = r"F:\Ming_python\ansys-unified-mcp\SKILLs"
dst_skills_2 = r"F:\Ming_python\ansys-unified-mcp\.kiro\skills"

# 嚴格限制：僅允許 ANSYS CAE 相關技能
ansys_skills_to_sync = [
    "ansys-spaceclaim",
    "pcb-warpage-analysis",
    "ansys-mechanical",
    "ansys-optislang",
    "ansys-lsdyna",
    "ansys-ls-prepost",
    "act-extension-development",
    "pymechanical-operations",
    "ansys-error-catalog",
    "pdf-to-md",
]

for s in ansys_skills_to_sync:
    src_p = os.path.join(src_skills, s)
    if os.path.exists(src_p):
        for target_dir in [dst_skills_1, dst_skills_2]:
            dst_p = os.path.join(target_dir, s)
            if os.path.exists(dst_p):
                shutil.rmtree(dst_p)
            shutil.copytree(src_p, dst_p)
            print(f"Synced ANSYS skill: {s} -> {target_dir}")

print("ANSYS pure skills synchronization finished!")
