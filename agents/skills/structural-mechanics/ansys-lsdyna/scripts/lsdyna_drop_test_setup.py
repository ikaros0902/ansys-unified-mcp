# -*- coding: utf-8 -*-

def log_usage(act_name, act_version, elapsed_sec, manual_sec):
    try:
        import clr
        import datetime
        clr.AddReference("System")
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

# Safe assembly references and namespace shim
try:
    import clr
    for _asm in [
        "System",
        "System.Windows.Forms",
        "Ansys.ACT.Interfaces",
        "Ansys.Mechanical.DataModel",
        "Ansys.Core"
    ]:
        try:
            clr.AddReference(_asm)
        except Exception:
            pass
except Exception:
    pass

import System
try:
    import System.Windows.Forms as WinForms
except Exception:
    WinForms = None

try:
    from Ansys.Mechanical.DataModel.Enums import (
        DataModelObjectCategory,
        GeometryDefineByType,
        CoordinateSystemType,
        CoordinateSystemAlignmentType,
        StiffnessBehavior,
        DropDirection,
        GravityOrientationType,
        SizingBehavior
    )
except Exception:
    class _EnumFallback(object):
        def __getattr__(self, name):
            return name

    DataModelObjectCategory = _EnumFallback()
    GeometryDefineByType = _EnumFallback()
    CoordinateSystemType = _EnumFallback()
    CoordinateSystemAlignmentType = _EnumFallback()
    StiffnessBehavior = _EnumFallback()
    DropDirection = _EnumFallback()
    GravityOrientationType = _EnumFallback()
    SizingBehavior = _EnumFallback()

try:
    from Ansys.ACT.Interfaces.Common import SelectionTypeEnum
except Exception:
    try:
        from Ansys.ACT.Automation.Mechanical import SelectionTypeEnum
    except Exception:
        class SelectionTypeEnum(object):
            GeometryEntities = "GeometryEntities"

try:
    from Ansys.ACT.Interfaces.Common import MechanicalUnitSystem
except Exception:
    try:
        from Ansys.ACT.Interfaces.Analysis import MechanicalUnitSystem
    except Exception:
        class MechanicalUnitSystem(object):
            StandardNMM = "StandardNMM"

try:
    from Ansys.Core.Units import Quantity
except Exception:
    class Quantity(object):
        def __init__(self, value, *args, **kwargs):
            self.Value = value
        def __str__(self):
            return str(self.Value)
        def __repr__(self):
            return "Quantity('{}')".format(self.Value)

try:
    from Ansys.ACT.Mechanical import Transaction
except Exception:
    try:
        from Ansys.ACT.Automation.Mechanical import Transaction
    except Exception:
        class Transaction(object):
            def __init__(self, *args, **kwargs):
                pass
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc_val, exc_tb):
                return False

def onupdateStep(step):
    import time as _act_time
    _ACT_START_TIME = _act_time.time()

    import time
    import os
    import clr
    import datetime
    import math

    try:
        clr.AddReference("System.Windows.Forms")
    except Exception:
        pass

    global Transaction, SelectionTypeEnum, MechanicalUnitSystem, Quantity
    global DataModelObjectCategory, GeometryDefineByType, CoordinateSystemType
    global CoordinateSystemAlignmentType, StiffnessBehavior, DropDirection
    global GravityOrientationType, SizingBehavior

    startTime = time.time()
    
    Drop_height = step.Properties['Drop_height'].Value
    DropHist_pts = step.Properties['DropHist_pts'].Value

    drop_faces_config = [
        {'name': 'Top', 'enabled': step.Properties['Check_top'].Value, 'rotation': [180, 0, 0], 'orientation': {'X': [1,0,0], 'Y': [0,1,0], 'Z': [0,0,1]}},
        {'name': 'Bottom', 'enabled': step.Properties['Check_bottom'].Value, 'rotation': [0, 0, 0], 'orientation': {'X': [1,0,0], 'Y': [0,-1,0], 'Z': [0,0,1]}},
        {'name': 'Front', 'enabled': step.Properties['Check_front'].Value, 'rotation': [90, 0, 0], 'orientation': {'X': [1,0,0], 'Y': [0,0,-1], 'Z': [0,1,0]}},
        {'name': 'Rear', 'enabled': step.Properties['Check_rear'].Value, 'rotation': [270, 0, 0], 'orientation': {'X': [1,0,0], 'Y': [0,0,1], 'Z': [0,1,0]}},
        {'name': 'Right', 'enabled': step.Properties['Check_right'].Value, 'rotation': [0, 0, 270], 'orientation': {'X': [0,1,0], 'Y': [-1,0,0], 'Z': [0,0,1]}},
        {'name': 'Left', 'enabled': step.Properties['Check_left'].Value, 'rotation': [0, 0, 90], 'orientation': {'X': [0,1,0], 'Y': [1,0,0], 'Z': [0,0,1]}}
    ]

    Drop_faces = [face for face in drop_faces_config if face['enabled']]
    
    velsetupdate = step.Properties['velsetupdate'].Value
    Anssetupdate = step.Properties['Anssetupdate'].Value
    Outputkfile = step.Properties['Outputkfile'].Value
    kfile_dir = step.Properties['kfile_dir'].Value

    debug_messages = []
    
    def safe_print(message):
        try:
            debug_messages.append(str(message))
            if "ERROR" in str(message) or "SUCCESS" in str(message):
                ExtAPI.Log.WriteMessage(str(message))
        except:
            pass

    def _safe_val(x):
        return getattr(x, 'Value', x)

    def _get_owner_body(entity):
        if entity is None:
            return None
        tname = type(entity).__name__
        if tname in ['GeoBodyWrapper', 'Body']:
            return entity
        for attr in ['Body', 'OwningBody', 'GetOwningBody']:
            if hasattr(entity, attr):
                try:
                    b = getattr(entity, attr)
                    b = b() if callable(b) else b
                    if b:
                        return b
                except:
                    pass
        return None

    def _is_shell_like(body_or_entity):
        b = _get_owner_body(body_or_entity) or body_or_entity
        if b is None:
            return None

        for attr in ['IsSheetBody', 'IsSurfaceBody']:
            if hasattr(b, attr):
                try:
                    flag = getattr(b, attr)
                    flag = flag() if callable(b) else flag
                    if isinstance(flag, bool):
                        return flag
                except:
                    pass

        for attr in ['BodyType', 'Type']:
            if hasattr(b, attr):
                try:
                    bt = getattr(b, attr)
                    bt = bt() if callable(bt) else bt
                    s = str(bt).lower()
                    if 'surface' in s or 'sheet' in s:
                        return True
                    if 'solid' in s:
                        return False
                except:
                    pass
        return None

    def _get_body_thickness(body):
        if body is None:
            return None

        candidate_names = [
            "Thickness", "ShellThickness", "SectionThickness", 
            "AssignedThickness", "BodyThickness"
        ]

        for nm in candidate_names:
            if hasattr(body, nm):
                try:
                    v = getattr(body, nm)
                    v = v() if callable(v) else v
                    v = _safe_val(v)
                    if v is not None:
                        return float(v)
                except:
                    pass

        for method in ['GetPropertyByName', 'PropertyByName']:
            if hasattr(body, method):
                for nm in candidate_names:
                    try:
                        p = getattr(body, method)
                        p = p(nm)
                        for pv in ['Value', 'InternalValue']:
                            if hasattr(p, pv):
                                val = getattr(p, pv)
                                val = _safe_val(val)
                                if val is not None:
                                    return float(val)
                    except:
                        pass
        return None

    def FreezeMeshForNamedSelection(ns_name):
        try:
            with Transaction(True):
                target_ns = None
                AllNS = GetAllNamedSelections()
                for ns in AllNS:
                    if hasattr(ns, 'Name') and ns.Name.ToLower() == ns_name.ToLower():
                        target_ns = ns
                        break
                
                if not target_ns:
                    safe_print("ERROR: Named Selection '{}' not found for mesh freezing".format(ns_name))
                    return False

                entities = target_ns.Location.Entities if hasattr(target_ns, 'Location') else []
                if not entities:
                    safe_print("ERROR: No entities found in Named Selection '{}'".format(ns_name))
                    return False

                part_ids = set()
                for entity in entities:
                    try:
                        body = _get_owner_body(entity)
                        if body:
                            if hasattr(body, 'Part'):
                                part = body.Part
                                if hasattr(part, 'Id'):
                                    part_ids.add(part.Id)
                            elif hasattr(body, 'GetPart'):
                                part = body.GetPart()
                                if part and hasattr(part, 'Id'):
                                    part_ids.add(part.Id)

                        if hasattr(entity, 'Part'):
                            part = entity.Part
                            if hasattr(part, 'Id'):
                                part_ids.add(part.Id)
                                
                    except Exception as e:
                        safe_print("WARNING: Could not get part ID from entity: {}".format(e))
                        continue

                if not part_ids:
                    safe_print("ERROR: No valid part IDs found for mesh freezing")
                    return False

                part_id_list = list(part_ids)
                geo_part_list = []
                
                for part_id in part_id_list:
                    try:
                        geo_part = DataModel.GeoData.GeoPartById(part_id)
                        if geo_part:
                            geo_part_list.append(geo_part)
                    except Exception as e:
                        safe_print("WARNING: Could not get GeoPart for ID {}: {}".format(part_id, e))
                        continue

                if not geo_part_list:
                    safe_print("ERROR: No valid GeoPart objects found for mesh freezing")
                    return False

                Model.FreezeMeshOnSelectedParts(geo_part_list)
                
                safe_print("SUCCESS: Mesh frozen for '{}' - {} parts affected".format(ns_name, len(geo_part_list)))
                return True
                    
        except Exception as e:
            safe_print("ERROR: Failed to freeze mesh: {}".format(e))
            return False

    def UnfreezeMeshForNamedSelection(ns_name):
        try:
            with Transaction(True):
                target_ns = None
                AllNS = GetAllNamedSelections()
                for ns in AllNS:
                    if hasattr(ns, 'Name') and ns.Name.ToLower() == ns_name.ToLower():
                        target_ns = ns
                        break
                
                if not target_ns:
                    safe_print("ERROR: Named Selection '{}' not found for mesh unfreezing".format(ns_name))
                    return False

                entities = target_ns.Location.Entities if hasattr(target_ns, 'Location') else []
                if not entities:
                    safe_print("ERROR: No entities found in Named Selection '{}'".format(ns_name))
                    return False

                part_ids = set()
                for entity in entities:
                    try:
                        body = _get_owner_body(entity)
                        if body:
                            if hasattr(body, 'Part'):
                                part = body.Part
                                if hasattr(part, 'Id'):
                                    part_ids.add(part.Id)
                            elif hasattr(body, 'GetPart'):
                                part = body.GetPart()
                                if part and hasattr(part, 'Id'):
                                    part_ids.add(part.Id)
                    except Exception as e:
                        continue

                part_id_list = list(part_ids)
                geo_part_list = []
                
                for part_id in part_id_list:
                    try:
                        geo_part = DataModel.GeoData.GeoPartById(part_id)
                        if geo_part:
                            geo_part_list.append(geo_part)
                    except Exception as e:
                        continue

                if geo_part_list:
                    Model.UnfreezeMeshOnSelectedParts(geo_part_list)
                    safe_print("SUCCESS: Mesh unfrozen for '{}' - {} parts affected".format(ns_name, len(geo_part_list)))
                    return True
                
                return False
                    
        except Exception as e:
            safe_print("ERROR: Failed to unfreeze mesh: {}".format(e))
            return False

    def get_named_selection_bounding_box(ns_name):
        safe_print("="*60)
        safe_print("INFO: Starting bounding box detection for: '" + ns_name + "'...")
        safe_print("="*60)

        try:
            target_ns = None
            AllNS = GetAllNamedSelections()
            
            for ns in AllNS:
                if hasattr(ns, 'Name') and ns.Name == ns_name:
                    target_ns = ns
                    break

            if not target_ns:
                safe_print("ERROR: Named Selection '" + ns_name + "' not found.")
                return None

            entities = None
            try:
                if hasattr(target_ns, 'Location') and target_ns.Location is not None:
                    entities = target_ns.Location.Entities
            except Exception as e:
                safe_print("Warning: Could not access Location.Entities: " + str(e))
                return None

            if not entities or len(entities) == 0:
                safe_print("WARNING: Named Selection '" + ns_name + "' is empty or its location is invalid.")
                return None

            min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
            max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')

            valid_entity_count = 0
            total_vertices_processed = 0
            
            for i, entity in enumerate(entities):
                try:
                    if entity is None:
                        continue
                        
                    entity_type_name = type(entity).__name__
                    vertices_to_process = []

                    if entity_type_name in ['GeoBodyWrapper', 'Body']:
                        if hasattr(entity, 'Vertices'):
                            try:
                                vertices_to_process = entity.Vertices
                            except Exception as e:
                                continue
                    elif entity_type_name == 'Face':
                        if hasattr(entity, 'Vertices'):
                            try:
                                vertices_to_process = entity.Vertices
                            except Exception as e:
                                continue
                    else:
                        continue

                    if vertices_to_process and len(vertices_to_process) > 0:
                        valid_entity_count += 1
                        
                        for j, vertex in enumerate(vertices_to_process):
                            try:
                                if vertex is None:
                                    continue

                                v_x = getattr(vertex.X, 'Value', vertex.X) if hasattr(vertex, 'X') else 0.0
                                v_y = getattr(vertex.Y, 'Value', vertex.Y) if hasattr(vertex, 'Y') else 0.0
                                v_z = getattr(vertex.Z, 'Value', vertex.Z) if hasattr(vertex, 'Z') else 0.0

                                if not (math.isnan(v_x) or math.isnan(v_y) or math.isnan(v_z) or
                                       math.isinf(v_x) or math.isinf(v_y) or math.isinf(v_z)):
                                    min_x = min(min_x, v_x)
                                    min_y = min(min_y, v_y)
                                    min_z = min(min_z, v_z)
                                    max_x = max(max_x, v_x)
                                    max_y = max(max_y, v_y)
                                    max_z = max(max_z, v_z)
                                    
                                    total_vertices_processed += 1
                                    
                            except Exception as e:
                                continue
                                    
                except Exception as e:
                    continue

            if valid_entity_count == 0:
                safe_print("WARNING: No valid entities with vertices found in '" + ns_name + "'.")
                return None

            if (min_x == float('inf') or max_x == float('-inf') or
                min_y == float('inf') or max_y == float('-inf') or
                min_z == float('inf') or max_z == float('-inf')):
                safe_print("WARNING: Invalid bounding box calculated for '" + ns_name + "'.")
                return None

            safe_print("SUCCESS: Bounding box calculated for '" + ns_name + "'")
            safe_print("SUCCESS: X-range: [{:.3f}, {:.3f}], Y-range: [{:.3f}, {:.3f}], Z-range: [{:.3f}, {:.3f}]".format(
                min_x*1000, max_x*1000, min_y*1000, max_y*1000, min_z*1000, max_z*1000))

            return {
                "bounding_box": [min_x, max_x, min_y, max_y, min_z, max_z],
                "center": [(min_x + max_x) / 2.0, (min_y + max_y) / 2.0, (min_z + max_z) / 2.0],
                "dimensions": {
                    "length_x": max_x - min_x,
                    "width_y": max_y - min_y,
                    "height_z": max_z - min_z
                },
                "statistics": {
                    "valid_entities": valid_entity_count,
                    "total_vertices": total_vertices_processed
                }
            }
            
        except Exception as e:
            safe_print("ERROR: Exception in get_named_selection_bounding_box: " + str(e))
            return None

    def calculate_rotated_collision_points(original_bbox_data):
        safe_print("INFO: Calculating collision points for all six faces using theoretical rotation...")
        
        if not original_bbox_data:
            safe_print("ERROR: No bounding box data provided")
            return None
            
        bb = original_bbox_data["bounding_box"]
        min_x, max_x, min_y, max_y, min_z, max_z = bb
        center = original_bbox_data["center"]

        length_x = max_x - min_x
        width_y = max_y - min_y  
        height_z = max_z - min_z
        
        safe_print("SUCCESS: Original geometry dimensions:")
        safe_print("  Length (X): {:.3f} mm".format(length_x * 1000))
        safe_print("  Width  (Y): {:.3f} mm".format(width_y * 1000))
        safe_print("  Height (Z): {:.3f} mm".format(height_z * 1000))
        
        collision_points = {}

        collision_points['Top'] = {
            'collision_point': [center[0] * 1000, max_y * 1000, center[2] * 1000],
            'ground_size': max(length_x, height_z) * 1000,
            'rotation': [180, 0, 0],
            'contact_face': 'Y_max'
        }

        collision_points['Bottom'] = {
            'collision_point': [center[0] * 1000, min_y * 1000, center[2] * 1000],
            'ground_size': max(length_x, height_z) * 1000,
            'rotation': [0, 0, 0],
            'contact_face': 'Y_min'
        }

        collision_points['Front'] = {
            'collision_point': [center[0] * 1000, center[1] * 1000, min_z * 1000],
            'ground_size': max(length_x, width_y) * 1000,
            'rotation': [90, 0, 0],
            'contact_face': 'Z_min'
        }

        collision_points['Rear'] = {
            'collision_point': [center[0] * 1000, center[1] * 1000, max_z * 1000],
            'ground_size': max(length_x, width_y) * 1000,
            'rotation': [-90, 0, 0],
            'contact_face': 'Z_max'
        }

        collision_points['Right'] = {
            'collision_point': [min_x * 1000, center[1] * 1000, center[2] * 1000],
            'ground_size': max(width_y, height_z) * 1000,
            'rotation': [0, 0, -90],
            'contact_face': 'X_min'
        }

        collision_points['Left'] = {
            'collision_point': [max_x * 1000, center[1] * 1000, center[2] * 1000],
            'ground_size': max(width_y, height_z) * 1000,
            'rotation': [0, 0, 90],
            'contact_face': 'X_max'
        }
        
        for face_name, data in collision_points.items():
            safe_print("SUCCESS: {} face collision point: X={:.3f}, Y={:.3f}, Z={:.3f} mm, Ground size: {:.1f} mm".format(
                face_name, data['collision_point'][0], data['collision_point'][1], 
                data['collision_point'][2], data['ground_size']))
        
        return collision_points

    def detect_shell_at_collision_face(ns_name, face_name, collision_data):
        safe_print("INFO: Detecting shell properties at collision face: {}".format(face_name))
        
        try:
            target_ns = None
            AllNS = GetAllNamedSelections()
            for ns in AllNS:
                if hasattr(ns, 'Name') and ns.Name == ns_name:
                    target_ns = ns
                    break

            if not target_ns:
                safe_print("ERROR: Named Selection '{}' not found".format(ns_name))
                return {'is_shell': False, 'thickness': None}

            entities = target_ns.Location.Entities if hasattr(target_ns, 'Location') else []
            if not entities:
                return {'is_shell': False, 'thickness': None}

            contact_face = collision_data['contact_face']
            collision_point = collision_data['collision_point']

            target_coordinate = None
            if contact_face in ['Y_max', 'Y_min']:
                target_coordinate = collision_point[1] / 1000 
                coordinate_index = 1
            elif contact_face in ['Z_max', 'Z_min']:
                target_coordinate = collision_point[2] / 1000
                coordinate_index = 2
            elif contact_face in ['X_max', 'X_min']:
                target_coordinate = collision_point[0] / 1000
                coordinate_index = 0

            closest_body = None
            min_distance = float('inf')

            for entity in entities:
                body = _get_owner_body(entity)
                if not body or not hasattr(body, 'Vertices'):
                    continue

                for vertex in body.Vertices:
                    try:
                        coords = [_safe_val(vertex.X), _safe_val(vertex.Y), _safe_val(vertex.Z)]
                        distance = abs(coords[coordinate_index] - target_coordinate)
                        
                        if distance < min_distance:
                            min_distance = distance
                            closest_body = body
                    except:
                        continue

            if closest_body:
                is_shell = _is_shell_like(closest_body)
                thickness = _get_body_thickness(closest_body)
                
                safe_print("SUCCESS: Shell detection for {} face - Is shell: {}, Thickness: {}".format(
                    face_name, is_shell, thickness))
                
                return {'is_shell': is_shell, 'thickness': thickness}
            
            return {'is_shell': False, 'thickness': None}
            
        except Exception as e:
            safe_print("ERROR: Exception in shell detection: {}".format(e))
            return {'is_shell': False, 'thickness': None}

    def GetAllNamedSelections():
        try:
            AllNS = ExtAPI.DataModel.Project.Model.GetChildren(DataModelObjectCategory.NamedSelection, True)
            if len(AllNS) > 0:
                return AllNS

            try:
                all_children = ExtAPI.DataModel.Project.Model.Children
                AllNS = []
                for child in all_children:
                    if str(child.GetType()).find('NamedSelection') != -1:
                        AllNS.append(child)
                return AllNS
            except:
                pass
                
            return []
            
        except Exception as e:
            safe_print("Error in GetAllNamedSelections: " + str(e))
            return []

    def _ensure_cs_uses_transformations(cs):

        try:
            cs.CoordinateSystemType = CoordinateSystemType.Cartesian
        except:
            pass

        for prop in ("DefineBy", "AlignmentDefineBy", "OrientationDefineBy"):
            if hasattr(cs, prop):
                try:
                    setattr(cs, prop, CoordinateSystemAlignmentType.Transformations)
                    break
                except:
                    pass

        for prop in ("ReferenceCoordinateSystem", "BaseCoordinateSystem", "BaseCS"):
            if hasattr(cs, prop):
                try:
                    base = Model.CoordinateSystems.Children[0]
                    setattr(cs, prop, base)
                    break
                except:
                    pass

    def CreateCollisionPointCoordinateSystem(initial_point_mm=[0, 0, 0], face_name=""):
        existing_cs = None
        for cs in Model.CoordinateSystems.Children:
            if cs.Name == "Collision Point":
                existing_cs = cs
                break

        if existing_cs is not None:
            safe_print("INFO: Collision Point coordinate system already exists, reusing...")
            return existing_cs

        with Transaction(True):
            cs = Model.CoordinateSystems.AddCoordinateSystem()
            cs.Name = "Collision Point"

            _ensure_cs_uses_transformations(cs)
            
            cs.OriginDefineBy = CoordinateSystemAlignmentType.Fixed
            gap_distance = 0.1 

            origin_x, origin_y, origin_z = initial_point_mm

            if face_name == 'Top':
                origin_y += gap_distance
            elif face_name == 'Bottom':
                origin_y -= gap_distance
            elif face_name == 'Front':
                origin_z -= gap_distance # Move ground away in -Z
            elif face_name == 'Rear':
                origin_z += gap_distance # Move ground away in +Z
            elif face_name == 'Right':
                origin_x -= gap_distance # Move ground away in -X
            elif face_name == 'Left':
                origin_x += gap_distance # Move ground away in +X
            else: # Default fallback, same as original logic
                origin_y -= gap_distance

            safe_print("INFO: Applying gap for face '{}'. Original Y: {:.3f}, New Origin Y: {:.3f}".format(
                face_name, initial_point_mm[1], origin_y))

            cs.OriginX = Quantity(str(origin_x) + " [mm]")
            cs.OriginY = Quantity(str(origin_y) + " [mm]")
            cs.OriginZ = Quantity(str(origin_z) + " [mm]")

            safe_print("SUCCESS: New Collision Point coordinate system created.")
            return cs

    def UpdateCollisionPointCoordinateSystem(collision_cs, new_point_mm, rotation_angles, face_name):
        with Transaction(True):
            gap_distance = 0.1

            origin_x, origin_y, origin_z = new_point_mm

            if face_name == 'Top':
                origin_y += gap_distance
            elif face_name == 'Bottom':
                origin_y -= gap_distance
            elif face_name == 'Front':
                origin_z -= gap_distance # Move ground away in -Z
            elif face_name == 'Rear':
                origin_z += gap_distance # Move ground away in +Z
            elif face_name == 'Right':
                origin_x -= gap_distance # Move ground away in -X
            elif face_name == 'Left':
                origin_x += gap_distance # Move ground away in +X
            else: 
                origin_y -= gap_distance

            safe_print("INFO: Updating gap for face '{}'. Original Y: {:.3f}, New Origin Y: {:.3f}".format(
                face_name, new_point_mm[1], origin_y))
                
            try:
                cs_name = collision_cs.Name
                cs_parent = collision_cs.Parent

                new_cs = cs_parent.AddCoordinateSystem()
                new_cs.Name = cs_name

                new_cs.OriginX = Quantity(str(origin_x) + " [mm]")
                new_cs.OriginY = Quantity(str(origin_y) + " [mm]")
                new_cs.OriginZ = Quantity(str(origin_z) + " [mm]")
                
                _ensure_cs_uses_transformations(new_cs)
                
                safe_print("INFO: Recreated coordinate system: {}".format(cs_name))

                x_angle, y_angle, z_angle = rotation_angles
                
                rotations_applied = 0

                if abs(float(x_angle)) > 1e-6:
                    x_rotations = int(round(float(x_angle) / 90.0))
                    for _ in range(abs(x_rotations)):
                        if x_rotations > 0:
                            new_cs.RotateX(90)
                        else:
                            new_cs.RotateX(-90)
                    safe_print("SUCCESS: Applied X rotation: {} degrees ({} x 90)".format(x_angle, x_rotations))
                    rotations_applied += 1

                if abs(float(y_angle)) > 1e-6:
                    y_rotations = int(round(float(y_angle) / 90.0))
                    for _ in range(abs(y_rotations)):
                        if y_rotations > 0:
                            new_cs.RotateY(90)
                        else:
                            new_cs.RotateY(-90)
                    safe_print("SUCCESS: Applied Y rotation: {} degrees ({} x 90)".format(y_angle, y_rotations))
                    rotations_applied += 1

                if abs(float(z_angle)) > 1e-6:
                    z_rotations = int(round(float(z_angle) / 90.0))
                    for _ in range(abs(z_rotations)):
                        if z_rotations > 0:
                            new_cs.RotateZ(90)
                        else:
                            new_cs.RotateZ(-90)
                    safe_print("SUCCESS: Applied Z rotation: {} degrees ({} x 90)".format(z_angle, z_rotations))
                    rotations_applied += 1
                
                if rotations_applied == 0:
                    safe_print("INFO: No rotation required for this orientation")
                
                safe_print("SUCCESS: Collision Point updated to: X={:.3f}, Y={:.3f}, Z={:.3f} mm with rotations [X:{}, Y:{}, Z:{}]".format(
                    new_point_mm[0], new_point_mm[1] - gap_distance, new_point_mm[2], x_angle, y_angle, z_angle))

                return new_cs
                                
            except Exception as e:
                safe_print("ERROR: Failed to update coordinate system transformations: {}".format(e))
                return collision_cs  
    
    def CreateGroundConstructionGeometry(collision_cs, ground_size_mm, shell_info, scale_factor=1.5):
        existing_construction = None
        for child in Model.Children:
            if hasattr(child, 'Name') and child.Name == "Scr_Ground_Construction":
                existing_construction = child
                break
        
        with Transaction(True):
            if existing_construction is None:
                construction = Model.AddConstructionGeometry()
                construction.Name = "Scr_Ground_Construction"
            else:
                construction = existing_construction

            for child in construction.Children:
                if hasattr(child, 'Name') and child.Name == "Scr_ground":
                    child.Delete()

            solid = construction.AddSolid()
            solid.Name = "Scr_ground"
            solid.CoordinateSystem = collision_cs

            y_offset = 0.0
            if shell_info and shell_info['is_shell'] and shell_info['thickness']:
                thickness_mm = shell_info['thickness'] * 1000
                y_offset = -thickness_mm / 2.0
                safe_print("SUCCESS: Shell detected with thickness {:.3f}mm, applying Y-offset: {:.3f}mm".format(
                    thickness_mm, y_offset))

            final_ground_size = ground_size_mm * scale_factor
            ground_thickness = 5.0
            
            solid.X1 = Quantity(str(final_ground_size/2) + " [mm]")
            solid.X2 = Quantity(str(-final_ground_size/2) + " [mm]")
            solid.Y1 = Quantity(str(y_offset) + " [mm]")
            solid.Y2 = Quantity(str(-ground_thickness + y_offset) + " [mm]")
            solid.Z1 = Quantity(str(final_ground_size/2) + " [mm]")
            solid.Z2 = Quantity(str(-final_ground_size/2) + " [mm]")

            solid.AddGeometry()
            
            safe_print("SUCCESS: Ground construction created - Size: {:.1f}mm, Y-offset: {:.3f}mm".format(
                final_ground_size, y_offset))

            try:
                construction.UpdateSolids()
            except Exception as e:
                safe_print("Warning during ground construction update: " + str(e))
            
            return construction

    def UpdateGroundGeometry(ground_construction, collision_cs, ground_size_mm, shell_info, scale_factor=1.5):
        with Transaction(True):
            ground_solid = None
            for child in ground_construction.Children:
                if hasattr(child, 'Name') and child.Name == "Scr_ground":
                    ground_solid = child
                    break
            
            if ground_solid is None:
                safe_print("ERROR: Ground solid not found for update")
                return False

            y_offset = 0.0
            if shell_info and shell_info['is_shell'] and shell_info['thickness']:
                thickness_mm = shell_info['thickness'] * 1000
                y_offset = -thickness_mm / 2.0
                safe_print("SUCCESS: Shell detected with thickness {:.3f}mm, applying Y-offset: {:.3f}mm".format(
                    thickness_mm, y_offset))

            final_ground_size = ground_size_mm * scale_factor
            ground_thickness = 5.0

            ground_solid.CoordinateSystem = collision_cs

            ground_solid.X1 = Quantity(str(final_ground_size/2) + " [mm]")
            ground_solid.X2 = Quantity(str(-final_ground_size/2) + " [mm]")
            ground_solid.Y1 = Quantity(str(y_offset) + " [mm]")
            ground_solid.Y2 = Quantity(str(-ground_thickness + y_offset) + " [mm]")
            ground_solid.Z1 = Quantity(str(final_ground_size/2) + " [mm]")
            ground_solid.Z2 = Quantity(str(-final_ground_size/2) + " [mm]")

            try:
                ground_solid.DeleteGeometry()
                ground_solid.AddGeometry()
                safe_print("INFO: Ground geometry recreated to ensure position update")
            except Exception as e:
                safe_print("WARNING: DeleteGeometry/AddGeometry failed: {}".format(e))
                try:
                    ground_solid.Generate()
                    safe_print("INFO: Ground geometry regenerated")
                except Exception as e2:
                    safe_print("WARNING: Generate method also failed: {}".format(e2))
            
            safe_print("SUCCESS: Ground geometry updated - Size: {:.1f}mm, Y-offset: {:.3f}mm".format(
                final_ground_size, y_offset))

            try:
                ground_construction.UpdateSolids()
                safe_print("INFO: Construction solids updated")
            except Exception as e:
                safe_print("WARNING: UpdateSolids failed: {}".format(e))

            try:
                DataModel.Tree.Refresh()
                safe_print("INFO: Model tree refreshed")
            except Exception as e:
                safe_print("WARNING: Tree refresh failed: {}".format(e))

            try:
                ground_construction.UpdateAllSolids()  
                safe_print("INFO: All solids updated")
            except Exception as e:
                safe_print("INFO: UpdateAllSolids not available or failed: {}".format(e))
            
            return True

    def SetScrGroundRigid():
        try:
            DataModel.Tree.Refresh()

            with Transaction(True):
                ground_body = None

                geometry = Model.Geometry
                for part in geometry.Children:
                    for body in part.Children:
                        if hasattr(body, "Name") and body.Name == "Scr_ground":
                            ground_body = body
                            break
                    if ground_body:
                        break

                if ground_body is None:
                    safe_print("ERROR: Scr_ground not found in Model.Geometry")
                    return False

                ground_body.StiffnessBehavior = StiffnessBehavior.Rigid
                safe_print("SUCCESS: Scr_ground stiffness set to Rigid")
                return True

        except Exception as e:
            safe_print("ERROR: Failed setting Rigid stiffness: " + str(e))
            return False

    def AssignMaterialToScrGround():
        try:
            DataModel.Tree.Refresh()

            with Transaction(True):
                structural_steel = None
                for mat in ExtAPI.DataModel.Project.Model.Materials.Children:
                    if mat.Name == "Structural Steel":
                        structural_steel = mat
                        break

                if structural_steel is None:
                    structural_steel = ExtAPI.DataModel.Project.Model.Materials.AddMaterial()
                    structural_steel.Name = "Structural Steel"
                    try:
                        structural_steel.Properties["Young's Modulus"] = "200000 [MPa]"
                        structural_steel.Properties["Poisson's Ratio"] = "0.3"
                        structural_steel.Properties["Density"] = "7850 [kg m^-3]"
                    except:
                        pass
                    safe_print("SUCCESS: Created Structural Steel material")

                ground_body = None
                for assembly in ExtAPI.DataModel.GeoData.Assemblies:
                    for part in assembly.Parts:
                        for body in part.Bodies:
                            if body.Name == "Scr_ground":
                                ground_body = body
                                break
                        if ground_body:
                            break
                    if ground_body:
                        break

                if ground_body is None:
                    safe_print("ERROR: Scr_ground not found for material assignment")
                    return False

                material_assignment = ExtAPI.DataModel.Project.Model.Materials.AddMaterialAssignment()
                material_assignment.Material = structural_steel.Name
                sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
                sel.Entities = [ground_body]
                material_assignment.Location = sel

                safe_print("SUCCESS: Assigned Structural Steel to Scr_ground")
                return True

        except Exception as e:
            safe_print("ERROR: AssignMaterialToScrGround failed: " + str(e))
            return False

    def CreateGroundNamedSelection():
        try:
            DataModel.Tree.Refresh()
            
            AllNS = GetAllNamedSelections()
            existing_ns = None
            for ns in AllNS:
                if hasattr(ns, 'Name') and ns.Name == "Scr_Ground":
                    existing_ns = ns
                    break
            
            with Transaction(True):
                if existing_ns is None:
                    ns = ExtAPI.DataModel.Project.Model.AddNamedSelection()
                    ns.Name = "Scr_Ground"
                else:
                    ns = existing_ns
                    ns.Ids = []
                
                ns.ScopingMethod = GeometryDefineByType.Worksheet

                ground_body = None
                for assembly in ExtAPI.DataModel.GeoData.Assemblies:
                    for part in assembly.Parts:
                        for body in part.Bodies:
                            if body.Name == "Scr_ground":
                                ground_body = body
                                break
                        if ground_body:
                            break
                    if ground_body:
                        break
                
                if ground_body is not None:
                    selection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
                    selection.Entities = [ground_body]
                    ns.Location = selection
                    safe_print("SUCCESS: Ground named selection created")
                    return ns
                else:
                    safe_print("WARNING: Ground body not found for named selection")
                    return None
                    
        except Exception as e:
            safe_print("ERROR: Failed creating ground named selection: " + str(e))
            return None

    def CreateNamedSelectionIfMissing(ns_name):
        try:
            AllNS = GetAllNamedSelections()

            for ns in AllNS:
                if hasattr(ns, 'Name') and ns.Name.ToLower() == ns_name.ToLower():
                    safe_print("Named selection already exists: " + ns_name)
                    return ns

            safe_print("Creating missing named selection: " + ns_name)
            
            with Transaction(True):
                try:
                    new_ns = Model.AddNamedSelection()
                    new_ns.Name = ns_name
                    new_ns.ScopingMethod = GeometryDefineByType.Worksheet

                    if ns_name.ToLower() == "scr_all_bodies":
                        try:
                            bodies_to_select = GetAllUnsuppressedBodies()
                            
                            if len(bodies_to_select) > 0:
                                selection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
                                selection.Entities = bodies_to_select
                                new_ns.Location = selection
                                safe_print("Named selection created with " + str(len(bodies_to_select)) + " bodies")
                        except Exception as e:
                            safe_print("Warning: Could not auto-populate named selection: " + str(e))
                    
                    DataModel.Tree.Refresh()
                    return new_ns
                    
                except Exception as e:
                    safe_print("Error creating named selection: " + str(e))
                    return None
                    
        except Exception as e:
            safe_print("Error in CreateNamedSelectionIfMissing: " + str(e))
            return None

    def GetAllUnsuppressedBodies():
        try:
            all_bodies = []
            for assembly in ExtAPI.DataModel.GeoData.Assemblies:
                for part in assembly.Parts:
                    for body in part.Bodies:
                        try:
                            if not body.Suppressed and "ground" not in body.Name.ToLower():
                                test_bb = body.GetBoundingBox()
                                if (test_bb is not None and 
                                    not math.isnan(test_bb.Min.X) and not math.isnan(test_bb.Max.X) and
                                    not math.isnan(test_bb.Min.Y) and not math.isnan(test_bb.Max.Y) and
                                    not math.isnan(test_bb.Min.Z) and not math.isnan(test_bb.Max.Z)):
                                    all_bodies.append(body)
                        except Exception as e:
                            continue
            
            safe_print("Total valid bodies found: " + str(len(all_bodies)))
            return all_bodies
        except Exception as e:
            safe_print("Error getting unsuppressed bodies: " + str(e))
            return []

    def AddMeshSizingToScrGround(mesh_size_mm=10.0):
        try:
            DataModel.Tree.Refresh()

            ground_ns = None
            try:
                AllNS = GetAllNamedSelections()
                for ns in AllNS:
                    if hasattr(ns, 'Name') and ns.Name == "Scr_Ground":
                        ground_ns = ns
                        break
            except:
                pass

            if ground_ns is None:
                ground_ns = CreateGroundNamedSelection()
                if ground_ns is None:
                    safe_print("ERROR: Cannot create Scr_Ground named selection")
                    return False

            with Transaction(True):
                sizing = None
                try:
                    for mc in Model.Mesh.Children:
                        if hasattr(mc, "Name") and mc.Name == "Scr_Ground_Sizing":
                            sizing = mc
                            break
                except:
                    pass

                if sizing is None:
                    sizing = Model.Mesh.AddSizing()
                    sizing.Name = "Scr_Ground_Sizing"

                sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
                sel.Ids = ground_ns.Ids
                sizing.Location = sel

                sizing.ElementSize = Quantity(str(mesh_size_mm) + " [mm]")

                try:
                    sizing.Behavior = SizingBehavior.Hard
                except:
                    pass

            safe_print("SUCCESS: Scr_ground mesh sizing set to {:.1f} mm".format(mesh_size_mm))
            return True
        except Exception as e:
            safe_print("ERROR: AddMeshSizingToScrGround failed: " + str(e))
            return False

    def SetupBoundaryConditions(face_name, collision_cs):
        AllNS = GetAllNamedSelections()
        
        existing_ics = []
        if hasattr(analysis, 'InitialConditions') and analysis.InitialConditions:
            try:
                for item in analysis.InitialConditions:
                    if hasattr(item, 'Name') and item.Name:
                        existing_ics.append(item.Name.lower())
            except Exception:
                pass

        existing_conditions = []
        if hasattr(analysis, 'Children') and analysis.Children:
            try:
                for item in analysis.Children:
                    if hasattr(item, 'Name') and item.Name:
                        existing_conditions.append(item.Name.lower())
            except Exception:
                pass
        
        with Transaction(True):
            if hasattr(analysis, 'Solution') and hasattr(analysis.Solution, 'Activate'):
                analysis.Solution.Activate()

            drop_height_name = "Scr_Drop_height_" + face_name
            drop_height_ic = None

            if drop_height_name.lower() in existing_ics:
                try:
                    for item in analysis.InitialConditions:
                        if hasattr(item, 'Name') and item.Name.lower() == drop_height_name.lower():
                            drop_height_ic = item
                            break
                except Exception:
                    pass

            if drop_height_ic is None:
                # Locate initial conditions container under current analysis
                ic_group = None
                if hasattr(analysis, 'InitialConditions'):
                    if hasattr(analysis.InitialConditions, 'InsertDropHeight'):
                        ic_group = analysis.InitialConditions

                if ic_group is None and hasattr(analysis, 'Children'):
                    for child in analysis.Children:
                        c_name = str(getattr(child, 'Name', '')).lower()
                        c_type = str(child.GetType().Name if hasattr(child, 'GetType') else type(child).__name__).lower()
                        if 'initial' in c_name or 'initialcondition' in c_type:
                            if hasattr(child, 'InsertDropHeight'):
                                ic_group = child
                                break

                # Bounded fallback to model lookup checking analysis ownership
                if ic_group is None:
                    try:
                        found_ics = ExtAPI.DataModel.GetObjectsByName("Initial Conditions")
                        if found_ics and len(found_ics) > 0:
                            for candidate in found_ics:
                                parent_obj = getattr(candidate, 'Parent', None)
                                if parent_obj is not None and parent_obj == analysis:
                                    ic_group = candidate
                                    break
                            if ic_group is None:
                                ic_group = found_ics[0]
                    except Exception as ex_ic:
                        safe_print("Warning locating Initial Conditions by name: " + str(ex_ic))

                if ic_group is not None and hasattr(ic_group, 'InsertDropHeight'):
                    drop_height_ic = ic_group.InsertDropHeight()
                elif hasattr(analysis, 'AddDropHeight'):
                    drop_height_ic = analysis.AddDropHeight()
                else:
                    safe_print("ERROR: Cannot insert drop height initial condition under analysis")

            if drop_height_ic is not None:
                drop_height_ic.Name = drop_height_name
                
                try:
                    drop_height_value = float(Drop_height)
                    drop_height_str = "{:.3f} [mm]".format(drop_height_value)
                    drop_height_ic.DropHeight = Quantity(drop_height_str)
                except Exception as e:
                    safe_print("ERROR: Drop height format issue: {}".format(e))

                try:
                    drop_height_ic.DropDirection = DropDirection.NegativeY
                except Exception:
                    pass

                if collision_cs:
                    drop_height_ic.CoordinateSystem = collision_cs

                for ns in AllNS:
                    if hasattr(ns, 'Name') and ns.Name.lower() == "scr_all_bodies":
                        selection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
                        selection.Ids = ns.Ids
                        drop_height_ic.Location = selection
                        break

            gravity_name = "Scr_EarthGravity_" + face_name
            gravity = None
            if gravity_name.lower() in existing_conditions:
                try:
                    for child in analysis.Children:
                        if hasattr(child, 'Name') and child.Name.lower() == gravity_name.lower():
                            gravity = child
                            break
                except Exception:
                    pass

            if gravity is None:
                gravity = analysis.AddEarthGravity()
            
            gravity.Name = gravity_name
            try:
                gravity.Direction = GravityOrientationType.NegativeYAxis
            except Exception:
                pass

            if collision_cs:
                gravity.CoordinateSystem = collision_cs

            fs_name = "Scr_FixedSupport_" + face_name
            ground_ns = None
            for ns in AllNS:
                if hasattr(ns, 'Name') and ns.Name == "Scr_Ground":
                    ground_ns = ns
                    break
            
            if ground_ns is not None:
                fs = None
                if fs_name.lower() in existing_conditions:
                    try:
                        for child in analysis.Children:
                            if hasattr(child, 'Name') and child.Name.lower() == fs_name.lower():
                                fs = child
                                break
                    except Exception:
                        pass

                if fs is None:
                    fs = analysis.AddFixedSupport()
                
                fs.Name = fs_name
                selection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
                selection.Ids = ground_ns.Ids
                fs.Location = selection
                safe_print("SUCCESS: Fixed support applied to ground for {}".format(face_name))
            else:
                safe_print("WARNING: Ground named selection not found, cannot apply fixed support")

    def SuppressOtherBoundaryConditions(current_face_name):
        with Transaction(True):
            if hasattr(analysis, 'InitialConditions') and analysis.InitialConditions:
                for i in analysis.InitialConditions:
                    if hasattr(i, 'Name') and i.Name.startswith("Scr_Drop_height_"):
                        i.Suppressed = (i.Name != "Scr_Drop_height_" + current_face_name)
            if hasattr(analysis, 'Children') and analysis.Children:
                for i in analysis.Children:
                    if hasattr(i, 'Name'):
                        if i.Name.startswith("Scr_EarthGravity_"):
                            i.Suppressed = (i.Name != "Scr_EarthGravity_" + current_face_name)
                        elif i.Name.startswith("Scr_FixedSupport_"):
                            i.Suppressed = (i.Name != "Scr_FixedSupport_" + current_face_name)            
            DataModel.Tree.Refresh()

    def ProcessSingleDropFaceOptimized(face_config, all_collision_points, collision_cs, ground_construction, is_first_face):
        face_name = face_config['name']
        face_orientation = face_config['orientation']
        
        if face_name not in all_collision_points:
            safe_print("ERROR: No collision point data for face: {}".format(face_name))
            return collision_cs  
            
        collision_data = all_collision_points[face_name]
        collision_point = collision_data['collision_point']
        ground_size = collision_data['ground_size']
        
        safe_print("="*80)
        safe_print("SUCCESS: Processing drop face: {} (Theoretical calculation)".format(face_name))
        safe_print("  Collision point: X={:.3f}, Y={:.3f}, Z={:.3f} mm".format(
            collision_point[0], collision_point[1], collision_point[2]))
        safe_print("  Ground size: {:.1f} mm".format(ground_size))
        safe_print("  Target rotation: [X:{}, Y:{}, Z:{}]".format(
            face_config['rotation'][0], face_config['rotation'][1], face_config['rotation'][2]))
        safe_print("="*80)

        try:
            safe_print("INFO: Detecting shell properties for face: {}".format(face_name))
            shell_info = detect_shell_at_collision_face("Scr_All_Bodies", face_name, collision_data)

            safe_print("INFO: Updating collision point coordinate system for face: {}".format(face_name))
            updated_cs = UpdateCollisionPointCoordinateSystem(collision_cs, collision_point, face_config['rotation'], face_name)

            if updated_cs != collision_cs:
                collision_cs = updated_cs

            safe_print("INFO: Updating ground geometry for face: {}".format(face_name))
            if is_first_face:
                try:
                    ground_construction.UpdateSolids()
                except:
                    pass
            
            update_success = UpdateGroundGeometry(ground_construction, collision_cs, ground_size, shell_info)
            if not update_success:
                safe_print("ERROR: Failed to update ground geometry for face: {}".format(face_name))
                return collision_cs

            if is_first_face:
                safe_print("INFO: Setting up ground properties (first face only)")
                SetScrGroundRigid()
                AssignMaterialToScrGround()
                CreateGroundNamedSelection()
                AddMeshSizingToScrGround(10.0)
                
            safe_print("INFO: Setting up boundary conditions for face: {}".format(face_name))
            SetupBoundaryConditions(face_name, collision_cs)

            SuppressOtherBoundaryConditions(face_name)

            if Outputkfile:
                safe_print("INFO: Outputting K file for face: {}".format(face_name))
                try:
                    if not os.path.exists(kfile_dir):
                        os.makedirs(kfile_dir)
                    
                    face_dir = os.path.join(kfile_dir, face_name)
                    if not os.path.exists(face_dir):
                        os.makedirs(face_dir)
                    
                    kfile_path = os.path.join(face_dir, face_name + ".k")
                    analysis.WriteInputFile(kfile_path)
                    safe_print("SUCCESS: K file written to: {}".format(kfile_path))
                    
                except Exception as e:
                    safe_print("ERROR: Failed to write K file for {}: {}".format(face_name, e))

            safe_print("SUCCESS: Completed processing for face: {}".format(face_name))
            return collision_cs
            
        except Exception as e:
            safe_print("ERROR: Exception in ProcessSingleDropFaceOptimized for {}: {}".format(face_name, e))
            return collision_cs
        
    def GenerateMeshOnce():
        safe_print("INFO: Generating mesh (final operation)...")
        try:
            ExtAPI.DataModel.Project.Model.Mesh.Update()
            safe_print("SUCCESS: Final mesh generation completed")
        except Exception as e:
            safe_print("ERROR: Final mesh generation failed: {}".format(e))

    def Main(args):
        global analysis, analysis_settings

        def _is_lsdyna_candidate(an_obj):
            if an_obj is None:
                return False
            try:
                for attr_name in ['SystemType', 'AnalysisType', 'PhysicsType']:
                    if hasattr(an_obj, attr_name):
                        val = str(getattr(an_obj, attr_name)).upper()
                        if 'LSDYNA' in val or 'EXPLICIT' in val or 'DYNA' in val:
                            return True

                if hasattr(an_obj, 'Solver'):
                    solver_obj = getattr(an_obj, 'Solver')
                    if solver_obj is not None:
                        solver_name = str(getattr(solver_obj, 'Name', '')).upper()
                        solver_type = str(getattr(solver_obj, 'SolverType', '')).upper()
                        if 'LSDYNA' in solver_name or 'EXPLICIT' in solver_name or 'DYNA' in solver_name:
                            return True
                        if 'LSDYNA' in solver_type or 'EXPLICIT' in solver_type or 'DYNA' in solver_type:
                            return True

                if hasattr(an_obj, 'Properties'):
                    for prop in an_obj.Properties:
                        try:
                            prop_val = str(getattr(prop, 'StringValue', getattr(prop, 'Value', ''))).upper()
                            prop_name = str(getattr(prop, 'Name', '')).upper()
                            if 'LSDYNA' in prop_val or 'EXPLICIT' in prop_val or 'DYNA' in prop_val:
                                return True
                            if ('SOLVER' in prop_name or 'PHYSICS' in prop_name) and ('DYNA' in prop_val or 'EXPLICIT' in prop_val):
                                return True
                        except Exception:
                            pass

                obj_name = str(getattr(an_obj, 'Name', '')).upper()
                if 'LSDYNA' in obj_name or 'LS-DYNA' in obj_name or 'EXPLICIT' in obj_name:
                    return True
            except Exception:
                pass
            return False

        def _locate_all_analyses():
            results = []
            try:
                if 'ExtAPI' in globals() and hasattr(ExtAPI, 'DataModel'):
                    proj = getattr(ExtAPI.DataModel, 'Project', None)
                    if proj and hasattr(proj, 'Model') and hasattr(proj.Model, 'Analyses'):
                        results = list(proj.Model.Analyses)
            except Exception:
                pass
            if not results:
                try:
                    if 'Model' in globals() and hasattr(Model, 'Analyses'):
                        results = list(Model.Analyses)
                except Exception:
                    pass
            if not results:
                try:
                    if 'DataModel' in globals() and hasattr(DataModel, 'Project'):
                        results = list(DataModel.Project.Model.Analyses)
                except Exception:
                    pass
            return results

        target_analysis = None

        # Inspect active tree object safely
        try:
            actobj = None
            if 'Tree' in globals() and hasattr(Tree, 'FirstActiveObject'):
                actobj = Tree.FirstActiveObject
            elif 'ExtAPI' in globals() and hasattr(ExtAPI, 'DataModel') and hasattr(ExtAPI.DataModel, 'Tree'):
                actobj = ExtAPI.DataModel.Tree.FirstActiveObject

            curr_obj = actobj
            max_levels = 10
            level = 0
            while curr_obj is not None and level < max_levels:
                type_str = str(curr_obj.GetType().Name if hasattr(curr_obj, 'GetType') else type(curr_obj).__name__)
                if 'Analysis' in type_str:
                    if _is_lsdyna_candidate(curr_obj):
                        target_analysis = curr_obj
                        break
                curr_obj = getattr(curr_obj, 'Parent', None)
                level += 1
        except Exception as ex_tree:
            safe_print("Warning while inspecting active tree object: " + str(ex_tree))

        # Fallback to model analyses scan
        if target_analysis is None:
            all_analyses = _locate_all_analyses()
            for cand in all_analyses:
                if _is_lsdyna_candidate(cand):
                    target_analysis = cand
                    break

            if target_analysis is None and len(all_analyses) == 1:
                if _is_lsdyna_candidate(all_analyses[0]):
                    target_analysis = all_analyses[0]

        # Guard against missing LS-DYNA analysis
        if target_analysis is None:
            warning_text = (
                "No LS-DYNA analysis environment found in the current model.\n\n"
                "Please select or create an LS-DYNA analysis system before running this automation."
            )
            safe_print("ERROR: " + warning_text)
            print("Error: " + warning_text)
            try:
                print("[UI_OUTPUT] " + str(
                    warning_text,
                    "LS-DYNA Analysis Required",
                    System.Windows.Forms.MessageBoxButtons.OK,
                    System.Windows.Forms.MessageBoxIcon.Warning
                ))
            except Exception:
                pass
            return

        analysis = target_analysis
        safe_print("SUCCESS: Bound to target LS-DYNA analysis: " + str(getattr(analysis, 'Name', 'Analysis')))

        # Resolve Analysis Settings
        analysis_settings = getattr(analysis, 'AnalysisSettings', None)
        if analysis_settings is None:
            try:
                for ch in getattr(analysis, 'Children', []):
                    ch_name = str(getattr(ch, 'Name', ''))
                    if 'Analysis Settings' in ch_name:
                        analysis_settings = ch
                        break
            except Exception:
                pass

        if analysis_settings is None:
            safe_print("WARNING: Analysis Settings object could not be resolved directly.")
        else:
            safe_print("SUCCESS: Analysis Settings resolved: " + str(getattr(analysis_settings, 'Name', 'Analysis Settings')))

        try:
            safe_print("="*100)
            safe_print("STARTING OPTIMIZED DROP TEST AUTOMATION SETUP")
            safe_print("="*100)

            scr_all_bodies_ns = CreateNamedSelectionIfMissing("Scr_All_Bodies")
            if scr_all_bodies_ns is None:
                err_ns = 'Cannot create or find "Scr_All_Bodies" named selection.'
                safe_print("ERROR: " + err_ns)
                print('Error: ' + err_ns)
                try:
                    print("[UI_OUTPUT] " + str(
                        err_ns,
                        "Drop Test Automation Error",
                        System.Windows.Forms.MessageBoxButtons.OK,
                        System.Windows.Forms.MessageBoxIcon.Error
                    ))
                except Exception:
                    pass
                return

            freeze_success = FreezeMeshForNamedSelection("Scr_All_Bodies")
            if not freeze_success:
                safe_print("WARNING: Mesh freezing failed, continuing anyway...")

            original_bbox_data = get_named_selection_bounding_box("Scr_All_Bodies")
            if original_bbox_data is None:
                err_bb = 'Cannot get bounding box for "Scr_All_Bodies".'
                safe_print("ERROR: " + err_bb)
                print('Error: ' + err_bb)
                try:
                    print("[UI_OUTPUT] " + str(
                        err_bb,
                        "Drop Test Automation Error",
                        System.Windows.Forms.MessageBoxButtons.OK,
                        System.Windows.Forms.MessageBoxIcon.Error
                    ))
                except Exception:
                    pass
                return

            all_collision_points = calculate_rotated_collision_points(original_bbox_data)
            if all_collision_points is None:
                err_cp = 'Cannot calculate collision points.'
                safe_print("ERROR: " + err_cp)
                print('Error: ' + err_cp)
                try:
                    print("[UI_OUTPUT] " + str(
                        err_cp,
                        "Drop Test Automation Error",
                        System.Windows.Forms.MessageBoxButtons.OK,
                        System.Windows.Forms.MessageBoxIcon.Error
                    ))
                except Exception:
                    pass
                return

            first_face = Drop_faces[0]
            first_collision_point = all_collision_points[first_face['name']]['collision_point']
            collision_cs = CreateCollisionPointCoordinateSystem(first_collision_point, first_face['name'])

            first_ground_size = all_collision_points[first_face['name']]['ground_size']
            first_shell_info = detect_shell_at_collision_face("Scr_All_Bodies", first_face['name'], all_collision_points[first_face['name']])
            ground_construction = CreateGroundConstructionGeometry(collision_cs, first_ground_size, first_shell_info)

            processed_faces = []
            for i, face_config in enumerate(Drop_faces):
                if face_config['enabled']:
                    is_first_face = (i == 0)  
                    ProcessSingleDropFaceOptimized(
                        face_config, 
                        all_collision_points, 
                        collision_cs, 
                        ground_construction, 
                        is_first_face
                    )
                    processed_faces.append(face_config['name'])

            if len(processed_faces) == 0:
                warn_faces = 'No drop faces are enabled.'
                safe_print("WARNING: " + warn_faces)
                print('Warning: ' + warn_faces)
                try:
                    print("[UI_OUTPUT] " + str(
                        warn_faces,
                        "Drop Test Automation",
                        System.Windows.Forms.MessageBoxButtons.OK,
                        System.Windows.Forms.MessageBoxIcon.Warning
                    ))
                except Exception:
                    pass
                return

            unfreeze_success = UnfreezeMeshForNamedSelection("Scr_All_Bodies")
            if not unfreeze_success:
                safe_print("WARNING: Mesh unfreezing failed")

            GenerateMeshOnce()
            
            endTime = time.time()
            execution_time = endTime - startTime
            safe_print("="*100)
            safe_print("OPTIMIZATION SUMMARY:")
            safe_print("  - Original method: {} Part Transform rotations + {} Remesh operations".format(
                len(processed_faces), len(processed_faces)))
            safe_print("  - Optimized method: 0 Part Transform rotations + 1 Mesh operation")
            safe_print("  - Used unified collision point coordinate system and ground geometry")
            safe_print("  - Mesh frozen during processing to prevent unnecessary updates")
            safe_print("  - Time saving: Eliminated {} unnecessary rotation/remesh cycles".format(len(processed_faces)))
            safe_print("  - Processed faces: {}".format(", ".join(processed_faces)))
            safe_print("="*100)
            
            completion_msg = "Optimized Drop Test Automation completed successfully!\n"
            completion_msg += "Processed {} faces: {}\n".format(len(processed_faces), ", ".join(processed_faces))
            completion_msg += "Time saved by avoiding {} rotation/remesh cycles\n".format(len(processed_faces))
            completion_msg += "Used unified collision point and ground geometry approach\n"
            completion_msg += "Total Execution Time: {:.2f} seconds".format(execution_time)
            
            safe_print("SUCCESS: " + completion_msg)
            try:
                act_elapsed_sec = _act_time.time() - _ACT_START_TIME
                log_usage("ACT_Drop", "0915y25", act_elapsed_sec, 2700)
            except Exception:
                pass

            show_dialog = True
            if 'SHOW_DIALOGS' in globals() and not SHOW_DIALOGS:
                show_dialog = False

            if show_dialog:
                try:
                    print("[UI_OUTPUT] " + str(
                        completion_msg,
                        "Drop Test Automation Completed",
                        System.Windows.Forms.MessageBoxButtons.OK,
                        System.Windows.Forms.MessageBoxIcon.Information
                    ))
                except Exception:
                    pass
            
        except Exception as e:
            error_msg = "An error occurred during the drop test automation setup:\n" + str(e)
            safe_print("ERROR: " + error_msg)
            print(error_msg)
            try:
                print("[UI_OUTPUT] " + str(
                    error_msg,
                    "Drop Test Automation Error",
                    System.Windows.Forms.MessageBoxButtons.OK,
                    System.Windows.Forms.MessageBoxIcon.Error
                ))
            except Exception:
                pass

    expireddate = datetime.date(2035, 12, 31)
    nowdate = datetime.datetime.now()
    datedelta = nowdate.date() - expireddate

    if datedelta.days > 0:
        expired_msg = "The automation script has expired (valid through 2035-12-31). Please obtain an updated version."
        safe_print("ERROR: " + expired_msg)
        print(expired_msg)
        try:
            print("[UI_OUTPUT] " + str(
                expired_msg,
                "License Expired",
                System.Windows.Forms.MessageBoxButtons.OK,
                System.Windows.Forms.MessageBoxIcon.Warning
            ))
        except Exception:
            pass
        return

    try:
        try:
            if MechanicalUnitSystem is not None and hasattr(MechanicalUnitSystem, 'StandardNMM'):
                ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardNMM
        except Exception as unit_ex:
            safe_print("Warning applying unit system: " + str(unit_ex))

        args = [None]
        invoked = False
        try:
            if hasattr(ExtAPI.Application, 'InvokeUIThread'):
                ExtAPI.Application.InvokeUIThread(Main, args)
                invoked = True
        except Exception as ui_ex:
            safe_print("InvokeUIThread failed, falling back to direct execution: " + str(ui_ex))

        if not invoked:
            Main(args)
    except Exception as top_ex:
        top_err = "Unhandled error in drop test automation execution:\n" + str(top_ex)
        safe_print("ERROR: " + top_err)
        print(top_err)
        try:
            print("[UI_OUTPUT] " + str(
                top_err,
                "Drop Test Automation Error",
                System.Windows.Forms.MessageBoxButtons.OK,
                System.Windows.Forms.MessageBoxIcon.Error
            ))
        except Exception:
            pass