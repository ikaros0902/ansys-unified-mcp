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
    Automatic Joint Creation from SpaceClaim Named Selections
    Integrated ACT Extension
    
    Author: Based on Louis Liu's framework
    Version: 2024-11-13
    """
    
    import time
    import clr
    import datetime
    clr.AddReference("System.Windows.Forms")
    
    startTime = time.time()
    
    ###################################
    ### Get ACT Properties
    ###################################
    # Connection Method
    if step.Properties['ConnectionMethod'].Value == 'Remote Point':
        ConnectionMethod = 'RemotePoint'
    elif step.Properties['ConnectionMethod'].Value == 'Joint Fixed':
        ConnectionMethod = 'JointFixed'
    elif step.Properties['ConnectionMethod'].Value == 'Joint Revolute':
        ConnectionMethod = 'JointRevolute'
    elif step.Properties['ConnectionMethod'].Value == 'Joint Cylindrical':
        ConnectionMethod = 'JointCylindrical'
    
    # Named Selection Settings
    RMP_Name_Prefix = step.Properties['RMP_Name_Prefix'].Value
    Mobile_suffix = step.Properties['Mobile_suffix'].Value if 'Mobile_suffix' in step.Properties else "_Mobile"
    Reference_suffix = step.Properties['Reference_suffix'].Value if 'Reference_suffix' in step.Properties else "_Reference"
    
    # Operation Settings
    Del_execution = step.Properties['Del_execution'].Value
    Promote_To_RemotePoint = step.Properties['Promote_To_RemotePoint'].Value
    
    # Group Names
    Joints_grp_name = step.Properties['Joints_grp_name'].Value
    
    ###################################
    ### Check Expiration
    ###################################
    expireddate=datetime.date(2027,9,1)
    nowdate = datetime.datetime.now()
    datedelta = nowdate.date() - expireddate
    
    if datedelta.days > 0:
        try:
            act_elapsed_sec = _act_time.time() - _ACT_START_TIME
            log_usage("MECH_RM_Joint_Creation", "1.0", act_elapsed_sec, 4500)
        except:
            pass

        print("[UI_OUTPUT] " + str("Automation is expired. Please update."))
        return
    
    ###################################
    ### Initialize Counters
    ###################################
    Cnt_RMP_Create = 0
    Cnt_RMP_del = 0
    Cnt_Joint_Create = 0
    Cnt_Joint_del = 0
    Cnt_Joint_Promoted = 0
    
    ###################################
    ### Main Process
    ###################################
    
    if ConnectionMethod == 'RemotePoint':
        # ============================================
        # Remote Point Creation (Original ACT Logic)
        # ============================================
        with Transaction(True):
            # Delete existing Remote Points
            if Del_execution:
                ExtAPI.DataModel.Project.Model.RemotePoints.Activate()
                RM_grp_existing = ExtAPI.DataModel.Project.Model.RemotePoints.Children
                for rmp in RM_grp_existing:
                    if rmp.Name.startswith(RMP_Name_Prefix):
                        if 'Reference Remote Point' not in rmp.Name and 'Mobile Remote Point' not in rmp.Name:
                            rmp.Delete()
                            Cnt_RMP_del += 1
            
            # Create new Remote Points
            RM_grp_existing = ExtAPI.DataModel.Project.Model.RemotePoints.Children
            for ns in ExtAPI.DataModel.Project.Model.NamedSelections.Children:
                if ns.Name == 'Scr_RMgrp_ALL' or '_Mobile' in ns.Name or '_Reference' in ns.Name:
                    continue
                if ns.Name.startswith(RMP_Name_Prefix):
                    # Check if already exists
                    RM_done = False
                    for rmp in RM_grp_existing:
                        if rmp.Name == ns.Name:
                            RM_done = True
                            break
                    
                    if not RM_done:
                        # Check entity validity
                        if ns.Entities.Count <= 1:
                            continue
                        
                        list_bodies = []
                        for k_entity in ns.Entities:
                            try:
                                if k_entity.Bodies is not None and k_entity.Bodies.Count > 0:
                                    list_bodies.append(k_entity.Bodies[0].Id)
                            except:
                                pass
                        set_bodies = set(list_bodies)
                        
                        # Skip single solid part
                        if len(set_bodies) == 1 and ns.Entities[0].Bodies[0].Volume != 0:
                            continue
                        
                        # Create Remote Point
                        remote_points = ExtAPI.DataModel.Project.Model.RemotePoints
                        rmp = remote_points.AddRemotePoint()
                        rmp.Name = ns.Name
                        rmp.ScopingMethod = GeometryDefineByType.Component
                        rmp.Location = ns
                        rmp.Behavior = LoadBehavior.Rigid
                        rmp.DOFSelection = RemotePointDOFSelectionType.Manual
                        rmp.XComponent = ActiveOrInactive.Active
                        rmp.YComponent = ActiveOrInactive.Active
                        rmp.ZComponent = ActiveOrInactive.Active
                        rmp.RotationX = ActiveOrInactive.Active
                        rmp.RotationY = ActiveOrInactive.Active
                        rmp.RotationZ = ActiveOrInactive.Active
                        Cnt_RMP_Create += 1
    
    else:
        # ============================================
        # Joint Creation (Dual-Track Architecture)
        # ============================================
        cnt_underdefined_revolute = 0
        with Transaction(True):
            # Step 1: Create or Find Joint Group
            Scr_Joints_grp = None
            for connection_grp in ExtAPI.DataModel.Project.Model.Connections.Children:
                if connection_grp.Name == Joints_grp_name:
                    Scr_Joints_grp = connection_grp
                    Scr_Joints_grp.Activate()
                    break
            
            if Scr_Joints_grp is None:
                Scr_Joints_grp = ExtAPI.DataModel.Project.Model.Connections.AddConnectionGroup()
                Scr_Joints_grp.Name = Joints_grp_name
            
            # Step 2: Delete Existing Joints
            if Del_execution:
                existing_joints = list(Scr_Joints_grp.Children)
                for joint in existing_joints:
                    if joint.Name.startswith(RMP_Name_Prefix):
                        joint_name = joint.Name
                        joint.Delete()
                        Cnt_Joint_del += 1
                        
                        # Delete corresponding Remote Points
                        ref_rmp_name = joint_name + " - Reference Remote Point"
                        mobile_rmp_name = joint_name + " - Mobile Remote Point"
                        
                        for rmp in ExtAPI.DataModel.GetObjectsByName(ref_rmp_name):
                            rmp.Delete()
                            Cnt_RMP_del += 1
                        
                        for rmp in ExtAPI.DataModel.GetObjectsByName(mobile_rmp_name):
                            rmp.Delete()
                            Cnt_RMP_del += 1
            
            # Determine Joint Type
            if ConnectionMethod == 'JointFixed':
                JointType = Ansys.Mechanical.DataModel.Enums.JointType.Fixed
            elif ConnectionMethod == 'JointRevolute':
                JointType = Ansys.Mechanical.DataModel.Enums.JointType.Revolute
            elif ConnectionMethod == 'JointCylindrical':
                JointType = Ansys.Mechanical.DataModel.Enums.JointType.Cylindrical
            else:
                JointType = Ansys.Mechanical.DataModel.Enums.JointType.Revolute

            # Step 3: Iterate Named Selections and Create Joints
            all_named_selections = list(ExtAPI.DataModel.Project.Model.NamedSelections.Children)
            
            for ns in all_named_selections:
                if not ns.Name.startswith(RMP_Name_Prefix):
                    continue
                if ns.Name == 'Scr_RMgrp_ALL' or '_Mobile' in ns.Name or '_Reference' in ns.Name:
                    continue
                
                if ns.Entities.Count <= 1:
                    print("Skip: Group {} has <= 1 entity".format(ns.Name))
                    continue
                
                # Partition entities strictly by entity.Bodies[0].Id (strictly avoid Part.Id)
                body_entities_map = []
                for entity in ns.Entities:
                    try:
                        if entity.Bodies is not None and entity.Bodies.Count > 0:
                            b_id = entity.Bodies[0].Id
                        else:
                            continue
                    except:
                        continue
                    
                    found = False
                    for entry in body_entities_map:
                        if entry[0] == b_id:
                            entry[1].append(entity)
                            found = True
                            break
                    if not found:
                        body_entities_map.append((b_id, [entity]))
                
                # Exactly 2 distinct bodies required
                if len(body_entities_map) == 2:
                    ref_entities = body_entities_map[0][1]
                    mob_entities = body_entities_map[1][1]
                    
                    try:
                        joint = Scr_Joints_grp.AddJoint()
                        joint.Name = ns.Name
                        joint.Type = JointType
                        joint.ConnectionType = JointScopingType.BodyToBody
                        
                        ref_selection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
                        ref_selection.Ids = [e.Id for e in ref_entities]
                        joint.ReferenceLocation = ref_selection
                        
                        mobile_selection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
                        mobile_selection.Ids = [e.Id for e in mob_entities]
                        joint.MobileLocation = mobile_selection
                        
                        Cnt_Joint_Create += 1
                        print("Created Joint from group: {}".format(ns.Name))
                    except Exception as e:
                        print("Error creating Joint {}: {}".format(ns.Name, str(e)))
                else:
                    print("Skip: Group {} belongs to {} bodies (requires exactly 2 bodies)".format(ns.Name, len(body_entities_map)))

        # Step 4: Refresh Model Tree to update joint states
        ExtAPI.DataModel.Tree.Refresh()

        # Step 5: Inspect UnderDefined joints and enforce safety promote policy
        existing_joints = list(Scr_Joints_grp.Children)
        for joint in existing_joints:
            if joint.ObjectState == ObjectState.UnderDefined:
                if joint.Type == Ansys.Mechanical.DataModel.Enums.JointType.Revolute or joint.Type == Ansys.Mechanical.DataModel.Enums.JointType.Cylindrical:
                    cnt_underdefined_revolute += 1

        # Strictly block destructive Promote for Revolute and Cylindrical joints
        # Only allow Promote when ConnectionMethod is RemotePoint and Promote_To_RemotePoint is True
        if ConnectionMethod == 'RemotePoint' and Promote_To_RemotePoint:
            with Transaction(True):
                for joint in existing_joints:
                    if joint.ObjectState == ObjectState.UnderDefined:
                        try:
                            joint.Activate()
                            joint.PromoteToRemotePoint()
                            Cnt_Joint_Promoted += 1
                            print("Promoted: {}".format(joint.Name))
                        except Exception as e:
                            print("Promote failed for {}: {}".format(joint.Name, str(e)))
            ExtAPI.DataModel.Tree.Refresh()
        else:
            if cnt_underdefined_revolute > 0:
                print("Notice: Retained {} UnderDefined Revolute/Cylindrical joint(s) for solver computation without demotion.".format(cnt_underdefined_revolute))
    
    ###################################
    ### Display Results
    ###################################
    endTime = time.time()
    elapsed_time = round(endTime - startTime, 1)
    
    result_msg = "Completed in {} seconds\n\n".format(elapsed_time)
    
    if ConnectionMethod == 'RemotePoint':
        result_msg += "Remote Points:\n"
        result_msg += "   Deleted: {}\n".format(Cnt_RMP_del)
        result_msg += "   Created: {}\n".format(Cnt_RMP_Create)
        if Promote_To_RemotePoint and Cnt_Joint_Promoted > 0:
            result_msg += "   Promoted to Remote Point: {}\n".format(Cnt_Joint_Promoted)
    else:
        result_msg += "Joints:\n"
        result_msg += "   Deleted: {}\n".format(Cnt_Joint_del)
        result_msg += "   Created: {}\n".format(Cnt_Joint_Create)
        if cnt_underdefined_revolute > 0:
            result_msg += "\nNotice: Retained {} UnderDefined Revolute/Cylindrical Joint(s) for solver computation without demotion.\n".format(cnt_underdefined_revolute)
        if Cnt_RMP_del > 0:
            result_msg += "\nRemote Points Deleted: {}".format(Cnt_RMP_del)
    
    try:
        act_elapsed_sec = _act_time.time() - _ACT_START_TIME
        log_usage("MECH_RM_Joint_Creation", "1.0", act_elapsed_sec, 4500)
    except:
        pass

    print("[UI_OUTPUT] " + str(result_msg))
    print("\n========== Completed ==========")