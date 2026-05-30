## Summary

Describe the runtime, docs, metadata, or paper-surface change.

## Checks

- [ ] `git diff --check`
- [ ] `python scripts/generate_domain_matrix.py --check`
- [ ] `cdfd doctor --json`
- [ ] `cdfd gallery --json --out /tmp/cdfd-gallery.json`
- [ ] `python -m pytest -q tests/test_cli_runtime.py tests/test_new_engine_upgrades.py tests/test_release_surfaces.py`
- [ ] `papers/build_pdfs.sh` or 12 committed PDFs verified

## Boundary

- [ ] This change keeps runtime output inside the modeling and hypothesis-triage boundary.
