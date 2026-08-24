# Release Process

CDFD Runtime releases produce installable packages, machine-readable metadata,
runtime evidence, and JOSS-paper validation.

## Gates

```bash
python -m pip install -e ".[dev,experiments]"
git diff --check
python scripts/check_joss_paper.py
cdfd doctor --json
cdfd gallery --json --out /tmp/cdfd-gallery.json
python experiments/run_cdfl_smoke.py --out /tmp/cdfl-smoke.json
cdfd report /tmp/cdfd-gallery.json --format markdown --out /tmp/cdfd-gallery.md
cdfd explain /tmp/cdfd-gallery.json --format markdown --out /tmp/cdfd-gallery-explain.md
python -m pytest -q tests/test_cli_runtime.py tests/test_release_surfaces.py tests/test_joss_submission_assets.py
python -m build
python -m twine check dist/*
```

## Bundle Command

```bash
scripts/build_release_bundle.sh
```

The bundle contains:

- Source checkout archive
- Wheel and sdist
- SHA256 checksums
- Test report
- `doctor.json`
- `gallery.json`
- `cdfl_smoke.json`
- Markdown report and explanation output

## Metadata Surfaces

Keep these synchronized:

- `CITATION.cff`
- `.zenodo.json`
- `codemeta.json`
- `ro-crate-metadata.json`
- `pyproject.toml`
- `README.md`
- `ARCHIVE_NOTICE_2026-08-25.md`
