## Summary

Describe the runtime, docs, metadata, or paper-surface change.

## Checks

- [ ] `git diff --check`
- [ ] `python scripts/check_joss_paper.py`
- [ ] `cdfd doctor --json`
- [ ] `cdfd gallery --json --out /tmp/cdfd-gallery.json`
- [ ] `python experiments/run_cdfl_smoke.py --out /tmp/cdfl-smoke.json`
- [ ] `python -m pytest -q tests/test_cli_runtime.py tests/test_release_surfaces.py tests/test_joss_submission_assets.py`

## Boundary

- [ ] This change keeps runtime output inside the modeling and software-audit boundary.
