# Decisions only a human makes

For every item below: ask the engineer, wait for the answer, write it into the Decisions
table of `project_log.md` (value, decided by, reason), and where a JSON key exists, into the
project JSON. If the engineer does not know, they ask the requester; you wait.

You may propose a value and say where it comes from ("TH5 used 5 mm"). You may not apply it
until the engineer says yes. An example value in a document is not a decision.

| # | Decision | Step | Why a human | Where it is recorded |
|---|---|---|---|---|
| 1 | Which **thickness column** of the vendor stackup, and its unit when the header does not say | 2 | vendors list several (design, stacking, final); only the requester knows which is built | `inputs.vendor_stackup.thickness_column`, `thickness_unit` |
| 2 | **FR4 of a copper layer** between two different prepregs (N+M lamination) or between two cores, **when the design table does not state it on the copper row** | 2 | a process question, no rule gives it. Not asked when the design team wrote a library material on that copper row: the tool uses it and reports it (`docs/05_ambiguity_rules.md`, rule 0) | `answers` -> `copper_fr4.<layer>` with `_note` |
| 3 | Any other question in `open_questions_*.md` with more than one plausible answer (PCB step, merge dielectric rows, material of a row, total thickness outside 10 to 1000 mil) | 2 | see `docs/05_ambiguity_rules.md` | `answers` with `_note` |
| 4 | **Material data that is not in the library**: a material that is missing or was left out of `PCB_Material_Library.xml`, any value you would have to invent. Also: **which resin content** when the library has several for one model (question `material_variant.<KEY>`) | 2, 6 | assumed properties change the result. The defaults the library itself applies (Ez = 0.6 x in-plane E, K 0.59, Cp 1100, curves extended to 30 C) are listed per material in `PCB_Material_Library_report.md`: show them to the engineer once and record them | Assumptions table; `answers`. The workbook and the XML are changed by the material owner with the converter, never by you |
| 5 | Accepting a **WARN** of the verification report (for example the ODB++ outline differs from the 2D drawing) and which outline is right | 2, 4 | may mean a wrong drawing or revision | Warnings table |
| 6 | **v6 settings**: `FR4_MODEL` (orthotropic or isotropic FR4), `METHOD_CTE_XY` / `METHOD_CTE_Z` (ROM or Turner), `T_REF` | 6 | modelling choices; confirm even when the defaults are kept | Decisions table |
| 7 | **Mesh**: element size, elements through the thickness, element type | 5 | no standard yet (TH5 used 5 mm as an example) | Decisions table |
| 8 | **BGA footprint**: which BGA(s), rectangle in board coordinates, top or bottom surface | 7 | from the layout; you cannot read it from the model | Decisions table |
| 9 | **Support points** A, B, C: which corners or vertices | 8 | depends on the board outline | Decisions table |
| 10 | **Temperature points**: start, end, intermediate temperatures, reflow profile | 8 | follow the measured SMT profile of the project | Decisions table |
| 11 | **Leveling inputs**: unit of the exported displacement, `flip_z` (sign), which value column, whether a difference of two cases is wanted | 9 | export settings and viewing side differ per project | `leveling` section of the JSON |
| 12 | Accepting a **WARNING of the leveling script** (`accept_warnings`) | 9 | may mean a wrong unit or files from different solves | Warnings table, then the JSON |
| 13 | **Judging the result**: comparison with shadow moiré, JEDEC limits, pass or fail | 9 | engineering judgement | Results table |

## What you may decide yourself

Only what has exactly one answer that anyone can verify from the files:

- a sheet question when only one sheet has the copper count of the ODB++;
- a unit that is written in the column header;
- the newest PASS run as the input of step 3;
- file and folder names inside PROJECT_DIR.

Say what you decided and why, and write it into the journal.

## How to ask

- One question at a time, with the evidence the tool printed (candidate columns with header,
  first values and sums; the two prepreg materials; the warning text).
- Offer the options the tool lists, without a recommendation. What another project, an
  example or a document chose (for instance the TH5 answers quoted in `docs/`) is never a
  recommendation for this project; do not bring it up unless the engineer asks what was
  done before.
- Repeat the answer back in one line before you write it down.
