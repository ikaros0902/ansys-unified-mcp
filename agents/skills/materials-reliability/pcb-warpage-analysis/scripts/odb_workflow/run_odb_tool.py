# -*- coding: utf-8 -*-
"""Step 2 of the PCB thermal-warpage workflow (see SKILL.md / README_zh.md).
Main entry: vendor working-gerber ODB++ -> ANSYS-ready ODB++ with full stackup.

How to use
  1. Copy 4_config/project_config.template.json, fill the input paths (see the "_help" texts).
  2. Either set CONFIG_FILE below and press Run in VS Code,
     or run:  python run_odb_tool.py <project.json> [--non-interactive]
  3. Answer the questions the program asks (they are saved into the json).
  4. Read <output folder>/verification_report.md. RESULT must be PASS.

Exit codes: 0 PASS, 1 built but a check FAILED, 2 waiting for an answer, 3 input error.
Python environment: run setup_env.ps1 once (creates %USERPROFILE%\\.venvs\\pcb_thermal_warpage).
"""
import sys
from pathlib import Path

# ----------------------------------------------------------------------------------------
CONFIG_FILE = r""          # e.g. r"C:\Projects\TH5\TH5_SYE.json"  ("" = use the command line)
# ----------------------------------------------------------------------------------------

sys.dont_write_bytecode = True     # the tool folder is shared and read-only for projects: no __pycache__
sys.path.insert(0, str(Path(__file__).resolve().parent))
from odbtool.runner import main  # noqa: E402

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args and CONFIG_FILE:
        args = [CONFIG_FILE]
    sys.exit(main(args))
