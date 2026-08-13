# Designs & Results — condensed API

Design points and their results after a run. Native optiSLang Python. Terms
verified from `optiSLang_Users_Guide` / `optiSLang_Customization_API_and_Remote_Control`.

## Design Container

Result designs from an algorithm or from a Metamodel of Optimal Prognosis (MOP)
are collected in the **Design Container** managed by the ParametricSystemActor.
Design categories that appear in results/OMDB:

- Result designs (from the algorithm)
- Approximated designs / validated designs (from MOP)
- Reference design, nominal design (robustness/reliability)
- Deactivated designs (user-excluded)

## MOP (Metamodel of Optimal Prognosis)

MOP builds surrogate metamodels approximating the response over the design
space. Metamodels and approximated designs are stored alongside the result
designs.

## Reading results

Read designs/results by running native optiSLang Python via
`run_optislang_script` after `start_optislang_project()` completes. For the
exact accessors (iterating designs, extracting parameter/response values),
search `optiSLang_Customization_API_and_Remote_Control` — these vary by release.

## OMDB (optiSLang Monitoring Database)

The OMDB file persists results: Parameter Manager, Design Container, Metamodels,
approximated/validated designs, reference/nominal designs, and algorithm info.

## Notes

- The parametric problem (parameters + criteria, see
  `parameters_and_responses.md`) determines what each design records.
- For post-processing nodes, see `PostprocessingActor` in `nodes_and_actors.md`.
