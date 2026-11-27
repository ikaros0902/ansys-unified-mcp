"""pcb-thermal-warpage / ODB Modifying Tool: turn a PCB vendor working-gerber ODB++ into an ANSYS-ready ODB++.

Pipeline (see SKILL.md):
    intake   -> read vendor stackup + design material table + ODB++ matrix, resolve
                ambiguities (ask or record), produce one normalized stackup
    build    -> single step, copper layers only, PP layer between every copper pair,
                thickness + names written into the ODB++, origin moved
    coverage -> copper coverage per layer rendered from the ODB++ features
    matlib   -> PCB_Material_Library.xml (Engineering Data): names, subset of one project
    outputs  -> workinggerber CSV (LayerBuilder), layer map, v6 Mechanical script with the
                library materials of the board embedded
    verify   -> ANSYS 2025 R1 + 2026 R1 translators, EDB stackup read back and compared
"""
__version__ = "1.2.0"
