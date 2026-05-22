> **Release note (2026-05-19):** This file selects which CDFD Runtime experiment outputs are suitable to mention in the public papers. These are candidate simulation results and falsification targets, not empirical proof.

# Final Release Experiment Selection

## Runtime and Constant

- Runtime name: **CDFD Runtime**.
- Script language name: **CDFL**.
- Constant baseline: CODATA 2022, \(\chi^* = \alpha^{-1} = 137.035999177\).
- Generated outputs live under `experiments/outputs/`.

## Include

| Output | Result | How to use it |
|---|---:|---|
| `discovery_vacuum_hysteresis.h5` | peak center `M_s = 15.5843` | Use as the candidate vacuum-memory / hysteresis protocol. |
| `discovery_knot_n7.h5` | stability index `0.992686 -> 0.987976` | Use as a weak higher-knot self-stabilization stress test, not a proof. |
| `discovery_ool_phase_results.h5` | four grid points near `Lambda = 1` | Use only as a cross-Part-II phase-boundary bridge. |
| `frontier_sweep.h5` | 2500 points, 2487 non-trivial candidate records | Use as hypothesis triage for future tests. |
| `gigamarathon_1000_results.h5` | 10 domains x 100 points | Use as discovery-engine coverage evidence, not physical validation. |

## Do Not Use as Support

| Output | Reason |
|---|---|
| `discovery_surface_evolution.h5` | the overloaded run moved `Psi_s` from `5.1514` to `978.9943`; treat it as an instability boundary. |
| Legacy marathon/megamarthon narrative reports | They are retained as simulation logs only; the release-facing language is candidate/falsification language. |

## Paper Placement

- Paper I: mention the twelve-decimal CODATA 2022 recovery and the necessary conditions.
- Paper X: cite this experiment selection as CDFD Runtime hooks for vacuum engineering and Fibonacci transport optimization.
- Paper XII: use the vacuum-hysteresis, alpha-jitter, decoherence-memory, and pressure-gradient tests as falsifiable protocols.
- Reports: keep all report claims in simulation-log language.
