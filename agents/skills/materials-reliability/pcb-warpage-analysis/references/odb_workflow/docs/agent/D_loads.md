# Stage D - steps 7 and 8: BGA shadow, supports, thermal load

The engineer works in Mechanical. One step, then a checkpoint, as in stage C.
Full detail: `docs/07_downstream_workflow.md` (steps 7 and 8).

## Step 7 - named selection of the BGA shadow

Goal: the nodes of the PCB surface under the BGA package footprint.

1. **Ask (decision 8)**: which BGA or BGAs, the footprint rectangle of each in board
   coordinates (origin = board lower-left corner, as in the ODB++ of step 2), top or bottom
   surface. The engineer gets the rectangle from the layout. Do not derive it yourself.
2. They create it in Mechanical: Named Selection > Worksheet; `Geometry Type = Face` on the
   outer body (`Layer_1_...` for the top), convert to nodes, then filter `Location X` and
   `Location Y` by range to the footprint. One named selection per BGA, for example
   `NS_BGA_SHADOW_U1`.

Evidence: the name, the node count, the X and Y range of the selected nodes, and a
screenshot saved in PROJECT_DIR. Check that the range equals the rectangle they gave you and
that the node count is plausible for the mesh size (area / element size squared).

## Step 8a - supports

Warpage needs a support that removes the six rigid-body motions and nothing else, so that
the board can expand freely.

1. **Ask (decision 9)** which three corner vertices A, B and C are used.
2. They create:

   | Point | Object | Constrains |
   |---|---|---|
   | A, one corner | Fixed Support on 1 vertex | X, Y, Z |
   | B, a corner on the same edge as A | Displacement, Components | the two directions across that edge = 0, free along the edge (edge along X: Y = 0, Z = 0, X free) |
   | C, a third corner | Displacement, Components | Z = 0, X and Y free |

   Vertices only, never a face or an edge.

Evidence: for each of the three objects the scoping ("1 Vertex") and the component values.
Check: 3 + 2 + 1 = 6 constrained components in total.

## Step 8b - thermal load

1. **Ask (decision 10)** for the temperature points: start, end and the intermediate
   temperatures at which results are needed. They follow the measured SMT profile of the
   project (the documents list 30 / 100 / 150 / 183 / 200 / 220 C only as an example).
2. They insert a **Thermal Condition** on all PCB bodies with tabular temperature starting
   at `T_REF` (30 C unless decided otherwise in step 6) and ending at the peak, and set the
   analysis settings so that a result set exists at every temperature of interest.
3. They solve.

Evidence: the tabular data (time and temperature), the first value equals `T_REF`, the list
of result times with their temperatures, and after the solve: no errors in `solve.out`.

Three places must show the same reference temperature: `T_REF` in the v6 script, the reference
(environment) temperature of the analysis, the first value of the thermal load. Ask for all
three before the solve.

## Log entries

Step 7 and 8 `done` with the evidence above. Footprint, support points and temperature
points in the Decisions table.
