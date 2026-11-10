# -*- coding: utf-8 -*-
"""
assign_section_thickness.py
殼單元厚度 / 截面性質通用指派工具

依 analysis_type 參數切換兩種路徑：
  - "static" / "thermal" / "modal"：呼叫 Mechanical 隱式原生 API (Body.Thickness)
  - "lsdyna_explicit"：產生 *SECTION_SHELL / *SECTION_SOLID 關鍵字卡片字串

本腳本使用 `from __future__ import annotations` / `dataclasses` / 型別註解，
僅相容 CPython 3.7+，設計為透過 PyMechanical gRPC 連線執行。嚴禁直接貼入
ACT Script Editor：Mechanical ACT 腳本環境為 IronPython 2.7，不支援本檔語法，
貼入會在載入階段立即 SyntaxError。若需要 ACT 腳本版本，請改寫為 IronPython
2.7 相容語法（移除型別註解與 dataclass，改用全英文 ASCII 註解），此時
model/ExtAPI 才會是 ACT 環境自動注入的全域物件。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable


# 支援的分析類型常數，避免字串魔術值散落各處
ANALYSIS_TYPES_IMPLICIT = ("static", "thermal", "modal")
ANALYSIS_TYPE_EXPLICIT = "lsdyna_explicit"


@dataclass
class SectionAssignmentResult:
    """統一回傳格式，供呼叫端做客觀驗證（而非主觀判斷「應該設好了」）。"""

    analysis_type: str
    assigned_shell: int = 0
    assigned_solid: int = 0
    skipped_suppressed: int = 0
    skipped_unknown_type: int = 0
    explicit_cards: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "analysis_type": self.analysis_type,
            "assigned_shell": self.assigned_shell,
            "assigned_solid": self.assigned_solid,
            "skipped_suppressed": self.skipped_suppressed,
            "skipped_unknown_type": self.skipped_unknown_type,
            "explicit_card_count": len(self.explicit_cards),
        }


def _iter_active_bodies(model: Any) -> Iterable[Any]:
    """
    遍歷全機 Body 並過濾已抑制（Suppressed）項目。
    DataModelObjectCategory 為 ACT/PyMechanical 環境注入的全域列舉，
    此處不重新匯入，交由呼叫端環境（ACT 或 PyMechanical App）提供。
    """
    from Ansys.Mechanical.DataModel.Enums import DataModelObjectCategory  # type: ignore

    bodies = model.Geometry.GetChildren(DataModelObjectCategory.Body, True)
    for body in bodies:
        yield body


def assign_section_thickness(
    model: Any,
    analysis_type: str,
    shell_thickness_mm: float = 0.8,
    solid_mesh_form: str = "tet",
) -> SectionAssignmentResult:
    """
    統一入口：依 analysis_type 切換隱式 / 顯式路徑。

    Args:
        model: Mechanical Model 物件（ACT 全域 Model 或 PyMechanical app.DataModel.Project.Model）。
        analysis_type: "static" | "thermal" | "modal" | "lsdyna_explicit"。
        shell_thickness_mm: 殼體厚度（毫米），僅於未個別指定厚度時套用之預設值。
        solid_mesh_form: 顯式路徑下實體單元網格形態，"tet" 或 "hex"，決定 ELFORM 選型。

    Returns:
        SectionAssignmentResult: 含指派統計與（顯式路徑）產生的卡片字串清單。
    """
    if analysis_type in ANALYSIS_TYPES_IMPLICIT:
        return _assign_implicit(model, analysis_type, shell_thickness_mm)
    if analysis_type == ANALYSIS_TYPE_EXPLICIT:
        return _assign_explicit_lsdyna(model, shell_thickness_mm, solid_mesh_form)

    raise ValueError(
        "未知的 analysis_type: {!r}；允許值為 {} 或 {!r}".format(
            analysis_type, ANALYSIS_TYPES_IMPLICIT, ANALYSIS_TYPE_EXPLICIT
        )
    )


def _assign_implicit(
    model: Any, analysis_type: str, shell_thickness_mm: float
) -> SectionAssignmentResult:
    """
    Mechanical 隱式路徑：直接寫入 Body.Thickness 物件屬性。
    Body.CrossSection（梁截面）API 存在性已查證，但確切建立方式
    （AddCrossSection 掛載物件與 Dim1/Dim2 簽名）未能於 API 字典中
    找到完整證據，此處僅處理殼體厚度，梁截面留待 api_search 查證後再擴充。
    """
    from Ansys.Core.Units import Quantity  # type: ignore

    result = SectionAssignmentResult(analysis_type=analysis_type)

    for body in _iter_active_bodies(model):
        if getattr(body, "Suppressed", False):
            result.skipped_suppressed += 1
            continue

        geo_body = body.GetGeoBody()
        body_type_str = str(geo_body.BodyType) if geo_body else ""

        if body_type_str == "GeoBodySheet":
            body.Thickness = Quantity(shell_thickness_mm, "mm")
            result.assigned_shell += 1
        elif body_type_str == "GeoBodySolid":
            # 實體零件在隱式分析中無需指派厚度，體積本身已定義截面
            result.assigned_solid += 1
        else:
            result.skipped_unknown_type += 1

    return result


def _assign_explicit_lsdyna(
    model: Any, shell_thickness_mm: float, solid_mesh_form: str
) -> SectionAssignmentResult:
    """
    LS-DYNA 顯式路徑：掃描 Body 分類後產生 *SECTION_SHELL / *SECTION_SOLID 卡片字串。
    卡片數值寫入交由上層 .k 檔匯出流程處理，本函式僅負責分類與卡片字串生成。
    """
    result = SectionAssignmentResult(analysis_type=ANALYSIS_TYPE_EXPLICIT)

    shell_secid = 1
    solid_secid = 2
    shell_assigned = False
    solid_assigned = False

    for body in _iter_active_bodies(model):
        if getattr(body, "Suppressed", False):
            result.skipped_suppressed += 1
            continue

        geo_body = body.GetGeoBody()
        body_type_str = str(geo_body.BodyType) if geo_body else ""

        if body_type_str == "GeoBodySheet":
            result.assigned_shell += 1
            shell_assigned = True
        elif body_type_str == "GeoBodySolid":
            result.assigned_solid += 1
            solid_assigned = True
        else:
            result.skipped_unknown_type += 1

    if shell_assigned:
        result.explicit_cards.append(_build_section_shell_card(shell_secid, shell_thickness_mm))
    if solid_assigned:
        result.explicit_cards.append(_build_section_solid_card(solid_secid, solid_mesh_form))

    return result


def _build_section_shell_card(secid: int, thickness_mm: float) -> str:
    """
    產生 *SECTION_SHELL 卡片字串。
    ELFORM=16（Fully Integrated Shell）+ NIP=5，為衝擊/彎曲工況的標準起點。
    詳見 references/section_cards_explicit_lsdyna.md。
    """
    return (
        "*SECTION_SHELL\n"
        "$#   secid    elform      shrf       nip     propt     qr/ir     icomp      setyp\n"
        "{secid:>10}{elform:>10}{shrf:>10.3f}{nip:>10}{propt:>10}{qrir:>10}{icomp:>10}{setyp:>10}\n"
        "$#      t1        t2        t3        t4      nloc     marea      idof    edgset\n"
        "{t:>10.3f}{t:>10.3f}{t:>10.3f}{t:>10.3f}{nloc:>10.3f}{marea:>10.3f}{idof:>10.3f}{edgset:>10}"
    ).format(
        secid=secid, elform=16, shrf=1.000, nip=5, propt=1, qrir=0, icomp=0, setyp=1,
        t=thickness_mm, nloc=0.000, marea=0.000, idof=0.000, edgset=0,
    )


def _build_section_solid_card(secid: int, mesh_form: str) -> str:
    """
    產生 *SECTION_SOLID 卡片字串。
    Tet4 預設 ELFORM=10（1-Point Tetrahedron w/ Stabilization）；
    Hex8 預設 ELFORM=1（Constant Stress Solid，呼叫端須另行配置 *HOURGLASS）。
    """
    elform = 10 if mesh_form.lower() == "tet" else 1
    return (
        "*SECTION_SOLID\n"
        "$#   secid    elform       aet\n"
        "{secid:>10}{elform:>10}{aet:>10}"
    ).format(secid=secid, elform=elform, aet=0)


if __name__ == "__main__":
    # 獨立執行時僅示範卡片字串生成，不連線真實 Mechanical 實例
    print(_build_section_shell_card(1, 0.8))
    print()
    print(_build_section_solid_card(2, "tet"))
