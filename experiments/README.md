# CDFD Runtime Experiments

This folder holds the active public experiment surface for the slim CDFD Runtime
release. It supports the research-software paper (`docs/paper.md`) only: CDFL parse,
validation, execution, finite audit, and reproducible smoke output.

## Active experiment

- `run_cdfl_smoke.py` — runs the canonical `examples/heat_flow.cdfl` model through
  the same CLI backend used in production and writes JSON under `outputs/`.

```bash
python experiments/run_cdfl_smoke.py
python experiments/run_cdfl_smoke.py --out experiments/outputs/cdfl_smoke.json
```

The script records software facts only: parse validity, execution status, and the
finite-output audit envelope. It does not establish domain validation or
empirical proof.

## Archived legacy corpus

The former multi-domain experiment reports, notebooks, Part II diagnostics, and
196-adapter sweep material were moved to:

`/home/bampita/Projects/CDFD/CDFD-ARCHIVE-2026-08-24/runtime/one_paper_cleanup_2026-08-25/legacy_experiments/`

See `ARCHIVE_NOTICE_2026-08-25.md` at the repository root for the retained-release
scope.
