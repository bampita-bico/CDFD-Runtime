# CDFD Runtime v1.1.1 — Slim CDFL Research-Software Release

## Summary

This release replaces the earlier multi-paper, multi-domain runtime tree with a **focused research-software package**. CDFD Runtime is now a local command-line tool for CDFL parse, validate, execute, finite audit, reporting, and reproducible smoke output — not a cross-domain validation platform.

Before citing any output, read [`ARCHIVE_NOTICE_2026-08-25.md`](https://github.com/bampita-bico/CDFD-Runtime/blob/v1.1.1/ARCHIVE_NOTICE_2026-08-25.md) and [`CLAIM_BOUNDARY.md`](https://github.com/bampita-bico/CDFD-Runtime/blob/v1.1.1/CLAIM_BOUNDARY.md).

## What this release includes

- **CDFL CLI:** `validate`, `run`, `cdfl lint|format|ast|sample`, `gallery`, `doctor`, `report`, `explain`, optional `llm`
- **One canonical model:** `examples/heat_flow.cdfl`
- **One public experiment:** `experiments/run_cdfl_smoke.py`
- **One software paper:** `docs/paper.md` with `docs/paper.bib`
- **VS Code extension source:** `tools/cdfl-vscode/`
- **Focused tests + CI** for the slim surface (**23 tests passing**)

## What changed from v1.1.0

### Removed from the active repository

- 12-paper runtime TeX/PDF manuscript suite (`papers/`)
- 196 domain adapters (`domains/`; maturity-matrix registered count)
- Legacy experiment corpus, discovery notebooks, and domain sweep outputs
- Streamlit Runtime Studio (`webapp/`)
- Discovery/triage helpers (`discovery/`)
- Domain-heavy ontology packages and domain engine modules
- CLI commands: `domains`, `demo`, `compare`, `diagnostics`
- Domain maturity matrix and web dependency bundle

### Kept / simplified

- Physics-grid engine kernel and generic analysis helpers
- Slim ontology bookkeeping (`meta/`, `runtime/`, `actions/`)
- Result envelopes, finite audits, run bundles, and claim-boundary reporting
- Optional LLM interpretation layer (above saved results, not in the numerical engine)

### Documentation alignment

- Metadata, README, API docs, and JOSS paper text now describe **only** the slim release
- Research-software paper lives at `docs/paper.md`

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,experiments]"

cdfd doctor --json
cdfd gallery --json --out outputs/gallery.json
python experiments/run_cdfl_smoke.py --out outputs/cdfl_smoke.json
python -m pytest -q tests/
```

## Claim boundary

Runtime output is a **deterministic toy-model and software-audit surface**. It is not empirical validation, clinical advice, engineering certification, or a deployed decision system.

## Archive / provenance

Legacy material was **not deleted**. It is retained in the local working archive described in `ARCHIVE_NOTICE_2026-08-25.md` under `CDFD-ARCHIVE-2026-08-24/runtime/`.

## DOI note

- **Cite this snapshot:** [10.5281/zenodo.22090332](https://doi.org/10.5281/zenodo.22090332) (v1.1.1)
- **All-versions / concept-family DOI used in badges:** [10.5281/zenodo.20343160](https://doi.org/10.5281/zenodo.20343160)

## Verification for this tag

- `python scripts/check_joss_paper.py`
- `python -m pytest -q tests/` (23 passed)
- `git diff --check`
