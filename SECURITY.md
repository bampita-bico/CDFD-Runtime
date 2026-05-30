# Security Policy

## Supported Versions

Security fixes target the current public release line, `1.0.x`, and the active
main branch.

## Reporting

Send security reports to `msbico@gmail.com`. Include:

- A short description of the issue.
- The affected command, module, or file.
- Steps to reproduce.
- Whether secrets, generated artifacts, or external systems are involved.

## Runtime Boundary

CDFD Runtime does not store provider keys, run hosted user accounts, or manage
application authorization policy. `cdfd llm status` checks whether a provider
key is available without making a provider call or printing the key. `cdfd llm
providers` lists supported provider shapes without calling them. `cdfd llm
explain` can call a supported provider only when the user explicitly supplies
runtime key material when required and a model for that command. `--dry-run`
builds the prompt audit without sending a provider request.

The compatibility command `cdfd auth` is an alias for provider-key status. It
does not enforce a local runtime allowlist and does not use
`CDFD_RUNTIME_API_KEYS`.

Provider keys are redacted from CLI envelopes, prompt previews, provider error
messages, Markdown/HTML reports, and saved run bundles. Do not put raw secrets
in issues, pull requests, logs, run bundles, or screenshots.
