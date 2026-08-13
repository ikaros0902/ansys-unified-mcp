# Materials (`*MAT_*`) — condensed reference

Material models are defined with `*MAT_*` keywords, referenced by a material ID
(MID) that parts point to. Get exact card fields from `LS-DYNA_Users_Guide` via
search — do not guess field positions.

## How materials attach

```
*PART            -> references a SECTION id and a MID
*MAT_<model>     -> defines material MID with its constants
```

## Common material families

- Elastic / rigid: `*MAT_ELASTIC` (001), `*MAT_RIGID` (020).
- Metal plasticity: `*MAT_PLASTIC_KINEMATIC` (003),
  `*MAT_PIECEWISE_LINEAR_PLASTICITY` (024), `*MAT_JOHNSON_COOK` (015).
- Foams / rubbers: `*MAT_LOW_DENSITY_FOAM`, `*MAT_OGDEN_RUBBER`,
  `*MAT_MOONEY-RIVLIN_RUBBER`.
- Composites: `*MAT_ENHANCED_COMPOSITE_DAMAGE` (054/055), `*MAT_LAMINATED_*`.
- Concrete / soil / geomaterials: `*MAT_CONCRETE_DAMAGE`, `*MAT_SOIL_AND_FOAM`.
- Equation of state (fluids/high-rate): pair a `*MAT_*` with an `*EOS_*` (see
  `specialized_solvers.md`).

## Finding the right card

```
search_ansys_docs("*MAT_PIECEWISE_LINEAR_PLASTICITY", scope="all")
search_ansys_docs("MAT_JOHNSON_COOK", scope="all")
```

- Material numbers (e.g. 024) and names both work as `*MAT_<NAME>` or `*MAT_<nnn>`.
- Rate effects, failure, and EOS coupling are model-specific — check the card.

## Notes

- A material is inert until a `*PART` references its MID together with a
  `*SECTION` (see `elements_sections_parts.md`).
- For temperature-dependent runs, thermal material variants exist (`*MAT_THERMAL_*`).
