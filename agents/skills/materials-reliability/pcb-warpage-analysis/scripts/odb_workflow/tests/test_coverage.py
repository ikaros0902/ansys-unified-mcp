"""Coverage renderer against shapes with known area."""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from odbtool import coverage  # noqa: E402

PROFILE = "#\n#Layer features\n#\nS P 0\nOB 0 0 I\nOS 0 2\nOS 2 2\nOS 2 0\nOS 0 0\nOE\nSE\n"


def _run(tmp_path, features, res_mil=1.0):
    layer = tmp_path / "steps" / "pcb" / "layers" / "l1"
    layer.mkdir(parents=True)
    (layer / "features").write_text(features, encoding="latin-1")
    bias = coverage.measure_bias()
    r = coverage._layer_job((str(tmp_path), str(layer), res_mil, (0.0, 0.0, 2.0, 2.0), {}, "INCH", bias, None, None))
    return r["regions"]["profile"]["copper_in2"], r


@pytest.mark.parametrize("res", [1.0, 2.0])
def test_known_shapes(tmp_path, res):
    feats = "\n".join([
        "UNITS=INCH",
        "$0 r10", "$1 r20", "$2 rect50x20", "$3 r100", "$4 oval60x20",
        "L 0.2 0.2 1.2 0.2 0 P 0",                      # 10 mil line, 1 in long, round caps
        "P 1.5 1.5 1 P 0 0",                           # 20 mil round pad
        "P 1.5 0.5 2 P 0 8 45",                        # 50x20 mil rect at 45 deg
        "P 0.3 1.6 4 P 0 0",                           # oval 60x20 mil
        "S P 0",
        "OB 0.5 0.5 I", "OS 0.5 1.0", "OS 1.0 1.0", "OS 1.0 0.5", "OS 0.5 0.5", "OE",
        "OB 0.6 0.6 H", "OS 0.8 0.6", "OS 0.8 0.8", "OS 0.6 0.8", "OS 0.6 0.6", "OE",
        "SE",
        "P 0.9 0.9 3 N 0",                             # negative 100 mil pad inside the surface
    ]) + "\n"
    exact = (1.0 * 0.01 + math.pi * 0.005 ** 2) + math.pi * 0.01 ** 2 + 0.05 * 0.02 \
        + (0.04 * 0.02 + math.pi * 0.01 ** 2) + (0.25 - 0.04) - (math.pi * 0.05 ** 2 - 0.0)
    # the negative pad (0.85..0.95) overlaps the surface only (hole is 0.6..0.8): full circle removed
    got, r = _run(tmp_path, feats, res)
    assert not r["unrendered"]
    assert got == pytest.approx(exact, rel=0.003)


def test_thin_lines_resolution_independent(tmp_path):
    lines = ["UNITS=INCH", "$0 r3.5"]
    for i in range(50):
        y = 0.1 + i * 0.03
        lines.append(f"L 0.1 {y:.4f} 1.9 {y + 0.0123:.4f} 0 P 0")
    exact = 50 * (math.hypot(1.8, 0.0123) * 0.0035 + math.pi * 0.00175 ** 2)
    got, _ = _run(tmp_path, "\n".join(lines) + "\n", 1.0)
    assert got == pytest.approx(exact, rel=0.01)


def test_arc_and_user_symbol(tmp_path):
    sym = tmp_path / "symbols" / "blk" / "features"
    sym.parent.mkdir(parents=True)
    sym.write_text("UNITS=INCH\nS P 0\nOB -0.05 -0.05 I\nOS -0.05 0.05\nOS 0.05 0.05\nOS 0.05 -0.05\n"
                   "OS -0.05 -0.05\nOE\nSE\n", encoding="latin-1")
    feats = "UNITS=INCH\n$0 r10\n$1 blk\nA 1.5 1.0 0.5 1.0 1.0 1.0 0 P 0 Y\nP 0.3 0.3 1 P 0 0\n"
    # half circle arc radius 0.5 (clockwise from right to left over the top), 10 mil wide, round caps
    exact = math.pi * 0.5 * 0.01 + math.pi * 0.005 ** 2 + 0.1 * 0.1
    got, r = _run(tmp_path, feats, 1.0)
    assert r["stats"].get("user symbol pads") == 1
    assert got == pytest.approx(exact, rel=0.01)
