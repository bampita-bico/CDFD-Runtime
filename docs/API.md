# API Surface

CDFD Runtime exposes a console command and a small Python command backend.

## Console

After installation:

```bash
cdfd --help
cdfd doctor --json
cdfd gallery --save-run --json --out outputs/gallery.json
cdfd compare origins_of_life --scenarios mixed_source_surface_trap meteoritic_seed_retained --json
cdfd report outputs/gallery.json --format markdown --out outputs/gallery_report.md
cdfd explain outputs/gallery.json --format markdown --out outputs/gallery_explain.md
cdfd cdfl lint examples/heat_flow.cdfl --json
cdfd cdfl format examples/heat_flow.cdfl --json
cdfd cdfl ast examples/heat_flow.cdfl --json
cdfd cdfl sample --out /tmp/heat_flow.cdfl
cdfd llm providers --json
cdfd llm status --provider openai --model <model> --json
cdfd llm explain outputs/gallery.json --provider openai --model <model> --dry-run
cdfd llm explain outputs/gallery.json --provider openai --model <model> --question "research interpretation"
```

From a source checkout, `python cdfd.py ...` remains equivalent.

`cdfd llm` is optional. It sits above saved deterministic runtime outputs and
uses provider keys supplied at command time through provider-specific
environment variables, `CDFD_LLM_API_KEY`, `--key-env`, or `--api-key-file`.
Provider keys are not printed. `cdfd llm providers` lists direct support for
`openai`, `openai-compatible`, `anthropic`, `gemini`, `mistral`, `groq`,
`openrouter`, and `ollama`. `cdfd auth` remains as a compatibility alias for
`cdfd llm status`; it no longer checks a local runtime allowlist.
`cdfd llm explain ... --save-run` stores separate `llm_interpretation.json` and
`llm_interpretation.md` artifacts with provider/model/base-host provenance,
temperature, max-token, context-length, and prompt-template metadata. These
artifacts are interpretive only; the deterministic runtime result stays in
`result.json`.

## Python Backend

The CLI delegates to `runtime.runner`:

- `runtime_info()`
- `doctor()`
- `gallery(nx=4, ny=4, steps=1)`
- `compare_domain(domain, scenarios, nx=4, ny=4, steps=1)`
- `run_domain(domain, payload=None, nx=16, ny=16, steps=24, dt=None)`
- `validate_cdfl(path)`
- `run_cdfl(path, nx=16, ny=16)`
- `lint_cdfl(path)`
- `format_cdfl_file(path, output_path=None, in_place=False, indent_size=2)`
- `cdfl_ast(path)`
- `cdfl_sample(output_path=None, force=False)`
- `report_result(input_path, output_path=None, fmt="markdown")`
- `explain_result(input_path, output_path=None, fmt="markdown")`
- `llm_provider_inventory()`
- `llm_provider_status(provider=None, model=None, base_url=None, api_key_file=None)`
- `llm_explain_result(input_path, question=None, provider=None, model=None, base_url=None, api_key_file=None)`

Each public backend function returns a strict result envelope:

```json
{
  "kind": "runtime_gallery",
  "status": "ok",
  "payload": {},
  "finite_audit": {
    "all_finite": true,
    "non_finite_paths": []
  },
  "provenance": {}
}
```

## Claim Boundary

The API returns modeling diagnostics and, only when `llm_explain_result` is
explicitly called, provider-generated research interpretation. It does not
return clinical advice, engineering certification, financial advice, legal
advice, or deployed safety decisions.
