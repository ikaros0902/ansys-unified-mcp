"""Intake detection, FR4 pairing, matrix format, shifting and packing (no ANSYS needed)."""
import gzip
import sys
import tarfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from odbtool import odb  # noqa: E402
from odbtool.asker import Asker  # noqa: E402
from odbtool.intake import Layer, find_stack_table, pair_copper_materials, pick_thickness_column  # noqa: E402
from odbtool.util import NeedAnswer, norm_material  # noqa: E402

TOOL = Path(__file__).resolve().parents[1]
EX = TOOL / "2_examples"


def _asker(answers=None):
    return Asker(False, dict(answers or {}), lambda *a: None)


def _grid():
    # 3 copper + 2 dielectric, solder mask rows, a header with two thickness columns
    return [
        ["Layer", "Type", "Design Thickness", "Final Thickness (mil)", "Material"],
        [None, "Solder mask", 1.4, 1.4, None],
        ["TOP", "Copper", 2.0, 2.1, None],
        [None, "p.p", 3.0, 2.8, "EM892K2"],
        ["L2", "Copper", 1.2, 1.2, None],
        [None, "Core", 4.0, 4.0, "EM370(Z)"],
        ["BOT", "Copper", 2.0, 2.1, None],
        [None, "Solder mask", 1.4, 1.4, None],
    ]


def test_find_table_and_thickness_column():
    t = find_stack_table("x.xlsx", "S", _grid())
    assert t is not None and t.n_cu() == 3 and len(t.groups) == 5
    notes = []
    c, f = pick_thickness_column(t, "vendor_stackup", "Final Thickness", None, _asker(), notes)
    assert c == 3 and f == 1.0
    with pytest.raises(NeedAnswer):                        # "Thickness" matches two columns
        pick_thickness_column(t, "vendor_stackup", "Thickness", None, _asker(), [])
    c, _ = pick_thickness_column(t, "vendor_stackup", "Thickness", "mil",
                                 _asker({"vendor_stackup.thickness_column": "C"}), [])
    assert c == 2


def test_merged_dielectric_rows():
    g = _grid()
    g.insert(4, [None, "p.p", 1.0, 1.0, "EM892K2"])       # second PP row between TOP and L2
    t = find_stack_table("x", "S", g)
    assert len(t.groups) == 5 and len(t.groups[1]) == 2


def _layers(spec):
    out = []
    for i, (kind, dt, mat) in enumerate(spec, 1):
        out.append(Layer(seq=i, kind=kind, thickness_mil=1, material=mat, diel_type=dt, ecad_name=f"L{i}"))
    return out


def test_copper_fr4_pairing_rules():
    L = _layers([("copper", "", ""), ("dielectric", "prepreg", "EM892K2"), ("copper", "", ""),
                 ("dielectric", "core", "EM370Z"), ("copper", "", ""), ("dielectric", "prepreg", "EM370Z"),
                 ("copper", "", "")])
    pair_copper_materials(L, _asker(), [], ["EM370Z", "EM892K2"])
    assert [x.material for x in L if x.kind == "copper"] == ["EM892K2", "EM892K2", "EM370Z", "EM370Z"]


def test_copper_fr4_nm_lamination_is_asked():
    L = _layers([("copper", "", ""), ("dielectric", "prepreg", "EM892K2"), ("copper", "", ""),
                 ("dielectric", "prepreg", "EM370Z"), ("copper", "", "")])
    with pytest.raises(NeedAnswer):
        pair_copper_materials(L, _asker(), [], ["EM370Z", "EM892K2"])
    pair_copper_materials(L, _asker({"copper_fr4.L3": "EM370Z"}), [], ["EM370Z", "EM892K2"])
    assert L[2].material == "EM370Z"


def test_copper_fr4_stated_in_design_table_is_not_asked():
    L = _layers([("copper", "", ""), ("dielectric", "prepreg", "EM892K2"), ("copper", "", ""),
                 ("dielectric", "prepreg", "EM370Z"), ("copper", "", ""), ("dielectric", "prepreg", "EM370Z"),
                 ("copper", "", "")])
    L[2].design_fr4 = "EM370Z"                             # N+M layer: the table decides, no question
    L[4].design_fr4 = "EM892K2"                            # differs from the prepreg rule: table wins, DIFF
    notes = []
    pair_copper_materials(L, _asker(), notes, ["EM370Z", "EM892K2"])
    assert [x.material for x in L if x.kind == "copper"] == ["EM892K2", "EM370Z", "EM892K2", "EM370Z"]
    assert [k for k, _ in notes] == ["INFO", "DIFF"]


def test_copper_between_cores_is_asked():
    L = _layers([("copper", "", ""), ("dielectric", "core", "EM892K2"), ("copper", "", ""),
                 ("dielectric", "core", "EM892K2"), ("copper", "", "")])
    with pytest.raises(NeedAnswer):
        pair_copper_materials(L, _asker({"copper_fr4.L1": "EM892K2"}), [], ["EM892K2"])


def test_norm_material():
    assert norm_material("EM370(Z)") == "EM370Z"
    assert norm_material(" em-892k2 ") == "EM892K2"


def test_matrix_classic_format_has_no_version_line():
    txt = odb.format_matrix([{"NAME": "PCB"}], [
        {"CONTEXT": "BOARD", "TYPE": "SIGNAL", "NAME": "LAYER_1_EM892K2", "POLARITY": "POSITIVE",
         "OLD_NAME": "COMP", "LATIN_NAME": "COMP", "COLOR": "1"},
        {"CONTEXT": "BOARD", "TYPE": "DIELECTRIC", "NAME": "LAYER_2_EM892K2", "POLARITY": "POSITIVE",
         "DIELECTRIC_TYPE": "PREPREG", "DIELECTRIC_NAME": "EM892K2"}])
    assert not txt.lstrip().startswith("VERSION")
    assert "LATIN_NAME" not in txt and "COLOR" not in txt
    steps, layers = odb.parse_matrix(txt)
    assert [l["ROW"] for l in layers] == ["1", "2"] and "DIELECTRIC_TYPE" not in layers[0]
    assert layers[1]["DIELECTRIC_NAME"] == "EM892K2"


def test_shift_text_units_and_records():
    t = "UNITS=MM\nP 1 2 0 P 0 0\nL 0 0 1 1 0 P 0\nA 0 0 1 1 0.5 0.5 0 P 0 Y\nOB 0 0 I\nOC 1 1 0.5 0.5 Y\n"
    new, n, bad = odb.shift_text(t, 1.0, 0.0)           # 1 inch = 25.4 mm
    assert bad == 0 and n == 5
    assert "P 26.4 2 " in new and "OC 26.4 1 25.9 0.5 Y" in new


def test_pack_without_gzip_name(tmp_path):
    job = tmp_path / "job"
    (job / "matrix").mkdir(parents=True)
    (job / "matrix" / "matrix").write_text("x")
    out = odb.pack_tgz(job, tmp_path / "o.tgz")
    raw = out.read_bytes()
    assert raw[:2] == b"\x1f\x8b" and not (raw[3] & 0x08)   # FNAME flag not set
    with tarfile.open(out) as tf:
        assert tf.getnames()[0] == "job"
    with pytest.raises(Exception):
        odb.pack_tgz(job, out)                               # never overwrite


@pytest.mark.skipif(not (EX / "TH5_Founder" / "TH5_Founder.json").exists(), reason="examples missing")
@pytest.mark.parametrize("cfg, total", [("TH5_SYE/TH5_SYE.json", 222.174), ("TH5_Founder/TH5_Founder.json", 219.64)])
def test_examples_intake(cfg, total):
    import json
    from odbtool.intake import run_intake
    from odbtool.runner import load_config
    c = load_config(EX / cfg)
    job = odb.scan(Path(c["inputs"]["vendor_odb"]["path"]))
    answers = {k: v for k, v in c["answers"].items() if not k.startswith("_")}
    res = run_intake(c, [d["NAME"] for d in job.copper], _asker(answers), lambda *a: None)
    assert len(res.layers) == 83
    assert sum(L.thickness_mil for L in res.layers) == pytest.approx(total, abs=1e-6)
    names = [L.odb_name for L in res.layers]
    assert names[0] == "LAYER_1_EM892K2" and names[3] == "LAYER_4_EM370Z" and names[52] == "LAYER_53_EM370Z"
    ref = (EX / "TH5_common" / "reference_stackup_hand_made.csv")
    if ref.exists():
        rows = [l.split(",") for l in ref.read_text().splitlines()[1:]]
        assert [norm_material(r[4]) for r in rows] == [L.material for L in res.layers]
