# -*- coding: utf-8 -*-
"""
create_bonded_contacts_from_ns.py
由 2-face Named Selection（"Connect Topology*" 命名慣例）批次建立 Bonded Contact

通用於 static / thermal / lsdyna_explicit 三類分析；
ContactType / ContactPinballType 等列舉行為定義見
ansys-mechanical/references/connections_and_contacts.md，本檔不重複定義。

本腳本使用 `from __future__ import annotations` / `dataclasses` / 型別註解，
僅相容 CPython 3.7+，設計為透過 PyMechanical gRPC 連線執行。嚴禁直接貼入
ACT Script Editor：Mechanical ACT 腳本環境為 IronPython 2.7，不支援本檔語法，
貼入會在載入階段立即 SyntaxError。若需要 ACT 腳本版本，請改寫為 IronPython
2.7 相容語法（移除型別註解與 dataclass），此時 ExtAPI / Model 才會是 ACT
環境自動注入的全域物件。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


DEFAULT_PINBALL_MM = 1.22
DEFAULT_NS_PREFIX = "Connect Topology"
DEFAULT_GROUP_NAME = "_Bonded_by_script"


@dataclass
class BondedContactResult:
    """統一回傳格式，供呼叫端做客觀驗證。"""

    created: int = 0
    skipped_empty: int = 0
    skipped_not_pair: int = 0
    skipped_duplicate: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            "created": self.created,
            "skipped_empty": self.skipped_empty,
            "skipped_not_pair": self.skipped_not_pair,
            "skipped_duplicate": self.skipped_duplicate,
        }


def _get_or_create_connection_group(model: Any, group_name: str) -> Any:
    """
    尋找既有同名 ConnectionGroup，不存在則新建。
    避免每次執行都產生重複群組，與既有 Mech_bonded.py 行為一致。
    """
    for grp in model.Connections.Children:
        if grp.Name == group_name:
            return grp
    new_grp = model.Connections.AddConnectionGroup()
    new_grp.Name = group_name
    return new_grp


def create_bonded_contacts_from_ns(
    model: Any,
    ext_api: Any,
    named_selections: Iterable[Any] | None = None,
    pinball_mm: float = DEFAULT_PINBALL_MM,
    ns_prefix: str = DEFAULT_NS_PREFIX,
    group_name: str = DEFAULT_GROUP_NAME,
) -> BondedContactResult:
    """
    掃描指定前綴的 2-face Named Selection，批次建立 Bonded Contact。

    Args:
        model: Mechanical Model 物件。
        ext_api: ACT 全域 ExtAPI 物件（提供 SelectionManager）。
        named_selections: 待掃描的 NS 清單；省略則使用 model.NamedSelections.Children。
        pinball_mm: Pinball 搜尋半徑（毫米），預設沿用既有 1.22 mm 經驗值。
        ns_prefix: NS 名稱前綴判斷依據，預設 "Connect Topology"。
        group_name: 新建 Bonded Contact 所屬的 ConnectionGroup 名稱。

    Returns:
        BondedContactResult: 建立與跳過統計，供客觀驗收。
    """
    from Ansys.Core.Units import Quantity  # type: ignore
    from Ansys.ACT.Interfaces.Common import SelectionTypeEnum  # type: ignore
    from Ansys.Mechanical.DataModel.Enums import ContactType, ContactPinballType  # type: ignore

    result = BondedContactResult()
    group = _get_or_create_connection_group(model, group_name)
    existing_names = {c.Name for c in group.Children}

    ns_list = named_selections if named_selections is not None else model.NamedSelections.Children

    for ns in ns_list:
        if not ns.Name.startswith(ns_prefix):
            continue

        if ns.Entities.Count == 0:
            result.skipped_empty += 1
            continue

        pair_ids = ns.Location.Ids
        if len(pair_ids) != 2:
            result.skipped_not_pair += 1
            continue

        if ns.Name in existing_names:
            result.skipped_duplicate += 1
            continue

        face1 = ext_api.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
        face1.Ids = [pair_ids[0]]
        face2 = ext_api.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
        face2.Ids = [pair_ids[1]]

        bonded = group.AddContactRegion()
        bonded.Name = ns.Name
        bonded.ContactType = ContactType.Bonded
        bonded.SourceLocation = face1
        bonded.TargetLocation = face2
        bonded.PinballRegion = ContactPinballType.Radius
        bonded.PinballRadius = Quantity(pinball_mm, "mm")
        bonded.ShellThicknessEffect = False

        result.created += 1
        existing_names.add(ns.Name)

    return result


def verify_contacts_with_tool(analysis: Any) -> Any:
    """
    建立 Contact Tool 並觸發評估，回傳 contact_tool 物件供呼叫端讀取
    Status / Penetration 結果，判讀準則見
    references/contact_verification_and_overconstraint_guard.md。
    """
    contact_tool = analysis.Solution.AddContactTool()
    contact_tool.AddStatus()
    contact_tool.AddPenetration()
    contact_tool.EvaluateAllResults()
    return contact_tool


if __name__ == "__main__":
    # 獨立執行時僅驗證資料結構，不連線真實 Mechanical 實例
    demo_result = BondedContactResult(created=3, skipped_empty=1, skipped_not_pair=0, skipped_duplicate=0)
    print(demo_result.to_dict())
