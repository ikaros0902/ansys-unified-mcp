# Joint 與 Remote Point 建立演算法

本手冊整合 `MECH_Joint_Creation.py`（頂層單一 Revolute Joint 版）、`MECH_RM_Joint_Creation.py`（Fixed/Revolute/Cylindrical 雙軌版，整合於既有 `ansys-mechanical/scripts/rm_joint_creator.py`）與 `SC_RM_grp_creation.py`（SpaceClaim 側階層分類配對引擎）三份素材的核心演算法，改寫為通用版本。所有列出 API 已於 `mechanical_api.json` 查證存在（`JointType`、`JointScopingType`、`LoadBehavior`、`RemotePointDOFSelectionType`、`ObjectState`、`AddJoint`、`AddRemotePoint`、`PromoteToRemotePoint`）。

---

## 一、Named Selection 配對慣例（消費端判讀）

本技能消費 SpaceClaim 側依 `ansys-named-selection-rm-contact` 慣例產出的 NS，核心判讀規則：

1. **Mobile / Reference 配對**：Base name 相同、後綴分別為 `_Mobile` 與 `_Reference` 的兩個 NS 構成一組運動副。
2. **單一 NS 多實體（2 bodies）**：若單個 NS 的 `Entities` 分屬恰好 2 個不同 `Body.Id`，直接以該 NS 建立 BodyToBody Joint（`MECH_Joint_Creation.py` 的簡化模式）。
3. **跳過規則**：`Entities.Count <= 1`、名稱為 `Scr_RMgrp_ALL`，或名稱含 `_Mobile`/`_Reference` 子字串但未成對者，一律跳過並記錄原因（不可靜默忽略）。

---

## 二、依 Body.Id 分組實體（嚴格避免 Part.Id）

```python
# 一般繁體中文註解：以 entity.Bodies[0].Id 為鍵分組，嚴禁改用 Part.Id（多本體零件會誤判）
def partition_entities_by_body(ns_entities):
    body_entities_map = []
    for entity in ns_entities:
        try:
            if entity.Bodies is not None and entity.Bodies.Count > 0:
                b_id = entity.Bodies[0].Id
            else:
                continue
        except Exception:
            continue

        found = False
        for entry in body_entities_map:
            if entry[0] == b_id:
                entry[1].append(entity)
                found = True
                break
        if not found:
            body_entities_map.append((b_id, [entity]))
    return body_entities_map
```

此分組邏輯直接取自 `MECH_Joint_Creation.py` 與既有 `rm_joint_creator.py`，驗證於多個產品線穩定，故原樣保留（非待查證項目）。

---

## 三、Joint 建立（BodyToBody，支援 Fixed/Revolute/Cylindrical）

```python
# JointType, JointScopingType 已查證存在於 Ansys.Mechanical.DataModel.Enums
def create_body_to_body_joint(joints_group, ExtAPI, ns_name, ref_entities, mob_entities, joint_type):
    joint = joints_group.AddJoint()
    joint.Name = ns_name
    joint.Type = joint_type  # JointType.Fixed / Revolute / Cylindrical
    joint.ConnectionType = JointScopingType.BodyToBody

    ref_sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    ref_sel.Ids = [e.Id for e in ref_entities]
    joint.ReferenceLocation = ref_sel

    mob_sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    mob_sel.Ids = [e.Id for e in mob_entities]
    joint.MobileLocation = mob_sel
    return joint
```

**三種分析類型的 JointType 選用建議**：
- **static / modal**：機構運動（開關、滑軌、鉸鏈）選 `Revolute`/`Cylindrical`；剛性連接選 `Fixed`。
- **thermal**：Joint 本身不傳遞熱流，若零件間需保持幾何連動但不影響熱傳路徑，可用 `Fixed` 搭配獨立定義的接觸熱阻。
- **lsdyna_explicit**：機構衝擊中的旋轉鉸鏈（把手、退出機構）用 `Revolute`；注意顯式求解對運動副的穩定性要求較隱式更嚴格，`UnderDefined` 風險更高。

---

## 四、UnderDefined 判定與 `PromoteToRemotePoint` 安全防呆

**核心原則（三份素材一致採用）**：Revolute/Cylindrical Joint 若判定為 `ObjectState.UnderDefined`，**預設保留原狀供求解器計算，不自動降級**；僅在使用者明確要求時才呼叫 `PromoteToRemotePoint()`。

```python
# ObjectState 已查證存在；PromoteToRemotePoint 已查證存在於 Joint 相關類別
def guard_underdefined_joints(joints_group, promote_to_remote_point=False):
    cnt_underdefined = 0
    for joint in list(joints_group.Children):
        if joint.ObjectState == ObjectState.UnderDefined:
            if joint.Type in (JointType.Revolute, JointType.Cylindrical):
                cnt_underdefined += 1

    cnt_promoted = 0
    if promote_to_remote_point:
        for joint in list(joints_group.Children):
            if joint.ObjectState == ObjectState.UnderDefined:
                try:
                    joint.Activate()
                    joint.PromoteToRemotePoint()
                    cnt_promoted += 1
                except Exception:
                    pass  # 個別失敗不應中斷整批流程，但須於上層記錄失敗項目
    return cnt_underdefined, cnt_promoted
```

> [!CAUTION]
> `PromoteToRemotePoint()` 屬破壞性操作（會改變運動副定義為剛性遠端點約束），僅在呼叫端明確設定 `promote_to_remote_point=True` 時才執行；預設行為為保留 `UnderDefined` 狀態並記錄數量，交由使用者判斷是否需要人工介入。

---

## 五、Remote Point 建立（含 Deformable 防呆）

```python
# AddRemotePoint, RemotePointDOFSelectionType, LoadBehavior 均已查證存在
def create_remote_point_from_ns(remote_points_group, ns, behavior=None):
    if ns.Entities.Count == 0:
        return None  # 空集合必須先行過濾，呼叫端不應傳入空 NS

    rp = remote_points_group.AddRemotePoint()
    rp.Name = ns.Name
    rp.ScopingMethod = GeometryDefineByType.Component
    rp.Location = ns
    rp.Behavior = behavior if behavior is not None else LoadBehavior.Deformable
    rp.DOFSelection = RemotePointDOFSelectionType.Manual
    rp.XComponent = ActiveOrInactive.Active
    rp.YComponent = ActiveOrInactive.Active
    rp.ZComponent = ActiveOrInactive.Active
    rp.RotationX = ActiveOrInactive.Active
    rp.RotationY = ActiveOrInactive.Active
    rp.RotationZ = ActiveOrInactive.Active
    return rp
```

**Behavior 預設為 `Deformable` 而非 `Rigid`**：這是本手冊與單純套用 ACT 預設值的關鍵差異。多個 `Rigid` 遠端點共用同一鈑金節點會在 LS-DYNA 顯式求解觸發 Error 20110（詳見 `contact_verification_and_overconstraint_guard.md`），`Deformable` 為通用安全預設；若特定工況確實需要 `Rigid`（如模擬真實剛體配重點），呼叫端可明確傳入覆寫。

---

## 六、PromoteToRemotePoint 與獨立 Remote Point 建立的差異

| 情境 | 使用時機 |
|---|---|
| `create_remote_point_from_ns` | NS 僅對應單一介面（螺絲孔、配重點），直接建立獨立遠端點 |
| `joint.PromoteToRemotePoint()` | 既有 Joint 因拓樸退化判定 `UnderDefined`，需使用者確認後才降級為遠端點約束形式 |

兩者不可混用：不可對同一 NS 同時呼叫兩種建立路徑，否則會產生重複約束導致過度約束（見 `contact_verification_and_overconstraint_guard.md` 第二節）。
