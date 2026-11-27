# 05 Ambiguity rules - what is decided automatically and what is asked

Principle: **decide only when the evidence is unambiguous; otherwise ask, record the answer,
never guess.** Every question has a stable key. Answers live in the project JSON under
`answers` and are reused on every later run.

How a question is answered:

- `options.interactive = true`: the terminal shows the question with numbered options.
- `options.interactive = false`: the run stops with exit code 2 and writes
  `open_questions_<project>_<vendor>.md` next to the JSON. An AI or a colleague adds
  `"<key>": "<value>"` to `answers` and runs again.

## Decision table

| Key | Decided automatically when | Asked when | Typical answer |
|---|---|---|---|
| `vendor_stackup.sheet` / `design_material_table.sheet` | exactly one sheet has a stackup with the ODB++ copper count | none or several sheets qualify | sheet name |
| `<role>.thickness_column` | exactly one numeric column header contains **all** words of `thickness_column` (or the letter matches) | no or several columns match, or no name given | column letter |
| `<role>.thickness_unit` | header says mil / um / mm, or `thickness_unit` set | otherwise | `mil` |
| `<role>.merge_dielectric_rows` | never | two or more dielectric rows between one copper pair | `yes` |
| `<role>.material_column` | one column's dielectric cells match the material library names | otherwise | column letter |
| `dielectric_material.Layer_<n>` | the design table gives one material for the row(s) | missing, or several different materials in merged rows | `EM892K2` |
| `copper_fr4.<name>` | the design table states a library material on the copper row itself (rule 0), or exactly **one** prepreg is adjacent (above/below) or both adjacent prepregs have the same FR4 | two adjacent prepregs with different FR4 (N+M lamination layer), or only cores adjacent | `EM370Z` |
| `material_variant.<KEY>` | the library has one material for that model | the library has several resin contents of the model | `EM-370(Z)_RC51` |
| `odb.step` | one step, or one single-board step with a usual name | several candidates | `PCB` |
| `vendor_stackup.total_thickness_ok` | total between 10 and 1000 mil | outside (unit mistake?) | `yes` |

Hard stops (no question, the input must be fixed):

- copper count differs between ODB++, vendor stackup and design table
- copper/dielectric order differs between vendor and design table at the same position
- a dielectric material is not in the material library `PCB_Material_Library.xml` (the message says
  why the converter left it out, when the workbook has it)
- a thickness is 0 or negative
- a coordinate record cannot be parsed while shifting
- output folder / file already exists

## Copper FR4 pairing rule (agreed 2026-11-23)

Copper is one material; what differs between copper layers is the **FR4 that fills the
etched areas**. During lamination the filling resin comes from the **prepreg**, not from the
core. Therefore:

0. If the design table has a material-library name **on the copper row itself** (same
   material column as the dielectric rows), that FR4 is used and nothing is asked. This is
   the way for the design team to settle an N+M layer in the table. When it differs from
   rule 2 the report lists a `DIFF`; when it settles a rule 3 / 4 case the report lists an
   `INFO` with the design row. A copper row with an empty cell or other text (`Copper`,
   `HVLP`, ...) falls through to rules 1 to 4.
1. Take the adjacent dielectric layers (above and below).
2. If exactly one of them is a prepreg, or both are prepregs of the same material -> that FR4.
3. If both are prepregs with **different** materials -> ask. This is the N+M lamination
   layer of a hybrid build (TH5: L27, EM892K2 prepreg above, EM370(Z) prepreg below; the
   user chose **EM370Z**).
4. If no adjacent layer is a prepreg (copper between two cores) -> ask.

Checked on TH5: rule 2 reproduces the hand-made `stackup.csv` for 41 of 42 copper layers; the
remaining one is L27 (rule 3).

## Matching rules between sources

- Layers are matched **by order**, never by name. The copper count must be equal.
- Copper names differing between sources (TOP/L1/COMP/01CS) are listed in the report, not errors.
- Thickness comes **only** from the vendor table; material, type and names **only** from the
  design table. Differences (vendor PP vs design core, vendor material vs design material,
  vendor thickness vs design thickness) are listed as `DIFF` in the report.

## When you are an AI running this tool

1. Run with `--non-interactive`. Exit code 2 = questions.
2. Read `open_questions_*.md`. For each question, look for evidence in the input files (the
   question lists the candidate columns with header, first values and sums).
3. **Ask the human** for: which thickness column to use, FR4 of N+M lamination layers, the
   resin content when the library has several for one model, and
   anything where two answers are plausible. Do not choose these yourself.
4. You may answer on your own only when the evidence is unique and verifiable (for example a
   sheet question where only one sheet's copper count matches, or a unit stated in the header).
5. Write the answers into `answers` with a `_note` saying who decided and why, run again.
6. Exit code 0 = PASS. Read `verification_report.md` and give the human its result table.
