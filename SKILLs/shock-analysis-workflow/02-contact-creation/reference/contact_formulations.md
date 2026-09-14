# Contact Formulations & Joint Creation Scripts

本手冊為 Session 02: 接觸對與運動副自動建立（Contact & Joint Creation）之底層演算法與 LS-DYNA 關鍵字卡片實作細節。

---

### 2.1 自動運動副建立演算法 (`MECH_RM_Joint_Creation.py`)
自動掃描命名規則中包含 `_Mobile` 與 `_Reference` 後綴的 Named Selections，並建立對應之運動副：
```python
import clr
clr.AddReference("Ansys.ACT.Interfaces")
clr.AddReference("Ansys.Mechanical.DataModel")
from Ansys.Mechanical.DataModel.Enums import JointType, JointScopingType

def create_joints_from_ns(model, ExtAPI, prefix="RMP_", mobile_suffix="_Mobile", ref_suffix="_Reference", joint_type=JointType.Revolute):
    conn = model.Connections
    all_ns = model.NamedSelections.Children
    
    # 建立或取得專屬 Connections Group
    joints_grp = None
    for cg in conn.Children:
        if cg.Name == "Scr_Joints_Group":
            joints_grp = cg
            break
    if not joints_grp:
        joints_grp = conn.AddConnectionGroup()
        joints_grp.Name = "Scr_Joints_Group"
        
    # 收集 Base Names
    rm_base_names = set()
    for ns in all_ns:
        if ns.Name.startswith(prefix):
            b_name = ns.Name
            if b_name.endswith(mobile_suffix):
                b_name = b_name[:-len(mobile_suffix)]
            elif b_name.endswith(ref_suffix):
                b_name = b_name[:-len(ref_suffix)]
            rm_base_names.add(b_name)
            
    # 遍歷建立 Joint
    for base_name in rm_base_names:
        m_ns = None
        r_ns = None
        for ns in all_ns:
            if ns.Name == base_name + mobile_suffix:
                m_ns = ns
            elif ns.Name == base_name + ref_suffix:
                r_ns = ns
                
        if m_ns and r_ns and m_ns.Entities.Count > 0 and r_ns.Entities.Count > 0:
            joint = joints_grp.AddJoint()
            joint.Name = base_name
            joint.Type = joint_type
            joint.ConnectionType = JointScopingType.BodyToBody
            
            # 設定 Reference 與 Mobile Location
            ref_sel = ExtAPI.SelectionManager.CreateSelectionInfo(Ansys.ACT.Interfaces.Common.SelectionTypeEnum.GeometryEntities)
            ref_sel.Ids = r_ns.Location.Ids
            joint.ReferenceLocation = ref_sel
            
            mob_sel = ExtAPI.SelectionManager.CreateSelectionInfo(Ansys.ACT.Interfaces.Common.SelectionTypeEnum.GeometryEntities)
            mob_sel.Ids = m_ns.Location.Ids
            joint.MobileLocation = mob_sel
```

### 2.2 綁定接觸對批次配置 (`Mech_bonded.py`)
針對 SpaceClaim 匯出的 `Connect Topology` 2-face Named Selections，批次建立 Bonded Contact 並設定適當之 Pinball 搜尋半徑（防止數值公差導致漏綁）：
```python
from Ansys.Mechanical.DataModel.Enums import ContactType, ContactPinballType

def create_bonded_contacts(model, ExtAPI, pinball_mm=1.22):
    conn = model.Connections
    bonded_grp = conn.AddConnectionGroup()
    bonded_grp.Name = "_Bonded_by_script"
    
    for ns in model.NamedSelections.Children:
        if ns.Name.startswith("Connect Topology") and len(ns.Location.Ids) == 2:
            f1 = ExtAPI.SelectionManager.CreateSelectionInfo(Ansys.ACT.Interfaces.Common.SelectionTypeEnum.GeometryEntities)
            f1.Ids = [ns.Location.Ids[0]]
            f2 = ExtAPI.SelectionManager.CreateSelectionInfo(Ansys.ACT.Interfaces.Common.SelectionTypeEnum.GeometryEntities)
            f2.Ids = [ns.Location.Ids[1]]
            
            bonded = bonded_grp.AddContactRegion()
            bonded.Name = ns.Name
            bonded.ContactType = ContactType.Bonded
            bonded.SourceLocation = f1
            bonded.TargetLocation = f2
            bonded.PinballRegion = ContactPinballType.Radius
            bonded.PinballRadius = Quantity("{} [mm]".format(pinball_mm))
            bonded.ShellThicknessEffect = False
```

### 2.3 全域接觸卡片配置 (`*CONTACT_AUTOMATIC_SINGLE_SURFACE`)
在 LS-DYNA Keyword 中注入全域單表面接觸，適用於整機碰撞與跌落衝擊：
```
*CONTACT_AUTOMATIC_SINGLE_SURFACE
$#     cid                                                                 title
         1 Global Single Surface Contact
$#    ssid      msid     sstyp     mstyp    sboxid    mboxid       spr       mpr
         0         0         0         0         0         0         1         1
$#      fs        fd        dc        vc       vdc    penchk        bt        dt
     0.200     0.200     0.000     0.000    20.000         0     0.000 1.000E+20
$#     sfs       sfm       sst       mst      sfst      sfmt       fsf       vsf
     1.000     1.000     0.000     0.000     1.000     1.000     1.000     1.000
$#    soft    sofscl    lcidab    maxpar     tnbrx                depth      bsort
         1     0.100         0     1.025         0                    2         10
```

---
