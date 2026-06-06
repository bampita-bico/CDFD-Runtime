# CDFL Language Support

CDFL Language Support by Vura Labs adds editor support for CDFL, the Constraint-Driven Flux Language used by CDFD Runtime.

Repository: https://github.com/bampita-bico/CDFD-Runtime

## Features

- `.cdfl` file association with the `CDFL` language mode.
- Syntax highlighting for CDFL commands, runtime types, identifiers, Greek identifiers, numbers, strings, lists, braces, colons, commas, and simple operators.
- Editor configuration for brackets, indentation, folding, and line comments.
- Snippets for `SET`, `SYSTEM`, `RULE`, `RUN`, `OBSERVE`, `SCENARIO`, `SWEEP`, and `DISCOVER`.
- Local diagnostics for common CDFL mistakes: unknown statements, unmatched blocks/lists, malformed `SET`, `RUN`, `SYSTEM`, `RULE`, `IF`, and block key/value lines.
- Hover help, completions, document symbols, and formatting for `.cdfl` files.
- Command palette actions for runtime validation, linting, execution, AST inspection, runtime formatting, runtime doctor, the language reference, and a new heat-flow sample.

## CDFL Example

This sample mirrors the canonical `examples/heat_flow.cdfl` model in CDFD Runtime:

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

## Runtime Commands

The extension can call CDFD Runtime from VS Code:

- `CDFL: Validate Current File`
- `CDFL: Lint Current File`
- `CDFL: Run Current File`
- `CDFL: Show AST`
- `CDFL: Format with Runtime`
- `CDFL: Runtime Doctor`
- `CDFL: Create Heat Flow Sample`
- `CDFL: Open Language Reference`

When installed from this source checkout, the extension auto-detects the adjacent `cdfd.py` file and calls `cdfd cdfl ...`. In a standalone install, configure `cdfl.runtime.command` or install the `cdfd` command.

Useful settings:

- `cdfl.runtime.command`: optional runtime command prefix, such as `cdfd` or `python /path/to/cdfd.py`.
- `cdfl.runtime.cwd`: optional CDFD Runtime working directory.
- `cdfl.run.nx` and `cdfl.run.ny`: grid dimensions for `CDFL: Run Current File`.
- `cdfl.diagnostics.enabled`: local editor diagnostics toggle.

## Version Scope

Version `0.1.0` now includes editor intelligence and runtime command wiring. Local diagnostics are fast editor checks; CDFD Runtime remains the source of execution truth. Use runtime validation for semantic confirmation:

```bash
cdfd cdfl validate examples/heat_flow.cdfl
cdfd cdfl lint examples/heat_flow.cdfl
cdfd cdfl ast examples/heat_flow.cdfl --json
```

## Development

Open the extension in a VS Code Extension Development Host:

```bash
code --extensionDevelopmentPath=/path/to/CDFD-Runtime/tools/cdfl-vscode
```

Package the extension from this directory:

```bash
vsce package
```

To write the package outside the repo during release preparation:

```bash
npx @vscode/vsce package -o /tmp/cdfl-language-support-0.1.0.vsix
```

Publishing uses the Microsoft marketplace publisher `VuraLabs`:

```bash
vsce publish
```
