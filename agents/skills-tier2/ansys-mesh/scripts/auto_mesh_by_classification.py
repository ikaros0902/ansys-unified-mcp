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
    """
    AutoMesh Log
    [2026.5.25] by Terry Chang
    Update mesh algorithm from object control to obeject ID control.
    Update washer geometry seletion algorithm.

    [2025.10.22]
    Mesh Control Creation, 1x1, one geometry one mesh control
    + Shell Body Sizing
    + Solid Body Sizing
    + Solid Body Method
    + Edge Sizing
    + Edge Wahser from 2022-09-02
    + Face Mesh
    + Face Sizing
    + Shell Prime Mesh Method Create from 2025-10-22 by Wayne
    Author: Louis Liu
    louis_liu2@jabil.com

    """
    import time
    import os
    import clr
    import datetime
    import math
    import units
    import re
    import traceback 

    clr.AddReference("System.Windows.Forms")
    import System

    try:
        startTime = time.time()

        import Ansys
        clr.AddReference("Ans.Utilities")
        from Ansys.Utilities import ApplicationConfiguration

        version = ApplicationConfiguration.DefaultConfiguration.VersionInfo.VersionString
        ExtAPI.DataModel.Project.UnitSystem = UserUnitSystemType.StandardNMM
        ###################################
        ### Inputs for script
        ###################################
        # Is_ResetGroupMC=False
        # Is_DeleteUnDefined_MC=False
        # Is_GenerateMesh=False
        # Is_Sizing_ShellBody=True
        # shell_bodySizing_size=3.0
        # shell_DefeatureSize=0
        # Is_MeshMethod_SolidBody=True
        # Is_Sizing_SolidBody=True
        # solid_bodySizing_size_Max=2.0
        # solid_DefeatureSize=0
        # NS_FsMeshing_ALL_GT='Scr_fs_def_ALL_GT1.5MM2'
        # Is_FaceMeshing_DefeatureFs=False
        # Is_FaceSizing_DefeatureFs=False
        # FaceSizing_size=1.5
        # NS_EdgeSizing_RMgrp='Scr_RM_grp'
        # Is_EdgeSizing_RMgrp=True
        # EdgeSizing_size_RMgrp=1.5
        # Is_EdgeWasher_RMgrp=False
        # Washer_LayerNum=1

        ###################################
        ### Inputs for ACT
        ###################################
        Model = ExtAPI.DataModel.Project.Model

        Is_Sizing_ShellBody=step.Properties['ShellBodyMeshControls'].Properties['Is_Sizing_ShellBody'].Value
        Is_Prime_Mesh_Method_ShellBody=step.Properties['ShellBodyMeshControls'].Properties['Is_PrimeMeshMethod_ShellBody'].Value
        shell_bodySizing_size=step.Properties['ShellBodyMeshControls'].Properties['shell_bodySizing_size'].Value
        shell_DefeatureSize=step.Properties['ShellBodyMeshControls'].Properties['shell_DefeatureSize'].Value
        Is_MeshMethod_SolidBody=step.Properties['SolidBodyMeshControls'].Properties['Is_MeshMethod_SolidBody'].Value
        Is_Sizing_SolidBody=step.Properties['SolidBodyMeshControls'].Properties['Is_Sizing_SolidBody'].Value
        solid_bodySizing_size_Max=step.Properties['SolidBodyMeshControls'].Properties['solid_bodySizing_size_Max'].Value
        solid_DefeatureSize=step.Properties['SolidBodyMeshControls'].Properties['solid_DefeatureSize'].Value
        NS_FsMeshing_ALL_GT=step.Properties['FaceMeshControls'].Properties['NS_FsMeshing_ALL_GT'].Value
        Is_FaceMeshing_DefeatureFs=step.Properties['FaceMeshControls'].Properties['Is_FaceMeshing_DefeatureFs'].Value
        Is_FaceSizing_DefeatureFs=step.Properties['FaceMeshControls'].Properties['Is_FaceSizing_DefeatureFs'].Value
        FaceSizing_size=step.Properties['FaceMeshControls'].Properties['FaceSizing_size'].Value
        NS_EdgeSizing_RMgrp=step.Properties['EdgeMeshControls'].Properties['NS_EdgeSizing_RMgrp'].Value
        Is_EdgeSizing_RMgrp=step.Properties['EdgeMeshControls'].Properties['Is_EdgeSizing_RMgrp'].Value
        EdgeSizing_size_RMgrp=step.Properties['EdgeMeshControls'].Properties['EdgeSizing_size_RMgrp'].Value
        Is_EdgeWasher_RMgrp=step.Properties['EdgeMeshControls'].Properties['Is_EdgeWasher_RMgrp'].Value
        Washer_LayerNum=step.Properties['EdgeMeshControls'].Properties['Washer_LayerNum'].Value

        def Wait(ms):
            import System.Threading
            System.Threading.Thread.Sleep(ms)

        def SweepMesherInd(Body_Ids, NumThickElem=0, BotFace=None):
            if len(Body_Ids) != 0:
                AllLayerSelection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
                AllLayerSelection.Ids = Body_Ids

                SweepMeshMethod = MesherObj.AddAutomaticMethod()
                SweepMeshMethod.Location = AllLayerSelection
                SweepMeshMethod.Method = MethodType.Sweep
                if BotFace != None:
                    SweepMeshMethod.SourceTargetSelection = 4
                    FaceSelection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
                    FaceSelection.Entities = [BotFace]
                    SweepMeshMethod.SourceLocation = FaceSelection
                    FaceSelection = None # Release Memory
                else:
                    SweepMeshMethod.SourceTargetSelection = 0
                    
                SweepMeshMethod.FreeFaceMeshType = 2
                SweepMeshMethod.SweepNumberDivisions = NumThickElem
                AllLayerSelection = None # Release Memory

        def BodySizingFunc(BodyIdset, Size, DefeatureSize, strict=False, rate_of_growth=0.0):
            if len(BodyIdset) != 0:
                AllBodyelection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
                AllBodyelection.Ids = BodyIdset
                Sizing = MesherObj.AddSizing()
                temp_def=[]
                temp_caption_def=[]
                for i in Sizing.VisibleProperties:
                    temp_def.append(str(i))
                    temp_caption_def.append(i.Caption)
                Sizing.Location = AllBodyelection
                AllBodyelection = None # Release Memory
                Sizing.ElementSize = Quantity("{0} [{1}]".format(Size, 'mm'))
                Sizing.CaptureCurvature = False

                try:
                    if 'caption_MeshObj_prop' in globals() and 'Mesh Based Connection' in caption_MeshObj_prop:
                        prop_idx = caption_MeshObj_prop.index('Mesh Based Connection')
                        if not MesherObj.VisibleProperties[prop_idx].StringValue == 'Yes':
                            Sizing.Type = SizingType.ElementSize
                            Sizing.DefeatureSize = Quantity(DefeatureSize, "mm")
                            if 'SizingType' in temp_def:
                                Sizing.VisibleProperties[temp_def.index('SizingType')].InternalValue = 1
                    else:
                        Sizing.Type = SizingType.ElementSize
                        Sizing.DefeatureSize = Quantity(DefeatureSize, "mm")
                except:
                    pass
                    
                if strict:
                    Sizing.Behavior = SizingBehavior.Hard
                else:
                    Sizing.GrowthRate = rate_of_growth
                return Sizing

        def get_box_stats(Body):
            Geom = Model.Geometry
            TreeBody = Geom.GetBody(Body)
            Bound_Box = [TreeBody.LengthX.Value, TreeBody.LengthY.Value, TreeBody.LengthZ.Value]
            Bounding_box_Volume = Bound_Box[0] * Bound_Box[1] * Bound_Box[2] / (Length_factor ** 3)
            return min(Bound_Box),Bounding_box_Volume

        def get_edge_statistics(bd):
            Edge_list = []
            min_len = None
            min_Edge = None

            for edge in bd.Edges:
                if min_len == None:
                    min_len = edge.Length
                    Edge_list.append(min_len)
                    min_Edge = edge
                else:
                    temp_len = edge.Length
                    Edge_list.append(temp_len)
                    if temp_len < min_len:
                        min_len = temp_len
                        min_Edge = edge
            face_count = bd.Faces.Count
            edge_count = bd.Edges.Count
            Edge_list.sort()
            mid = len(Edge_list) // 2
            median = (Edge_list[mid] + Edge_list[~mid]) / 2
            avg_dim = sum(Edge_list) / len(Edge_list)
            return min_len * Length_factor, median * Length_factor, avg_dim * Length_factor, edge_count / face_count, min_Edge

        def shell_multizone_method(shell_bds, PresBoundKey):
            if len(shell_bds) != 0:
                PkgSelection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
                PkgSelection.Ids = shell_bds
                MeshMethod = MesherObj.AddAutomaticMethod()
                MeshMethod.Location = PkgSelection
                PkgSelection = None # Release Memory
                MeshMethod.Method = MethodType.QuadTri
                MeshMethod.PreserveBoundaries = PresBoundKey
                if PresBoundKey == 0:
                    MeshMethod.MeshBasedDefeaturing = True
                    MeshMethod.DefeaturingTolerance = MeshMethod.MinimumEdgeLength
                return MeshMethod

        def shell_quad_dominant(shell_bds):
            if len(shell_bds) != 0:
                PkgSelection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
                PkgSelection.Ids = shell_bds
                MeshMethod = MesherObj.AddAutomaticMethod()
                MeshMethod.Location = PkgSelection
                PkgSelection = None # Release Memory
                MeshMethod.Method = MethodType.Automatic
                return MeshMethod

        def add_face_meshing(FaceIdset):
            FaceSelection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
            FaceSelection.Ids=FaceIdset
            fm = MesherObj.AddFaceMeshing()
            fm.Location = FaceSelection
            FaceSelection = None # Release Memory
            return fm

        def MultiZoneMethod(Pkg, PresBoundKey):
            PkgSelection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
            PkgSelection.Ids = Pkg
            MeshMethod = MesherObj.AddAutomaticMethod()
            MeshMethod.Location = PkgSelection
            PkgSelection = None # Release Memory
            MeshMethod.Method = MethodType.MultiZone
            MeshMethod.SurfaceMeshMethod = 1
            MeshMethod.PreserveBoundaries = PresBoundKey
            if PresBoundKey == 0:
                MeshMethod.MeshBasedDefeaturing = True
                MeshMethod.DefeaturingTolerance = MeshMethod.MinimumEdgeLength
            return MeshMethod
            
        def EdgeSizingFunc(EdgeIdset,Size,Mode=0):
            AllSelection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
            AllSelection.Ids = EdgeIdset
            def_EdgeSizing=MesherObj.AddSizing()
            def_EdgeSizing.Location = AllSelection
            AllSelection = None # Release Memory
            if Mode==0:
                def_EdgeSizing.Type=SizingType.ElementSize
                def_EdgeSizing.ElementSize = Quantity(Size, "mm")
            elif Mode==1:
                def_EdgeSizing.Type=SizingType.NumberOfDivisions
                def_EdgeSizing.NumberOfDivisions = Size
            def_EdgeSizing.Behavior=SizingBehavior.Hard
            return def_EdgeSizing

        def EdgeWasherFunc(EdgeIdset,LayerNum=1):
            AllSelection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
            AllSelection.Ids = EdgeIdset
            def_EdgeWasher=MesherObj.AddWasher()
            def_EdgeWasher.Location = AllSelection
            AllSelection = None # Release Memory
            def_EdgeWasher.NumberOfWasherLayers=LayerNum
            return def_EdgeWasher

        def IsMeshApplied(geo,meshtype=None):
            MeshControls=ExtAPI.DataModel.Project.Model.Mesh.Children
            LocationType=geo.GetType()
            IsApplied=False
            for i in MeshControls:
                if i.GetType()==Ansys.ACT.Automation.Mechanical.TreeGroupingFolder:
                    continue
                elif i.GetType()==meshtype or meshtype==None:
                    try:
                        loc = i.Location
                        if loc is None:
                            continue
                    except:
                        continue
                        
                    if LocationType==Ansys.ACT.Automation.Mechanical.NamedSelection:
                        if geo.Id==loc.Id:
                            IsApplied=True
                            break
                    elif LocationType==Ansys.ACT.Common.Geometry.GeoBodyWrapper:
                        if hasattr(loc, 'Ids') and geo.Id in loc.Ids:
                            IsApplied=True
                            break
                    elif LocationType==Ansys.ACT.Common.Geometry.GeoFaceWrapper:
                        if hasattr(loc, 'Ids') and geo.Id in loc.Ids:
                            IsApplied=True
                            break
                    elif LocationType==Ansys.ACT.Common.Geometry.GeoEdgeWrapper:
                        if hasattr(loc, 'Ids') and geo.Id in loc.Ids:
                            IsApplied=True
                            break
            return IsApplied

        def CFLTimeStepCalc():
            CFLTimeStep_obj = ExtAPI.DataModel.CreateObject("TimeStepCalc",'LSDYNA')
            CFLTimeStep_obj.Properties["Time Step Safety Factor"].Value = 0.9
            CFLTimeStep_obj.Properties["Linear Viscosity Coefficient"].Value = 0.06
            allbodies = Model.Geometry.GetChildren(DataModelObjectCategory.Body, True)
            bodies = [x.GetGeoBody().Id for x in allbodies if x.Suppressed == False]
            sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
            sel.Ids = bodies
            CFLTimeStep_obj.Properties['Geometry/DefineBy/Geo'].Value = sel
            sel = None # ? step 4??
            CFLTimeStep_obj.Import()
            Model.Activate()
            CFLTimeStep_obj.Activate()
            return CFLTimeStep_obj.Properties['Minimum CFL value'].Value

        def FindUnMeshedParts():
            bodies = ExtAPI.DataModel.Project.Model.Geometry.GetChildren(DataModelObjectCategory.Body, True)
            UMbodies=[]
            for body in bodies:
                if body.Suppressed==False:
                    if body.Elements == 0:
                        UMbodies.append(body)
            return UMbodies

        SOLID_BODIES = []
        SHELL_BODIES = []
        BodyIDs=[]
        BodyFacesIDs=[]
        BodyEdgesIDs=[]
        BodyFacesIDs_2=[]
        BodyEdgesIDs_2=[]

        GeometryUnit = str(ExtAPI.DataModel.Project.Model.Geometry.LengthUnit) 
        UnitDict = {'StandardMKS': 'm', 'StandardNMM': 'mm', 'StandardUMKS': 'um', 'StandardBIN': 'in', 'StandardBFT': 'ft', 'StandardCGS': 'cm'}
        GeomUnit = UnitDict[GeometryUnit] 
        Length_factor = units.ConvertUnit(1, UnitDict[GeometryUnit], ExtAPI.DataModel.CurrentUnitFromQuantityName("Length"))

        current_sel = ExtAPI.SelectionManager.CurrentSelection
        has_graphics_selection = current_sel is not None and current_sel.Ids.Count > 0

        with Transaction(True):
            if has_graphics_selection:
                for entity in current_sel.Entities:
                    if entity.GetType()==Ansys.ACT.Common.Geometry.GeoBodyWrapper:
                        BodyIDs.append(entity.Id)
                        BodyFacesIDs.extend([face.Id for face in entity.Faces])
                        BodyEdgesIDs.extend([edge.Id for edge in entity.Edges])
                        if entity.BodyType.ToString() == "GeoBodySolid":
                            SOLID_BODIES.append(entity)
                        elif entity.BodyType.ToString() == "GeoBodySheet":
                            SHELL_BODIES.append(entity)
                    elif entity.GetType()==Ansys.ACT.Common.Geometry.GeoFaceWrapper:
                        BodyFacesIDs_2.append(entity.Id)
                    elif entity.GetType()==Ansys.ACT.Common.Geometry.GeoEdgeWrapper:
                        BodyEdgesIDs_2.append(entity.Id)
            else:
                active_objs = ExtAPI.DataModel.Tree.ActiveObjects
                is_geometry_node_selected = False
                if active_objs is not None:
                    for obj in active_objs:
                        if obj.GetType() == Ansys.ACT.Automation.Mechanical.Geometry:
                            is_geometry_node_selected = True
                            break
                
                if is_geometry_node_selected:
                    for Assembly in ExtAPI.DataModel.GeoData.Assemblies:
                        for Part in Assembly.Parts:
                            for Body in Part.Bodies:
                                if not Body.Suppressed:
                                    BodyIDs.append(Body.Id)
                                    BodyFacesIDs.extend([face.Id for face in Body.Faces])
                                    BodyEdgesIDs.extend([edge.Id for edge in Body.Edges])
                                    if Body.BodyType.ToString() == "GeoBodySolid":
                                        SOLID_BODIES.append(Body)
                                    elif Body.BodyType.ToString() == "GeoBodySheet":
                                        SHELL_BODIES.append(Body)
                else:
                    if active_objs is not None:
                        for obj in active_objs:
                            if obj.GetType()==Ansys.ACT.Automation.Mechanical.Body:
                                if not obj.Suppressed:
                                    geo_body = obj.GetGeoBody()
                                    BodyIDs.append(geo_body.Id)
                                    BodyFacesIDs.extend([face.Id for face in geo_body.Faces])
                                    BodyEdgesIDs.extend([edge.Id for edge in geo_body.Edges])
                                    if geo_body.BodyType.ToString() == "GeoBodySolid":
                                        SOLID_BODIES.append(geo_body)
                                    elif geo_body.BodyType.ToString() == "GeoBodySheet":
                                        SHELL_BODIES.append(geo_body)
        ### If the code is expired, would not execute main process.
        expireddate=datetime.date(2027,9,1)
        nowdate=datetime.datetime.now()
        datedelta=nowdate.date()-expireddate

        if datedelta.days>0:
            try:
                act_elapsed_sec = _act_time.time() - _ACT_START_TIME
                log_usage("MECH_AutoMesh", "1.0", act_elapsed_sec, 1500)
            except:
                pass

            print("[UI_OUTPUT] " + str("Automation is expired. Please update."))
        else:
            shell_criterion = {"Mesh_Range_Max": shell_bodySizing_size, "Mesh_Range_Min": shell_bodySizing_size, "Edge_Length": 0.5, "Warpage": 20.0, "Aspect_Ratio": 5, "Skew": 45, "Jacobian": 0.65, "Time_Step": 5 * 10 ^ -8}
            solid_criterion = {"Mesh_Range_Max": solid_bodySizing_size_Max, "Mesh_Range_Min": 1, "Edge_Length": 0.5, "Warpage": 20.0, "Aspect_Ratio": 5, "Skew": 45, "Jacobian": 0.65, "Time_Step": 5 * 10 ^ -8}

            MesherObj = ExtAPI.DataModel.Project.Model.Mesh
            name_MeshObj_prop=[]
            caption_MeshObj_prop=[]
            for i in MesherObj.VisibleProperties:
                name_MeshObj_prop.append(str(i))
                caption_MeshObj_prop.append(i.Caption)
                
            Temp_Size = max([shell_criterion["Mesh_Range_Max"]])
            if not MesherObj.ElementSize==Quantity("{0} [{1}]".format(Temp_Size, 'mm')):
                MesherObj.ElementSize = Quantity("{0} [{1}]".format(Temp_Size, 'mm'))
            
            MesherObj_Internal = MesherObj.InternalObject
            if not MesherObj_Internal.GlobalTargetJacobianRatio == min([shell_criterion["Jacobian"], solid_criterion["Jacobian"]]):
                MesherObj_Internal.GlobalTargetJacobianRatio = min([shell_criterion["Jacobian"], solid_criterion["Jacobian"]])
            if not MesherObj_Internal.GlobalTargetMinLength == min([shell_criterion["Edge_Length"], solid_criterion["Edge_Length"]]):
                MesherObj_Internal.GlobalTargetMinLength = min([shell_criterion["Edge_Length"], solid_criterion["Edge_Length"]])
            if not MesherObj_Internal.GlobalTargetSkewness == min([shell_criterion["Skew"], solid_criterion["Skew"]]):
                MesherObj_Internal.GlobalTargetSkewness = min([shell_criterion["Skew"], solid_criterion["Skew"]])
            
            SM = ExtAPI.SelectionManager
            MesherObj.Activate()
            Wait(1000)

            Is_ScrXXX_ready=False
            for i in MesherObj.Children:
                if i.Name=='Scr_XXX':
                    Is_ScrXXX_ready=True
            if Is_ScrXXX_ready==False:
                tempMC=ExtAPI.DataModel.Project.Model.Mesh.AddSizing()
                ExtAPI.DataModel.InternalObject["tree"].AddActiveObjectID(tempMC.ObjectId)
                myfolder = ExtAPI.DataModel.Project.Model.InternalObject.AddTreeGroupingFolder(MesherObj.ObjectId)
                myfolder.Name = "Scr_XXX"
                with Transaction(True):
                    tempMC.Delete()
                    ExtAPI.DataModel.Tree.Refresh()
            
            with Transaction(True):
                NewAddMeshCtrl=[]        
                if Is_Sizing_ShellBody==True:
                    for shell_body in SHELL_BODIES:
                        mesh_type=Ansys.ACT.Automation.Mechanical.MeshControls.Sizing
                        if not IsMeshApplied(shell_body,mesh_type)==True:
                            min_box_dim, box_vol = get_box_stats(shell_body)
                            min_size, median_size, avg_size, edge_face_ratio, min_feature = get_edge_statistics(shell_body)
                            mesh_size = 0.0
                            if median_size <= shell_criterion["Mesh_Range_Max"] and median_size >= shell_criterion["Mesh_Range_Min"]:
                                mesh_size = median_size
                            elif avg_size <= shell_criterion["Mesh_Range_Max"] and avg_size >= shell_criterion["Mesh_Range_Min"]:
                                mesh_size = avg_size
                            else:
                                mesh_size = shell_criterion["Mesh_Range_Max"]
                            temp_msh=BodySizingFunc([shell_body.Id], mesh_size,shell_DefeatureSize, False)
                            NewAddMeshCtrl.append(temp_msh)
                            if Is_Prime_Mesh_Method_ShellBody ==True:
                                Temp_Prime_Method = MesherObj.AddAutomaticMethod()
                                Prime_Shell_Id = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
                                Prime_Shell_Id.Ids = [shell_body.Id]
                                Temp_Prime_Method.Location = Prime_Shell_Id
                                Temp_Prime_Method.Method = MethodType.Prime
                                NewAddMeshCtrl.append(Temp_Prime_Method)
                                Prime_Shell_Id = None # Release Memory
            
                Solid_MutiZone=[]
                if Is_Sizing_SolidBody==True:
                    for solid_body in SOLID_BODIES:
                        mesh_type=Ansys.ACT.Automation.Mechanical.MeshControls.Sizing
                        if not IsMeshApplied(solid_body,mesh_type)==True:
                            min_size, median_size, avg_size, edge_face_ratio, min_feature = get_edge_statistics(solid_body)
                            min_box_dim, box_vol = get_box_stats(solid_body)
                            mesh_size = 0.0
                            if median_size <= solid_criterion["Mesh_Range_Max"] and median_size >= solid_criterion["Mesh_Range_Min"]:
                                mesh_size = median_size
                            elif avg_size <= solid_criterion["Mesh_Range_Max"] and avg_size >= solid_criterion["Mesh_Range_Min"]:
                                mesh_size = avg_size
                            else:
                                mesh_size = solid_criterion["Mesh_Range_Max"]
                            temp_msh=BodySizingFunc([solid_body.Id], mesh_size, solid_DefeatureSize, False)
                            NewAddMeshCtrl.append(temp_msh)
                
                if Is_MeshMethod_SolidBody==True:
                    for solid_body in SOLID_BODIES:
                        mesh_type=Ansys.ACT.Automation.Mechanical.MeshControls.AutomaticMethod
                        if not IsMeshApplied(solid_body,mesh_type)==True:
                            Solid_MutiZone.append(solid_body.Id)
                            temp_msh=MultiZoneMethod(Solid_MutiZone, 0)
                            NewAddMeshCtrl.append(temp_msh)
                            Solid_MutiZone=[]

                AllNS=ExtAPI.DataModel.Project.Model.GetChildren(DataModelObjectCategory.NamedSelection, True)
                NS_Active=[]
                for iNS in AllNS:
                    if not iNS.Location.Ids.Count==0:
                        NS_Active.append(iNS)
                circle_ns_pattern = r".*Scr_Circle_(\d+)$"
                FsMeshMode=1
                EdgeMeshMode=1
                
                if Is_EdgeSizing_RMgrp==True:
                    if EdgeMeshMode==1:
                        for iedgeID in BodyEdgesIDs_2:
                            selection=ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
                            selection.Ids=[iedgeID]
                            iGeo=selection.Entities[0]
                            mesh_type=Ansys.ACT.Automation.Mechanical.MeshControls.Sizing
                            if not IsMeshApplied(iGeo,mesh_type)==True:
                                edgeSizing=EdgeSizingFunc([iedgeID],EdgeSizing_size_RMgrp,0)
                                NewAddMeshCtrl.append(edgeSizing)
                            selection = None # Release Memory
                            iGeo = None
                
                if Is_FaceMeshing_DefeatureFs==True:
                    if FsMeshMode==1:
                        for ifsID in BodyFacesIDs_2:
                            selection=ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
                            selection.Ids=[ifsID]
                            iGeo=selection.Entities[0]
                            mesh_type=Ansys.ACT.Automation.Mechanical.MeshControls.FaceMeshing
                            if not IsMeshApplied(iGeo,mesh_type)==True:
                                faceMesh=add_face_meshing([ifsID])
                                NewAddMeshCtrl.append(faceMesh)
                                faceMesh.Method=FaceMeshingMethod.Quadrilaterals
                            selection = None # Release Memory
                            iGeo = None
                
                if Is_FaceSizing_DefeatureFs==True:
                    if FsMeshMode==1:
                        for ifsID in BodyFacesIDs_2:
                            selection=ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
                            selection.Ids=[ifsID]
                            iGeo=selection.Entities[0]
                            mesh_type=Ansys.ACT.Automation.Mechanical.MeshControls.Sizing
                            if not IsMeshApplied(iGeo,mesh_type)==True:
                                FaceSizing=BodySizingFunc([iGeo.Id], FaceSizing_size,True)
                                NewAddMeshCtrl.append(FaceSizing)
                            selection = None # Release Memory
                            iGeo = None

                EdgeMeshGeo=[]
                EdgeMeshGeoIDs=[]  
                FaceMeshGeo=[]
                FaceMeshGeoIDs=[]
                for ns in NS_Active:
                    if not ns.Name.IndexOf(NS_EdgeSizing_RMgrp)==-1:
                        EdgeMeshGeo.extend(ns.Location.Entities)
                        EdgeMeshGeoIDs.extend(ns.Location.Ids)
                    elif ns.Name==NS_FsMeshing_ALL_GT:
                        FaceMeshGeo.extend(ns.Location.Entities)
                        FaceMeshGeoIDs.extend(ns.Location.Ids)        
                    m = re.match(circle_ns_pattern,ns.Name)
                    if m !=None:
                        edgeCount = m.groups()[0]
                        if ns.Location.Entities[0].Type.ToString() == "GeoEdge":
                            EdgeSizingFunc(ns.Ids,int(edgeCount),1)

                if Is_EdgeSizing_RMgrp==True:
                    if EdgeMeshMode==1:
                        for iedgeID in EdgeMeshGeoIDs:
                            if iedgeID in BodyEdgesIDs:
                                selection=ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
                                selection.Ids=[iedgeID]
                                iGeo=selection.Entities[0]
                                mesh_type=Ansys.ACT.Automation.Mechanical.MeshControls.Sizing
                                if not IsMeshApplied(iGeo,mesh_type)==True:
                                    edgeSizing=EdgeSizingFunc([iedgeID],EdgeSizing_size_RMgrp,0)
                                    NewAddMeshCtrl.append(edgeSizing)
                                selection = None # Release Memory
                                iGeo = None
                
                if Is_FaceMeshing_DefeatureFs==True:    
                    if FsMeshMode==1:
                        for ifsID in FaceMeshGeoIDs:
                            if ifsID in BodyFacesIDs:
                                selection=ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
                                selection.Ids=[ifsID]
                                iGeo=selection.Entities[0]                                
                                mesh_type=Ansys.ACT.Automation.Mechanical.MeshControls.FaceMeshing                               
                                if not IsMeshApplied(iGeo,mesh_type)==True:
                                    faceMesh=add_face_meshing([ifsID])
                                    NewAddMeshCtrl.append(faceMesh)
                                    faceMesh.Method=FaceMeshingMethod.Quadrilaterals
                                selection = None # Release Memory
                                iGeo = None
                                
                if Is_FaceSizing_DefeatureFs==True:
                    for ifsID in FaceMeshGeoIDs:
                        if ifsID in BodyFacesIDs:
                            selection=ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
                            selection.Ids=[ifsID]
                            iGeo=selection.Entities[0] 
                            mesh_type=Ansys.ACT.Automation.Mechanical.MeshControls.Sizing
                            if not IsMeshApplied(iGeo,mesh_type)==True:
                                FaceSizing=BodySizingFunc([ifsID], FaceSizing_size,True)
                                NewAddMeshCtrl.append(FaceSizing)
                            selection = None # Release Memory
                            iGeo = None

                # =====================================================================
                # Washer Algorithm
                # =====================================================================
                if Is_EdgeWasher_RMgrp == True:
                    selected_edges = set(BodyEdgesIDs + BodyEdgesIDs_2)
                    ns_edges = set(EdgeMeshGeoIDs)
                    target_edges = list(selected_edges.intersection(ns_edges))
                    
                    if len(target_edges) > 0:
                        circular_edges = []
                        edge_ends = {}
                        
                        for eid in target_edges:
                            try:
                                geo = ExtAPI.DataModel.GeoData.GeoEntityById(eid)
                                if geo is None: continue
                                c_type = str(geo.CurveType).lower()
                                
                                if 'circle' in c_type or 'arc' in c_type:
                                    circular_edges.append(eid)
                                    try:
                                        v1 = geo.StartVertex.Id
                                        v2 = geo.EndVertex.Id
                                        if v1 == v2:
                                            edge_ends[eid] = [] 
                                        else:
                                            edge_ends[eid] = [v1, v2]
                                    except:
                                        verts = [v.Id for v in geo.Vertices]
                                        if len(verts) <= 1:
                                            edge_ends[eid] = []
                                        else:
                                            edge_ends[eid] = verts
                            except:
                                pass
                        
                        groups = []
                        visited = set()
                        for eid in circular_edges:
                            if eid not in visited:
                                current_group = []
                                queue = [eid]
                                visited.add(eid)
                                
                                while queue:
                                    curr = queue.pop(0)
                                    current_group.append(curr)
                                    curr_verts = set(edge_ends.get(curr, []))
                                    
                                    for other_eid in circular_edges:
                                        if other_eid not in visited:
                                            other_verts = set(edge_ends.get(other_eid, []))
                                            if curr_verts.intersection(other_verts): 
                                                visited.add(other_eid)
                                                queue.append(other_eid)
                                groups.append(current_group)
                                
                        for grp in groups:
                            selection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
                            selection.Ids = [grp[0]] 
                            iGeo = selection.Entities[0]
                            mesh_type = Ansys.ACT.Automation.Mechanical.MeshControls.Washer
                            
                            if not IsMeshApplied(iGeo, mesh_type):
                                edgeWasher = EdgeWasherFunc(grp, Washer_LayerNum)
                                NewAddMeshCtrl.append(edgeWasher)
                                
                            selection = None # Release Memory
                            iGeo = None
                # =====================================================================
                                
            Cnt_NewAdd=len(NewAddMeshCtrl)
            
            with Transaction(True):
                for i in NewAddMeshCtrl:
                    i.RenameBasedOnDefinition()
                    
            import System.Threading
            System.Threading.Thread.Sleep(500)
            ExtAPI.DataModel.Tree.Refresh()
            
            endTime = time.time()
            
            str_MsgBox="Done, took {} seconds".format(round(endTime - startTime,1))+"\n\n\n"
            str_MsgBox=str_MsgBox+'Geometry Selected:'+"\n"+'   Bodies '+str(len(BodyIDs))+"\n"+'     Faces '+str(len(BodyFacesIDs_2))+"\n"+'    Edges '+str(len(BodyEdgesIDs_2))
            str_MsgBox=str_MsgBox+"\n\n"+'Mesh Controls:'+"\n"+'   Created '+str(Cnt_NewAdd)+"\n"
            
            try:
                clr.AddReference("Ansys.Mechanical.DataModel")
                import Ansys.Mechanical.DataModel.Enums.MessageSeverityType as MessageSeverityType
                ExtAPI.Application.Messages.AddMessage(MessageSeverityType.Info, str_MsgBox)
            except:
                ExtAPI.Log.WriteMessage(str_MsgBox) 
            
            try:
                act_elapsed_sec = _act_time.time() - _ACT_START_TIME
                log_usage("MECH_AutoMesh", "1.0", act_elapsed_sec, 1500)
            except:
                pass

            print("[UI_OUTPUT] " + str(str_MsgBox))
            
            return True

    except Exception as e:
        err_msg = traceback.format_exc()
        ExtAPI.Log.WriteError(err_msg)
        try:
            act_elapsed_sec = _act_time.time() - _ACT_START_TIME
            log_usage("MECH_AutoMesh", "1.0", act_elapsed_sec, 1500)
        except:
            pass

        print("[UI_OUTPUT] " + str("[Internal Script Errors] \n\n" + err_msg))
        return False
