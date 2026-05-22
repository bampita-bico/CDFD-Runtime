# Public and Private Repo Split

## Public Repo

Repository: `CDFD-Runtime`

The public repo contains the runnable CLI, CDFL grammar, runtime engine, domain
adapter layer, ontology execution layer, curated public experiments, papers,
tests, license files, keywords, GitHub topics, and public claim-boundary docs.

The public repo is suitable for GitHub release because users can clone it,
install dependencies, run the CLI, inspect the papers, and run tests on their
own machines.

## Private Repo

Repository: `CDFD-Runtime-Private`

The private repo preserves unfinished web app work, raw discovery logs, internal
progress notes, local release handoffs, renamed internal CRT notes, and any
experimental material that is not part of the first public runtime surface.

## Excluded From Public

- Web app and application UI code until it has a separate release pass.
- Raw mega-discovery logs such as `FRONTIER_DISCOVERIES.md`.
- Local progress files such as paper-upgrade and CLI handoff notes.
- Private deployment state, secrets, API keys, databases, caches, and generated
  local outputs.
- Internal notes whose title or framing is not release-ready.
