# CDFD Runtime Archive Notice — 2026-08-25

This notice defines the active slim software release after the one-paper cleanup.

## Active in `CDFD-Runtime`

- CLI/runtime source: `cdfd.py`, `runtime/`, `dsl/`, `engine/`, `ontology/`
- Core engine only: physics grid kernel plus generic analysis helpers
- Core ontology only: `meta/`, `runtime/`, `actions/`, and the slim `engine.py`
- Canonical example: `examples/heat_flow.cdfl`
- Public experiment: `experiments/run_cdfl_smoke.py`
- Research-software paper: `docs/paper.md`, `docs/paper.bib`
- Claim boundary: `CLAIM_BOUNDARY.md`
- Tests, CI, packaging metadata, VS Code CDFL extension source

## Archived outside the repository

Working and legacy material is retained under:

`/home/bampita/Projects/CDFD/CDFD-ARCHIVE-2026-08-24/runtime/`

Notable archived paths from the 2026-08-25 cleanup:

- `one_paper_cleanup_2026-08-25/legacy_manuscript_suite/` — former 12-paper runtime TeX/PDF suite
- `one_paper_cleanup_2026-08-25/legacy_domain_adapters/` — 196 domain adapters
- `one_paper_cleanup_2026-08-25/legacy_experiments/` — legacy reports, notebooks, and outputs
- `one_paper_cleanup_2026-08-25/legacy_domain_maturity/` — domain maturity matrix tooling
- `one_paper_cleanup_2026-08-25/legacy_webapp/` — Streamlit Runtime Studio
- `one_paper_cleanup_2026-08-25/legacy_discovery/` — discovery/triage helpers
- `one_paper_cleanup_2026-08-25/legacy_ontology_domains/` — domain ontology packages
- `one_paper_cleanup_2026-08-25/legacy_engine_domains/engine/` — domain engine modules
- `one_paper_cleanup_2026-08-25/legacy_runtime_orchestration/` — parallel/queue/task helpers
- `one_paper_cleanup_2026-08-25/legacy_methods_package/methods/` — copied methods package
- `requirements-web.txt` — removed from active tree; web dependencies archived with Streamlit Studio
- `planning/` — JOSS submission and correction planning records
- `generated_artifacts/` — build bundles, dist output, prior run folders
- `generated_caches/` — Python/pytest caches

Nothing was deleted. Archived material is provenance only and does not change the
active software claim boundary in `CLAIM_BOUNDARY.md`.

## Removed CLI surfaces

The active CLI no longer exposes bundled domain demos, scenario comparison, or
Part II diagnostic exports. Use CDFL validate/run/gallery/report/explain instead.
