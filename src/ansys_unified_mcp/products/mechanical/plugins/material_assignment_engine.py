# -*- coding: utf-8 -*-
import clr
import os
import sys
import re
import datetime
import time as _act_time

clr.AddReference("System")
clr.AddReference("System.Windows.Forms")
clr.AddReference("Ansys.ACT.Interfaces")
clr.AddReference("Ansys.Mechanical.DataModel")

import System
import System.Windows.Forms as WinForms
from System.Collections.Generic import List
from Ansys.Mechanical.DataModel.Enums import DataModelObjectCategory

_ACT_START_TIME = _act_time.time()

def isValidBOMPath(task, property):
    return True

def log_usage(act_name, act_version, elapsed_sec, manual_sec):
    try:
        from System import Environment
        from System.IO import FileStream, StreamWriter, FileMode, FileAccess, FileShare, Directory
        user_name = Environment.UserName
        machine_name = Environment.MachineName
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        month = datetime.datetime.now().strftime("%Y_%m")
        log_dir = r"\\Twtrkei017\e\Structure_shared_folder\03. Team member\Ikaros\Test_ACT_usage_rate"
        if not Directory.Exists(log_dir):
            Directory.CreateDirectory(log_dir)
        log_path = log_dir + "\\usage_" + month + ".csv"
        saved_sec = manual_sec - elapsed_sec
        log_line = "{},{},{},{},{},{},{},{}\n".format(
            timestamp, user_name, machine_name,
            act_name, act_version,
            "%.1f" % elapsed_sec,
            manual_sec,
            "%.1f" % saved_sec
        )
        fs = FileStream(log_path, FileMode.Append, FileAccess.Write, FileShare.ReadWrite)
        writer = StreamWriter(fs)
        writer.Write(log_line)
        writer.Flush()
        writer.Close()
        fs.Close()
    except Exception as e:
        pass

def clean_name_string(name_str):
    if name_str is None:
        return ""
    try:
        raw = unicode(name_str)
        # Strip component path prefix before backslash (e.g. Component\BodyName -> BodyName)
        raw = re.sub(r'^.*\\', u'', raw)
        s = raw.encode('ascii', 'ignore')
    except:
        try:
            s = "".join([c for c in str(name_str) if ord(c) < 128])
            s = re.sub(r'^.*\\', '', s)
        except:
            s = ""
            
    # Strip SpaceClaim Midsurface prefixes and instance numbers
    s = re.sub(r'(?i)^\s*midsurface\s*[-\s_]*', '', s)
    s = re.sub(r'(?i)\s*[\(\[]\s*(Solid|Surface|Sheet|Body|Part|Midsurface\d*)\s*[\)\]]', '', s)
    s = re.sub(r'(?i)(\.prt|\.asm)\.\d+$', '', s)
    s = re.sub(r'(?i)\.(asm|prt|sldprt|sldasm)$', '', s)
    s = re.sub(r':\d+$', '', s)
    s = re.sub(r'-\d+$', '', s)
    return s.strip().upper()

def is_default_structural_steel(mat_name_str):
    if not mat_name_str:
        return True
    try:
        u_mat = unicode(mat_name_str).strip()
        if u_mat in [u"Structural Steel", u"Default", u"None", u""]:
            return True
        if u"Steel" in u_mat:
            if u"Stainless" not in u_mat and u"301" not in u_mat and u"304" not in u_mat and u"SAE" not in u_mat:
                return True
    except:
        s = str(mat_name_str).strip()
        if s in ["Structural Steel", "Default", "None", ""]:
            return True
    return False

def load_bom_mapping(excel_path):
    bom_map = {}
    if not excel_path:
        return bom_map
    clean_path = str(excel_path).strip()
    if not clean_path or not os.path.exists(clean_path):
        return bom_map
        
    excel_app = None
    wb = None
    try:
        clr.AddReference("Microsoft.Office.Interop.Excel")
        import Microsoft.Office.Interop.Excel as Excel
        excel_app = Excel.ApplicationClass()
        excel_app.Visible = False
        excel_app.DisplayAlerts = False
        wb = excel_app.Workbooks.Open(clean_path, False, True)
        
        for sheet_idx in range(1, wb.Sheets.Count + 1):
            sheet = wb.Sheets[sheet_idx]
            used_range = sheet.UsedRange
            r_cnt = used_range.Rows.Count
            c_cnt = used_range.Columns.Count
            
            # Dynamic header detection within the first 10 rows
            header_row = None
            col_map = {}
            for r in range(1, min(11, r_cnt + 1)):
                row_vals = []
                for c in range(1, min(35, c_cnt + 1)):
                    cell_val = sheet.Cells[r, c].Value2
                    v_str = str(cell_val or "").strip().upper()
                    row_vals.append((c, v_str))
                    
                has_part = any(k in v for _, v in row_vals for k in ["PART NUMBER", "DWG", "FILE NAME", "JPN", "ITEM"])
                has_mat = any("MATERIAL" in v for _, v in row_vals)
                has_desc = any(k in v for _, v in row_vals for k in ["DESC", "DESCRIPTION", "COMMON NAME"])
                
                if (has_part or has_desc) and has_mat:
                    header_row = r
                    for c_idx, v in row_vals:
                        if ("DWG" in v or "DRAWING" in v or "FILE NAME" in v) and "dwg" not in col_map:
                            col_map["dwg"] = c_idx
                        elif ("JPN" in v or "PART NUMBER" in v or "PART NO" in v) and "jpn" not in col_map:
                            col_map["jpn"] = c_idx
                        elif ("DESC" in v or "DESCRIPTION" in v or "COMMON NAME" in v) and "desc" not in col_map:
                            col_map["desc"] = c_idx
                        elif ("PROPERTY" in v or "PART TYPE" in v or "TYPE" in v) and "prop" not in col_map:
                            col_map["prop"] = c_idx
                        elif ("MATERIAL" in v and "ADDITIONAL" not in v and "COLOR" not in v) and "mat" not in col_map:
                            col_map["mat"] = c_idx
                    break
                    
            if header_row and "mat" in col_map:
                dwg_col = col_map.get("dwg", None)
                jpn_col = col_map.get("jpn", None)
                desc_col = col_map.get("desc", None)
                prop_col = col_map.get("prop", None)
                mat_col = col_map.get("mat", None)
                
                for r in range(header_row + 1, r_cnt + 1):
                    dwg_val = sheet.Cells[r, dwg_col].Value2 if dwg_col else ""
                    jpn_val = sheet.Cells[r, jpn_col].Value2 if jpn_col else ""
                    desc_val = sheet.Cells[r, desc_col].Value2 if desc_col else ""
                    prop_val = sheet.Cells[r, prop_col].Value2 if prop_col else ""
                    mat_val = sheet.Cells[r, mat_col].Value2 if mat_col else ""
                    
                    entry = {
                        "dwg": unicode(dwg_val).strip() if dwg_val is not None else u"",
                        "jpn": unicode(jpn_val).strip() if jpn_val is not None else u"",
                        "desc": unicode(desc_val).strip() if desc_val is not None else u"",
                        "prop": unicode(prop_val).strip() if prop_val is not None else u"",
                        "material": unicode(mat_val).strip() if mat_val is not None else u""
                    }
                    
                    k_dwg = clean_name_string(dwg_val)
                    k_jpn = clean_name_string(jpn_val)
                    if k_dwg:
                        bom_map[k_dwg] = entry
                    if k_jpn:
                        bom_map[k_jpn] = entry
                        
    except Exception as e:
        print("BOM Loading Warning: " + str(e))
    finally:
        if wb is not None:
            try:
                wb.Close(False)
            except:
                pass
        if excel_app is not None:
            try:
                excel_app.Quit()
            except:
                pass
    return bom_map

def normalize_material_name(raw_mat_str, desc_str="", prop_str="", available_eng_mats=None):
    raw_s = unicode(raw_mat_str) + u" " + unicode(desc_str)
    s = raw_s.upper().strip()
    p = unicode(prop_str).upper().strip()
    clean_mat = unicode(raw_mat_str).strip() if raw_mat_str else u""
    clean_mat_upper = clean_mat.upper()
    
    mat_case_map = {}
    if available_eng_mats:
        for em in available_eng_mats:
            mat_case_map[em.upper()] = em
    
    # Direct Exact Match with Engineering Data
    if mat_case_map and clean_mat:
        if clean_mat_upper in mat_case_map:
            return mat_case_map[clean_mat_upper]
        for em_upper, em_real in mat_case_map.items():
            if em_upper in clean_mat_upper:
                return em_real
            if len(clean_mat) >= 4 and clean_mat_upper in em_upper:
                return em_real

    def pick_mat(preferred_list):
        for pref in preferred_list:
            if pref.upper() in mat_case_map:
                return mat_case_map[pref.upper()]
        return preferred_list[0]

    # Foam, Cushion, Gasket, Mylar
    if any(k in s for k in [u"CR2030", u"FOAM", u"SPONGE", u"GASKET", u"RUBBER", u"MYLAR", u"PE-LD", u"NBR", u"EPE"]):
        return pick_mat(["EPE_Jojnson_Cook", "PE-LD foam (cross-linked, closed cell, 0.045)"])
        
    # Stainless Steel & Springs
    if any(k in s for k in [u"301", u"SUS301", u"SUS304", u"SUS303", u"SUS", u"MUSIC WIRE", u"SWPB", u"STAINLESS", u"SST", u"EMI"]):
        return pick_mat(["Stainless Steel - 301 1/2H"])
        
    # Copper & Brass
    if any(k in s for k in [u"COPPER", u"C1100", u"BRASS", u"BE-CU", u"HEATPIPE"]) or bool(re.search(r'\bCU\b', s)):
        return pick_mat(["Copper Alloy"])

    # Wood, Fixture, Pallet
    if any(k in s for k in [u"PALLET", u"WOOD", u"FIXTURE", u"OAK"]):
        return pick_mat(["Wood, Oak"])

    # Sheet Metal
    if u"SGC400" in s:
        return pick_mat(["SGC400", "SGCC"])
    if u"SGCC" in s or u"SPCC" in s or u"SHEET METAL" in p:
        return pick_mat(["SGCC", "SGC400"])

    # High Modulus PC+ABS
    if u"C6200" in s:
        return pick_mat(["SABIC Cycoloy C6200 PC+ABS", "PC+ABS-SABIC Cycoloy C6200", "PC+ABS-SABIC Cycoloy C2950"])
        
    # Flame Retardant PC+ABS
    if u"FR3010" in s or u"BAYBLEND" in s:
        return pick_mat(["PC+ABS-Bayblend FR 3010"])
        
    # Standard PC+ABS
    if u"PC/ABS" in s or u"PC+ABS" in s or u"CYCOLOY" in s:
        return pick_mat(["PC+ABS-SABIC Cycoloy C2950", "SABIC Cycoloy C6200 PC+ABS", "PC+ABS-SABIC Cycoloy C6200"])

    # PCB / PCBA
    if u"FR4" in s or u"FR-4" in s or u"PCB" in s or u"PBA" in s or u"PCBA" in s or u"PCBA" in p:
        return pick_mat(["PCB laminate, Epoxy/Glass fiber, FR-4"])

    # Carbon Steel Fasteners
    if u"CARBON STEEL" in s or u"CARBON_STEEL" in s or u"HARDWARE" in p or u"SAE1215" in s:
        return pick_mat(["SAE1215 - STF"])

    # Aluminum
    if u"6061" in s or u"ALUMINUM" in s or u"AL6061" in s or u"AL_" in s:
        return pick_mat(["Aluminum alloy, wrought, 6061, T6", "Aluminum Alloy"])

    # Nylon
    if u"NYLON" in s or u"PA66" in s or u"PA6" in s:
        return pick_mat(["NYLON 66 Zytel-1.5%", "NYLON 66"])

    # Connector LCP
    if u"LCP" in s or (u"CONNECTOR" in s and u"PCIE" in s):
        return pick_mat(["SMT Connector plastic - LCP - E471i (BigGoot Amphenol PCIe connector)"])

    # Die Casting Zinc
    if u"ZA8" in s or u"ZA5" in s or u"ZINC" in s or u"DIE-CASTING" in s:
        return pick_mat(["Die Casting - ZA8, Zinc Alloy"])
        
    # Packaging
    if any(k in s for k in [u"CARTON", u"CORRUGATED", u"BOX"]):
        return pick_mat(["Carton One direction"])
        
    # Chipset & Solder
    if any(k in s for k in [u"CHIPSET", u"ASIC", u"BGA", u"SILICON CHIP", u"CPU_DIE"]) or bool(re.search(r'\bDIE\b', s)):
        return pick_mat(["chipset", "Chipset"])
    if any(k in s for k in [u"SAC305", u"SOLDER"]):
        return pick_mat(["SAC305"])

    return clean_mat if clean_mat else None

def match_keyword_rules(name_str, available_eng_mats=None):
    s = clean_name_string(name_str)
    if not s:
        return None, None
        
    mat_case_map = {}
    if available_eng_mats:
        for em in available_eng_mats:
            mat_case_map[em.upper()] = em

    def pick_mat(preferred_list):
        for pref in preferred_list:
            if pref.upper() in mat_case_map:
                return mat_case_map[pref.upper()]
        return preferred_list[0]

    # Foam, Sponge, Gasket, Mylar (Preempts host names like AIR-DUCT)
    if any(k in s for k in ["SPONGE", "FOAM", "GASKET", "CR2030", "CUSHION", "ISOLATION_PAD", "MYLAR", "RUBBER", "PE-LD", "NBR"]) or s.startswith("SPONGE_") or s.startswith("FOAM_") or s.startswith("JVDCM"):
        return pick_mat(["EPE_Jojnson_Cook", "PE-LD foam (cross-linked, closed cell, 0.045)"]), "Sealing & Foam / Mylar"

    # Springs & EMI Shielding (Preempts generic BKT)
    if any(k in s for k in ["EMI", "SPRING", "TORSION", "SWPB", "MUSIC WIRE", "EJECTOR_SPRING", "SUS301", "SUS304", "SUS303", "SUS", "STAINLESS", "SST"]):
        return pick_mat(["Stainless Steel - 301 1/2H"]), "Springs & EMI Shielding"

    # Thermal & Copper (Preempts generic BASE)
    if any(k in s for k in ["CUBASE", "HEATPIPE", "VAPOR", "FIN", "HEATSINK", "1U_CU", "2U_CU", "COPPER", "C1100", "BRASS", "BE-CU", "BERYLLIUM COPPER"]) or bool(re.search(r'\bCU\b', s)) or s.startswith("CC-"):
        return pick_mat(["Copper Alloy"]), "Thermal Copper & Brass"

    # Jabil Direct Prefixes
    if s.startswith("JVMTS"):
        return pick_mat(["SGCC", "SGC400"]), "Jabil Sheet Metal (JVMTS)"
    if s.startswith("JVPBA") or s.startswith("PCBA_") or s.startswith("PBA_"):
        return pick_mat(["PCB laminate, Epoxy/Glass fiber, FR-4"]), "Jabil PCBA (JVPBA)"
    if s.startswith("JVPLS"):
        if "C6200" in s:
            return pick_mat(["SABIC Cycoloy C6200 PC+ABS", "PC+ABS-SABIC Cycoloy C6200", "PC+ABS-SABIC Cycoloy C2950"]), "Jabil Plastic C6200 (JVPLS)"
        return pick_mat(["PC+ABS-SABIC Cycoloy C2950", "SABIC Cycoloy C6200 PC+ABS", "PC+ABS-SABIC Cycoloy C6200"]), "Jabil Plastic (JVPLS)"
    if s.startswith("JVHDW"):
        return pick_mat(["SAE1215 - STF"]), "Jabil Hardware Fastener (JVHDW)"
    if s.startswith("JVMIS") and any(k in s for k in ["CABLE", "TIE", "MIS"]):
        return pick_mat(["NYLON 66 Zytel-1.5%", "NYLON 66"]), "Jabil Nylon Miscellaneous (JVMIS)"

    # High Speed Connectors
    if any(k in s for k in ["LCP", "E471I", "MCIO", "SLIMSAS", "FH34", "MINIDP", "HEADER", "SLOT"]) or (("CONN" in s or "CONNECTOR" in s) and "PCIE" in s):
        return pick_mat(["SMT Connector plastic - LCP - E471i (BigGoot Amphenol PCIe connector)"]), "High-Speed Connector LCP"

    # Wood, Pallet, Fixture (Evaluated before generic Sheet Metal/Hardware to ensure fixtures are wood)
    if any(k in s for k in ["PALLET", "WOOD", "FIXTURE", "OAK"]):
        return pick_mat(["Wood, Oak"]), "Wood Fixture / Pallet"

    # Sheet Metal Enclosures
    if any(k in s for k in ["SGC400", "SGC 400"]):
        return pick_mat(["SGC400", "SGCC"]), "Material: SGC400"
    if any(k in s for k in ["SGCC", "SPCC", "SHEET METAL", "CHASSIS", "BASEPAN", "BASE PAN", "TOP-COVER", "TOP_COVER", "TRAY", "CAGE", "BRACKET", "BKT", "WALL", "WINDOW", "BAR", "PANEL", "BEZEL", "PARTITION", "BAREBONE", "STAKE"]) or s.startswith("SM_") or s.startswith("SM-") or bool(re.search(r'(?:^|[_\s-])(TOP|BASE)(?:[_\s-]|$)', s)):
        return pick_mat(["SGCC", "SGC400"]), "Sheet Metal Chassis & Bracket"

    # Plastic Functional Parts
    if any(k in s for k in ["AIR-DUCT", "AIRDUCT", "DUCT", "SHROUD", "HOLDER", "CLIP", "RAIL", "LATCH", "HOUSING", "PLASTIC", "PLS", "EAR-L-LATCH", "HANDLE", "CARRIER", "ISOLATOR"]) or s.startswith("PL_") or s.startswith("PLS_") or s.startswith("PLS-"):
        if "C6200" in s:
            return pick_mat(["SABIC Cycoloy C6200 PC+ABS", "PC+ABS-SABIC Cycoloy C6200"]), "High Modulus Plastic C6200"
        return pick_mat(["PC+ABS-SABIC Cycoloy C2950", "SABIC Cycoloy C6200 PC+ABS"]), "Plastic Shroud & Housing"

    # Fasteners & Hardware
    if any(k in s for k in ["SCREW", "PIN", "T-PIN", "STANDOFF", "T-STANDOFF", "RIVET", "NUT", "HDW", "SAE1215", "CARBON STEEL", "CARBON_STEEL", "ST-", "SI-", "TP-", "60H"]) or s.startswith("HDW_") or s.startswith("HDW-"):
        return pick_mat(["SAE1215 - STF"]), "Hardware Fastener"

    # PCBA & Electronics
    if any(k in s for k in ["PCB", "PCBA", "PBA", "MB_", "DIMM", "RISER", "EGS-", "MID-PLANE", "MIDPLANE", "ODP", "CPLD", "WHITLEY", "CARD", "DUMMY BOARD"]):
        return pick_mat(["PCB laminate, Epoxy/Glass fiber, FR-4"]), "PCB Assembly"
    if re.match(r'^(D|J|R|C|U|L|Q|SW|LED)\d+', s):
        return pick_mat(["PCB laminate, Epoxy/Glass fiber, FR-4"]), "SMT Component (D/J/R/C/U)"

    # Aluminum Extrusions & Die-Casting
    if any(k in s for k in ["6061", "AL6061", "6061-T6", "ALUMINUM", "FRAME", "FRAME-FIN", "DIE-CASTING", "DIE_CASTING", "CASTING"]) or s.startswith("AL_") or s.startswith("HS_FRAME"):
        return pick_mat(["Aluminum alloy, wrought, 6061, T6", "Aluminum Alloy"]), "Aluminum Extruded Frame"

    # Packaging Carton
    if any(k in s for k in ["BOX", "CARTON", "PACKAGING_BOX", "SHIPPING_BOX", "CORRUGATED"]):
        return pick_mat(["Carton One direction"]), "Packaging Carton"

    # Nylon, Chipset (Word boundary \bDIE\b prevents collision with 'Bodies'), Solder
    if any(k in s for k in ["NYLON", "PA66", "PA6", "ZYTEL", "CABLE TIE"]):
        return pick_mat(["NYLON 66 Zytel-1.5%", "NYLON 66"]), "Nylon 66"
    if any(k in s for k in ["CHIPSET", "BGA", "ASIC", "SILICON CHIP", "CPU_DIE"]) or bool(re.search(r'\bDIE\b', s)):
        return pick_mat(["chipset", "Chipset"]), "Silicon Chipset"
    if any(k in s for k in ["SAC305", "SOLDER", "SN96.5", "SOLDER_BALL"]):
        return pick_mat(["SAC305"]), "SAC305 Solder"

    return None, None

def get_prop_val(step, prop_name, default_val=None):
    try:
        if step is not None and hasattr(step, "Properties"):
            p = step.Properties[prop_name]
            if p is not None:
                return p.Value
    except:
        pass
    return default_val

def cleanup_mat_grouping_folders(node):
    if not hasattr(node, "Children"):
        return
    for child in list(node.Children):
        try:
            if "TreeGroupingFolder" in str(child.GetType()):
                cleanup_mat_grouping_folders(child)
                if child.Name.startswith("[Mat]"):
                    child.Ungroup()
            elif hasattr(child, "Children"):
                cleanup_mat_grouping_folders(child)
        except:
            pass

def update_unassigned_named_selection(Model, ExtAPI, unassigned_bodies):
    try:
        ns_name = "[Mat] Unassigned_Bodies"
        existing_ns = None
        if Model.NamedSelections:
            for child in Model.NamedSelections.Children:
                if child.Name == ns_name:
                    existing_ns = child
                    break
                    
        if unassigned_bodies and len(unassigned_bodies) > 0:
            if not existing_ns:
                existing_ns = Model.AddNamedSelection()
                existing_ns.Name = ns_name
            sel_mgr = ExtAPI.SelectionManager
            sel_info = sel_mgr.CreateSelectionInfo(Ansys.ACT.Interfaces.Common.SelectionTypeEnum.GeometryEntities)
            geo_bodies = []
            for b in unassigned_bodies:
                gb = b.GetGeoBody()
                if gb:
                    geo_bodies.append(gb)
            sel_info.Entities = geo_bodies
            existing_ns.Location = sel_info
        elif existing_ns:
            try:
                existing_ns.Delete()
            except:
                pass
    except Exception as nse:
        print("Named Selection Notice: " + str(nse))

def resolve_candidate_bodies(Model, ExtAPI):
    all_bodies = list(Model.Geometry.GetChildren(DataModelObjectCategory.Body, True))
    geo_id_map = {}
    for b in all_bodies:
        try:
            gb = b.GetGeoBody()
            if gb:
                geo_id_map[gb.Id] = b
        except:
            pass
            
    selected_bodies = []
    seen_obj_ids = set()
    
    # 3D Graphics Viewport Selection
    try:
        sel = ExtAPI.SelectionManager.CurrentSelection
        if sel and hasattr(sel, "Entities") and sel.Entities.Count > 0:
            for e in sel.Entities:
                eid = getattr(e, "Id", None)
                if eid and eid in geo_id_map:
                    b = geo_id_map[eid]
                    if b.ObjectId not in seen_obj_ids:
                        selected_bodies.append(b)
                        seen_obj_ids.add(b.ObjectId)
                elif hasattr(e, "Body"):
                    b_id = getattr(e.Body, "Id", None)
                    if b_id and b_id in geo_id_map:
                        b = geo_id_map[b_id]
                        if b.ObjectId not in seen_obj_ids:
                            selected_bodies.append(b)
                            seen_obj_ids.add(b.ObjectId)
    except Exception as se:
        print("3D Selection Resolver Notice: " + str(se))
        
    # Model Tree Active Objects fallback
    if len(selected_bodies) == 0:
        try:
            active_objs = ExtAPI.DataModel.Tree.ActiveObjects
            if active_objs:
                for obj in active_objs:
                    if hasattr(obj, "DataModelObjectCategory"):
                        cat = str(obj.DataModelObjectCategory)
                        if cat == "Body":
                            if obj.ObjectId not in seen_obj_ids:
                                selected_bodies.append(obj)
                                seen_obj_ids.add(obj.ObjectId)
                        elif cat == "Part" or hasattr(obj, "GetChildren"):
                            for child in obj.GetChildren(DataModelObjectCategory.Body, True):
                                if child.ObjectId not in seen_obj_ids:
                                    selected_bodies.append(child)
                                    seen_obj_ids.add(child.ObjectId)
        except Exception as te:
            print("Tree Selection Resolver Notice: " + str(te))
            
    if len(selected_bodies) > 0:
        return selected_bodies, "Selected Bodies ({})".format(len(selected_bodies))
    else:
        return all_bodies, "All Geometry Bodies (Auto-Detect: {})".format(len(all_bodies))

def onupdateStep(step):
    startTime = _act_time.time()
    
    # Safe property extraction
    BOM_FilePath = get_prop_val(step, 'BOM_FilePath', '')
    OverwriteExisting = bool(get_prop_val(step, 'OverwriteExisting', False))
    GroupFolders = bool(get_prop_val(step, 'GroupFolders', False))
    
    # Check Expiration Date
    expireddate = datetime.date(2027, 9, 1)
    nowdate = datetime.datetime.now()
    if (nowdate.date() - expireddate).days > 0:
        try:
            WinForms.print("[UI_OUTPUT] " + str("This ACT automation has expired. Please update to the latest release."))
        except:
            pass
        return
        
    # Model & Selection Scope
    Model = ExtAPI.DataModel.Project.Model
    candidate_bodies, scope_desc = resolve_candidate_bodies(Model, ExtAPI)
    
    # Retrieve available materials from active project Engineering Data
    available_eng_mats = []
    mat_case_map = {}
    if Model.Materials:
        try:
            for m in Model.Materials.Children:
                available_eng_mats.append(m.Name)
                mat_case_map[m.Name.upper()] = m.Name
        except:
            pass
        
    print("\n========== Automated Material Assignment ==========")
    print("Scope: {} ({} bodies candidate)".format(scope_desc, len(candidate_bodies)))
    print("Available Engineering Data Materials: {}".format(len(available_eng_mats)))
    
    # Load BOM if provided
    bom_map = {}
    has_bom = False
    if BOM_FilePath and str(BOM_FilePath).strip():
        clean_path = str(BOM_FilePath).strip()
        if os.path.exists(clean_path):
            print("Loading BOM from: {}".format(clean_path))
            bom_map = load_bom_mapping(clean_path)
            print("Loaded {} BOM Keys dynamically".format(len(bom_map)))
            has_bom = True
        else:
            print("Notice: Provided BOM file path does not exist, running in Keyword-Only mode.")
    else:
        print("No BOM file provided, running in Keyword-Only mode.")
        
    # Counters & Collections
    cnt_total = len(candidate_bodies)
    cnt_skipped_suppressed = 0
    cnt_skipped_custom_mat = 0
    cnt_assigned_bom = 0
    cnt_assigned_kw = 0
    cnt_unassigned = 0
    
    assigned_groups = {}
    all_assigned_bodies = []
    unassigned_bodies = []
    
    for b in candidate_bodies:
        # Check Suppressed
        if b.Suppressed:
            cnt_skipped_suppressed += 1
            continue
            
        # Check Overwrite Policy
        current_mat = b.Material
        if not OverwriteExisting and not is_default_structural_steel(current_mat):
            cnt_skipped_custom_mat += 1
            all_assigned_bodies.append(b)
            continue
            
        b_name = b.Name
        p_name = b.Parent.Name if b.Parent else ""
        
        clean_b = clean_name_string(b_name)
        clean_p = clean_name_string(p_name)
        candidates = [clean_b, clean_p]
        
        matched_mat = None
        match_source = None
        is_from_bom = False
        
        # Step 1: BOM Lookup
        if has_bom and bom_map:
            for c in candidates:
                if not c: continue
                if c in bom_map:
                    entry = bom_map[c]
                    m = normalize_material_name(entry["material"], entry["desc"], entry["prop"], available_eng_mats)
                    if m:
                        matched_mat = m
                        match_source = "BOM DWG/JPN ({})".format(c)
                        is_from_bom = True
                        break
                # Fuzzy match
                if not matched_mat:
                    for k, entry in bom_map.items():
                        if (len(k) >= 6 and k in c) or (len(c) >= 6 and c in k):
                            m = normalize_material_name(entry["material"], entry["desc"], entry["prop"], available_eng_mats)
                            if m:
                                matched_mat = m
                                match_source = "BOM Fuzzy ({})".format(k)
                                is_from_bom = True
                                break
                if matched_mat:
                    break
                    
        # Step 2: Keyword Matching Fallback
        if not matched_mat:
            for c in candidates:
                if not c: continue
                kw_m, kw_src = match_keyword_rules(c, available_eng_mats)
                if kw_m:
                    matched_mat = kw_m
                    match_source = kw_src
                    break
            if not matched_mat:
                kw_m, kw_src = match_keyword_rules(clean_p + "_" + clean_b, available_eng_mats)
                if kw_m:
                    matched_mat = kw_m
                    match_source = kw_src
                    
        # Apply Material Assignment & Update Counters ONLY on Actual Success
        assigned_successfully = False
        if matched_mat:
            # Reconcile exact casing against Engineering Data
            final_mat = matched_mat
            if matched_mat.upper() in mat_case_map:
                final_mat = mat_case_map[matched_mat.upper()]
                
            try:
                b.Material = str(final_mat)
                if final_mat not in assigned_groups:
                    assigned_groups[final_mat] = []
                assigned_groups[final_mat].append(b)
                all_assigned_bodies.append(b)
                assigned_successfully = True
                
                if is_from_bom:
                    cnt_assigned_bom += 1
                else:
                    cnt_assigned_kw += 1
            except Exception as e:
                assigned_successfully = False
                
        if not assigned_successfully:
            unassigned_bodies.append(b)
            cnt_unassigned += 1
            
    # Clean up old [Mat] folders
    try:
        cleanup_mat_grouping_folders(Model.Geometry)
    except:
        pass
        
    # Group Folders in Tree if requested
    if GroupFolders:
        try:
            for mat_name, b_list in assigned_groups.items():
                if b_list and len(b_list) > 0:
                    try:
                        grp = ExtAPI.DataModel.Tree.Group(b_list)
                        if grp:
                            grp.Name = "[Mat] {}".format(mat_name)
                    except Exception as ge:
                        print("Grouping error for " + str(mat_name) + ": " + str(ge))
                        
            if unassigned_bodies and len(unassigned_bodies) > 0:
                try:
                    u_grp = ExtAPI.DataModel.Tree.Group(unassigned_bodies)
                    if u_grp:
                        u_grp.Name = "[Mat] Unassigned"
                except Exception as ue:
                    print("Grouping error for unassigned: " + str(ue))
        except Exception as e:
            print("Tree Grouping Notice: " + str(e))
            
    # Update Named Selection
    update_unassigned_named_selection(Model, ExtAPI, unassigned_bodies)
    
    # Batch Visibility Control: Hide Assigned, Show Unassigned
    try:
        for b in all_assigned_bodies:
            b.Visible = False
        for b in unassigned_bodies:
            b.Visible = True
    except Exception as ve:
        print("Visibility Notice: " + str(ve))
        
    # Refresh Model Tree & Activate Geometry to guarantee Details pane is fully intact
    try:
        if hasattr(ExtAPI.DataModel.Tree, "Refresh"):
            ExtAPI.DataModel.Tree.Refresh()
        if hasattr(ExtAPI.DataModel.Tree, "Activate"):
            ExtAPI.DataModel.Tree.Activate([Model.Geometry])
        if hasattr(ExtAPI, "Graphics") and hasattr(ExtAPI.Graphics, "Redraw"):
            ExtAPI.Graphics.Redraw()
        WinForms.Application.DoEvents()
    except:
        pass
        
    endTime = _act_time.time()
    elapsed = round(endTime - startTime, 2)
    total_assigned = cnt_assigned_bom + cnt_assigned_kw
    processed_count = cnt_total - cnt_skipped_suppressed - cnt_skipped_custom_mat
    match_pct = (float(total_assigned) / float(processed_count) * 100.0) if processed_count > 0 else 0.0
    
    # Summary Report Message
    msg = "Automated Material Assignment Completed!\n"
    msg += "Execution Time: {} seconds\n\n".format(elapsed)
    msg += "Scope: {}\n".format(scope_desc)
    msg += "- Total Bodies in Scope: {}\n".format(cnt_total)
    if cnt_skipped_suppressed > 0:
        msg += "- Skipped Suppressed Bodies: {}\n".format(cnt_skipped_suppressed)
    if cnt_skipped_custom_mat > 0:
        msg += "- Preserved Existing Custom Materials: {}\n".format(cnt_skipped_custom_mat)
    msg += "- Active Candidates Processed: {}\n\n".format(processed_count)
    msg += "========================================\n"
    msg += "Assignment Summary (Coverage: %.1f%%):\n" % match_pct
    if cnt_assigned_bom > 0:
        msg += "- Assigned by BOM Lookup: {}\n".format(cnt_assigned_bom)
    msg += "- Assigned by Keyword Rules: {}\n".format(cnt_assigned_kw)
    msg += "- Total Successfully Assigned: {}\n".format(total_assigned)
    msg += "- Unassigned Bodies (Manual Check): {}\n".format(cnt_unassigned)
    msg += "========================================\n\n"
    msg += "Graphics & Selection Status:\n"
    msg += "- Named Selection: '[Mat] Unassigned_Bodies' ({} bodies)\n".format(len(unassigned_bodies))
    msg += "- Assigned Bodies: Hidden in 3D View ({} bodies)\n".format(len(all_assigned_bodies))
    msg += "- Unassigned Bodies: Shown in 3D View ({} bodies)\n\n".format(len(unassigned_bodies))
    
    if assigned_groups:
        msg += "Assigned Materials Breakdown:\n"
        for mat_name, b_list in sorted(assigned_groups.items(), key=lambda x: len(x[1]), reverse=True):
            msg += "  - {}: {} bodies\n".format(mat_name, len(b_list))
            
    try:
        act_elapsed_sec = _act_time.time() - _ACT_START_TIME
        log_usage("MECH_Material_Assignment", "1.0", act_elapsed_sec, 3600)
    except:
        pass
        
    print(msg)
    try:
        WinForms.print("[UI_OUTPUT] " + str(msg, "Material Assignment Summary"))
    except:
        pass
    print("========== Completed ==========\n")
