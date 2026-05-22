# CDFD Runtime

CDFD Runtime is the public command-line runtime for Constraint-Driven Flux
Dynamics (CDFD) and the CDFL executable model grammar.

The runtime runs locally on the user's machine after clone or download. It does
not run on the author's laptop, and it does not require access to private
servers, private datasets, API keys, or hosted infrastructure.

## Author

Steve Bico Mujjabi, MD<br>
ORCID: https://orcid.org/0009-0001-0556-5516

## Release Naming

CDFD Runtime: Constraint-Driven Flux Dynamics and CDFL Execution Engine

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

## Quickstart

```bash
git clone https://github.com/bampita-bico/CDFD-Runtime.git
cd CDFD-Runtime
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Check the CLI:

```bash
python cdfd.py --help
python cdfd.py info
python cdfd.py domains
```

Run a domain demo:

```bash
python cdfd.py demo physics --steps 1 --nx 4 --ny 4
```

Validate and run a CDFL model:

```bash
python cdfd.py validate examples/heat_flow.cdfl
python cdfd.py run examples/heat_flow.cdfl --nx 4 --ny 4
```

Save a run result:

```bash
mkdir -p outputs
python cdfd.py run examples/heat_flow.cdfl --nx 4 --ny 4 --out outputs/heat_flow_run.json
python cdfd.py export outputs/heat_flow_run.json --out outputs/heat_flow_export.json
```

Run tests:

```bash
python -m pytest -q tests/test_cli_runtime.py tests/test_new_engine_upgrades.py
```

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
- `CITATION.cff`: GitHub citation metadata.
- `.zenodo.json`: Zenodo deposit metadata and keywords.
- `KEYWORDS.md` and `GITHUB_TOPICS.md`: public indexing terms.
- `MUJJABI_RUNTIME_LAWS_AND_TESTS.md`: named runtime laws, principles, and
  falsification tests.

Private web apps, raw exploratory logs, local progress notes, private handoff
files, unfinished UI code, and internal deployment material are not part of the
public repo.

## Runtime Boundary

The CDFD Runtime is a deterministic research engine and CLI. It does not store
LLM provider keys, call LLM providers, host user accounts, or decide application
workflow policy. Those responsibilities belong in applications built above the
runtime.

The `auth` command checks application API keys against
`CDFD_RUNTIME_API_KEYS` without writing raw secrets to output:

```bash
CDFD_RUNTIME_API_KEYS=runtime-secret python cdfd.py auth --api-key runtime-secret --json
```

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

Use `CITATION.cff` for software citation metadata. The runtime is separate from
the Part I and Part II scholarly archives, but it references those releases as
the public CDFD/CDFL context:

- CDFD Part I: Fundamental Physics, https://doi.org/10.5281/zenodo.20250821
- CDFD Part II: Origins of Life and Tri-Regime Bioenergetics,
  https://doi.org/10.5281/zenodo.20264779
