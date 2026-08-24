# Release Checklist

Use this checklist from a clean release branch or tag.

## Local Gates

```bash
python -m pip install -e ".[dev,experiments]"
git diff --check
python scripts/check_joss_paper.py
cdfd doctor --json
cdfd gallery --json --out /tmp/cdfd-gallery.json
python experiments/run_cdfl_smoke.py --out /tmp/cdfl-smoke.json
python -m pytest -q tests/test_cli_runtime.py tests/test_release_surfaces.py tests/test_joss_submission_assets.py
python -m build
python -m twine check dist/*
```

## Bundle

```bash
scripts/build_release_bundle.sh
```

The bundle writes wheel/sdist output, checkout archive, SHA256 checksums, test
report, doctor JSON, gallery JSON, smoke experiment JSON, and generated reports
under `dist/release-bundle-*`.

## Before Publication

- `CITATION.cff`, `.zenodo.json`, `codemeta.json`, and
  `ro-crate-metadata.json` contain the same title, version, DOI, author, and
  license.
- `README.md` installation commands match `pyproject.toml`.
- `ARCHIVE_NOTICE_2026-08-25.md` matches the retained active tree.
- Release notes state the claim boundary plainly.
