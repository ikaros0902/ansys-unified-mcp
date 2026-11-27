# 00 Session start, project folder and project log

Read this at the start of every session, before any stage playbook.

## 1. Find out where you are

Ask the engineer (skip what you already know from the conversation):

1. Which board and which PCB vendor is this about?
2. Where is, or where should be, the project folder (PROJECT_DIR)?

Then look into PROJECT_DIR:

- `project_log.md` exists -> read all of it. It is the memory of the project. Continue at
  the first step that is not `done`. Do not repeat finished steps unless the engineer asks.
- No log but files exist (a JSON, `runs\`, `.scdocx`) -> list what you find, ask the engineer
  what was done by hand, write a log from that, then continue.
- Empty or missing -> create the layout below and a new log, start at stage A.

PROJECT_DIR must not be inside TOOL_DIR. If the engineer points you into TOOL_DIR (for
example `2_examples\`), ask for another folder; only the tool owner works inside TOOL_DIR.

## 2. Project folder layout

```
PROJECT_DIR\
  <PROJECT>_<VENDOR>.json     one JSON for steps 2, 3 and 9 (copy of 4_config\project_config.template.json)
  project_log.md              the log you keep
  inputs\                     optional copies of input files (the JSON may point to files elsewhere)
  runs\<run>\                 step 2 output, one new folder per run (never overwritten)
  geometry\                   step 3 output (.scdocx)
  results\<case>\             step 9 input: the exported Z displacement + ds.dat of one solve
  leveling\<case>\            step 9 output
```

Two vendors of one board are two JSON files and two logs (`project_log_<VENDOR>.md`) in the
same folder, or two folders. Ask which the engineer prefers.

## 3. project_log.md

Create it from this template. Keep it in English. Update it **before** you move to the next
step, not at the end of the session: a session can stop at any time.

```markdown
# Project log - <PROJECT> / <VENDOR>

| Item | Value |
|---|---|
| Project folder | <PROJECT_DIR> |
| Project JSON | <PROJECT>_<VENDOR>.json |
| Tool | <TOOL_DIR>, ODB Modifying Tool <version from the run log> |
| Engineer | <name> |
| Started | <YYYY-MM-DD> |

## Status

| Step | What | Status | Date | Evidence |
|---|---|---|---|---|
| 1 | Inputs collected | open | | |
| 2 | ANSYS-ready ODB++ | open | | |
| 3 | Stacked 3D model | open | | |
| 4 | Workbench + External Data | open | | |
| 5 | Mesh + Trace Mapping | open | | |
| 6 | Equivalent material (v6) | open | | |
| 7 | BGA-shadow named selection | open | | |
| 8 | Supports + thermal load | open | | |
| 9 | Z export + leveling | open | | |

## Decisions (made by a human)

| Date | Decision | Value | Decided by | Reason |
|---|---|---|---|---|

## Assumptions (not measured, not in the library)

| Date | Quantity | Value | Source / reason | Accepted by |
|---|---|---|---|---|

## Warnings and open points

| Date | Step | Warning | Outcome |
|---|---|---|---|

## Results

| Date | Case | Warpage um | Warpage mil | Shape | Files |
|---|---|---|---|---|---|

## Journal

- <YYYY-MM-DD HH:MM> <what was done, what was checked, what came back>
```

Rules for the log:

- Status values: `open`, `in progress`, `done`, `blocked (<why>)`.
- Evidence is something a colleague can open or read: a run folder name, a file name, the
  numbers the engineer reported ("83 bodies, 5.643 mm"), a screenshot file name.
- A decision without "decided by" is not a decision. Use the engineer's name, never "AI".
- Copy every assumption the tools report (for example the defaults and assumptions listed per material in `PCB_Material_Library_report.md`) into
  the Assumptions table.
- When a step is redone (new run, re-mesh), keep the old line in the journal and update the
  status line; never delete history.

## 4. What to tell the engineer at the start

Two or three sentences: the step the project is at, what you will do next, and what you
will need from them. For a new project, also say that the ANSYS user-interface steps (4 to 8)
are theirs and that you will check each one with them before the next.
