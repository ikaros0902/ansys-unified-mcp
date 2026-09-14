# -*- coding: utf-8 -*-
"""
Standalone Small-Batch Validation Script for Session 01: Material Assignment.
Connects to live Mechanical session on Port 10000 via PyMechanical gRPC,
validates clean_name_string, material keyword matching rules, assigns materials
to a 10-body sample subset, updates/verifies [Mat] Unassigned_Bodies Named Selection,
and reports verification metrics.
"""
import sys
import os

# Include source path for MechanicalController
from pathlib import Path
_repo_src = str(Path(__file__).resolve().parents[3] / "src")
if _repo_src not in sys.path:
    sys.path.insert(0, _repo_src)
from ansys_unified_mcp.products.mechanical import MechanicalController

TEST_SCRIPT_IRONPYTHON = """
import re
import clr
clr.AddReference("Ansys.ACT.Interfaces")
clr.AddReference("Ansys.Mechanical.DataModel")
from Ansys.Mechanical.DataModel.Enums import DataModelObjectCategory

def clean_name_string(name_str):
    if name_str is None:
        return ""
    try:
        s = "".join([c for c in str(name_str) if ord(c) < 128])
    except:
        s = str(name_str)
    # Strip CAD body/surface/part suffixes and file extensions
    s = re.sub(r'(?i)\\\\s*[\\\\(\\\\[]\\\\s*(Solid|Surface|Sheet|Body|Part)\\\\s*[\\\\)\\\\]]', '', s)
    s = re.sub(r'(?i)(\\\\.prt|\\\\.asm)\\\\.\\\\d+$', '', s)
    s = re.sub(r'(?i)\\\\.(asm|prt|sldprt|sldasm)$', '', s)
    s = re.sub(r':\\\\d+$', '', s)
    return s.strip().upper()

def match_keyword_rules(name_str):
    s = str(name_str).upper()
    
    # Priority 2: Direct Material Keywords
    if 'SGCC' in s or 'SGC400' in s:
        return "SGCC", "Direct Material: SGCC"
    if '6061' in s or 'AL6061' in s or '6061-T6' in s or 'ALUMINUM' in s:
        return "Aluminum alloy, wrought, 6061, T6", "Direct Material: 6061 Aluminum"
    if '301' in s or 'SUS301' in s or 'SUS304' in s or 'STAINLESS' in s:
        return "Stainless Steel - 301 1/2H", "Direct Material: 301 Stainless"
    if 'FR4' in s or 'FR-4' in s:
        return "PCB laminate, Epoxy/Glass fiber, FR-4", "Direct Material: FR-4"
    if 'PC+ABS' in s or 'PC/ABS' in s or 'CYCOLOY' in s or 'BAYBLEND' in s or 'C6200' in s or 'C2950' in s:
        return "SABIC Cycoloy C6200 PC+ABS", "Direct Material: PC+ABS"
    if 'NYLON' in s or 'PA66' in s or 'PA6' in s:
        return "NYLON 66", "Direct Material: Nylon"
    if 'COPPER' in s or 'C1100' in s or 'CU' in s:
        return "Copper Alloy", "Direct Material: Copper"
    if 'SAE1215' in s or 'CARBON STEEL' in s:
        return "SAE1215 - STF", "Direct Material: Carbon Steel"
    if 'ZA8' in s or 'ZINC' in s:
        return "Die Casting - ZA8, Zinc Alloy", "Direct Material: Zinc ZA8"
        
    # Priority 3: Functional Structural Keywords
    if any(k in s for k in ['CHASSIS', 'BOTTOM', 'TOP-COVER', 'COVER', 'TRAY', 'CAGE', 'BRACKET', 'BKT', 'WALL', 'WINDOW', 'BAR', 'PANEL', 'BEZEL', 'PARTITION', 'BAREBONE', 'STAKE']):
        return "SGCC", "Functional: Sheet Metal Chassis"
    if any(k in s for k in ['PCB', 'PBA', 'PCBA', 'MB_', 'DIMM', 'RISER', 'EGS-', 'MID-PLANE', 'ODP', 'CPLD', 'WHITLEY', 'CARD', 'ITS_']):
        return "PCB laminate, Epoxy/Glass fiber, FR-4", "Functional: PCB Assembly"
    if any(k in s for k in ['FIN', 'CUBASE', 'HEATPIPE', 'VAPOR', 'BASE', 'HEATSINK', '1U_CU', 'HS']):
        return "Aluminum alloy, wrought, 6061, T6" if "AL" in s else "Copper Alloy", "Functional: Thermal Heatsink"
    if any(k in s for k in ['AIR-DUCT', 'AIR_DUCT', 'DUCT', 'SHROUD', 'HOLDER', 'CLIP', 'RAIL', 'LATCH', 'HOUSING', 'PLASTIC', 'JVPLS', 'EAR-L-LATCH', 'LEVER', 'CARRIER']):
        return "SABIC Cycoloy C6200 PC+ABS", "Functional: Plastic / Shroud"
    if any(k in s for k in ['CONN', 'MCIO', 'SLIMSAS', 'FH34', 'USB', 'MINIDP', 'HEADER', 'SLOT']):
        return "SABIC Cycoloy C6200 PC+ABS", "Functional: Connector LCP"
    if any(k in s for k in ['SCREW', 'STANDOFF', 'RIVET', 'NUT', 'HDW', 'JVHDW', 'ST-', 'SI-', 'TP-', '60H', 'SCR']):
        return "SAE1215 - STF", "Functional: Hardware Fastener"
    if any(k in s for k in ['FAN', 'DFPK']):
        return "Plastic, PA6", "Functional: Fan Module"
    if any(k in s for k in ['SPRING', 'SUS']):
        return "Stainless Steel - 301 1/2H", "Functional: Spring"
    if any(k in s for k in ['DIE-CASTING', 'DIE_CASTING', 'CASTING']):
        return "Aluminum alloy, wrought, 6061, T6", "Functional: Die Casting"
        
    # Priority 4: SMT Board Components Regex (Diodes, Jumpers, Chips)
    if re.match(r'^(D|J|R|C|U|L|Q|SW|LED)\\\\d+', s):
        return "PCB laminate, Epoxy/Glass fiber, FR-4", "SMT Component (D/J/R/C/U)"
        
    return None, None

def run_small_batch_material_test():
    model = ExtAPI.DataModel.Project.Model
    avail_mats = [m.Name for m in model.Materials.Children]
    all_bodies = list(model.Geometry.GetChildren(DataModelObjectCategory.Body, True))
    sample_bodies = all_bodies[:10]
    
    print("==================================================")
    print("SESSION 01: SMALL-BATCH MATERIAL ASSIGNMENT TEST")
    print("==================================================")
    print("Total bodies in model: " + str(len(all_bodies)))
    print("Sample test batch size: " + str(len(sample_bodies)))
    print("Available Materials in Project: " + str(len(avail_mats)))
    
    assigned_count = 0
    unassigned_bodies = []
    
    for idx, b in enumerate(sample_bodies):
        b_raw = b.Name
        parts = b_raw.split('\\\\')
        clean_parts = [clean_name_string(p) for p in parts if p]
        if b.Parent:
            clean_parts.append(clean_name_string(b.Parent.Name))
            
        matched_mat = None
        match_src = None
        for cp in clean_parts:
            matched_mat, match_src = match_keyword_rules(cp)
            if matched_mat:
                break
        if not matched_mat:
            matched_mat, match_src = match_keyword_rules('_'.join(clean_parts))
            
        if matched_mat and matched_mat in avail_mats:
            orig_mat = b.Material
            b.Material = matched_mat
            assigned_count += 1
            print(" [{:02d}] Body: '{}'".format(idx+1, b_raw))
            print("      -> Matched: '{}' via [{}]".format(matched_mat, match_src))
            print("      -> Assigned: '{}' (Previous: '{}')".format(b.Material, orig_mat))
        else:
            unassigned_bodies.append(b)
            print(" [{:02d}] Body: '{}' -> UNASSIGNED (Fallback needed)".format(idx+1, b_raw))
            
    # Update/Verify [Mat] Unassigned_Bodies Named Selection
    ns_name = "[Mat] Unassigned_Bodies"
    existing_ns = None
    if model.NamedSelections:
        for child in model.NamedSelections.Children:
            if child.Name == ns_name:
                existing_ns = child
                break
                
    if unassigned_bodies:
        if not existing_ns:
            existing_ns = model.AddNamedSelection()
            existing_ns.Name = ns_name
        sel_mgr = ExtAPI.SelectionManager
        sel_info = sel_mgr.CreateSelectionInfo(Ansys.ACT.Interfaces.Common.SelectionTypeEnum.GeometryEntities)
        geo_bodies = [b.GetGeoBody() for b in unassigned_bodies if b.GetGeoBody()]
        sel_info.Entities = geo_bodies
        existing_ns.Location = sel_info
        print("\\nNamed Selection '{}' created/updated with {} orphan bodies.".format(ns_name, len(unassigned_bodies)))
    else:
        print("\\nAll {} sample bodies successfully assigned materials (0 unassigned).".format(len(sample_bodies)))
        
    print("==================================================")
    print("METRICS SUMMARY:")
    print(" - Sample Size: {}".format(len(sample_bodies)))
    print(" - Successfully Assigned: {}".format(assigned_count))
    print(" - Unassigned: {}".format(len(unassigned_bodies)))
    print(" - Coverage Rate: {:.1f}%".format(float(assigned_count)/float(len(sample_bodies))*100.0))
    print("==================================================")
    return assigned_count

run_small_batch_material_test()
"""

def main():
    print("Connecting to live ANSYS Mechanical instance via PyMechanical (Port 10000)...")
    mc = MechanicalController()
    res = mc.connect(port=10000)
    if not res.get("ok"):
        print("Error connecting to Mechanical:", res)
        return False
    
    print("Executing Session 01 Small-Batch Test Script...")
    result = mc.run_script(TEST_SCRIPT_IRONPYTHON)
    print(result)
    return True

if __name__ == "__main__":
    main()
