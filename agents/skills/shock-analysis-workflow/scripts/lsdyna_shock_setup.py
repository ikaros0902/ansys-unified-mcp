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
    LS-Dyna shock setup
        - Add LS-DYNA analysis
        - Analysis Settings
        - Add load cases
        - Write/Ouput .k file
    ### 2022-05-10 Compatible to ACT

    Required Naming Rules
    1. Upper case or Lower case doesn't matter. The script deems upper case and lower case the same.
    2.
        Component:
            Shock fixtures: "scr","fixture" & face/orientation are required
            for examples:"scr_Bottom_fixture_01" or "Scr_left_fixture"
        Named Selection:
            "Scr_All_Bodies": All bodies will be applied for initial velocity's geometry scoping.
            "Scr_fixture_frontback": "scr","fixture" & face/orientation are required
            "Scr_fixture_L10.5": This is for applying velocity change boundary in L10.5
            for examples:"Scr_Fixture_top-BoTTom" or "Scr_fixture_left" or "Scr_fixture_frontback"
    3. Shock_faces as script input below (for script only. If ACT, skip this.)
        Shock_faces=["+Y_top","-y_boTtom","+X_right","-X_left","+z_front","-Z_back"]
        The format is 
        1st: "+" or "-"
        2nd: "X" or "Y" or "Z"
        3rd: "_" (underline)
        4th: face/orientation, e.g., "top", "bottom", "left", "right", "front", "back"

    Author: Louis Liu
    louis_liu2@jabil.com
    """
    import time
    import os
    import clr
    import datetime
    import math
    clr.AddReference("System.Windows.Forms ")

    startTime = time.time()
    
    ###################################
    ### Inputs for script
    ###################################
    # Shock_type=0 ## 0:L10, 1:L10.5
    # Shock_wave_list=['SquareWave','HalfSine']
    # Shock_wave=0 ## 0:SW, 1:HS
    # Shock_G=71 ## Shock G level
    # SWShock_Vcips=152 ## Square shock profile velocity change in ips
    # HSShock_Ts=0.002 ## Half-sine shock duration in second
    # ShockHist_pts=50 ## Total data points for velocity inputs
    #Shock_faces=["+Y_Top","-Y_Bottom","+X_Right","-X_Left","+Z_Front","-Z_Back"]
    #Shock_faces=["+Y_Top","+X_Right"]
    ### e.g., Shock_faces=["+Y_Top","-Y_Bottom"]
    #Shock_faces=["+x_right"]
    #Shock_faces=["-X_Left"]
    #Shock_faces=["+y_toP"]
    #Shock_faces=["-Y_Bottom"]
    #Shock_faces=["+Z_Front"]
    #Shock_faces=["-Z_Back"]
    #AddPtT0=True  # Add one more point for t=0
    #velsetupdate=True
    #Anssetupdate=True
    #Outputkfile=True
    #kfile_dir="D:\\Shock_KFiles"     ## The folder directory for .K files

    ###################################
    ### Inputs for ACT
    ###################################
    if step.Properties['Shock_type'].Value=='L10':
        Shock_type=0
    elif step.Properties['Shock_type'].Value=='L10.5/L11':
        Shock_type=1
    if step.Properties['Shock_wave_list'].Value=='Square Wave':
        Shock_wave=0
    elif step.Properties['Shock_wave_list'].Value=='Half Sine':
        Shock_wave=1
    Shock_G=step.Properties['Shock_wave_list'].Properties['Shock_G'].Value
    SWShock_Vcips=step.Properties['Shock_wave_list'].Properties['SWShock_Vcips'].Value
    HSShock_Ts=step.Properties['Shock_wave_list'].Properties['HSShock_Ts'].Value
    ShockHist_pts=step.Properties['Shock_wave_list'].Properties['ShockHist_pts'].Value
    top_str=step.Properties['Axis of top'].Value+'_Top'
    bottom_str=step.Properties['Axis of bottom'].Value+'_Bottom'
    right_str=step.Properties['Axis of right'].Value+'_Right'
    left_str=step.Properties['Axis of left'].Value+'_Left'
    front_str=step.Properties['Axis of front'].Value+'_Front'
    back_str=step.Properties['Axis of back'].Value+'_Back'
    Shock_faces=[]
    if step.Properties['Check_top'].Value==True: Shock_faces.append(top_str)
    if step.Properties['Check_bottom'].Value==True: Shock_faces.append(bottom_str)
    if step.Properties['Check_right'].Value==True: Shock_faces.append(right_str)
    if step.Properties['Check_left'].Value==True: Shock_faces.append(left_str)
    if step.Properties['Check_front'].Value==True: Shock_faces.append(front_str)
    if step.Properties['Check_back'].Value==True: Shock_faces.append(back_str)
    velsetupdate=step.Properties['velsetupdate'].Value
    AddPtT0=step.Properties['AddPtT0'].Value
    Anssetupdate=step.Properties['Anssetupdate'].Value
    Outputkfile=step.Properties['Outputkfile'].Value
    kfile_dir=step.Properties['kfile_dir'].Value
    #ExtAPI.Log.WriteMessage(kfile_dir)
    
    ### Do for pointed analysis by index#
    #analysis=ExtAPI.DataModel.Project.Model.Analyses[0]
    #analysis_settings=DataModel.GetObjectsByName("Analysis Settings")[0]

    def GenerateHSShockAVDHist(G,Ts,pts=20,axis_dir="-"):
    # G: Half-sine shock G level
    # Ts: shock duration in second
    # pts: points for history list
    # axis_dir: "+" or "-" will determine G in positive or negative
        dt=Ts/pts
        TList=list()
        w=2*math.pi/2/Ts
        AccList=list()
        VelList=list()
        DisList=list()
        if axis_dir=="+":
            G=G*(-1)
        for i in range(pts+1):
            t=i*dt
            TList.append(t)
            AccList.append(G*sin(w*t))
            VelList.append(G*(-1)*9806.65/w*cos(w*t)-G*9806.65/w)
            DisList.append(G*(-1)*9806.65/w/w*sin(w*t)-G*9806.65/w*t)
        return TList,AccList,VelList,DisList,dt

    def GenerateSWShockAVDHist(G,Vcips,t1=0.0,pts=20,axis_dir="-"):
    # G: SquareWave shock G level
    # Vcips: Velocity change in per second(ips)
    # t1: climbing duration for trapezoid shock(Not work yet, using 0.0 by default)
    # pts: points for history list
    # axis_dir: "+" or "-" will determine G in positive or negative
        Ts=Vcips*2.54/100/G/9.80665
        dt=Ts/pts
        TList=list()
        AccList=list()
        VelList=list()
        DisList=list()
        if axis_dir=="+":
            G=G*(-1)
        for i in range(pts+1):
            t=i*dt
            TList.append(t)
            AccList.append(G)
            VelList.append(G*(-1)*9806.65*(Ts-t))
            DisList.append(G*(-1)*9806.65*(Ts*t-t*t/2))
        return TList,AccList,VelList,DisList,dt

    def ShockFixtureSetup(axis_str):
        gm = Model.Geometry
        with Transaction(True):
            for Assembly in ExtAPI.DataModel.GeoData.Assemblies:
                for Part in Assembly.Parts:
                    for Body in Part.Bodies:
                        a = Body.Name
                        if Shock_type==0:
                            if axis_str[3:].ToLower()=="top": axis_str2="bottom"
                            elif axis_str[3:].ToLower()=="bottom": axis_str2="top"
                            elif axis_str[3:].ToLower()=="left": axis_str2="right"
                            elif axis_str[3:].ToLower()=="right": axis_str2="left"
                            elif axis_str[3:].ToLower()=="front": axis_str2="back"
                            elif axis_str[3:].ToLower()=="back": axis_str2="front"
                            if a.ToLower().IndexOf("scr")!=-1 and a.ToLower().IndexOf("fixture")!=-1 and (a.ToLower().IndexOf(axis_str[3:].ToLower())!=-1 or a.ToLower().IndexOf(axis_str2.ToLower())!=-1):
                                gm.GetBody(Body).Suppressed=False  # Gives you the Tree object
                            elif a.ToLower().IndexOf("scr")!=-1 and a.ToLower().IndexOf("fixture")!=-1 and a.ToLower().IndexOf(axis_str[3:].ToLower())==-1:
                                gm.GetBody(Body).Suppressed=True
                        elif Shock_type==1:
                            if a.ToLower().IndexOf("scr")!=-1 and a.ToLower().IndexOf("fixture")!=-1:
                                gm.GetBody(Body).Suppressed=True  # Gives you the Tree object                    
        #ExtAPI.DataModel.Tree.Refresh()
        try:
            Model.NamedSelections.GenerateAllNamedSelections()    # refresh all NameSelections
        except:
            print("NamedSelections.GenerateAllNamedSelections() doesn't work in 2021R1")

    def Main(args):
        global analysis,analysis_settings
        ### Do for Active Analysis
        ### analysis=Tree.FirstActiveObject # Get Active object
        actobj=Tree.FirstActiveObject # Get Active object
        objns=str(actobj.GetType())
        if not objns.IndexOf('Analysis')==-1:
            analysis=actobj
            if analysis.Properties[6].StringValue.IndexOf('LSDYNA')==-1:
                try:
                    act_elapsed_sec = _act_time.time() - _ACT_START_TIME
                    log_usage("MECH_LSDYNA_Shock", "1.0", act_elapsed_sec, 1800)
                except:
                    pass

                print("[UI_OUTPUT] " + str('Error: This automation is for LS-Dyna analysis only.'))
        else:
            for i in range(3):
                actobj=actobj.Parent
                objns=str(actobj.GetType())
                if not objns.IndexOf('Analysis')==-1:
                    analysis=actobj
                    if analysis.Properties[6].StringValue.IndexOf('LSDYNA')==-1:
                        try:
                            act_elapsed_sec = _act_time.time() - _ACT_START_TIME
                            log_usage("MECH_LSDYNA_Shock", "1.0", act_elapsed_sec, 1800)
                        except:
                            pass

                        print("[UI_OUTPUT] " + str('Error: This automation is for LS-Dyna analysis only.'))
                    break
                
        for i in analysis.Children:
            if not i.Name.IndexOf('Analysis Settings')==-1:
                analysis_settings=i

        """
        Analysis Settings
        """
        if Anssetupdate==True:
            temp=list()
            for i in analysis_settings.Properties:
                temp.append(str(i))
            
            ## Change some solver settings
            analysis_settings.Activate()
            analysis_settings.Properties[temp.index('Step Controls/Endtime')].InternalValue=step.Properties['StepControlsEndtime'].Value
            if step.Properties['Memory Allocation'].Value=='Program Controlled': temp_input=0 ## 0:Program Controlled, 1:Manual
            elif step.Properties['Memory Allocation'].Value=='Manual': temp_input=1
            analysis_settings.Properties[temp.index('Memory Management/Memory Allocation')].InternalValue=temp_input ## 1:Manual
            analysis_settings.Properties[temp.index('Memory Management/--- Value')].InternalValue=step.Properties['Memory Value'].Value
            analysis_settings.Properties[temp.index('Memory Management/NCPUS')].InternalValue=step.Properties['NCPUS'].Value
            #analysis_settings.Properties[temp.index('Memory Management/Processing Type')].InternalValue=1 ## 1:SMP
            if step.Properties['Solver Precision'].Value=='Program Controlled': temp_input=0 ## 0:DoubleProgram Controlled,1:Single,2:Double
            elif step.Properties['Solver Precision'].Value=='Single': temp_input=1
            elif step.Properties['Solver Precision'].Value=='Double': temp_input=2
            analysis_settings.Properties[temp.index('Solver Controls/Solver Precision')].InternalValue=temp_input 
            analysis_settings.Properties[temp.index('Output Controls/Binary File Size Scale Factor')].InternalValue=step.Properties['BinaryFileSizeScaleFactor'].Value
            if step.Properties['OutputControlsStress'].Value=='No': temp_input=0 ## 0:No, 1:Yes
            elif step.Properties['OutputControlsStress'].Value=='Yes': temp_input=1
            analysis_settings.Properties[temp.index('Output Controls/Stress')].InternalValue=temp_input
            if step.Properties['OutputControlsStrain'].Value=='No': temp_input=0 ## 0:No, 1:Yes
            elif step.Properties['OutputControlsStrain'].Value=='Yes': temp_input=1
            analysis_settings.Properties[temp.index('Output Controls/Strain')].InternalValue=temp_input ## 1:Yes
            if step.Properties['OutputControlsPlasticStrain'].Value=='No': temp_input=0 ## 0:No, 1:Yes
            elif step.Properties['OutputControlsPlasticStrain'].Value=='Yes': temp_input=1
            analysis_settings.Properties[temp.index('Output Controls/Plastic Strain')].InternalValue=temp_input ## 1:Yes
            if step.Properties['OutputControlsCalculateResultsAt'].Value=='Program Controlled': temp_input=0
            elif step.Properties['OutputControlsCalculateResultsAt'].Value=='Equally Spaced Points': temp_input=1
            elif step.Properties['OutputControlsCalculateResultsAt'].Value=='Time': temp_input=2
            analysis_settings.Properties[temp.index('Output Controls/Calculate Results At')].InternalValue=temp_input ## 0:No , 1:Equally Spaced Points
            analysis_settings.Properties[temp.index('Output Controls/--- Value')].InternalValue=step.Properties['OutputControlsValue'].Value
            if step.Properties['TimeHistoryOutputControlsCalculateResultsAt'].Value=='No': temp_input=0
            elif step.Properties['TimeHistoryOutputControlsCalculateResultsAt'].Value=='Equally Spaced Points': temp_input=1
            analysis_settings.Properties[temp.index('Time History Output Controls/Calculate Results At')].InternalValue=temp_input ## 0:No , 1:Equally Spaced Points
            analysis_settings.Properties[temp.index('Time History Output Controls/--- Value')].InternalValue=step.Properties['TimeHistoryOutputControlsValue'].Value
            
            DataModel.Tree.Refresh()
        
        """
        Add load cases setting
            - Initial velocity
            - velocity change profile
        """
        AllNS=ExtAPI.DataModel.Project.Model.GetChildren(DataModelObjectCategory.NamedSelection, True) #Getting all namedselections
        MeshBatchSettingSave=ExtAPI.DataModel.Project.Model.Mesh.MeshBasedConnection    # Record original Mesh Batch connection setting
        AllICs_Names=list()
        for i in analysis.InitialConditions:
            AllICs_Names.append(i.Name.ToLower())
        AllAnaChd_Names=list()
        for i in analysis.Children:
            AllAnaChd_Names.append(i.Name.ToLower())
        if velsetupdate==True or Outputkfile==True:
            for i_face in range(len(Shock_faces)):
                ShockFixtureSetup(Shock_faces[i_face])  # Setup fixtures
                with Transaction(True):
                    analysis.Solution.Activate() ## Purpose is to move screen to make vel and ICs visible
                    if velsetupdate==True:
                        if Shock_wave==0: # 0 meaning SW shock
                            Shock_tAVD=GenerateSWShockAVDHist(Shock_G,SWShock_Vcips,pts=ShockHist_pts,axis_dir=Shock_faces[i_face][0])
                        elif Shock_wave==1: # 1 meaning HS shock
                            Shock_tAVD=GenerateHSShockAVDHist(Shock_G,HSShock_Ts,pts=ShockHist_pts,axis_dir=Shock_faces[i_face][0])
                        if AddPtT0==True:
                            Shock_tAVD[0].append(Shock_tAVD[0][-1]+Shock_tAVD[4])
                            Shock_tAVD[1].insert(0,0)
                            Shock_tAVD[2].insert(0,Shock_tAVD[2][0])
                            Shock_tAVD[3].insert(0,Shock_tAVD[3][0])
                        Initial_velocity_str=str(Shock_tAVD[2][0])+" [mm sec^-1]"
                        Ini_vel_name="Scr_Initial_vel_"+str(Shock_faces[i_face])
                        if AllICs_Names.IndexOf(Ini_vel_name.ToLower())==-1:
                            Ini_vel=analysis.AddInitialVelocity()
                        elif AllICs_Names.IndexOf(Ini_vel_name.ToLower())!=-1:
                            Ini_vel=analysis.InitialConditions[AllICs_Names.IndexOf(Ini_vel_name.ToLower())]
                        Ini_vel.Name=Ini_vel_name
                        for i_NS in AllNS:
                            NS_IniVel="Scr_All_Bodies"
                            #NS_IniVel2="All_Bodies"
                            if i_NS.Name[0:len(NS_IniVel)].ToLower() == NS_IniVel.ToLower(): #or i_NS.Name[0:len(NS_IniVel2)].ToLower() == NS_IniVel2.ToLower():
                                #selection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
                                #selection.Ids= i_NS.Location.Ids
                                if Ini_vel.Location.Name!=i_NS.Name:
                                    Ini_vel.Location=i_NS
                                break
                        Ini_vel.DefineBy=LoadDefineBy.Components
                        exec_string="Ini_vel."+str(Shock_faces[i_face][1]).ToUpper()+"Component=Quantity(Initial_velocity_str)"
                        #Ini_vel.YComponent = Quantity(Initial_velocity_str)
                        exec(exec_string) in globals(), locals()
                        vel_Name="Scr_Velocity_"+str(Shock_faces[i_face])
                        if AllAnaChd_Names.IndexOf(vel_Name.ToLower())==-1:
                            vel=analysis.AddVelocity()
                        elif AllAnaChd_Names.IndexOf(vel_Name.ToLower())!=-1:
                            vel=analysis.Children[AllAnaChd_Names.IndexOf(vel_Name.ToLower())]
                        vel.Name=vel_Name
                        for i_NS in AllNS:
                            if Shock_type==0: #L10 shock                        
                                if i_NS.Name.ToLower().IndexOf("scr")!=-1 and i_NS.Name.ToLower().IndexOf("fixture")!=-1 and i_NS.Name.ToLower().IndexOf(Shock_faces[i_face][3:].ToLower())!=-1:
                                    vel.Location=i_NS
                                    break
                            elif Shock_type==1: #L10.5 shock
                                if i_NS.Name.ToLower().IndexOf("scr")!=-1 and i_NS.Name.ToLower().IndexOf("fixture")!=-1 and i_NS.Name.ToLower().IndexOf("l10.5")!=-1:
                                    vel.Location=i_NS
                                    break
                        vel.DefineBy=LoadDefineBy.Components
                        for i_XYZ in ["X","Y","Z"]:
                            #vel.XComponent.Inputs[0].DiscreteValues=[Quantity(str(tt)+"[s]") for tt in Shock_tAVD[0]]
                            #vel.XComponent.Output.DiscreteValues=[Quantity(str(tt)+"[mm/s]") for tt in Shock_tAVD[2]]
                            exec_string1="vel."+i_XYZ.ToUpper()+"Component.Inputs[0].DiscreteValues=[Quantity(str(tt)+'[s]') for tt in Shock_tAVD[0]]"
                            exec(exec_string1) in globals(), locals()
                            if i_XYZ.ToLower()==str(Shock_faces[i_face][1]).ToLower():
                                exec_string2="vel."+i_XYZ.ToUpper()+"Component.Output.DiscreteValues=[Quantity(str(tt)+'[mm/s]') for tt in Shock_tAVD[2]]"
                            else:
                                exec_string2="vel."+i_XYZ.ToUpper()+"Component.Output.DiscreteValues=[Quantity('0.0[mm/s]') for tt in Shock_tAVD[2]]"
                            exec(exec_string2) in globals(), locals()
                    ## Keep required items for the pointed shock face and suppress unrequired items for
                    ## - Initial velocity
                    ## - Velocity
                    for i in analysis.InitialConditions:
                        if i.Name[0:len("Scr_Initial_vel_")]=="Scr_Initial_vel_" and i.Name.ToLower().IndexOf(Shock_faces[i_face][0:2].ToLower())!=-1:
                            i.Suppressed=False
                        elif i.Name[0:len("Scr_Initial_vel_")]=="Scr_Initial_vel_" and i.Name.ToLower().IndexOf(Shock_faces[i_face][0:2].ToLower())==-1:
                            i.Suppressed=True
                    for i in analysis.Children:
                        if i.Name[0:len("Scr_Velocity_")]=="Scr_Velocity_" and i.Name.ToLower().IndexOf(Shock_faces[i_face][0:2].ToLower())!=-1:
                            i.Suppressed=False
                        elif i.Name[0:len("Scr_Velocity_")]=="Scr_Velocity_" and i.Name.ToLower().IndexOf(Shock_faces[i_face][0:2].ToLower())==-1:
                            i.Suppressed=True
                ## With Transaction End
                
                ## Write/Ouput LS-Dyna .k file
                #kfile_dir
                if Outputkfile==True:
                    if os.path.exists(kfile_dir+"\\")==False:
                        try:
                            os.mkdir(kfile_dir+"\\")
                        except:
                            print("failed")
                    if os.path.exists(kfile_dir+"\\"+str(Shock_faces[i_face])+"\\")==False:
                        try:
                            os.mkdir(kfile_dir+"\\"+str(Shock_faces[i_face])+"\\")
                        except:
                            print("failed")
                    kfile_str=kfile_dir+"\\"+str(Shock_faces[i_face])+"\\"+str(Shock_faces[i_face])+".k"
                    if MeshBatchSettingSave==True:
                        if ExtAPI.DataModel.Project.Model.Mesh.ObjectState==ObjectState.NotSolved:
                            if ExtAPI.DataModel.Project.Model.Mesh.MeshBasedConnection==True:  # If Batch connection = Yes
                                ExtAPI.DataModel.Project.Model.Mesh.MeshBasedConnection=False   # Set Batch connection = No
                            with Transaction(True):
                                try:
                                    ExtAPI.DataModel.Project.Model.Mesh.InternalObject.ForceUpdateMeshStates()
                                except:
                                    None
                                ExtAPI.DataModel.Tree.Refresh()
                        if ExtAPI.DataModel.Project.Model.Mesh.ObjectState==ObjectState.NotSolved:
                            with Transaction(True):
                                try:
                                    ExtAPI.DataModel.Project.Model.Mesh.GenerateMesh()
                                except:
                                    None
                                ExtAPI.DataModel.Tree.Refresh()
                    analysis.WriteInputFile(kfile_str)
        ## Change batch connection setting back to the original setting
        if not MeshBatchSettingSave==ExtAPI.DataModel.Project.Model.Mesh.MeshBasedConnection:
            ExtAPI.DataModel.Project.Model.Mesh.MeshBasedConnection=MeshBatchSettingSave
            with Transaction(True):
                try:
                    ExtAPI.DataModel.Project.Model.Mesh.InternalObject.ForceUpdateMeshStates()
                except:
                    None
                ExtAPI.DataModel.Tree.Refresh()

    ### If the code is expired, would not execute main process.
    expireddate=datetime.date(2027,9,1)
    nowdate=datetime.datetime.now()
    datedelta=nowdate.date()-expireddate

    if datedelta.days>0:
        try:
            act_elapsed_sec = _act_time.time() - _ACT_START_TIME
            log_usage("MECH_LSDYNA_Shock", "1.0", act_elapsed_sec, 1800)
        except:
            pass

        print("[UI_OUTPUT] " + str("Automation is expired. Please update."))
    else:
        ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardNMM
        config=ExtAPI.Application.SolveConfigurations["My Computer"]
        args=[None]
        ExtAPI.Application.InvokeUIThread(Main,args)

        endTime = time.time()
        # print("Done, took {} seconds".format(endTime - startTime))
        try:
            act_elapsed_sec = _act_time.time() - _ACT_START_TIME
            log_usage("MECH_LSDYNA_Shock", "1.0", act_elapsed_sec, 1800)
        except:
            pass

        print("[UI_OUTPUT] " + str("Done, took {} seconds".format(endTime - startTime)))

