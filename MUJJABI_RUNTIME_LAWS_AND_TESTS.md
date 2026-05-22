# Mujjabi Runtime Laws, Principles, and Tests

This file gives the public naming layer for CDFD Runtime. The names are strong
by design, but every entry is tied to a mathematical role and a status. A law
here means a law inside the CDFD runtime framework until independent experiment
or external benchmark establishes a stronger physical status.

## Core Laws and Principles

| Name | Symbolic form | Role in CDFD Runtime | Status |
|---|---|---|---|
| Mujjabi Adaptive Operating Ratio | `Psi_s = (Phi / C) * S * M_s` | Shared runtime grammar for flow, constraint, responsiveness, and structural memory. | Core notation. |
| Mujjabi Runtime Constraint Law | `C > 0` and finite output required for any accepted run | Prevents division artifacts and non-finite diagnostics from entering public output as discoveries. | Runtime guardrail. |
| Mujjabi CDFL Execution Principle | Model text must parse, execute, and emit structured provenance | Makes CDFL models reproducible from source files rather than screenshots or prose. | Public software principle. |
| Mujjabi Domain Adapter Principle | Domain variables must map explicitly into `Phi`, `C`, `S`, `M_s`, or derived diagnostics | Keeps cross-domain analogies inspectable and falsifiable. | Adapter contract. |
| Mujjabi Finite-Audit Principle | `NaN`, `Inf`, and non-finite values are release blockers unless explicitly labeled as failed diagnostics | Protects papers and demos from hidden numerical failure. | Release guardrail. |
| Mujjabi App-Boundary Principle | Applications own user identity, API keys, LLM routing, and workflow policy; the runtime owns deterministic execution | Separates the public engine from unfinished products and private services. | Architecture principle. |
| Mujjabi Discovery-Triage Principle | Candidate discoveries select follow-up tests; they do not count as proof by themselves | Keeps autonomous discovery framed as hypothesis generation. | Claim-discipline rule. |

## Mujjabi Runtime Tests

| Test | Prediction | Primary observable | Falsification condition |
|---|---|---|---|
| Mujjabi CLI Reproducibility Test | The same CDFL file and parameters produce the same structured result envelope. | `python cdfd.py run examples/heat_flow.cdfl` output. | Results change without source, parameter, or dependency changes. |
| Mujjabi CDFL Parse-Run Test | Valid CDFL parses into typed nodes and executes through the runtime executor. | Validation status, node count, and run result blocks. | Valid syntax cannot be parsed or executed. |
| Mujjabi Domain Adapter Mapping Test | A registered domain maps payload values into bounded engine variables. | `python cdfd.py demo <domain>` final regime and finite audit. | Domain output is non-finite or lacks an inspectable mapping. |
| Mujjabi Finite Output Test | Public JSON output contains only finite, serializable values. | `finite_audit.all_finite == true`. | `NaN`, `Inf`, or unserializable values appear in output. |
| Mujjabi App API-Key Boundary Test | The runtime can check caller keys without storing or printing raw secrets. | `auth` result with accepted status and redacted fingerprint. | Raw key appears in output or an invalid key is accepted. |
| Mujjabi Vacuum Hysteresis Candidate Test | History-loaded systems may show bounded memory residuals under controlled conditions. | Candidate hysteresis output from public experiment scripts. | Residuals vanish under controls or reduce to ordinary numerical artifacts. |
| Mujjabi n=7 Knot Stability Candidate Test | The public runtime can reproduce the candidate n=7 stability probe as a falsification target. | Curated knot-stability script/output pair. | The signal does not survive parameter, seed, and resolution checks. |
| Mujjabi Life Number Boundary Test | Origins-of-life diagnostics should occupy a finite near-critical band, not a single magic point. | Life-number sweep output and CDFL/runtime diagnostics. | Any single variable predicts persistence as well as the coupled gate. |

## Public Use Standard

Runtime output must stay attached to source files, commands, parameters, and
failure conditions. A candidate law that cannot be rerun, falsified, or compared
against a baseline does not belong in the public release surface.
