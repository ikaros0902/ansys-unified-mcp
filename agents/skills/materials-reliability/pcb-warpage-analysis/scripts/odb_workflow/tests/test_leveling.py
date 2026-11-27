"""Step 9 leveling: NBLOCK lookup, plane removal, warpage, units, warnings, differences."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "1_Scripts"))
import level_bga_shadow as lv  # noqa: E402

EX = ROOT / "2_examples" / "leveling_sample"


def _write_case(tmp, name, nodes, xyz, uz, header="Directional Deformation (mm)", fixed=True):
    res = tmp / f"{name}.txt"
    res.write_text("Node Number\t%s\n" % header + "".join(f"{n}\t{v:.9g}\n" for n, v in zip(nodes, uz)),
                   encoding="utf-8")
    dat = tmp / f"{name}.dat"
    L = ["/com,--- Data in consistent NMM units. See Solving Units", "/units,MPA", "nblock,3,,%d" % len(nodes),
         "(1i9,3e20.9e3)"]
    for n, (x, y, z) in zip(nodes, xyz):
        L.append("%9d%20.9E%20.9E%20.9E" % (n, x, y, z) if fixed else f"{n} {x} {y} {z}")
    L += ["-1", "et,1,185"]
    dat.write_text("\n".join(L) + "\n", encoding="latin-1")
    return res, dat


def _grid(nx=9, ny=7, pitch=5.0, x0=100.0, y0=200.0):
    xs, ys = np.meshgrid(np.arange(nx) * pitch + x0, np.arange(ny) * pitch + y0)
    return xs.ravel(), ys.ravel()


def _cfg(tmp, cases, **kw):
    lev = {"z_unit": "mm", "xy_unit": "mm", "html": False, "png": False, "cases": cases}
    lev.update(kw)
    p = tmp / "proj.json"
    p.write_text(json.dumps({"leveling": lev}), encoding="utf-8")
    return p


def _summary(tmp):
    rows = (tmp / "leveling" / "leveling_summary.csv").read_text(encoding="utf-8-sig").splitlines()
    head = rows[0].split(",")
    return [dict(zip(head, r.split(","))) for r in rows[1:]]


def test_tilted_bowl_is_leveled(tmp_path):
    """A bowl of known depth on a tilted plane: the tilt is removed, the depth is the warpage."""
    x, y = _grid()
    xc, yc = x.mean(), y.mean()
    bowl = 0.004 * (((x - xc) / (x.max() - xc)) ** 2 + ((y - yc) / (y.max() - yc)) ** 2)   # 0 .. 8 um, centre low
    uz = bowl + 0.002 * x - 0.001 * y + 1.5
    nodes = np.arange(1000, 1000 + len(x))
    res, dat = _write_case(tmp_path, "c1", nodes, zip(x, y, np.full(len(x), 5.6)), uz)
    cfg = _cfg(tmp_path, [{"name": "c1", "result": res.name, "dat": dat.name}])
    assert lv.run(cfg) == lv.EXIT_OK
    s = _summary(tmp_path)[0]
    assert s["shape"] == "Smile" and int(s["nodes"]) == len(x)
    # the least-squares plane of a symmetric bowl is horizontal -> warpage = bowl depth
    assert float(s["warpage_um"]) == pytest.approx(8.0, abs=0.01)
    assert float(s["tilt_deg"]) == pytest.approx(np.degrees(np.arctan(np.hypot(0.002, 0.001))), rel=1e-4)
    out = (tmp_path / "leveling" / "c1" / "c1_leveled.csv").read_text(encoding="utf-8-sig").splitlines()
    assert out[0].startswith("node,X_board_mm") and len(out) == len(x) + 1


def test_flip_changes_shape_not_size(tmp_path):
    x, y = _grid()
    uz = 0.004 * ((x - x.mean()) ** 2 + (y - y.mean()) ** 2) / 400.0
    nodes = np.arange(1, len(x) + 1)
    res, dat = _write_case(tmp_path, "c1", nodes, zip(x, y, np.zeros(len(x))), uz, fixed=False)
    w = {}
    for flip in (False, True):
        cfg = _cfg(tmp_path, [{"name": "c1", "result": res.name, "dat": dat.name}], flip_z=flip)
        assert lv.run(cfg) == lv.EXIT_OK
        w[flip] = _summary(tmp_path)[0]
    assert w[False]["shape"] == "Smile" and w[True]["shape"] == "Cry"
    assert float(w[False]["warpage_um"]) == pytest.approx(float(w[True]["warpage_um"]), rel=1e-9)


def test_unit_conflict_and_missing_unit(tmp_path):
    x, y = _grid()
    uz = 1e-6 * (x - x.mean()) ** 2
    nodes = np.arange(1, len(x) + 1)
    res, dat = _write_case(tmp_path, "c1", nodes, zip(x, y, np.zeros(len(x))), uz)
    cfg = _cfg(tmp_path, [{"name": "c1", "result": res.name, "dat": dat.name}], z_unit="m")
    assert lv.run(cfg) == lv.EXIT_INPUT                       # header says mm, JSON says m -> stop
    res2, dat2 = _write_case(tmp_path, "c2", nodes, zip(x, y, np.zeros(len(x))), uz, header="Z")
    cfg = _cfg(tmp_path, [{"name": "c2", "result": res2.name, "dat": dat2.name}])
    assert lv.run(cfg) == lv.EXIT_WARN                        # no unit in the header -> a human confirms
    cfg = _cfg(tmp_path, [{"name": "c2", "result": res2.name, "dat": dat2.name}], accept_warnings=True)
    assert lv.run(cfg) == lv.EXIT_OK


def test_wrong_dat_and_ambiguous_column(tmp_path):
    x, y = _grid()
    nodes = np.arange(1, len(x) + 1)
    res, _ = _write_case(tmp_path, "c1", nodes, zip(x, y, np.zeros(len(x))), 1e-3 * x)
    _, dat_other = _write_case(tmp_path, "other", nodes + 10000, zip(x, y, np.zeros(len(x))), 1e-3 * x)
    cfg = _cfg(tmp_path, [{"name": "c1", "result": res.name, "dat": dat_other.name}])
    assert lv.run(cfg) == lv.EXIT_INPUT                       # no common node: not the same solve
    two = tmp_path / "two.csv"
    two.write_text("Node Number,Zoriginal,Z\n" + "".join(f"{n},{-v},{v}\n" for n, v in zip(nodes, 1e-3 * x)))
    _, dat = _write_case(tmp_path, "c3", nodes, zip(x, y, np.zeros(len(x))), 1e-3 * x)
    cfg = _cfg(tmp_path, [{"name": "c3", "result": two.name, "dat": dat.name}])
    assert lv.run(cfg) == lv.EXIT_INPUT                       # two value columns: ask, never guess
    cfg = _cfg(tmp_path, [{"name": "c3", "result": two.name, "dat": dat.name}], value_column="Zoriginal",
               accept_warnings=True)
    assert lv.run(cfg) == lv.EXIT_OK


def test_difference_of_two_cases(tmp_path):
    x, y = _grid()
    r2 = ((x - x.mean()) ** 2 + (y - y.mean()) ** 2) / 400.0
    nodes = np.arange(1, len(x) + 1)
    xyz = list(zip(x, y, np.zeros(len(x))))
    ra, da = _write_case(tmp_path, "hot", nodes, xyz, 0.010 * r2 + 0.001 * x)
    rb, db = _write_case(tmp_path, "cold", nodes, xyz, 0.004 * r2 - 0.002 * y)
    cfg = _cfg(tmp_path, [{"name": "hot", "result": ra.name, "dat": da.name},
                          {"name": "cold", "result": rb.name, "dat": db.name}],
               differences=[{"name": "hot_minus_cold", "minuend": "hot", "subtrahend": "cold"}])
    assert lv.run(cfg) == lv.EXIT_OK
    s = {r["case"]: float(r["warpage_um"]) for r in _summary(tmp_path)}
    assert s["hot_minus_cold"] == pytest.approx(s["hot"] - s["cold"], rel=1e-6)


def test_rotate_equals_detrend_for_small_tilt(tmp_path):
    x, y = _grid()
    uz = 0.004 * ((x - x.mean()) ** 2 + (y - y.mean()) ** 2) / 400.0 + 1e-4 * x
    _, _, zd, _ = lv.level(x, y, uz, "OLS", "detrend")
    _, _, zr, _ = lv.level(x, y, uz, "OLS", "rotate")
    assert np.ptp(zr) == pytest.approx(np.ptp(zd), rel=1e-4)


def test_robust_methods_ignore_an_outlier():
    x, y = _grid(15, 15)
    z = 0.001 * x + 0.002 * y + 0.5
    z2 = z.copy()
    z2[7] += 5.0
    for m in ("Huber", "Tukey", "RANSAC"):
        a, b, _ = lv.fit_plane(x, y, z2, m)
        assert a == pytest.approx(0.001, abs=2e-5) and b == pytest.approx(0.002, abs=2e-5)


@pytest.mark.skipif(not (EX / "inputs" / "ds.dat").is_file(), reason="leveling example not present")
def test_th5_example_reproduces_the_reference(tmp_path):
    """Earlier-project sample, 323 BGA-shadow nodes: 0.057539 mm in the 2026-03-25 study (Leveling_Auto_v4, detrend)."""
    cfg = json.loads((EX / "leveling_sample.json").read_text(encoding="utf-8"))
    for c in cfg["leveling"]["cases"]:
        c["result"] = str(EX / c["result"])
        c["dat"] = str(EX / c["dat"])
    cfg["leveling"].update(html=True, png=True, output_dir=str(tmp_path / "out"), flip_z=True)
    p = tmp_path / "th5.json"
    p.write_text(json.dumps(cfg), encoding="utf-8")
    assert lv.run(p) == lv.EXIT_OK
    rows = (tmp_path / "out" / "leveling_summary.csv").read_text(encoding="utf-8-sig").splitlines()
    s = dict(zip(rows[0].split(","), rows[1].split(",")))
    assert int(s["nodes"]) == 323 and s["shape"] == "Cry"
    assert float(s["warpage_um"]) == pytest.approx(57.539, abs=0.01)
    d = tmp_path / "out" / "sample_30to220C"
    for f in ("sample_30to220C_leveled.csv", "sample_30to220C_report.md", "sample_30to220C.html",
              "sample_30to220C_contour.png", "sample_30to220C_3d.png"):
        assert (d / f).stat().st_size > 1000
