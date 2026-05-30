# Release Process

CDFD Runtime releases produce installable packages, machine-readable metadata,
runtime evidence, and paper-build evidence.

## Gates

```bash
python -m pip install -e ".[dev,web,experiments]"
git diff --check
python scripts/generate_domain_matrix.py --check
cdfd doctor --json
cdfd gallery --json --out /tmp/cdfd-gallery.json
cdfd compare origins_of_life --scenarios mixed_source_surface_trap meteoritic_seed_retained --json
cdfd report /tmp/cdfd-gallery.json --format markdown --out /tmp/cdfd-gallery.md
cdfd explain /tmp/cdfd-gallery.json --format markdown --out /tmp/cdfd-gallery-explain.md
python -m pytest -q tests/test_cli_runtime.py tests/test_new_engine_upgrades.py tests/test_release_surfaces.py
python -m build
python -m twine check dist/*
```

When `latexmk` is present:

```bash
papers/build_pdfs.sh
```

Without `latexmk`, verify the committed `papers/PDFs/` set has 12 PDFs before
publication.

## Bundle Command

```bash
scripts/build_release_bundle.sh
```

The bundle contains:

- Source checkout archive.
- Wheel and sdist.
- SHA256 checksums.
- Test report.
- `doctor.json`.
- `gallery.json`.
- origins-of-life comparison JSON.
- Markdown report and explanation output.
- PDF build log or PDF-presence evidence.

## Metadata Surfaces

Keep these synchronized:

- `CITATION.cff`
- `.zenodo.json`
- `codemeta.json`
- `ro-crate-metadata.json`
- `pyproject.toml`
- `README.md`
