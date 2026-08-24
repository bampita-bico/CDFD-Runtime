---
title: "CDFD Runtime: a local executable grammar and audit trail for declared toy models"
tags:
  - Python
  - domain-specific language
  - reproducible research
  - scientific computing
authors:
  - name: Steve Bico Mujjabi
    orcid: 0009-0001-0556-5516
    affiliation: 1
affiliations:
  - name: Vura Labs, Kampala, Uganda
    index: 1
date: 25 August 2026
bibliography: paper.bib
---

# Summary

CDFD Runtime is a local, command-line research-software package for specifying
and executing declared toy models in the Constraint-Driven Flux Language
(CDFL). A CDFL source file is parsed into an abstract syntax tree, executed by a
deterministic numerical engine, and returned as a structured JSON result
envelope. The command-line interface also provides validation, linting,
formatting, syntax-tree inspection, exports, finite-value audits, reports, and
timestamped run bundles.

The package is intended for researchers who need a small, inspectable workflow
for prototype field or state models without treating a notebook or an ad hoc
script as the complete record. A run bundle stores the result JSON, finite
audit, command provenance, a machine-readable manifest, and Markdown and HTML
reports. CDFL tooling exposes syntax and structural diagnostics before a model
is run. A VS Code language extension provides editor support, but the
command-line runtime is the execution reference.

CDFD Runtime does not establish that a CDFL variable maps to a measurable
quantity, that a numerical threshold is calibrated, or that the underlying
CDFD hypotheses describe nature. Its outputs are deterministic toy-model
diagnostics and software-audit artifacts. The package is not a clinical,
engineering, financial, safety, or decision-support system.

# Statement of need

Small exploratory simulation projects commonly combine a model definition,
execution code, output serialization, and narrative interpretation in a single
script or notebook. That arrangement is flexible, but it makes it easy to lose
the exact input, command, output checks, and claim boundary associated with an
individual result. CDFD Runtime addresses this narrow workflow problem for its
own field/state-model grammar: a text model can be checked, executed locally,
and saved with a finite audit and a durable run manifest from one command-line
surface.

The package is useful when a research group needs all of the following in one
lightweight local tool: a human-readable input grammar; deterministic execution
on a small grid; machine-readable parse and lint diagnostics; a recursive check
for non-finite JSON-visible output; and portable result bundles for review.
The design intentionally separates these software guarantees from scientific
validation. A finite output shows only that the recorded computation completed
without non-finite values; it does not show convergence, calibration, or
empirical adequacy.

# Software design

CDFL tooling follows a lexer--parser--AST--executor path. The `cdfd cdfl`
commands validate and lint source, render a canonical formatter output, expose
the AST, and execute supported model statements. The runtime wraps commands in
a common result envelope containing command provenance, warnings and errors, a
finite audit, and an explicit claim boundary. `create_run_bundle` then writes
the envelope, reports, manifest, and plots directory under a timestamped
directory. This makes a saved bundle a reviewable computational record rather
than an inferred reconstruction from console output.

The active release ships one canonical example model
(`examples/heat_flow.cdfl`), one reproducible smoke experiment
(`experiments/run_cdfl_smoke.py`), and focused tests for the CLI, parser,
release surfaces, and editor extension. Core installation requires only NumPy,
SciPy, Numba, and Requests. Optional experiment dependencies are used for the
public smoke script and checkpoint helpers, not for bundled domain-validation
demos.

The project is installable as a Python package with an installed `cdfd` command,
an AGPL-3.0-or-later license, versioned citation metadata, and continuous
integration. Legacy multi-paper runtime manuscripts, bundled cross-domain adapter
corpora, and visual studio layers were moved to a local archive described in
`ARCHIVE_NOTICE_2026-08-25.md`; they are not part of the active software claim.

# State of the field

CDFD Runtime is not a replacement for established biological-model exchange or
simulation ecosystems. SBML is an extensible standard for exchange and reuse of
biological models [@sbml]; SED-ML describes simulation experiments independently
of a particular simulator [@sedml]; and COPASI provides mature simulation and
analysis for biochemical networks [@copasi]. Those tools are preferable when a
study needs their model semantics, standards interoperability, solver breadth,
or established biological analysis workflows.

| Tool or approach | Primary strength | Boundary relative to CDFD Runtime |
| --- | --- | --- |
| SBML | Exchangeable representation of biological models | CDFL is not SBML-compatible and does not provide SBML's biological model semantics. |
| SED-ML | Tool-independent simulation-experiment description | CDFD Runtime does not implement SED-ML or COMBINE archives; its run manifest is a package-local provenance record. |
| COPASI | Mature biochemical-network simulation and analysis | CDFD Runtime does not reproduce COPASI's biochemical analyses or solver scope. |
| Python/NumPy/SciPy scripts | General numerical flexibility | CDFD Runtime trades generality for a fixed CLI, CDFL diagnostics, result envelope, finite audit, and bundled reports. |

The contribution is therefore not a new general-purpose solver or a new
interchange standard. It is a constrained, local workflow that makes the input
grammar, finite-output check, provenance, and claim boundary first-class output
artifacts for a family of explicitly declared toy models.

# Research impact statement

As of 2026-08-25, the repository records developer use in the CDFD correction
work but no independently documented external research user, publication, or
integration. This paper is therefore a prepared draft, not a JOSS submission.
The software must not be submitted until a versioned archival release, a public
reviewable commit, and concrete evidence of use beyond this author's own
manuscript series are available. A credible evidence record could be an
external research workflow that preserves its own declared model, run bundle,
and claim boundary, or a reproducible comparison showing that the CDFL and
audit workflow prevents a documented failure mode that established tools do not
address for the stated use case.

# Research applications and limitations

The runtime supports CDFL toy models such as the bundled heat-flow example and
the public smoke experiment. It can support preregistered empirical workflows by
saving the code-visible input and output record, but it does not turn a model
extension into evidence. Negative results from the wider CDFD scholarly
programme remain outside this package: they are cited only as boundary context,
not as validation of the slim runtime release.

Researchers using CDFD Runtime should provide domain-native observables,
units, comparison baselines, held-out evaluation, uncertainty analysis, and a
negative-result rule outside the runtime. The software does not supply those
elements automatically. It should not be used to label a state as disease,
intervention efficacy, material failure, physical mechanism, or life detection.

# Availability

The source code, documentation, tests, release metadata, canonical example, and
smoke experiment are available at https://github.com/bampita-bico/CDFD-Runtime
under AGPL-3.0-or-later. The current corrected local release is version 1.1.1.
A new versioned archival deposit is required before citing that version's DOI;
the repository records that distinction explicitly in `ARCHIVE_NOTICE_2026-08-25.md`.

# AI usage disclosure

Generative-AI assistance was used for documentation restructuring,
claim-boundary editing, refactoring support, and test scaffolding during the
2026 correction work. Before submission, the author must replace this
provisional statement with the tools/models and versions used, the locations of
their use in code, documentation, and paper text, and confirmation that the
author reviewed, edited, and validated all assisted output and made the core
design decisions. The author remains responsible for the code, paper, and
claims.
