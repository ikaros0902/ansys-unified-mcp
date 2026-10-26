# -*- coding: utf-8 -*-
"""
create_joints_from_ns.py
由 _Mobile / _Reference 配對 Named Selection 建立 Fixed / Revolute / Cylindrical Joint

整合 rm_joint_creator.py 與 MECH_Joint_Creation.py 之核心演算法，
改寫為通用版本，支援 static / thermal / lsdyna_explicit 三類分析。
UnderDefined 判定與 PromoteToRemotePoint 防呆邏輯見
references/joint_and_remote_point_creation.md。

本腳本使用 `from __future__ import annotations` / `dataclasses` / 型別註解，
僅相容 CPython 3.7+，設計為透過 PyMechanical gRPC 連線執行（`run_python_script`
或本機直連皆可）。嚴禁直接貼入 ACT Script Editor：Mechanical ACT 腳本環境為
IronPython 2.7，不支援本檔語法，貼入會在載入階段立即 SyntaxError。若需要
ACT 腳本版本，請依 references/joint_and_remote_point_creation.md 改寫為
IronPython 2.7 相容語法（移除型別註解與 dataclass，改用一般函式與 dict）。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


DEFAULT_GROUP_NAME = "Scr_Joints_Group"
DEFAULT_PREFIX = "Scr_RM_grp"
MOBILE_SUFFIX = "_Mobile"
REFERENCE_SUFFIX = "_Reference"

# 字串 -> JointType 對照，呼叫端以字串指定較不易出錯（避免跨模組匯入列舉型別）
_JOINT_TYPE_NAMES = ("Fixed", "Revolute", "Cylindrical")


@dataclass
class JointCreationResult:
    """統一回傳格式，供呼叫端做客觀驗證。"""

    created: int = 0
    skipped_empty: int = 0
    skipped_not_two_bodies: int = 0
    underdefined_revolute_or_cylindrical: int = 0
    promoted_to_remote_point: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            "created": self.created,
            "skipped_empty": self.skipped_empty,
            "skipped_not_two_bodies": self.skipped_not_two_bodies,
            "underdefined_revolute_or_cylindrical": self.underdefined_revolute_or_cylindrical,
            "promoted_to_remote_point": self.promoted_to_remote_point,
        }


def _partition_entities_by_body(ns_entities: Iterable[Any]) -> list[tuple[int, list[Any]]]:
    """
    以 entity.Bodies[0].Id 為鍵分組，嚴禁改用 Part.Id（多本體零件會誤判）。
    與 MECH_Joint_Creation.py 行為一致，供 2-face/多實體單一 NS 分流判斷使用。
    """
    body_entities_map: list[tuple[int, list[Any]]] = []
    for entity in ns_entities:
        try:
            if entity.Bodies is not None and entity.Bodies.Count > 0:
                b_id = entity.Bodies[0].Id
            else:
                continue
        except Exception:
            continue

        found = False
        for idx, (existing_id, entities) in enumerate(body_entities_map):
            if existing_id == b_id:
                entities.append(entity)
                found = True
                break
        if not found:
            body_entities_map.append((b_id, [entity]))
    return body_entities_map


def _get_or_create_joint_group(model: Any, group_name: str) -> Any:
    for grp in model.Connections.Children:
        if grp.Name == group_name:
            return grp
    new_grp = model.Connections.AddConnectionGroup()
    new_grp.Name = group_name
    return new_grp


def create_joints_from_ns(
    model: Any,
    ext_api: Any,
    joint_type_name: str,
    named_selections: Iterable[Any] | None = None,
    prefix: str = DEFAULT_PREFIX,
    group_name: str = DEFAULT_GROUP_NAME,
    promote_underdefined_to_remote_point: bool = False,
) -> JointCreationResult:
    """
    掃描指定前綴之 Named Selection，依「單一 NS 恰含 2 個 Body 的實體」規則建立 BodyToBody Joint。

    Args:
        model: Mechanical Model 物件。
        ext_api: ACT 全域 ExtAPI 物件。
        joint_type_name: "Fixed" | "Revolute" | "Cylindrical"。
        named_selections: 待掃描的 NS 清單；省略則使用 model.NamedSelections.Children。
        prefix: NS 名稱前綴判斷依據。
        group_name: 新建 Joint 所屬的 ConnectionGroup 名稱。
        promote_underdefined_to_remote_point: 是否對 UnderDefined 的 Revolute/Cylindrical
            Joint 執行破壞性降級 PromoteToRemotePoint()；預設 False（保留原狀）。

    Returns:
        JointCreationResult: 建立、跳過與 UnderDefined 統計，供客觀驗收。
    """
    from Ansys.ACT.Interfaces.Common import SelectionTypeEnum  # type: ignore
    from Ansys.Mechanical.DataModel.Enums import JointType, JointScopingType, ObjectState  # type: ignore

    if joint_type_name not in _JOINT_TYPE_NAMES:
        raise ValueError(
            "未知的 joint_type_name: {!r}；允許值為 {}".format(joint_type_name, _JOINT_TYPE_NAMES)
        )
    joint_type = getattr(JointType, joint_type_name)

    result = JointCreationResult()
    group = _get_or_create_joint_group(model, group_name)

    ns_list = named_selections if named_selections is not None else model.NamedSelections.Children

    for ns in ns_list:
        if not ns.Name.startswith(prefix):
            continue
        if ns.Name == "Scr_RMgrp_ALL" or MOBILE_SUFFIX in ns.Name or REFERENCE_SUFFIX in ns.Name:
            continue

        if ns.Entities.Count == 0:
            result.skipped_empty += 1
            continue

        body_entities_map = _partition_entities_by_body(ns.Entities)
        if len(body_entities_map) != 2:
            result.skipped_not_two_bodies += 1
            continue

        ref_entities = body_entities_map[0][1]
        mob_entities = body_entities_map[1][1]

        joint = group.AddJoint()
        joint.Name = ns.Name
        joint.Type = joint_type
        joint.ConnectionType = JointScopingType.BodyToBody

        ref_sel = ext_api.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
        ref_sel.Ids = [e.Id for e in ref_entities]
        joint.ReferenceLocation = ref_sel

        mob_sel = ext_api.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
        mob_sel.Ids = [e.Id for e in mob_entities]
        joint.MobileLocation = mob_sel

        result.created += 1

    # UnderDefined 判定與安全防呆：預設不做破壞性降級
    for joint in list(group.Children):
        if joint.ObjectState == ObjectState.UnderDefined:
            if joint.Type in (JointType.Revolute, JointType.Cylindrical):
                result.underdefined_revolute_or_cylindrical += 1

    if promote_underdefined_to_remote_point:
        for joint in list(group.Children):
            if joint.ObjectState == ObjectState.UnderDefined:
                try:
                    joint.Activate()
                    joint.PromoteToRemotePoint()
                    result.promoted_to_remote_point += 1
                except Exception:
                    pass  # 個別失敗不中斷整批流程，呼叫端應核對 created vs promoted 數量落差

    return result


if __name__ == "__main__":
    # 獨立執行時僅驗證資料結構，不連線真實 Mechanical 實例
    demo_result = JointCreationResult(created=2, skipped_empty=1, skipped_not_two_bodies=0,
                                       underdefined_revolute_or_cylindrical=1, promoted_to_remote_point=0)
    print(demo_result.to_dict())
