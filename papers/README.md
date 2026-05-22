# CDFD Runtime Papers

This folder contains the active 12-paper runtime spine. The papers were upgraded
in May 2026 to align with the current CLI-first runtime, CDFL command surface,
local discovery experiments, Part I/II citations, schematic figures, and stricter
claim discipline.

Runtime software DOI: https://doi.org/10.5281/zenodo.20343160

## Active Spine

1. `01_Axioms_State_Variables_and_Claim_Boundaries.tex`
2. `02_Layered_Ontology_for_Adaptive_Systems.tex`
3. `03_Dynamics_Regimes_and_Stability_Tests.tex`
4. `04_Engine_CLI_and_Reproducible_Execution.tex`
5. `05_CDFL_and_Executable_Model_Grammar.tex`
6. `06_CLI_First_Platform_and_Web_Architecture.tex`
7. `07_Autonomous_Discovery_Hypothesis_Triage_and_Falsification.tex`
8. `08_Proto_Regime_Boundary_Conditions_and_Theoretical_Discovery.tex`
9. `09_Tri_Regime_Bioenergetics_and_Life_Number_Diagnostics.tex`
10. `10_Multi_Domain_Isomorphism_and_Adapter_Evidence.tex`
11. `11_Validation_Precision_and_Falsifiability.tex`
12. `12_Candidate_Laws_Discovery_Program_and_Responsible_Use.tex`

## Experiment Surface

Use `../experiments/reports/FINAL_RELEASE_EXPERIMENT_SELECTION.md` as the public
selection filter. It marks the following outputs as suitable to discuss with
candidate/falsification language:

- `../experiments/outputs/discovery_vacuum_hysteresis.h5`
- `../experiments/outputs/discovery_knot_n7.h5`
- `../experiments/outputs/discovery_ool_phase_results.h5`
- `../experiments/outputs/frontier_sweep.h5`
- `../experiments/outputs/gigamarathon_1000_results.h5`

The overloaded adaptive-surface run is an instability boundary, not support for
an engineering success claim.

## Claim Discipline

Runtime experiments are model diagnostics unless independently validated. Use
phrases such as candidate simulation result, hypothesis triage, falsification
target, and model diagnostic. Avoid proof, oracle, validated, or device/clinical
claim language unless the supporting evidence actually exists.

## Metadata Standard

The active papers use `Steve Bico Mujjabi, MD`, the Part I ORCID
`0009-0001-0556-5516`, and month-year dates. Each paper includes a compact
schematic and prior-work references.

## Build

Compile to a temporary build directory from the runtime root:

```bash
mkdir -p /tmp/cdfd_runtime_papers_build
for f in papers/[0-9][0-9]_*.tex; do
  pdflatex -interaction=nonstopmode -halt-on-error \
    -output-directory /tmp/cdfd_runtime_papers_build "$f"
done
```
