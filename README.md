# CDFD Runtime

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20343160.svg)](https://doi.org/10.5281/zenodo.20343160)

CDFD Runtime is the public command-line runtime for Constraint-Driven Flux
Dynamics (CDFD) and the CDFL executable model grammar.

The active release is a **slim research-software package**: CDFL parse, validate,
execute, finite audit, report/export, optional LLM interpretation, one public
smoke experiment, and one research-software paper (`docs/paper.md`). It does not ship
the former 12-paper runtime manuscript suite, 196 domain adapters, or legacy
experiment corpus. See `ARCHIVE_NOTICE_2026-08-25.md`.

## Author

Steve Bico Mujjabi, MD
Independent Researcher, Founder, Vura Labs
Kampala, Uganda
ORCID: https://orcid.org/0009-0001-0556-5516

## 5-Minute Path

```bash
git clone https://github.com/bampita-bico/CDFD-Runtime.git
cd CDFD-Runtime
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

```bash
cdfd --help
cdfd doctor --json
cdfd gallery --save-run --json --out outputs/gallery.json
cdfd report outputs/gallery.json --format markdown --out outputs/gallery_report.md
python experiments/run_cdfl_smoke.py
```

From a source checkout, `python cdfd.py ...` is equivalent to `cdfd ...`.

## Install Modes

Core CLI/runtime:

```bash
python -m pip install -e .
```

Development, experiments, packaging, and tests:

```bash
python -m pip install -e ".[dev,experiments]"
```

## CLI Examples

```bash
cdfd info
cdfd doctor --json
cdfd gallery --json
cdfd cdfl lint examples/heat_flow.cdfl
cdfd cdfl ast examples/heat_flow.cdfl --json
cdfd validate examples/heat_flow.cdfl
cdfd run examples/heat_flow.cdfl --nx 4 --ny 4 --out outputs/heat_flow_run.json
cdfd export outputs/heat_flow_run.json --out outputs/heat_flow_export.json
```

Run tests:

```bash
python -m pytest -q tests/test_cli_runtime.py tests/test_release_surfaces.py tests/test_joss_submission_assets.py
```

## Active Release Surfaces

- `cdfd.py` — public CLI entrypoint
- `runtime/` — command backend, result envelopes, finite audits, export helpers
- `dsl/` — CDFL lexer, parser, AST, scheduler, executor
- `engine/` — physics grid kernel and generic analysis helpers
- `ontology/` — slim semantic bookkeeping layer (`meta/`, `runtime/`, `actions/`)
- `examples/heat_flow.cdfl` — canonical public model
- `experiments/run_cdfl_smoke.py` — reproducible software smoke experiment
- `docs/paper.md`, `docs/paper.bib` — research-software paper draft
- `CLAIM_BOUNDARY.md`, `ARCHIVE_NOTICE_2026-08-25.md` — claim and archive scope
- `tools/cdfl-vscode/` — VS Code CDFL extension source
- `tests/`, `.github/workflows/ci.yml`, `scripts/check_joss_paper.py`

## Claim Boundary

CDFD Runtime output is a deterministic toy-model and software-audit surface.
It is not medical advice, engineering certification, empirical evidence, a
calibrated forecast, or a deployed decision system. Read `CLAIM_BOUNDARY.md`
before citing runtime output as support for a domain claim.

## Research-Software Paper

The active publication surface is `docs/paper.md` (JOSS-style research-software
paper). The former 12-paper runtime TeX/PDF suite is archived outside the repo;
see `ARCHIVE_NOTICE_2026-08-25.md`.

## Licensing

Dual-licensed:

1. Academic/personal use: [GNU AGPLv3](LICENSE)
2. Commercial use: separate license required

Contact msbico@gmail.com for commercial licensing.

## Citation

Use `CITATION.cff` for software metadata. The slim release is version `1.1.1`; mint a
new Zenodo version before citing that snapshot by DOI.

Mujjabi, S. B. (2026). CDFD Runtime: Constraint-Driven Flux Dynamics and CDFL Execution Engine. Zenodo.
https://doi.org/10.5281/zenodo.20343160

The runtime is separate from the Part I–IV scholarly archives.
