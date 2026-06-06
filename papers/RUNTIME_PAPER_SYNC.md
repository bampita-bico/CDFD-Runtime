# Runtime Paper Sync (May-June 2026)

This checklist maps the 12 runtime papers to the current public repository state.
Rebuild PDFs after LaTeX edits: `bash papers/build_pdfs.sh`.

## Platform

| Runtime fact | Papers |
|---|---|
| Primary surface: `python cdfd.py` (CLI-first) | 04, 06, 11 |
| Commands: info, domains, demo, diagnostics, cdfl, validate, run, gallery, compare, report, explain, llm, export, auth | 01, 04, 06 |
| CDFL workbench: lint, format, AST, sample, runtime-backed validation/run | 02, 04, 05, 06, 11 |
| `python cdfd.py diagnostics` → `experiments/outputs/part_ii_runtime_diagnostics.json` | 01, 04, 09, 11 |
| Optional web: `python -m webapp.run_server` with CDFL Workbench (not a second engine) | 06 |
| `webapp/neo4j_ontology.py` (does not shadow `ontology/` package) | 04, 06 |
| 196 domain adapters (`cdfd.py domains`) | 10 |
| Result envelopes + `finite_audit` on CLI output | 04, 05, 11 |
| VS Code extension under `tools/cdfl-vscode` calls the same runtime CDFL tooling | 05, 11 |
| `cdfd.py llm ...` provider interpretation sits above deterministic results; `auth` aliases provider-key status | 04, 06, 12 |

## Part II diagnostics

| Runtime fact | Papers |
|---|---|
| `runtime/diagnostics.py`: aromatic source-mix, Life Number, guardrails | 03, 04, 09 |
| Best scenario: `mixed_source_surface_trap`, functional score `0.610` | 09, 11 |
| `cdfd.py demo origins_of_life --source-scenario <name>` | 04, 09, 10 |
| Eumelanin/chlorophyll as mature endpoints, not origin requirements | 09, 12 |
| Runtime paper bibliography uses Part II DOI `10.5281/zenodo.20264779` | 01-12 |

## Engine & discovery

| Runtime fact | Papers |
|---|---|
| `engine/causal_graph.py` (Granger-style edges from history) | 07, 06 (web) |
| `engine/kernel.py` rich history (Φ, C, S, M_s means per step) | 04, 06 |
| Domain demo per-step `trace` | 04 |
| Selected `.h5` experiments + `FINAL_RELEASE_EXPERIMENT_SELECTION.md` | 01, 07, 08, 11, 12 |
| `MUJJABI_RUNTIME_LAWS_AND_TESTS.md` | 12 |

## Verification

| Runtime fact | Papers |
|---|---|
| `tests/test_cli_runtime.py`, `tests/test_release_surfaces.py`, `tests/test_cdfl_vscode_extension.py`: 38 focused tests in the June sync pass | 04, 11 |
| `cdfd.py doctor --json`: 11 ok checks in the June sync pass | 04, 11 |
| `cdfd.py gallery --steps 1 --nx 4 --ny 4 --json`: ok finite-audited gallery in the June sync pass | 04, 11 |
| VS Code Extension Development Host smoke: `.cdfl` mode, commands, diagnostics, formatting, validate/run | 05, 11 |

## Already aligned (no May 2026 text change required)

- Greek-symbol convention paragraph: all 12 papers
- Prior CDFD basis + evidence-path figure: all 12 papers
- Claim discipline (candidate / falsification language): all 12 papers

## Not claimed in papers (by design)

- API server (listed as future service/API wrapper in Paper 06 ordering only)
- Empirical validation of CDFD theory
- Neo4j required for CLI operation
- LLM output as validation, engine input, or deterministic evidence
