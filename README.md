# CDFD Runtime

CDFD Runtime is the public command-line runtime for Constraint-Driven Flux
Dynamics (CDFD) and the CDFL executable model grammar.

The runtime runs locally on the user's machine after clone or download. It does
not run on the author's laptop, and it does not require access to private
servers, private datasets, API keys, or hosted infrastructure.

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

## Licensing

This project is dual-licensed:

1. **Academic/Personal Use**: Licensed under [GNU AGPLv3](LICENSE). This version
   is free for students, researchers, and hobbyists.
2. **Commercial Use**: A separate commercial license is required for any company
   or individual wishing to use this software in a proprietary or commercial
   environment without the restrictions of the AGPLv3.

**Contact msbico@gmail.com to purchase a commercial license.**
