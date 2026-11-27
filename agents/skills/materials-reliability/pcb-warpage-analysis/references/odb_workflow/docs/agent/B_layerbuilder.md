# Stage B - step 3: stacked 3D model (LayerBuilder)

You run the script. The engineer opens the result in SpaceClaim and confirms it.
Precondition: step 2 is `done` with a PASS run, and the 2D drawing (`.stp`) is in the JSON
(`inputs.step_2d_drawing.path`).

## What the script does

It extrudes the planar face of the drawing once per row of the run's
`*_workinggerber.csv` (row 1 = top layer, highest Z), names every body
`Layer_<n>_<FR4>_<copper ratio>` (for example `Layer_1_EM892K2_0.296`), deletes the original
face, sets Share Topology on the component `Stackup` and saves a `.scdocx`.

The body name carries the layer number that step 6 reads. Tell the engineer not to rename
bodies.

## Settings (project JSON, section `layerbuilder`)

All keys may stay `null`:

| Key | `null` means |
|---|---|
| `stackup_csv` | the `*_workinggerber.csv` of the newest run under `output.root`; that run must be PASS |
| `step_file` | `inputs.step_2d_drawing.path` |
| `output_scdocx` | `PROJECT_DIR\geometry\<PROJECT>_<VENDOR>_Stackup.scdocx` |

An existing output file stops the run (nothing is overwritten). To rebuild after a new
step-2 run, ask the engineer whether to rename the old file or to set another
`output_scdocx`.

## Run

1. Dry check, no ANSYS needed:
   ```
   python TOOL_DIR\1_Scripts\LayerBuilder_pyansys.py <json> --check
   ```
   It prints the stackup CSV, the drawing and the output path it will use. Read the three
   lines to the engineer; the CSV must be from the run they accepted in step 2.
2. Tell the engineer the build starts an ANSYS Geometry service (Discovery / SpaceClaim
   licence) and takes a few minutes. Then:
   ```
   python TOOL_DIR\1_Scripts\LayerBuilder_pyansys.py <json>
   ```

| Exit | What to do |
|---|---|
| 0 | `RESULT: DONE` with body count, total thickness and the output path |
| 3 | input error (file missing, output exists, no PASS run): read the message |
| 1 | build failed: show the `ERROR` line. No licence or no ANSYS on this PC is the usual cause; the engineer can run the same command on a PC that has it |

A `WARNING` that the start face does not begin at (0, 0) has two possible causes: the face
is smaller than the outline rectangle (cut-outs, an edge set back; harmless, TH5 shows
Y = 1.2 mm), or the drawing uses another origin than the ODB++ (then External Data will not
land on the model in step 4). Show the engineer the numbers and ask which it is; record the
answer in the Warnings table. Do not decide it yourself.

## Checkpoint (the engineer, in SpaceClaim)

Ask them to open the `.scdocx` and report:

- number of bodies in the component `Stackup` (must equal the layer count of step 2);
- total thickness (must equal the report total, for example 5.643 mm for TH5 SYE);
- two body names, the top and the bottom one (`Layer_1_...`, `Layer_<N>_...`);
- Share Topology of the component is `Share`.

## Log entry

Step 3 `done`; evidence = the `.scdocx` file name, body count, total thickness as reported by
the engineer, and which run folder the CSV came from.
