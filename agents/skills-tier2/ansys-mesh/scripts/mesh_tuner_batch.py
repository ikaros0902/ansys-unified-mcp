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

def onupdateStep(step):
    import time as _act_time
    _ACT_START_TIME = _act_time.time()
    # ACT Script: Auto optimize mesh size for Solid & Shell based on CFL timestep
    # Features:
    # - record initial (current) mesh CFL
    # - scan mesh sizes with early-stop by Criteria_MinCFLTimeStep
    # - after GenerateMesh(), check Body.ObjectState to detect success
    # - if Hex-like method fails, switch to Tetra and retry
    # - write back best mesh size to each body's Mesh Control (Sizing)
    # - final popup shows results

    import time, datetime
    import csv
    import os
    import clr
    clr.AddReference("System.Windows.Forms")
    import System.Windows.Forms
    import sys

    ###################################
    ### Inputs for script
    ###################################
    # --------------------- Config ---------------------
    '''
    NumSimultaneousMesh = 3
    Criteria_MinCFLTimeStep = 9e-7

    meshsize_min_solidbody = 1.0
    meshsize_max_solidbody = 3.0
    meshsize_delta_solidbody = 0.5

    meshsize_min_shellbody = 1.0
    meshsize_max_shellbody = 4.0
    meshsize_delta_shellbody = 0.5
    '''
    ###################################
    ### Inputs for ACT
    ###################################
    NumSimultaneousMesh = step.Properties['Number_of_Part_Process'].Value
    Criteria_MinCFLTimeStep = step.Properties['Criteria_MinCFLTimeStep'].Value

    # Tuning mode selector (Fixed / Floating / Percentage)
    mode_str = step.Properties['Option_mode_mc_tunesize'].Value
    opt = step.Properties['Option_mode_mc_tunesize']

    # Defaults (used as fallback)
    meshsize_min_solidbody = 1.0
    meshsize_max_solidbody = 3.0
    meshsize_delta_solidbody = 0.5
    meshsize_min_shellbody = 1.0
    meshsize_max_shellbody = 4.0
    meshsize_delta_shellbody = 0.5
    meshsize_offset_up = 1.0
    meshsize_offset_down = 1.0
    meshsize_upper_percentage = 1.5
    meshsize_lower_percentage = 0.7
    Diverse = 5

    def _getp(name, default):
        try:
            v = opt.Properties[name].Value
            return v if v is not None else default
        except:
            return default

    if mode_str == 'Fixed Range':
        mode_tune = 0
        meshsize_min_solidbody = _getp('meshsize_min_solidbody', meshsize_min_solidbody)
        meshsize_max_solidbody = _getp('meshsize_max_solidbody', meshsize_max_solidbody)
        meshsize_delta_solidbody = _getp('meshsize_delta_solidbody', meshsize_delta_solidbody)
        meshsize_min_shellbody = _getp('meshsize_min_shellbody', meshsize_min_shellbody)
        meshsize_max_shellbody = _getp('meshsize_max_shellbody', meshsize_max_shellbody)
        meshsize_delta_shellbody = _getp('meshsize_delta_shellbody', meshsize_delta_shellbody)
    elif mode_str == 'Floating Range':
        mode_tune = 1
        meshsize_offset_up = _getp('meshsize_offset_up', meshsize_offset_up)
        meshsize_offset_down = _getp('meshsize_offset_down', meshsize_offset_down)
        meshsize_delta_solidbody = _getp('meshsize_delta_solidbody', meshsize_delta_solidbody)
        meshsize_delta_shellbody = _getp('meshsize_delta_shellbody', meshsize_delta_shellbody)
    elif mode_str == 'Percentage Range':
        mode_tune = 2
        meshsize_upper_percentage = round(_getp('meshsize_upper_percentage', 150) / 100.0, 4)
        meshsize_lower_percentage = round(_getp('meshsize_lower_percentage', 70) / 100.0, 4)
        try:
            Diverse = int(_getp('Diverse', 5))
        except:
            Diverse = 5
        if Diverse < 2:
            Diverse = 2
    else:
        mode_tune = 0



    # --------------------- Global containers ---------------------
    list_CFL = []              # ?body ??CFL ? (list of lists)
    list_MC = []               # ?body ??mesh-size ? (list of lists)
    list_best_meshsize = []    # ?body ???mesh size
    list_body_names = []       # ? body ????

    # --------------------- Helper functions ---------------------
    def chunk(lst, n):
        """chunk list"""
        return [lst[i:i + n] for i in range(0, len(lst), n)]

    def classify_bodies():
        """  bodies   solid_bodies   shell_bodies"""
        SOLID_BODIES = []
        SHELL_BODIES = []
        for body in ExtAPI.DataModel.Project.Model.Geometry.GetChildren(DataModelObjectCategory.Body, True):
            if body.Suppressed:
                continue
            geo_body = body.GetGeoBody()
            t = geo_body.BodyType.ToString()
            if t == "GeoBodySolid":
                SOLID_BODIES.append(body)
            elif t == "GeoBodySheet":
                SHELL_BODIES.append(body)
        return SOLID_BODIES, SHELL_BODIES

    def classify_bodies_by_select(body_select):
        """  bodies   solid_bodies   shell_bodies"""
        SOLID_BODIES = []
        SHELL_BODIES = []
        for body in body_select:
            if body.Suppressed:
                continue
            geo_body = body.GetGeoBody()
            t = geo_body.BodyType.ToString()
            if t == "GeoBodySolid":
                SOLID_BODIES.append(body)
            elif t == "GeoBodySheet":
                SHELL_BODIES.append(body)
        return SOLID_BODIES, SHELL_BODIES

    def find_geo_meshcontrols(geo, toBody=True, toFace=True, toEdge=True, skipSuppressed=True):
        """???geo ????Mesh Controls (Sizing / Method)"""
        BodyIDs = [geo.Id]
        FaceIDs = [face.Id for face in geo.Faces]
        EdgeIDs = [edge.Id for edge in geo.Edges]
        AllGeoIDs = []
        if toBody: AllGeoIDs.extend(BodyIDs)
        if toFace: AllGeoIDs.extend(FaceIDs)
        if toEdge: AllGeoIDs.extend(EdgeIDs)

        AllMeshCtrl = ExtAPI.DataModel.Project.Model.Mesh.Children
        res = []
        for iMC in AllMeshCtrl:
            #  grouping folder
            try:
                if iMC.GetType() == Ansys.ACT.Automation.Mechanical.TreeGroupingFolder:
                    continue
            except:
                pass
            try:
                # iMC.Location.Ids ??????? try
                if hasattr(iMC, "Location") and iMC.Location and hasattr(iMC.Location, "Ids"):
                    if set(iMC.Location.Ids) & set(AllGeoIDs):
                        if skipSuppressed:
                            if not getattr(iMC, "Suppressed", False):
                                res.append(iMC)
                        else:
                            res.append(iMC)
            except:
                pass
        return res

    def CFLTimeStepCalcbybody(bodyId):
        """? LSDYNA TimeStepCalc object ??body?? object ( Activate/Import)"""
        CFL_obj = ExtAPI.DataModel.CreateObject("TimeStepCalc", 'LSDYNA')
        CFL_obj.Properties["Time Step Safety Factor"].Value = 0.9
        CFL_obj.Properties["Linear Viscosity Coefficient"].Value = 0.06
        sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
        sel.Ids = [bodyId]
        CFL_obj.Properties['Geometry/DefineBy/Geo'].Value = sel
        return CFL_obj

    def deleteCFL(CFLid):
        """???? TimeStepCalc object"""
        with Transaction(True):
            try:
                obj = DataModel.GetObjectById(CFLid)
                DataModel.Remove(obj)
            except:
                pass

    def suppress_others_except(group, all_bodies):
        """????group ??bodies  suppressed"""
        with Transaction(True):
            for body in all_bodies:
                body.Suppressed = (body not in group)

    def prepare_mesh_controls(group, body_type):
        list_mc = []
        list_sizing_history = []
        for body in group:
            geo = body.GetGeoBody()
            mcs = find_geo_meshcontrols(geo, True, True, True, True)
            sizing = None
            method = None
            for mc in mcs:
                if isinstance(mc, Ansys.ACT.Automation.Mechanical.MeshControls.Sizing):
                    sizing = mc
                elif isinstance(mc, Ansys.ACT.Automation.Mechanical.MeshControls.AutomaticMethod):
                    method = mc
            if body_type == "solid":
                list_mc.append((sizing, method))
            else:
                list_mc.append((sizing,))
            list_sizing_history.append([sizing.ElementSize if sizing else None])
        return list_mc, list_sizing_history

    def adjust_mesh_size(mesh_ctrls, size):
        """??sizing ?????size (mm)"""
        with Transaction(True):
            for mc_tuple in mesh_ctrls:
                sizing = mc_tuple[0]
                if sizing is not None:
                    try:
                        sizing.ElementSize = Quantity(size, 'mm')
                    except:
                        try:
                            sizing.ElementSize = size
                        except:
                            pass

    def evaluate_cfl(group):
        """
        ??TimeStepCalc ? group ???body ??Minimum CFL value?
        ? list (??? group)
        """
        cfl_values = []
        for body in group:
            # ??body ??? meshed???0? None?
            if body.ObjectState != ObjectState.Meshed and body.ObjectState != ObjectState.Ready:
                cfl_values.append(0.0)
                continue
            # ? TimeStepCalc ??
            cfl_obj = CFLTimeStepCalcbybody(body.GetGeoBody().Id)
            cfl_obj.Activate()
            cfl_obj.NotifyChange()
            cfl_obj.Import()

            try:
                val = cfl_obj.Properties['Minimum CFL value'].Value
                cfl_values.append(round(val, 10))
            except:
                cfl_values.append(0.0)
            deleteCFL(cfl_obj.ObjectId)
        return cfl_values

    def evaluate_cfl_fast(group):
        """
        Reuse a single TimeStepCalc object to evaluate CFL for multiple bodies.
        This avoids repeated object creation/destruction.
        """
        cfl_values = []
        # ??CFL ??
        cfl_obj = ExtAPI.DataModel.CreateObject("TimeStepCalc", 'LSDYNA')
        cfl_obj.Properties["Time Step Safety Factor"].Value = 0.9
        cfl_obj.Properties["Linear Viscosity Coefficient"].Value = 0.06

        sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)

        for body in group:
            if body.ObjectState != ObjectState.Meshed:
                cfl_values.append(0.0)
                continue

            try:
                # ? selection
                sel.Ids = [body.GetGeoBody().Id]
                cfl_obj.Properties['Geometry/DefineBy/Geo'].Value = sel

                # ??
                cfl_obj.Activate()
                cfl_obj.NotifyChange()
                cfl_obj.Import()

                # ??
                val = cfl_obj.Properties['Minimum CFL value'].Value
                cfl_values.append(round(val, 10) if val is not None else 0.0)

            except:
                cfl_values.append(0.0)

        # ??
        with Transaction(True):
            try:
                DataModel.Remove(cfl_obj)
            except:
                pass

        return cfl_values


    def try_generate_mesh_with_objectstate_check(group, mesh_ctrls):
        """
        ? GenerateMesh()????body ??ObjectState ????
        ???solid ??method ??Hex-like ???body ??ObjectState ??
        ???body's method ?? Tetra ??
        ? (success, switched_index_list)
          - success: True/False?? Tetra ????
          - switched_index_list: ?? body ?? Hex->Tetra ???log?
        """
        switched = []
        # ??????generate
        ExtAPI.DataModel.Project.Model.Mesh.ClearGeneratedData()
        ExtAPI.DataModel.Project.Model.Mesh.GenerateMesh()

        # ?body ??ObjectState??? Meshed ??Ready?
        failed_indices = []
        for i, body in enumerate(group):
            try:
                state = body.ObjectState
                # ????ObjectState.Meshed ??ObjectState.Ready ???
                ok = False
                try:
                    ok = (state == ObjectState.Meshed)
                except:
                    # fallback ???
                    s = str(state).lower()
                    if "meshed" in s or "ready" in s or "solved" in s:
                        ok = True
                if not ok:
                    failed_indices.append(i)
            except:
                failed_indices.append(i)

        if not failed_indices:
            return True, switched

        # ???????solid ??? method -> Tetra?? method control ?method ? Hex-like?
        for i in failed_indices:
            mc_tuple = mesh_ctrls[i] if i < len(mesh_ctrls) else None
            if mc_tuple is None:
                continue
            # ????method control ??solid ????
            if len(mc_tuple) >= 2 and mc_tuple[1] is not None:
                method_ctrl = mc_tuple[1]
                try:
                    method_str = method_ctrl.Method.ToString()
                except:
                    try:
                        method_str = str(method_ctrl.Method).lower()
                    except:
                        method_str = ""
                if any(k in method_str for k in ["Hex", "hex", "Sweep", "sweep", "MultiZone", "multizone"]):
                    # ????Tetra
                    try:
                        method_ctrl.Method = MethodType.AllTriAllTet
                        switched.append(i)
                    except:
                        # ??direct enum ?????????????
                        try:
                            method_ctrl.Method = "Tetrahedrons"
                            switched.append(i)
                        except:
                            pass

        if not switched:
            # ????????????
            return False, switched

        # ???? Generate
        ExtAPI.DataModel.Project.Model.Mesh.ClearGeneratedData()
        ExtAPI.DataModel.Project.Model.Mesh.GenerateMesh()

        # ? object state
        failed_after = []
        for i, body in enumerate(group):
            try:
                state = body.ObjectState
                ok = False
                try:
                    ok = (state == ObjectState.Meshed)
                except:
                    s = str(state).lower()
                    if "meshed" in s or "ready" in s or "solved" in s:
                        ok = True
                if not ok:
                    failed_after.append(i)
            except:
                failed_after.append(i)

        success = (len(failed_after) == 0)
        return success, switched

    # --------------------- ????? ---------------------
    def process_group(group, group_type, all_bodies):
        """
        group: list of bodies (unsuppressed)
        group_type: "solid" or "shell"
        all_bodies: ???suppressed ??bodies (? suppress_others_except)
        """
        #global list_CFL, list_MC, list_best_meshsize, list_body_names

        # mesh size ? config ??
        mesh_min = meshsize_min_solidbody if group_type == "solid" else meshsize_min_shellbody
        mesh_max = meshsize_max_solidbody if group_type == "solid" else meshsize_max_shellbody
        delta = meshsize_delta_solidbody if group_type == "solid" else meshsize_delta_shellbody

        # Fixed Range shared candidate list (max -> min by delta)
        size_candidates = []
        val = mesh_max
        while val >= mesh_min:
            size_candidates.append(round(val, 4))
            val -= delta

        # suppress others, keep only this group
        suppress_others_except(group, all_bodies)

        # get each body's sizing & method control
        mesh_ctrls, sizing_history = prepare_mesh_controls(group, group_type)

        # helper: read a body's current sizing element size as float
        def _cur_size(mc_tuple):
            sizing = mc_tuple[0]
            if sizing is None:
                return 0.0
            try:
                v = sizing.ElementSize
                v = v.Value if hasattr(v, "Value") else v
                return float(v)
            except:
                return 0.0

        # Build per-body candidate lists.
        #   Fixed(0)     : every body shares size_candidates
        #   Floating(1)  : per body, current size +/- offset, step = delta
        #   Percentage(2): per body, current size * (lower..upper), Diverse steps
        per_body_candidates = []
        for i in range(len(group)):
            if mode_tune == 0:
                per_body_candidates.append(list(size_candidates))
            elif mode_tune == 1:
                base = _cur_size(mesh_ctrls[i])
                if base <= 0:
                    base = mesh_max
                mx = base + meshsize_offset_up
                mn = base - meshsize_offset_down
                if mn < delta:
                    mn = delta
                cand = []
                v = mx
                while v >= mn - 1e-9:
                    if v > 0:
                        cand.append(round(v, 4))
                    v -= delta
                if not cand:
                    cand.append(round(base, 4))
                per_body_candidates.append(cand)
            else:
                base = _cur_size(mesh_ctrls[i])
                if base <= 0:
                    base = mesh_max
                mx = round(base * meshsize_upper_percentage, 4)
                mn = round(base * meshsize_lower_percentage, 4)
                nsteps = Diverse if Diverse >= 2 else 2
                stp = (mx - mn) / (nsteps - 1) if nsteps > 1 else 0.0
                cand = []
                for j in range(nsteps):
                    s = round(mx - j * stp, 4)
                    if s > 0:
                        cand.append(s)
                if not cand:
                    cand.append(round(base, 4))
                per_body_candidates.append(cand)

        # per-body size setter for one sweep round
        def adjust_mesh_size_perbody(sizes_for_round):
            with Transaction(True):
                for idx in range(len(mesh_ctrls)):
                    sizing = mesh_ctrls[idx][0]
                    s = sizes_for_round[idx]
                    if sizing is not None and s is not None:
                        try:
                            sizing.ElementSize = Quantity(s, 'mm')
                        except:
                            try:
                                sizing.ElementSize = s
                            except:
                                pass

        # ????mini-records
        MiniCFLs = [[] for _ in group]
        best_sizes = [None] * len(group)
        done_flags = [False] * len(group)

        # ----- Step A: ?????? mesh ???baseline CFL -----
        with Transaction(True):
            ok, switched = try_generate_mesh_with_objectstate_check(group, mesh_ctrls)
            #if not ok:
               # print("[UI_OUTPUT] " + str("Initial mesh generation failed for some bodies even after Hex->Tetra fallback. Those bodies will show CFL=0."))
        results = evaluate_cfl_fast(group)
        # ??baseline ??sizing value  sizing_history
        for i in range(len(group)):
            MiniCFLs[i].append(results[i])
            # sizing_history ?????? sizing valueprepare_mesh_controls ??
            # ??prepare ????????? sizing
            try:
                cur_s = sizing_history[i][0]
                if cur_s is None and mesh_ctrls[i][0] is not None:
                    v = mesh_ctrls[i][0].ElementSize
                    try:
                        v = v.Value if hasattr(v, "Value") else v
                    except:
                        pass
                    sizing_history[i][0] = v
            except:
                pass
            # ??baseline ?? mark done
            try:
                if results[i] >= Criteria_MinCFLTimeStep:
                    best_sizes[i] = sizing_history[i][-1]
                    done_flags[i] = True
            except:
                pass

        # ----- Step B: sweep each round; every body walks its own candidates -----
        max_len = max([len(c) for c in per_body_candidates]) if per_body_candidates else 0
        for k in range(max_len):
            # stop when every body reached the criteria
            if all(done_flags):
                break

            # per-body size for this round (None -> keep last, out of range)
            sizes_for_round = []
            for i in range(len(group)):
                if k < len(per_body_candidates[i]):
                    sizes_for_round.append(per_body_candidates[i][k])
                else:
                    sizes_for_round.append(None)

            # apply sizes then group-mesh (Hex->Tetra fallback inside)
            adjust_mesh_size_perbody(sizes_for_round)
            with Transaction(True):
                ok, switched = try_generate_mesh_with_objectstate_check(group, mesh_ctrls)

            # one shared CFL object evaluates the whole group
            results = evaluate_cfl_fast(group)

            for i in range(len(group)):
                if not done_flags[i]:
                    applied = sizes_for_round[i]
                    if applied is None:
                        applied = sizing_history[i][-1] if sizing_history[i] else None
                    MiniCFLs[i].append(results[i])
                    sizing_history[i].append(applied)
                    try:
                        if results[i] >= Criteria_MinCFLTimeStep and best_sizes[i] is None:
                            best_sizes[i] = applied
                            done_flags[i] = True
                    except:
                        pass
                else:
                    # already converged: carry previous values forward
                    if MiniCFLs[i]:
                        MiniCFLs[i].append(MiniCFLs[i][-1])
                    else:
                        MiniCFLs[i].append(0)
                    sizing_history[i].append(sizing_history[i][-1])

        # ----- Step C: ???????MeshControl -----
        for i in range(len(group)):
            # ????size ???????tested size  best
            if best_sizes[i] is None:
                try:
                     # ? CFL ?? index
                    max_idx = MiniCFLs[i].index(max(MiniCFLs[i]))
                    best_sizes[i] = sizing_history[i][max_idx]
                except:
                    best_sizes[i] = None

            list_CFL.append(MiniCFLs[i])
            list_MC.append(sizing_history[i])
            list_best_meshsize.append(best_sizes[i])

            # ??body name
            try:
                list_body_names.append(group[i].Name)
            except:
                list_body_names.append("Body_{}".format(i))

            # ???mesh size ??sizing control
            try:
                if mesh_ctrls[i][0] is not None and best_sizes[i] is not None:
                    # ??Quantity ?????
                    try:
                        mesh_ctrls[i][0].ElementSize = Quantity(best_sizes[i], 'mm')
                    except:
                        try:
                            mesh_ctrls[i][0].ElementSize = best_sizes[i]
                        except:
                            pass
            except:
                pass

    def sel_advance():
        #SOLID_BODIES = []
        #SHELL_BODIES = []
        BodyIDs = []
        BodyFaces = []
        BodyEdges = []
        BodyFacesIDs = []
        BodyEdgesIDs = []
        BodyFacesIDs_2 = []
        BodyEdgesIDs_2 = []
        Tree_All_Select = []
        Tree_Single_Select = []
        GUI_Select = []
        bodies_selected = []

        Meshctrl_sel = ExtAPI.DataModel.Tree.ActiveObjects
        gm = Model.Geometry
        if ExtAPI.DataModel.Tree.FirstActiveObject.GetType() == Ansys.ACT.Automation.Mechanical.Geometry:
            SOLID_BODIES = []
            SHELL_BODIES = []
            for Assembly in ExtAPI.DataModel.GeoData.Assemblies:
                for Part in Assembly.Parts:
                    for Body in Part.Bodies:
                        if not Body.Suppressed:
                            BodyIDs.append(Body.Id)
                            BodyFaces.extend(Body.Faces)
                            BodyEdges.extend(Body.Edges)
                            a = Body.Name
                            if Body.BodyType.ToString() == "GeoBodySolid":
                                SOLID_BODIES.append(Body)
                            elif Body.BodyType.ToString() == "GeoBodySheet":
                                SHELL_BODIES.append(Body)
                            gm.GetBody(Body)  # Gives you the Tree object
            for ibd in SHELL_BODIES:
                Tree_All_Select.append(gm.GetBody(ibd))
            for ibd in SOLID_BODIES:
                Tree_All_Select.append(gm.GetBody(ibd))
        if not len(ExtAPI.SelectionManager.CurrentSelection.Entities)==0:
            SOLID_BODIES = []
            SHELL_BODIES = []
            for Body in ExtAPI.SelectionManager.CurrentSelection.Entities:
                # if not Body.Suppressed:    ### Body can be selected is MUST not suppressed.
                if Body.GetType() == Ansys.ACT.Common.Geometry.GeoBodyWrapper:
                    BodyIDs.append(Body.Id)
                    BodyFaces.extend(Body.Faces)
                    BodyEdges.extend(Body.Edges)
                    a = Body.Name
                    if Body.BodyType.ToString() == "GeoBodySolid":
                        SOLID_BODIES.append(Body)
                    elif Body.BodyType.ToString() == "GeoBodySheet":
                        SHELL_BODIES.append(Body)
                    gm.GetBody(Body)  # Gives you the Tree object
                elif Body.GetType() == Ansys.ACT.Common.Geometry.GeoFaceWrapper:
                    BodyFacesIDs_2.append(Body.Id)
                elif Body.GetType() == Ansys.ACT.Common.Geometry.GeoEdgeWrapper:
                    BodyEdgesIDs_2.append(Body.Id)
                    
            for ibd in SHELL_BODIES:
                GUI_Select.append(gm.GetBody(ibd))
            for ibd in SOLID_BODIES:
                GUI_Select.append(gm.GetBody(ibd))
        if not len(Meshctrl_sel) == 0:
            SOLID_BODIES = []
            SHELL_BODIES = []
            for Body in Meshctrl_sel:
                if Body.GetType() == Ansys.ACT.Automation.Mechanical.Body:
                    if not Body.Suppressed:
                        BodyIDs.append(Body.GetGeoBody().Id)
                        BodyFaces.extend(Body.GetGeoBody().Faces)
                        BodyEdges.extend(Body.GetGeoBody().Edges)
                        a = Body.Name
                        if Body.GetGeoBody().BodyType.ToString() == "GeoBodySolid":
                            SOLID_BODIES.append(Body.GetGeoBody())
                        elif Body.GetGeoBody().BodyType.ToString() == "GeoBodySheet":
                            SHELL_BODIES.append(Body.GetGeoBody())
                        gm.GetBody(Body.GetGeoBody())  # Gives you the Tree object
                        
            for ibd in SHELL_BODIES:
                Tree_Single_Select.append(gm.GetBody(ibd))
            for ibd in SOLID_BODIES:
                Tree_Single_Select.append(gm.GetBody(ibd))
        Tree_All_Number = len(Tree_All_Select)
        Tree_Single_Number = len(Tree_Single_Select)
        GUI_Select_Number = len(GUI_Select)
        if not Tree_All_Number ==0 and Tree_Single_Number==0 and GUI_Select_Number == 0: ###Wayne:Comdition 1 Only Model All Select, Result:Model All
            for i in Tree_All_Select:
                bodies_selected.append(i)
        elif Tree_All_Number ==0 and not Tree_Single_Number==0 and GUI_Select_Number == 0:###Wayne:Comdition 2 Only Model Tree Select, Result:Model Tree
            for i in Tree_Single_Select:
                bodies_selected.append(i)
        elif Tree_All_Number ==0 and Tree_Single_Number==0 and not GUI_Select_Number == 0:###Wayne:Comdition 3 Only GUI Select, Result:GUI
            for i in GUI_Select:
                bodies_selected.append(i)
        elif not Tree_All_Number ==0 and not Tree_Single_Number==0 and GUI_Select_Number == 0:###Wayne:Comdition 4 Model All and Model Tree Select, Result:Model All
            for i in Tree_All_Select:
                bodies_selected.append(i)
        elif not Tree_All_Number ==0 and Tree_Single_Number==0 and not GUI_Select_Number == 0:###Wayne:Comdition 5 Model All and GUI Select, Result:GUI
            for i in GUI_Select:
                bodies_selected.append(i)
        elif Tree_All_Number ==0 and not Tree_Single_Number==0 and not GUI_Select_Number == 0:###Wayne:Comdition 6 Model Tree and GUI Select, Result:GUI
            for i in GUI_Select:
                bodies_selected.append(i)
        elif not Tree_All_Number ==0 and not Tree_Single_Number==0 and not GUI_Select_Number == 0:###Wayne:Comdition 7 Model All and Model Tree and GUI Select, Result:GUI
            for i in GUI_Select:
                bodies_selected.append(i)
        return bodies_selected, BodyIDs,Tree_All_Select,Tree_Single_Select,GUI_Select

    # ?????????baseline ?? size ??CFL ???mesh?
    def export_result():
        # ?
        header = ["Body Name", "Mesh Sizes", "CFLs", "Best Mesh Size"]
        rows = []

        for idx in range(len(list_MC)):
            name = list_body_names[idx] if idx < len(list_body_names) else "Body{}".format(idx)
            sizes = list_MC[idx]
            cfls = list_CFL[idx]
            best = list_best_meshsize[idx]

            sizes_str = ", ".join([str(s) for s in sizes])
            cfls_str = ", ".join(["{:.2E}".format(v) for v in cfls])
            rows.append([name, sizes_str, cfls_str, best])

        # ----- ASCII  -----
        # ????
        col_widths = [max(len(str(row[i])) for row in [header] + rows) for i in range(len(header))]

        # 
        table_str = " | ".join(header[i].ljust(col_widths[i]) for i in range(len(header))) + "\n"
        table_str += "-+-".join("-" * col_widths[i] for i in range(len(header))) + "\n"

        # ???
        for row in rows:
            table_str += " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(header))) + "\n"

        # -----  CSV ?-----

        analysis=ExtAPI.DataModel.Project.Model.Analyses[0]
        folder_path = analysis.WorkingDir
        out_file_name = "Mesh_CFL_Report_{}_{}_{}_{}.csv".format(
            datetime.datetime.now().date(),
            datetime.datetime.now().hour,
            datetime.datetime.now().minute,
            datetime.datetime.now().second)
        csv_path = os.path.join(folder_path, out_file_name)
        try:
            with open(csv_path, "wb") as f:
                writer = csv.writer(f)
                writer.writerow(["Body", "Best Size", "Best CFL"])
                writer.writerows(rows)
        except:
            csv_path = "(failed to save CSV)"

        return "\nCSV saved at: {}".format(csv_path)+"\n\n"+table_str 

    # --------------------- Main ---------------------
    startTime = time.time()

    bodies_all = ExtAPI.DataModel.Project.Model.Geometry.GetChildren(DataModelObjectCategory.Body, True)
    # Save original Suppressed state for all bodies before tuning begins
    original_suppressed_state = {}
    for _b in bodies_all:
        try:
            original_suppressed_state[_b.ObjectId] = _b.Suppressed
        except:
            pass
    ## To collect all unsuppressed GeoBodies
    bodies_original_suppress_all = [] ###Wayne :Totally ObjectState :Suppressed
    bodies_need_suppress_first_all_Freeze = [] ###Wayne :Totally ObjectState : Freeze
    bodies_need_suppress_first_all_Hidden = []###Wayne :Totally ObjectState :Hidden 
    bodies_unmesh_all = []###Wayne :Totally ObjectState :unmesh
    bodies_mesh_all = []###Wayne :Totally ObjectState :mesh
    bodies_unsuppressed=[]
    bodies_visible=[]
    bodies_selected=[]###Wayne:List for store selected body w/o freeze mesh body
    bodies_selected_ALL=[]###Wayne:Create list for store all selected body for filter freeze mesh body
    bodies_freeze=[]###Wayne:Store freeze mesh body
    bodies_meshed = []###Wayne:Store already mesh body
    Tree_All_Selected = []###Wayne:Store Model Tree All Select Parts
    Tree_Single_Selected = []###Wayne:Store Model Tree Single Select Parts
    GUI_Selected = [] ###Wayne:Store GUI Select Parts

    for body in bodies_all:
        if body.ObjectState == ObjectState.Suppressed:
            bodies_original_suppress_all.append(body)
        elif body.ObjectState == ObjectState.FullyDefined:
            bodies_unmesh_all.append(body)
            bodies_unsuppressed.append(body)
        elif body.ObjectState == ObjectState.Meshed:
            bodies_mesh_all.append(body)
            bodies_unsuppressed.append(body)
        elif body.ObjectState == ObjectState.Hidden:
            bodies_need_suppress_first_all_Hidden.append(body)
        else:
            bodies_need_suppress_first_all_Freeze.append(body)

    bodies_selected_ALL, BodyIDs, Tree_All_Selected, Tree_Single_Selected, GUI_Selected = sel_advance()

    with Transaction(True):
        for body in bodies_selected_ALL:
            #print(body.ObjectState)
            if body.ObjectState == ObjectState.Meshed:
                bodies_meshed.append(body)
                for ib in bodies_mesh_all:
                    if ib==body:
                        bodies_selected.append(body)
                        bodies_mesh_all.remove(body)
            elif body.ObjectState == ObjectState.FullyDefined:
                bodies_selected.append(body)
     
        solid_bodies, shell_bodies = classify_bodies_by_select(bodies_selected)
        bodies_selected_1 = solid_bodies + shell_bodies  # ???????

        if bodies_selected_1.Count == 0:
            try:
                act_elapsed_sec = _act_time.time() - _ACT_START_TIME
                log_usage("MECH_MeshTuner", "2.0", act_elapsed_sec, 5400)
            except:
                pass

            print("[UI_OUTPUT] " + str("No parts found for meshing."))
            return
     
        for body in bodies_need_suppress_first_all_Hidden:
            body.Suppressed = True
        for body in bodies_need_suppress_first_all_Freeze:
            body.Suppressed = True
        for body in bodies_mesh_all:
            Freeze_Body = body.GetGeoBody().Part###Wayne 
            Model.FreezeMeshOnSelectedParts(Freeze_Body)###Wayne 
            body.Suppressed = True


    # ??? bodies suppressed ??
    #bodies_all = ExtAPI.DataModel.Project.Model.Geometry.GetChildren(DataModelObjectCategory.Body, True)
    #bodies_unsuppressed = [b for b in bodies_all if not b.Suppressed]



    # ?solid ?group ??
    Solid_Process_StartTime = time.time()
    for group in chunk(solid_bodies, NumSimultaneousMesh):
        process_group(group, "solid", bodies_unsuppressed)
    Solid_Process_EndTime = time.time()


    # ?shell ?group ??


    # ?shell ?group ??
    Shell_Process_StartTime = time.time()
    for group in chunk(shell_bodies, NumSimultaneousMesh):
        process_group(group, "shell", bodies_unsuppressed)
    Shell_Process_EndTime = time.time()

    # Restore ALL bodies to their original Suppressed state before final GenerateMesh
    with Transaction(True):
        for _b in bodies_all:
            try:
                _orig = original_suppressed_state.get(_b.ObjectId, False)
                _b.Suppressed = _orig
            except:
                pass

    Select_Final_MeshStartTime = time.time()
    # ClearGeneratedData removed: it destroys ALL mesh including unselected geometry
    # GenerateMesh kept: it only regenerates mesh for bodies currently in "unmeshed" state
    # Bodies that retained their mesh (e.g. frozen/unaffected) will NOT be re-meshed
    ExtAPI.DataModel.Project.Model.Mesh.GenerateMesh()
    Select_Final_MeshEndTime = time.time()
    Select_Final_Mesh_Time = round(Select_Final_MeshEndTime - Select_Final_MeshStartTime, 1)

    # ????bodies ??suppressed ???un-suppress?
    Total_Select_Number = len(bodies_selected_1)
    if len(solid_bodies) == 0:
        Total_Solid_Number = 0
    else:
        Total_Solid_Number = len(solid_bodies)

    if len(shell_bodies) == 0:
        Total_Shell_Number = 0
    else:
        Total_Shell_Number = len(shell_bodies)

    infor = export_result()
    ExtAPI.DataModel.Tree.Refresh()
    ExtAPI.DataModel.Project.Model.Mesh.InternalObject.ForceUpdateMeshStates()
    endTime = time.time()
    Total_Select = "Total Select:{} parts ( Solid : {} and Shell: {} )".format(Total_Select_Number,Total_Solid_Number,Total_Shell_Number)+"\n"
    Total_Time = "Total Time: {} seconds".format(round(endTime - startTime, 1)) + "\n"
    Solid_Process_Time = "Solid Process Time: {} seconds".format(round(Solid_Process_EndTime-Solid_Process_StartTime, 1))+"\n"
    Shell_Process_Time = "Shell Process Time: {} seconds".format(round(Shell_Process_EndTime-Shell_Process_StartTime, 1))+"\n"
    Generate_Selct_Mesh_Time = "Final Generate Mesh Time {} seconds".format(Select_Final_Mesh_Time)+"\n"
    Final = Total_Select + Total_Time + Solid_Process_Time + Shell_Process_Time + Generate_Selct_Mesh_Time +infor

    try:
        act_elapsed_sec = _act_time.time() - _ACT_START_TIME
        log_usage("MECH_MeshTuner", "2.0", act_elapsed_sec, 5400)
    except:
        pass

    print("[UI_OUTPUT] " + str(Final))


