# Changelog

## 1.1.0 - 2026-06-06

- Added `pyproject.toml` packaging metadata and the installed `cdfd` console command.
- Split dependencies into core, web, experiments, dev, and docs groups.
- Expanded release gates for tests, doctor, gallery, compare, reporting, packaging, and PDF presence.
- Added CodeMeta, RO-Crate, contribution, security, support, and release-process surfaces.
- Added a generated 196-domain maturity matrix with risk classifications.
- Added the `cdfd cdfl` workbench commands for validate, run, lint, format, AST, and sample generation.
- Added optional Runtime Studio CDFL Workbench controls over the same deterministic engine.
- Added the CDFL Language Support VS Code extension source under `tools/cdfl-vscode`.
- Refreshed the 12-paper runtime spine and rebuilt the public PDFs.
- Kept provider/LLM interpretation outside the deterministic engine and audit path.

## 1.0.2 - 2026-06-05

- Updated release metadata and public runtime papers for Zenodo archival.
- Published rebuilt runtime PDFs and release-facing DOI metadata.

## 1.0.1 - 2026-05-22

- Published the CDFD Runtime public release with DOI `10.5281/zenodo.20343160`.
- Included CLI runtime, CDFL parser/executor, domain adapters, runtime papers,
  compiled PDFs, finite-audit envelopes, and focused tests.
