# CDFD Runtime Studio

Streamlit Studio over the same engine, runtime envelopes, finite audit,
provenance, and report helpers used by `cdfd.py`. The web layer does not
duplicate physics (Runtime Paper 06).

## Launch

```bash
cd CDFD-Runtime
python -m venv .venv && source .venv/bin/activate
python -m pip install -e ".[web]"
python -m webapp.run_server
```

Or directly:

```bash
streamlit run webapp/dashboard.py
```

## Panels

| Tab | Content |
|-----|---------|
| **Runtime Cockpit** | Runtime status, domain count, selected run, finite audit, doctor checks, provenance |
| **Physics Lab** | Kernel runs with interactive Ψ_s trajectory, phase-space trace, replay snapshots, and PNG/SVG/HTML exports |
| **Origins Lab** | Source-mix comparison, Life Number map, photochemical guardrails, Part II diagnostic envelopes |
| **Domain Atlas** | Searchable domain map, field filters, adapter run controls, side-by-side domain demos |
| **Evidence & Falsification** | Selected-result report exports, causal graph/timeline, exact artifact references, claim boundaries |
| **VOS Preview** | Provider-key status, run queue sketch, saved experiment bundles above the deterministic runtime |

## Boundaries

- Modeling and hypothesis-triage surface only — not medical advice or empirical proof.
- VOS/app/LLM orchestration stays above the runtime; optional provider calls never enter the engine.
- Neo4j ontology helpers live in `neo4j_ontology.py` (not `ontology.py`, which would shadow the `ontology/` package when Streamlit runs).
