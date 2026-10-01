# Output & Export — condensed reference

Where script results can go. Verified from `lsppscripting`.

## Output destinations

An SCL/Python script's results can be sent to:

- the **LS-PrePost message file**,
- a **user-created file** (e.g. `exam4.txt`, `curve.txt`),
- back into **LS-PrePost** for fringing or plotting (user-defined fringe data /
  XY-plot).

## Common patterns (from doc examples)

- Measure mass, center of gravity, and volume of all solid parts → write to a
  text file.
- Measure angular velocity of all solid parts → write to a text file.
- Compute a per-node/per-element quantity per state → write one file per state,
  and/or fringe it in LSPP.
- Create a load curve → write to `curve.txt` → load back into the XY-plot.
- Write nodal coordinates from the selection buffer to a file (file name passed
  on the `runscript`/`runpython` command line).

## Export parts / model

- Write a selected part to a keyword file (e.g. keep the solid part, write it
  out) — see `model_build.md`.

## Fringe computed data back into LSPP

Computed arrays can be loaded back as **user-defined fringe data**, displaying
like a built-in result. This is the bridge from custom computation to LSPP
visualization.

## Notes

- Passing the output file name as a command-line argument makes a script
  reusable across runs (see `session_and_cfile.md`).
- For image/animation export and report generation, use the GUI command tokens
  from `Ansys_LS-PrePost_Users_Guide`.
