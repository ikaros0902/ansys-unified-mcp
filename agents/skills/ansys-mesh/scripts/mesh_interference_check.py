# -*- coding: utf-8 -*-

import time



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

    # Ansys Mechanical ACT Script - Combined Interference Check (Built-in + KD-Tree + CSV Export)



    import math, time, os, csv, clr, sys

    clr.AddReference("System.Windows.Forms")

    from System.Windows.Forms import MessageBox, FolderBrowserDialog, DialogResult



    # ??????????????????????????????

    # KD-Tree Implementation

    # ??????????????????????????????

    class KDTreeNode:

        def __init__(self, point, index, left=None, right=None, axis=0):

            self.point = point

            self.index = index

            self.left = left

            self.right = right

            self.axis = axis



    def classify_bodies_by_select(body_select):

        """Return (solid_bodies, shell_bodies); exclude suppressed"""

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





    def build_kdtree_iterative(points):

        if not points:

            return None

        stack = [(0, points, None, None)]

        root = None

        while stack:

            depth, pts, parent, is_left = stack.pop()

            if not pts:

                continue

            axis = depth % 3

            pts.sort(key=lambda p: p[0][axis])

            mid = len(pts) // 2

            node_data = pts[mid]

            node = KDTreeNode(node_data[0], node_data[1], axis=axis)

            if parent is None:

                root = node

            else:

                if is_left:

                    parent.left = node

                else:

                    parent.right = node

            stack.append((depth + 1, pts[mid + 1:], node, False))

            stack.append((depth + 1, pts[:mid], node, True))

        return root



    def euclidean_dist(p1, p2):

        dx, dy, dz = p1[0]-p2[0], p1[1]-p2[1], p1[2]-p2[2]

        return math.sqrt(dx*dx + dy*dy + dz*dz)



    def radius_search_iterative(root, target, radius):

        results = []

        stack = [(root, 0)]

        rabs = abs(radius)

        while stack:

            node, depth = stack.pop()

            if node is None:

                continue

            axis = depth % 3

            diff = target[axis] - node.point[axis]

            if abs(diff) <= rabs:

                if euclidean_dist(node.point, target) <= rabs:

                    results.append((node.index, 0.0))

            if diff <= 0:

                stack.append((node.left, depth+1))

                if abs(diff) <= rabs:

                    stack.append((node.right, depth+1))

            else:

                stack.append((node.right, depth+1))

                if abs(diff) <= rabs:

                    stack.append((node.left, depth+1))

        return results



    def bodie_been_select():

        Error_msg_lines1 = ''

        Error_msg_lines2 = ''

        Error_msg_lines3 = ''

        Error_Check1 = False

        Error_Check2 = False

        Error_Check3 = False

        bodies_all = ExtAPI.DataModel.Project.Model.Geometry.GetChildren(DataModelObjectCategory.Body, True)

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

        

        for body in bodies_selected_ALL:

            if body.ObjectState == ObjectState.UnderDefined:

                Error_msg_lines1 = "Some objects are not fully defined (missing material or thickness)" + '\n'

                Error_Check1 = True

            elif body.ObjectState == ObjectState.FullyDefined:

                Error_msg_lines2 = "Some objects are not meshed" + '\n'

                Error_Check2 = True   

        if len(bodies_selected_ALL) ==0:

            Error_msg_lines3 = ("Please select objects to check"+'\n')

            Error_Check3 = True    

        if Error_Check1 or Error_Check2 or Error_Check3:

            try:

                act_elapsed_sec = _act_time.time() - _ACT_START_TIME

                log_usage("Mech_Interference_Check", "20250827", act_elapsed_sec, 7200)

            except:

                pass



            print("[UI_OUTPUT] " + str(Error_msg_lines1 + Error_msg_lines2 + Error_msg_lines3))

            return None

            

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

        return bodies_selected



    def run_combined_interference_check():

        total_start = time.time()

        api = ExtAPI

        model = api.DataModel.Project.Model

        geometry = model.Geometry

        mesh = model.MeshData if hasattr(model, "MeshData") else model.Analyses[0].MeshData



        msg_lines = []

        built_in_set, kd_set, final_ids = set(), set(), set()

        element_info = []

        bodies_selected = bodie_been_select()                



        if not bodies_selected:

            return

        

        solid_bodies, shell_bodies = classify_bodies_by_select(bodies_selected)

        

        msg_lines.append("Selected {} objects for interference check".format(len(bodies_selected)))

        

        # ???????????????

        # Step 1: Built-in Interference Check

        

        # ???????????????

        try:

            Inner_Check_start = time.time()

            ns_name = "Jabil Interference Check Results"

            # Delete old Named Selection

            for ns_old in list(model.NamedSelections.Children):

                if ns_old.Name == ns_name:

                    ns_old.Delete()



            # Create interference check Named Selection

            ns = model.AddNamedSelection()

            ns.Name = ns_name

            ns.ScopingMethod = GeometryDefineByType.Worksheet

            ns.GenerationCriteria.Add(None)

            ns.GenerationCriteria[0].EntityType = SelectionType.GeoBody

            ns.GenerationCriteria[0].Criterion = SelectionCriterionType.Size

            ns.GenerationCriteria[0].Operator = SelectionOperatorType.GreaterThan

            ns.GenerationCriteria[0].Value = Quantity("0 [mm mm mm]")



            ns.GenerationCriteria.Add(None)

            ns.GenerationCriteria[1].Action = SelectionActionType.Diagnostics

            ns.GenerationCriteria[1].EntityType = SelectionType.MeshElement

            ns.GenerationCriteria[1].Criterion = SelectionCriterionType.BodyInterferenceMesh



            ns.Generate()



            count_built_in = ns.Properties[10].InternalValue

            Inner_Check_End = time.time()

            Inner_Check_Total = Inner_Check_End - Inner_Check_start

            msg_lines.append("Built-in check: found {} interference elements, elapsed {:.2f} seconds".format(count_built_in,Inner_Check_Total))



            try:

                built_in_set = set(ns.Location.Ids)

                ns.Delete()

            except:

                pass

            

        except Exception as e:

            msg_lines.append("Built-in check failed: {}".format(str(e)))



        # ???????????????

        # Step 2: KD-Tree Shell Interference Check

        # ???????????????

        try:

            if mesh is None:

                raise Exception("Please create mesh before execution")

                

            KD_Check_start = time.time()

            

            body_thk = {}

            for b in shell_bodies:

                if getattr(b, "Thickness", None) and b.Thickness.Value > 0:

                    body_thk[b.GetGeoBody().Id] = b.Thickness.Value



            node_by_id = mesh.NodeById

            element_by_id = mesh.ElementById

            mm = 1000.0

            global_max_thickness = 0.0



            for eid in mesh.ElementIds:

                el = element_by_id(eid)

                b = el.GetBody()

                if b.Id not in body_thk:

                    continue

                sX=sY=sZ=0.0

                for nid in el.NodeIds:

                    nd = node_by_id(nid)

                    sX += nd.X; sY += nd.Y; sZ += nd.Z

                c = ((sX/len(el.NodeIds))*mm,

                     (sY/len(el.NodeIds))*mm,

                     (sZ/len(el.NodeIds))*mm)

                thk = body_thk[b.Id]

                if thk>global_max_thickness: global_max_thickness=thk

                element_info.append({"id":eid,"body":b.Id,"centroid":c,"thk":thk})



            kd_points = [(e["centroid"], i) for i,e in enumerate(element_info)]

            tree = build_kdtree_iterative(kd_points)



            half_global = 0.5*global_max_thickness

            checked_pairs=set()

            for i,e1 in enumerate(element_info):

                r = 0.5*e1["thk"] + half_global

                neighbors = radius_search_iterative(tree, e1["centroid"], r)

                for j,_ in neighbors:

                    if j==i: continue

                    e2 = element_info[j]

                    if e1["body"]==e2["body"]: continue

                    key = (min(e1["id"],e2["id"]), max(e1["id"],e2["id"]))

                    if key in checked_pairs: continue

                    checked_pairs.add(key)

                    if euclidean_dist(e1["centroid"], e2["centroid"]) < 0.5*(e1["thk"]+e2["thk"]):

                        kd_set.add(e1["id"]); kd_set.add(e2["id"])

            KD_Check_End = time.time()

            KD_Check_Total_Time = KD_Check_End - KD_Check_start

            msg_lines.append("Shell to Shell check: found {} interference elements, elapsed {:.2f} seconds".format(len(kd_set),KD_Check_Total_Time))

        except Exception as e:

            msg_lines.append("Shell to Shell check failed: {}".format(str(e)))



        # ???????????????

        # Step 3: Merge Results + Named Selection

        # ???????????????

        final_ids = built_in_set.union(kd_set)

        msg_lines.append("Final merge: {} interference elements".format(len(final_ids)))



        if final_ids:

            ns_final = model.AddNamedSelection()

            ns_final.Name = "Jabil Interference Check Results"

            sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.MeshElements)

            sel.Ids = list(final_ids)

            ns_final.Location = sel

            ExtAPI.DataModel.Tree.Refresh() 



        # ???????????????

        # Step 4: Export CSV

        # ???????????????

        '''

        try:

            dialog = FolderBrowserDialog()

            dialog.Description = "Select folder to export CSV"

            dialog.ShowNewFolderButton = True

            result = dialog.ShowDialog()

            if result == DialogResult.OK:

                out_dir = dialog.SelectedPath

                # Export element list

                csv1 = os.path.join(out_dir, "interference_elements.csv")

                with open(csv1, "wb") as f:

                    writer = csv.writer(f)

                    writer.writerow(["Element ID", "Body ID", "Centroid X(mm)", "Centroid Y(mm)", "Centroid Z(mm)", "Thickness(mm)"])

                    for e in element_info:

                        if e["id"] in final_ids:

                            cx,cy,cz=e["centroid"]

                            writer.writerow([e["id"], e["body"], "{:.6f}".format(cx), "{:.6f}".format(cy), "{:.6f}".format(cz), "{:.3f}".format(e["thk"])])

                            

                msg_lines.append("CSV exported: interference_elements.csv")

        except Exception as e:

            msg_lines.append("Export failed: {}".format(str(e)))

        '''



        total_elapsed = time.time()-total_start

        msg_lines.append("Total elapsed time {:.2f} seconds".format(total_elapsed))

        try:

            act_elapsed_sec = _act_time.time() - _ACT_START_TIME

            log_usage("Mech_Interference_Check", "20250827", act_elapsed_sec, 7200)

        except:

            pass



        print("[UI_OUTPUT] " + str("\n".join(msg_lines)))





    # ???????????????

    # Execute

    # ???????????????

    run_combined_interference_check()

