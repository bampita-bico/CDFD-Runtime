# Release Checklist

Use this checklist from a clean release branch or tag.

## Local Gates

```bash
python -m pip install -e ".[dev,web,experiments]"
git diff --check
python scripts/generate_domain_matrix.py --check
cdfd doctor --json
cdfd gallery --json --out /tmp/cdfd-gallery.json
cdfd compare origins_of_life --scenarios mixed_source_surface_trap meteoritic_seed_retained --json
python -m pytest -q tests/test_cli_runtime.py tests/test_new_engine_upgrades.py tests/test_release_surfaces.py
python -m build
python -m twine check dist/*
```

When LaTeX is installed:

```bash
papers/build_pdfs.sh
```

## Bundle

```bash
scripts/build_release_bundle.sh
```

The bundle writes wheel/sdist output, checkout archive, SHA256 checksums, test
report, doctor JSON, gallery JSON, compare JSON, generated reports, and PDF
build evidence under `dist/release-bundle-*`.

## Before Publication

- `CITATION.cff`, `.zenodo.json`, `codemeta.json`, and
  `ro-crate-metadata.json` contain the same title, version, DOI, author, and
  license.
- `README.md` installation commands match `pyproject.toml`.
- `docs/domain_maturity_matrix.json` matches the current registry.
- Runtime papers and committed PDFs are synchronized.
- Release notes state the claim boundary plainly.
