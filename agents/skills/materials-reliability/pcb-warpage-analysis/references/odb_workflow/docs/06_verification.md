# 06 Verification - acceptance criteria

A run is **PASS** only if every check below passes. The report (`verification_report.md`)
lists each check with its value.

| # | Check | Criterion |
|---|---|---|
| 1 | Translator 2025 R1 (`v251`) | `Total Errors: 0` |
| 2 | Translator 2026 R1 (`v261`) | `Total Errors: 0` |
| 3 | Layer count | EDB layers = stackup layers = 2 x copper - 1 |
| 4 | Layer names and order | EDB name = `layer_<seq>_<fr4>` (lower case) at every position |
| 5 | Layer type | copper -> `signal`, dielectric -> `dielectric` |
| 6 | Thickness per layer | abs(EDB - stackup) <= 0.01 mil, every layer, both versions |
| 7 | Total thickness | abs(EDB total - stackup total) <= 0.01 mil |
| 8 | Origin | profile lower-left = (0, 0) within 1e-6 in (mode `profile_lower_left`) |
| 9 | Vendor files untouched | SHA-256 of ODB++, vendor stackup, design table equal before/after |

Warnings are **not** failures; they are grouped by kind in the report. Expected warnings on
a working gerber: `Stopped reading file .../attrlist` (one per copper layer, D8),
`ODB File '.../eda/data' does not exist` and `Not translating nets ...` (D9).
Unexpected warnings (unsupported symbols on copper, D12) must be read.

## How the check works

1. The output `.tgz` is copied to `%TEMP%` (D18) and translated:
   `anstranslator.exe <tgz> <aedb> -l=<log>` for v251 and v261, one after the other (D15).
2. `edb.def` is read as bytes; every `SLayer(Layer(N=..,T=..),SubL(Th=..))` record gives
   name, type and thickness (converted to mil).
3. Compared with the stackup position by position. The EDB is deleted afterwards.

## What is NOT verified automatically (do it by hand once per project)

- SpaceClaim / Workbench import of the ODB++ (D16) - open it and check the layer list and
  thicknesses.
- External Data placement on the 3D model (`07_downstream_workflow.md`, step 4).
- Copper coverage vs Mechanical Trace Mapping: the v6 script prints the mean copper fraction
  per layer; compare it with the coverage table of the report - they should be close
  (differences come from mesh size and the region: the ODB++ profile may be larger than the
  SMB, D10).

## Earlier results (reference)

| Run | Translator | Layers | Total | Mismatches |
|---|---|---|---|---|
| THE_SYE (2026-11-19, script version) | v261 | 83 | 224.960 mil (Stacking Thickness) | 0 |
| THE_FOUNDER (2026-11-20, script version) | v261 | 83 | 219.640 mil (Final Thickness) | 0 |
| tool 1.0.0 `2_examples/TH5_SYE/runs/TH5_SYE_20261124_140934` | v251 + v261 | 83 | 222.174 mil (SYE Final Thickness) | 0 |
| tool 1.0.0 `2_examples/TH5_Founder/runs/TH5_Founder_20261124_164054` | v251 + v261 | 83 | 219.640 mil (Final Thickness) | 0 |

Use these two runs as the regression baseline: a changed tool must reproduce the same layer
names, thicknesses and (within 0.001) the same coverage.

## Re-check only the translators

After a licence outage (D15) or on another PC:
`python run_odb_tool.py --reverify <run folder>` -> `reverification_<timestamp>.md`.
