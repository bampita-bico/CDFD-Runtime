# Contributing

CDFD Runtime is CLI-first research software. Contributions must preserve the
runtime boundary: deterministic modeling, finite-audited result envelopes, and
clear claim limits.

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,experiments]"
```

Core CLI-only work can use:

```bash
python -m pip install -e .
```

## Checks

Run the focused public gates before opening a pull request:

```bash
git diff --check
python scripts/check_joss_paper.py
cdfd doctor --json
cdfd gallery --json --out /tmp/cdfd-gallery.json
python experiments/run_cdfl_smoke.py --out /tmp/cdfl-smoke.json
python -m pytest -q tests/test_cli_runtime.py tests/test_release_surfaces.py tests/test_joss_submission_assets.py
```

## Public Claims

Do not present runtime output as empirical proof, clinical advice, engineering
certification, financial advice, or deployed safety logic. Use release-paper,
DOI, and result-envelope evidence when a public statement refers to a runtime
artifact.

Legacy domain adapters, multi-paper runtime manuscripts, and the old experiment
corpus are archived outside the repo. See `ARCHIVE_NOTICE_2026-08-25.md`.
