"""相容入口；實作由 pcb-warpage-analysis 技能維護。"""

from pathlib import Path
import runpy


if __name__ == "__main__":
    target = (
        Path(__file__).resolve().parents[3]
        / "agents"
        / "skills"
        / "materials-reliability"
        / "pcb-warpage-analysis"
        / "scripts"
        / Path(__file__).name
    )
    runpy.run_path(str(target), run_name="__main__")
