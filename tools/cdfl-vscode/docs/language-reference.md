# CDFL Language Reference

CDFL is the Constraint-Driven Flux Language used by CDFD Runtime. The VS Code extension gives editor help; the runtime remains the source of execution truth.

## Canonical Model

```cdfl
SET domain: physics

SYSTEM HeatChannel {
  flux: 1.2
  constraint: 0.9
  state: psi
}

RULE HeatOverload {
  IF psi > 1.1
  ACTION reduce_flux
}

RUN Engine {
  duration: 0.05
  dt: 0.01
}

OBSERVE {
  metrics: [psi]
}
```

## Core Statements

- `SET key: value` sets runtime context. `SET domain: physics` is the common first line.
- `SYSTEM Name { ... }` defines a named system with `flux`, `constraint`, and `state`.
- `RULE Name { ... }` defines threshold/action behavior with `IF` and `ACTION`.
- `RUN Engine { ... }` executes the runtime engine parameters.
- `OBSERVE { metrics: [...] }` declares observed outputs.
- `SCENARIO Name { ... }` groups executable statements.
- `SWEEP parameter [values...]` declares parameter sweeps.
- `DISCOVER { ... }`, `ANALYZE { ... }`, `BIFURCATE { ... }`, `EMERGE { ... }`, `ATTRACTOR { ... }`, and `INFOFLOW { ... }` describe advanced analysis surfaces.

## Editor Commands

- `CDFL: Validate Current File` runs CDFD Runtime validation on the active saved file.
- `CDFL: Lint Current File` runs CDFD Runtime CDFL diagnostics on the active saved file.
- `CDFL: Run Current File` runs the active saved file through CDFD Runtime.
- `CDFL: Show AST` emits the runtime parser's JSON-safe AST summary.
- `CDFL: Format with Runtime` applies the shared runtime CDFL formatter.
- `CDFL: Runtime Doctor` runs the runtime doctor command.
- `CDFL: Create Heat Flow Sample` opens the canonical example in a new editor.
- `CDFL: Open Language Reference` opens this document.

## Runtime Settings

- `cdfl.runtime.command`: optional command prefix. Leave empty for auto-detection.
- `cdfl.runtime.cwd`: optional CDFD Runtime working directory. Leave empty for auto-detection.
- `cdfl.run.nx` and `cdfl.run.ny`: grid dimensions for `CDFL: Run Current File`.
- `cdfl.diagnostics.enabled`: enables local editor diagnostics.

When installed from the source checkout, the extension auto-detects the adjacent `cdfd.py` and runs `cdfd cdfl ...` with Python. In a standalone install, configure `cdfl.runtime.command` or install the `cdfd` command.
