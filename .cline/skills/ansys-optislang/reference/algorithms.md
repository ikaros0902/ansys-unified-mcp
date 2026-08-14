# Algorithms — condensed API

Sensitivity, sampling/DoE, optimization, and robustness are each an actor.
Native optiSLang Python. Verified actor names from
`optiSLang_Customization_API_and_Remote_Control`.

## Sampling / sensitivity / robustness

```python
sens = actors.SensitivityActor("Sensitivity")   # sensitivity / DoE study
add_actor(sens)

rob  = actors.RobustnessActor("Robustness")      # robustness analysis
samp = actors.SamplingActor("Sampling")          # sampling
```

## Optimization actors

Optimizers derive from `OptimizationBaseActor`:

- `ARSMActor` — Adaptive Response Surface Method.
- `NLPQLPActor` — gradient-based NLPQLP.
- `NOAActor` — nature-inspired optimization, including `EAActor` (evolutionary),
  `PSOActor` (particle swarm), `SDIActor`.
- `SimplexActor` — simplex.
- `MemeticActor` — memetic (hybrid).

```python
opt = actors.NLPQLPActor("Optimization")
add_actor(opt)
```

## Algorithm settings

The `AlgorithmSystemActor` supports binfile writing; algorithm settings are
modified via the set functionality of the specific algorithm actor. For the
exact setter names (population size, iterations, tolerances), search
`optiSLang_Customization_API_and_Remote_Control` by the actor class name, or the
method guides (`Methods_for_Parametric_Design_Optimization`,
`optiSLang_Methods_for_Multi-Disciplinary_Optimization_and_Robustness_Analysis`).

## Choosing a method

- Screening / understanding drivers → `SensitivityActor` (DoE + MOP).
- Smooth, few variables → `NLPQLPActor` or `ARSMActor`.
- Rugged / global / many variables → `NOAActor` (EA/PSO).
- Scatter / tolerances → `RobustnessActor`.
