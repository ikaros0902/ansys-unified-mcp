# 04 Build procedure - exactly what is changed in the ODB++

Order of operations in `odbtool/build.py`. Nothing is done in the vendor archive; everything
happens in an extracted copy under `%TEMP%\pcb_thermal_warpage\<run>`.

1. **Scan** the archive (small text files only): job folder, `misc/info`, matrix, every
   `stephdr` and `profile`.
2. **Choose the step** (D1): config `pcb_step`; else the only step; else the single
   single-board step named PCB/UNIT/BOARD/EDIT/ORIG/SINGLE; else ask (list with profile size).
   A step with `STEP-REPEAT` in its `stephdr` is a panel and is never chosen.
3. **Extract selectively**: `matrix`, `misc`, `symbols`, `fonts`, and from the chosen step
   only `stephdr`, `profile`, `attrlist` and the copper layer folders. Not extracted: other
   steps, non-copper layers, `netlists chk tha pstack_info eda boxes` (D11), CAM history (D13).
4. **Job name**: `misc/info` `JOB_NAME` and `misc/job_name` set to `output_job_name`; the
   top folder is renamed. ODB++ < 8 is stamped 8.1 (D3).
5. **Origin** (D6): shift = minus the profile lower-left corner (or `keep` / `offset_mm`).
   Applied to `profile`, `stephdr` X/Y_DATUM and every copper `features` record
   (P, L, A, T, B, OB, OS, OC). Units per file (`UNITS=MM` / `INCH`). Any coordinate
   record that cannot be parsed stops the run.
6. **Copper layers** (top to bottom, matched by order with the stackup):
   - folder renamed to `layer_<seq>_<fr4>`, matrix NAME `LAYER_<seq>_<FR4>`, OLD_NAME = vendor name
   - `features.Z` decompressed (D7), shifted
   - attrlist: `.copper_weight = mil/1.4`, `.layer_dielectric = 0` **first** (D8)
7. **Dielectric layers** inserted after every copper but the last:
   - empty `features`, attrlist `.layer_dielectric = <inch>`
   - matrix: `CONTEXT=BOARD TYPE=DIELECTRIC DIELECTRIC_TYPE=PREPREG|CORE DIELECTRIC_NAME=<FR4>`
8. **Matrix** written in the classic form (D4), rows renumbered, one STEP block.
9. All `.sum` checksum files of changed files deleted (InCAM regenerates them; ANSYS ignores them).
10. **Pack** (D5): GNU tar, gzip without stored name, one top folder. Existing output file -> stop.

## Naming rule

| Item | Pattern | Example |
|---|---|---|
| ODB++ layer (matrix NAME) | `LAYER_<seq>_<FR4>` | `LAYER_53_EM370Z` |
| ODB++ layer folder | lower case of the name | `layer_53_em370z` |
| CSV / body name (LayerBuilder) | `Layer_<seq>_<FR4>` | `Layer_53_EM370Z` |
| SpaceClaim body (LayerBuilder adds ratio) | `Layer_<seq>_<FR4>_<copper ratio>` | `Layer_53_EM370Z_0.912` |

`seq` = 1..N from the top; odd = copper, even = dielectric (for an all-alternating stack).
`FR4` = normalized material key; for copper the paired FR4 (`05_ambiguity_rules.md`).

## Thickness encoding

| Layer | Attribute | Value | Unit |
|---|---|---|---|
| copper | `.copper_weight` | thickness_mil / 1.4 | oz |
| copper | `.layer_dielectric` | 0 | inch |
| dielectric | `.layer_dielectric` | thickness_mil / 1000 | inch |

## Copper coverage (`odbtool/coverage.py`)

- coverage = copper area inside the region / region area (0..1)
- regions: `profile` (always), `drawing` (2D drawing rectangle, if given), `extra_regions_mm`
- rendering: anti-aliased at `resolution_mil` (default 1 mil). The renderer grows every filled
  edge by a constant 0.246 px; this is measured at start and removed by an inward offset, so
  the result does not depend on resolution. Unit tests (`tests/test_coverage.py`) check
  lines, arcs, pads at 45 deg, ovals, surfaces with holes, negative pads and user symbols
  against exact areas (within 0.3-1 %).
- supported: line/arc with r/s symbols; pads r s rect (rounded/chamfered) oval di oct
  donut_r donut_s el hex_l hex_s tri; user symbols (recursive); surfaces with holes;
  negative polarity. Thermals are drawn as full donuts (counted as "approximated").
  Text and barcodes are not drawn (counted as "unrendered"). The report lists both per layer.
- dielectric layers get coverage 0 in the workinggerber CSV.
