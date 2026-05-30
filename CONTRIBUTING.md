# Contributing

CDFD Runtime is CLI-first research software. Contributions must preserve the
runtime boundary: deterministic modeling, finite-audited result envelopes, and
clear claim limits.

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,web,experiments]"
```

Core CLI-only work can use:

```bash
python -m pip install -e .
```

## Checks

Run the focused public gates before opening a pull request:

```bash
git diff --check
python scripts/generate_domain_matrix.py --check
cdfd doctor --json
cdfd gallery --json --out /tmp/cdfd-gallery.json
python -m pytest -q tests/test_cli_runtime.py tests/test_new_engine_upgrades.py tests/test_release_surfaces.py
```

When LaTeX is available:

```bash
papers/build_pdfs.sh
```

## Adapter Changes

Domain adapters need to:

- Map inputs into CDFD runtime variables without external network state.
- Return finite JSON-visible outputs.
- Keep medical, engineering, financial, policy, and safety domains inside the
  modeling boundary.
- Update `docs/domain_maturity_matrix.json` through
  `python scripts/generate_domain_matrix.py` when adapter registration changes.

## Public Claims

Do not present runtime output as empirical proof, clinical advice, engineering
certification, financial advice, or deployed safety logic. Use release-paper,
DOI, and result-envelope evidence when a public statement refers to a runtime
capability.
