# CDFD Runtime

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20343160.svg)](https://doi.org/10.5281/zenodo.20343160)

CDFD Runtime is the public command-line runtime for Constraint-Driven Flux
Dynamics (CDFD) and the CDFL executable model grammar.

The runtime runs locally on the user's machine after clone or download. It does
not run on the author's laptop, and it does not require access to private
servers, private datasets, API keys, or hosted infrastructure.

## Author

Steve Bico Mujjabi, MD<br>
Independent Researcher<br>
Founder, Vura Labs<br>
Kampala, Uganda<br>
ORCID: https://orcid.org/0009-0001-0556-5516

Institutional home: **Vura Labs**

## Release Naming

CDFD Runtime: Constraint-Driven Flux Dynamics and CDFL Execution Engine

Software DOI: https://doi.org/10.5281/zenodo.20343160

## Keywords

Constraint-Driven Flux Dynamics; CDFD; CDFD Runtime; CDFL; executable model
grammar; adaptive operating ratio; structural memory; domain adapters;
ontology runtime; deterministic execution; finite audit; scientific computing;
computational modeling; systems science; complex systems; physics simulation;
origins of life; bioenergetics; hypothesis triage; falsification; candidate
laws; Mujjabi laws; Mujjabi tests; reproducible research; open science;
research software.

## GitHub Topics

`cdfd`, `cdfd-runtime`, `cdfl`, `constraint-driven-flux-dynamics`,
`adaptive-systems`, `scientific-computing`, `computational-modeling`,
`systems-science`, `complex-systems`, `physics-simulation`, `ontology`,
`domain-adapters`, `reproducible-research`, `open-science`,
`origins-of-life`, `bioenergetics`, `validation`, `falsifiability`,
`research-software`, `agplv3`

## 5-Minute Path

```bash
git clone https://github.com/bampita-bico/CDFD-Runtime.git
cd CDFD-Runtime
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[web]"
```

Run the installed CLI:

```bash
cdfd --help
cdfd doctor --json
mkdir -p outputs
cdfd gallery --save-run --json --out outputs/gallery.json
cdfd report outputs/gallery.json --format markdown --out outputs/gallery_report.md
cdfd explain outputs/gallery.json --format markdown --out outputs/gallery_explain.md
python -m webapp.run_server
```

From a source checkout, `python cdfd.py ...` is equivalent to `cdfd ...`.

## Install Modes

Core CLI/runtime only:

```bash
python -m pip install -e .
```

Optional Streamlit Studio:

```bash
python -m pip install -e ".[web]"
```

Development, experiments, packaging, and tests:

```bash
python -m pip install -e ".[dev,web,experiments]"
```

The split requirements files mirror these modes:

- `requirements.txt`: core CLI/runtime dependencies.
- `requirements-web.txt`: Streamlit Studio dependencies.
- `requirements-experiments.txt`: public experiment dependencies.
- `requirements-dev.txt`: release and test dependencies.

## CLI Examples

Check runtime state:

```bash
cdfd info
cdfd domains
cdfd doctor --json
```

Run domain demos:

```bash
cdfd demo physics --steps 1 --nx 4 --ny 4
cdfd demo origins_of_life --source-scenario mixed_source_surface_trap
```

Validate and run a CDFL model:

```bash
cdfd validate examples/heat_flow.cdfl
cdfd run examples/heat_flow.cdfl --nx 4 --ny 4 --out outputs/heat_flow_run.json
cdfd export outputs/heat_flow_run.json --out outputs/heat_flow_export.json
```

Run tests:

```bash
python -m pytest -q tests/test_cli_runtime.py tests/test_new_engine_upgrades.py tests/test_release_surfaces.py
```

Part II diagnostics (CLI):

```bash
cdfd diagnostics
# writes experiments/outputs/part_ii_runtime_diagnostics.json by default
```

These diagnostics mirror the Part II follow-up additions: Paper 7 aromatic
source-mix scenarios, the Life Number supply guardrail, and Paper 11
photochemical endpoint status where chlorophyll and eumelanin are mature
examples rather than origin requirements.

Optional visual layer (same engine, not a separate physics stack):

```bash
python -m webapp.run_server
```

See `webapp/README.md` for panel descriptions.

## Documentation and Release Surfaces

- `pyproject.toml`: installable Python package metadata and `cdfd` console command.
- `.github/workflows/ci.yml`: CI gates for tests, doctor, gallery, compare,
  reports, packaging, generated matrix checks, and PDF presence.
- `docs/API.md`: CLI and Python backend surface.
- `docs/domain_maturity_matrix.json`: machine-readable classification for all
  196 registered domain adapters.
- `docs/DOMAIN_MATURITY.md`: generated summary of core, paper-backed,
  experimental, demo-only, medical-risk, and engineering-risk adapters.
- `docs/RELEASE_PROCESS.md` and `RELEASE_CHECKLIST.md`: local release gates and
  bundle process.
- `codemeta.json` and `ro-crate-metadata.json`: machine-readable research
  software and research-object metadata.

## What Is Public Here

- `cdfd.py`: public CLI entrypoint.
- `runtime/`: command backend, result envelopes, finite audits, export helpers.
- `dsl/`: CDFL lexer, parser, AST, scheduler, graph, and executor.
- `engine/`: numerical state, update kernel, and domain engines.
- `domains/`: domain adapters that map fields into CDFD runtime variables.
- `ontology/`: semantic process layer used by CDFL execution.
- `discovery/`: public discovery and hypothesis-triage helpers.
- `experiments/`: curated public scripts, selected outputs, and release-facing reports.
- `papers/`: 12 runtime papers and rebuilt PDFs.
- `tests/`: smoke and regression tests for the public runtime surface.
- `webapp/`: Streamlit visualization over the public engine (CDFD Runtime Studio).
- `CITATION.cff`: GitHub citation metadata.
- `.zenodo.json`: Zenodo deposit metadata and keywords.
- `codemeta.json` and `ro-crate-metadata.json`: research software metadata.
- `pyproject.toml`: Python package metadata and installed console command.
- `KEYWORDS.md` and `GITHUB_TOPICS.md`: public indexing terms.
- `MUJJABI_RUNTIME_LAWS_AND_TESTS.md`: restored cross-series Mujjabi laws,
  runtime principles, and falsification tests.

Private web apps, raw exploratory logs, local progress notes, private handoff
files, unfinished UI code, and internal deployment material are not part of the
public repo.

## Runtime Boundary

The CDFD Runtime is a deterministic research engine and CLI. It does not store
LLM provider keys, host user accounts, or decide application workflow policy.
Provider calls are optional research-assistant actions above saved runtime
outputs; they do not enter the numerical engine.

Check provider-key status without making a provider call:

```bash
python cdfd.py llm providers --json
OPENAI_API_KEY=... python cdfd.py llm status --provider openai --model <model> --json
ANTHROPIC_API_KEY=... python cdfd.py llm status --provider anthropic --model <model> --json
GEMINI_API_KEY=... python cdfd.py llm status --provider gemini --model <model> --json
```

Call a provider only when you explicitly ask for research interpretation of a
saved result. Use `--dry-run` first when you want to inspect the bounded prompt
audit without sending anything to a provider:

```bash
python cdfd.py llm explain runs/<run>/result.json \
  --provider openai \
  --model <model> \
  --question "Explain what this deterministic run supports and what remains unproven." \
  --dry-run

OPENAI_API_KEY=... python cdfd.py llm explain runs/<run>/result.json \
  --provider openai \
  --model <model> \
  --question "Explain what this deterministic run supports and what remains unproven."
```

Direct provider shapes are explicit, not universal. Current direct support is:
`openai`, `anthropic`, `gemini`, `mistral`, `groq`, `openrouter`, `ollama`, and
generic `openai-compatible` `/v1/chat/completions` servers. Other LLMs work only
if they expose one of those shapes or receive a small new adapter. `ollama`
defaults to `http://localhost:11434/v1` and normally does not require a key.
`openrouter` is the hosted OpenAI-compatible example with base URL
`https://openrouter.ai/api/v1`.

The compatibility command `python cdfd.py auth` now aliases provider-key status.
It no longer checks a local `CDFD_RUNTIME_API_KEYS` allowlist. Prefer provider
keys from environment variables or `--api-key-file`; raw keys are never printed
in CLI JSON, human output, Markdown/HTML reports, failed provider responses, or
run bundles. When `cdfd llm explain ... --save-run` is used, the run folder also
gets `llm_interpretation.json` and `llm_interpretation.md`, both marked as
interpretive LLM output rather than deterministic CDFD evidence. LLM provenance
records provider, model, base URL host, temperature, max tokens, context length,
and prompt template version, never the key.

## Claim Boundary

CDFD Runtime output is a modeling and hypothesis-triage surface. It is not
medical advice, engineering certification, empirical proof, or a deployed
clinical, financial, or safety system. Candidate laws and tests remain open to
falsification.

## Runtime Papers

The `papers/` folder contains a 12-paper runtime spine with LaTeX sources and
compiled PDFs. The papers describe the state variables, CDFL grammar, CLI
execution path, ontology layer, discovery-triage surface, domain adapters, and
claim boundaries used by the public runtime.

The runtime-paper bibliography cites the Part II archive DOI separately from
the Part I framework DOI:

- Part I framework DOI: https://doi.org/10.5281/zenodo.20250821
- Part II origins-of-life DOI: https://doi.org/10.5281/zenodo.20264779

The release-facing experiment filter is
`experiments/reports/FINAL_RELEASE_EXPERIMENT_SELECTION.md`. It marks selected
outputs as candidate simulation results and falsification targets, not empirical
proof.

## Review Status

This repository is research software with accompanying preprint-style papers.
The tests and public experiments exercise the runtime surface, but they do not
establish external validation for clinical, engineering, financial, or safety
decisions.

## Licensing

This project is dual-licensed:

1. **Academic/Personal Use**: Licensed under [GNU AGPLv3](LICENSE). This version
   is free for students, researchers, and hobbyists.
2. **Commercial Use**: A separate commercial license is required for any company
   or individual wishing to use this software in a proprietary or commercial
   environment without the restrictions of the AGPLv3.

**Contact msbico@gmail.com to purchase a commercial license.**

## Citation

Mujjabi, S. B. (2026). CDFD Runtime: Constraint-Driven Flux Dynamics and CDFL Execution Engine. Zenodo.<br>
https://doi.org/10.5281/zenodo.20343160

Use `CITATION.cff` for software citation metadata. The runtime is separate from
the Part I and Part II scholarly archives, but it references those releases as
the public CDFD/CDFL context:

- CDFD Part I: Fundamental Physics, https://doi.org/10.5281/zenodo.20250821
- CDFD Part II: Origins of Life and Tri-Regime Bioenergetics,
  https://doi.org/10.5281/zenodo.20264779
