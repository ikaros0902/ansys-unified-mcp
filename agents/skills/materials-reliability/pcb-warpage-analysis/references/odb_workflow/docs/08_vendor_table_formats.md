# 08 Vendor and design table formats seen so far

The tool does not use fixed cell positions. It finds:

- the **kind column**: most cells reading `copper`, `cu`, `pp`, `p.p`, `prepreg`, `core`,
  `laminate`, `dielectric` (case, dots and spaces ignored);
- the **name column**: most cells reading `TOP`, `BOT`, `BOTTOM`, `L<n>`, `Layer<n>`;
- the **stackup rows**: the longest run of classified rows, copper at both ends, copper and
  dielectric alternating (solder mask rows cut the run, they are never stackup layers);
- the **thickness column**: by header words (from the JSON) among columns that have a number
  on every stackup row; headers are read from up to 12 rows above the first stackup row;
- the **material column** (design table): the column whose dielectric cells are material
  library names.

## TH5 - SYE (`SYE_TH5_Workging Gerber_Stackup.xlsx`, sheet `Stackup`)

| Item | Where |
|---|---|
| stackup rows | 6-88 (83 layers), solder mask rows 5 and 89 |
| kind | column H (`Copper`, `p.p`, `Core`) |
| copper names | column F (TOP, L2 .. BOT) |
| thickness columns | M `Design Thickness`, N `Stacking Thickness`, R `SYE Final Thickness mil` |
| used | **R** (`thickness_column = "SYE Final Thickness"`) - total 222.174 mil |
| other | C material, D a ready `Layer_n_<mat>` name, L copper coverage % (not real) |
| history | the 2026-11-19 file had thickness in J; columns A-E were inserted later (D19) |

## TH5 - Founder (`TH5_Founder_Workging Gerber_Stackup.xls`, sheet `Stack-up new`)

| Item | Where |
|---|---|
| stackup rows | 4-86, no solder mask rows |
| kind | column C (`PP`, `CORE`; copper rows have the oz text here) |
| copper names | column B (L1 .. L42) |
| thickness | E original dielectric, F suggested dielectric, **K `Final Thickness(mil)`** (copper + dielectric) - total 219.640 mil |
| material | column J (EM892K2, EM370(Z)) |
| impedance tables | rows 88+ and columns AA+ (ignored: no kind/name run) |

Copper rows: column C holds `1oz`, `0.500oz+plating`; the row is recognised as copper through
the name column (`L3`).

## TH5 - Design table (`STACKUP, 42 LAYER, Hybrid, EM892K2_EM370Z_REV 06.xlsx`)

| Item | Where |
|---|---|
| sheet | `Stackup_L42_EM892K2+EM370Z` (the other sheets `stackup1`, `stckup2` are 13/23-layer templates -> rejected by copper count) |
| stackup rows | 16-98, solder mask rows 15 and 99 |
| kind | column G (`Copper`, `p.p`, `core`) |
| names | column D (TOP .. BOT), sequence number in column E |
| material | column C on dielectric rows (`EM892K2`, `EM370(Z)`) |
| glass | column H (`PP(1078_RC67%)x1`, `Core(1067_RC64.5%)x1`) |
| copper oz | column H on copper rows |
| function | column F (SIG/GND/PWR), foil column A |
| thickness | L design, M thickness (only for the report) |

## Adding a new format

Usually nothing is needed. If the tool cannot find the stackup:

1. Run with `--intake-only` and read the INFO lines (which sheet, rows, columns it took).
2. If the kind words are unusual (e.g. `Prepreg 1080`, `Laminate`), add the normalized token
   to `KIND_TOKENS` in `odbtool/intake.py` and a test.
3. If copper names are unusual (e.g. `ART01`), add a pattern to `NAME_RE`.
4. Set `sheet` in the JSON if the workbook has several valid stackups.
5. Record the format in this file.
