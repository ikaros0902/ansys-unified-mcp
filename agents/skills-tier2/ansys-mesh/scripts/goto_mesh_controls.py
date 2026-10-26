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
    GoTo_MeshControls
    ### 2022-07-09 Compatible to ACT

    Seleciton by
    + Geometry tree selection
    + Geometry model selection
    + Mesh control selection

    Geometry types:
    + Body
    + Face
    + Edge
    + Could extending to the associated Body, Face, Edge

    Author: Louis Liu
    louis_liu2@jabil.com

    """

    import time
    import clr
    import datetime
    clr.AddReference("System.Windows.Forms ")

    ###################################
    ### Inputs for script
    ###################################
    # Is_ResetGroupMC=False
    # Is_SkipSuppressedMC=False
    # Is_GoToBodyMC=True
    # Is_GoToFaceMC=True
    # Is_GoToEdgeMC=True
    # Is_ExtendToBodySel=False
    # Is_ExtendToFaceSel=False
    # Is_ExtendToEdgeSel=False

    ###################################
    ### Inputs for ACT
    ###################################
    Is_ResetGroupMC=step.Properties['Is_ResetGroupMC'].Value
    Is_SkipSuppressedMC=step.Properties['Is_SkipSuppressedMC'].Value
    Is_GoToBodyMC=step.Properties['Is_GoToBodyMC'].Value
    Is_GoToFaceMC=step.Properties['Is_GoToFaceMC'].Value
    Is_GoToEdgeMC=step.Properties['Is_GoToEdgeMC'].Value
    Is_ExtendToBodySel=step.Properties['Is_ExtendToBodySel'].Value
    Is_ExtendToFaceSel=step.Properties['Is_ExtendToFaceSel'].Value
    Is_ExtendToEdgeSel=step.Properties['Is_ExtendToEdgeSel'].Value


    ### If the code is expired, would not execute main process.
    expireddate=datetime.date(2027,9,1)
    nowdate=datetime.datetime.now()
    datedelta=nowdate.date()-expireddate

    if datedelta.days>0:
        try:
            act_elapsed_sec = _act_time.time() - _ACT_START_TIME
            log_usage("MECH_GoToMeshControls", "1.0", act_elapsed_sec, 600)
        except:
            pass

        print("[UI_OUTPUT] " + str("Automation is expired. Please update."))
    else:
        startTime = time.time()
        
        model = ExtAPI.DataModel.Project.Model
        AllMeshObj=ExtAPI.DataModel.Project.Model.Mesh
        AllMeshCtrl=AllMeshObj.Children
        selection_obj=ExtAPI.SelectionManager.CurrentSelection
        BodyIDs=[]
        BodyFaces=[]
        BodyEdges=[]
        BodyFacesIDs=[]
        BodyEdgesIDs=[]
        cnt_geo=0
        for iGeo in selection_obj.Entities:
            if iGeo.GetType()==Ansys.ACT.Common.Geometry.GeoBodyWrapper:
                BodyIDs.append(iGeo.Id)
                cnt_geo=cnt_geo+1
                if Is_ExtendToFaceSel==True:
                    BodyFaces.extend(iGeo.Faces)
                if Is_ExtendToEdgeSel==True:
                    BodyEdges.extend(iGeo.Edges)
            elif iGeo.GetType()==Ansys.ACT.Common.Geometry.GeoFaceWrapper:
                BodyFaces.append(iGeo)
                cnt_geo=cnt_geo+1
                if Is_ExtendToBodySel==True:
                    BodyIDs.append(iGeo.Bodies[0].Id)
                if Is_ExtendToEdgeSel==True:
                    BodyEdges.extend(iGeo.Edges)
            elif iGeo.GetType()==Ansys.ACT.Common.Geometry.GeoEdgeWrapper:
                BodyEdges.append(iGeo)
                cnt_geo=cnt_geo+1
                if Is_ExtendToBodySel==True:
                    BodyIDs.append(iGeo.Bodies[0].Id)
                if Is_ExtendToFaceSel==True:
                    BodyFaces.extend(iGeo.Faces)
        for iObj in ExtAPI.DataModel.Tree.ActiveObjects:
            if iObj.GetType()==Ansys.ACT.Automation.Mechanical.Body:
                if not iObj.Suppressed:
                    BodyIDs.append(iObj.GetGeoBody().Id)
                    cnt_geo=cnt_geo+1
                    if Is_ExtendToFaceSel==True:
                        BodyFaces.extend(iObj.GetGeoBody().Faces)
                    if Is_ExtendToEdgeSel==True:
                        BodyEdges.extend(iObj.GetGeoBody().Edges)
            elif not iObj.GetType().ToString().IndexOf('Ansys.ACT.Automation.Mechanical.MeshControls')==-1:
                # To make sure iObj.Location.Entities is available
                # For some MC, no Location, e.g., Contact Sizing
                test=False
                try:
                    test=iObj.Location.Entities 
                    test=True
                except:
                    test=False
                # If iObj.Location.Entities is available, then go ahead.
                if test==True:
                    for iGeo in iObj.Location.Entities:
                        if iGeo.GetType()==Ansys.ACT.Common.Geometry.GeoBodyWrapper:
                            BodyIDs.append(iGeo.Id)
                            cnt_geo=cnt_geo+1
                            if Is_ExtendToFaceSel==True:
                                BodyFaces.extend(iGeo.Faces)
                            if Is_ExtendToEdgeSel==True:
                                BodyEdges.extend(iGeo.Edges)
                        elif iGeo.GetType()==Ansys.ACT.Common.Geometry.GeoFaceWrapper:
                            BodyFaces.append(iGeo)
                            cnt_geo=cnt_geo+1
                            if Is_ExtendToBodySel==True:
                                BodyIDs.append(iGeo.Bodies[0].Id)
                            if Is_ExtendToEdgeSel==True:
                                BodyEdges.extend(iGeo.Edges)
                        elif iGeo.GetType()==Ansys.ACT.Common.Geometry.GeoEdgeWrapper:
                            BodyEdges.append(iGeo)
                            cnt_geo=cnt_geo+1
                            if Is_ExtendToBodySel==True:
                                BodyIDs.append(iGeo.Bodies[0].Id)
                            if Is_ExtendToFaceSel==True:
                                BodyFaces.extend(iGeo.Faces)
                
        for ifs in BodyFaces:
            BodyFacesIDs.append(ifs.Id)
        for iedge in BodyEdges:
            BodyEdgesIDs.append(iedge.Id)
        
        AllGeoIDs=[]
        if Is_GoToBodyMC==True:
            AllGeoIDs.extend(BodyIDs)
        if Is_GoToFaceMC==True:
            AllGeoIDs.extend(BodyFacesIDs)
        if Is_GoToEdgeMC==True:
            AllGeoIDs.extend(BodyEdgesIDs)

        ## To avoid active object is mesh, so make NS as active object on purpose.
        # ExtAPI.DataModel.Project.Model.NamedSelections.Activate()   ## active_object = NamedSelections
        MeshTypes=[Ansys.ACT.Automation.Mechanical.MeshControls.Sizing, Ansys.ACT.Automation.Mechanical.MeshControls.FaceMeshing, Ansys.ACT.Automation.Mechanical.MeshControls.AutomaticMethod]
        if Is_ResetGroupMC==True:
            with Transaction(True):
                for iMC in AllMeshCtrl:
                    if iMC.GetType()==Ansys.ACT.Automation.Mechanical.TreeGroupingFolder:
                        if iMC.Name.ToLower().IndexOf('Scr_XXX'.ToLower())==-1:
                            iMC.Ungroup()
            with Transaction(True):
                AllMeshObj.GroupAllSimilarChildren()
        elif cnt_geo==0:
            try:
                act_elapsed_sec = _act_time.time() - _ACT_START_TIME
                log_usage("MECH_GoToMeshControls", "1.0", act_elapsed_sec, 600)
            except:
                pass

            print("[UI_OUTPUT] " + str("Nothing was selected!"))
        else:
            with Transaction(True):
                MC_last=None
                for iMC in AllMeshCtrl:
                    if iMC.GetType()==Ansys.ACT.Automation.Mechanical.TreeGroupingFolder:
                        continue
                    else:#elif iMC.GetType() in MeshTypes:
                        try:
                            for i in iMC.Location.Ids:
                                if i in AllGeoIDs:
                                    if not Is_SkipSuppressedMC==True or not iMC.Suppressed==True:
                                        MC_last=iMC
                                        ExtAPI.DataModel.InternalObject["tree"].AddActiveObjectID(iMC.ObjectId)
                        except:
                            None
            if MC_last==None:
                try:
                    act_elapsed_sec = _act_time.time() - _ACT_START_TIME
                    log_usage("MECH_GoToMeshControls", "1.0", act_elapsed_sec, 600)
                except:
                    pass

                print("[UI_OUTPUT] " + str('No associated mesh control.'))
            else:
                # we need model and the object under which you want to created the folder, mesh.ObjectId in this case
                myfolder = model.InternalObject.AddTreeGroupingFolder(AllMeshObj.ObjectId)
                myfolder.Name = "Scr_GoToMeshControls"
                ExtAPI.DataModel.Tree.Refresh()
                MC_last.Activate()
                endTime = time.time()
                # print("Done, took {} seconds".format(endTime - startTime))
                try:
                    act_elapsed_sec = _act_time.time() - _ACT_START_TIME
                    log_usage("MECH_GoToMeshControls", "1.0", act_elapsed_sec, 600)
                except:
                    pass

                #print("[UI_OUTPUT] " + str("Done, took {} seconds".format(endTime - startTime)))