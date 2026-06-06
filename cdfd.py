#!/usr/bin/env python3
"""CDFD Runtime CLI — primary public surface (CLI-first platform)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from runtime.artifacts import create_run_bundle
from runtime.diagnostics import clean_json, write_json
from runtime.reporting import result_to_html, result_to_markdown
from runtime.runner import (
    app_auth_status,
    cdfl_ast,
    cdfl_sample,
    compare_domain,
    doctor,
    explain_result,
    export_result,
    format_cdfl_file,
    gallery,
    lint_cdfl,
    list_domains,
    load_json_object,
    llm_explain_result,
    llm_provider_inventory,
    llm_provider_status,
    part_ii_diagnostics,
    report_result,
    run_cdfl,
    run_domain,
    runtime_info,
    validate_cdfl,
)

CLI_FORMATS = ("table", "markdown", "html", "json")

CLI_EPILOG = """
CLI-first workflow:
  python cdfd.py info
  python cdfd.py doctor
  python cdfd.py gallery --save-run
  python cdfd.py compare origins_of_life --scenarios mixed_source_surface_trap meteoritic_seed_retained
  python cdfd.py report runs/<run>/result.json --format html
  python cdfd.py explain runs/<run>/result.json --format markdown
  python cdfd.py llm providers
  python cdfd.py llm status
  python cdfd.py llm explain runs/<run>/result.json --question "research interpretation" --dry-run
  python cdfd.py domains
  python cdfd.py demo physics --steps 1 --nx 4 --ny 4
  python cdfd.py demo origins_of_life --source-scenario mixed_source_surface_trap
  python cdfd.py diagnostics
  python cdfd.py cdfl lint examples/heat_flow.cdfl
  python cdfd.py cdfl format examples/heat_flow.cdfl
  python cdfd.py cdfl ast examples/heat_flow.cdfl --json
  python cdfd.py cdfl sample --out /tmp/heat_flow.cdfl
  python cdfd.py validate examples/heat_flow.cdfl
  python cdfd.py run examples/heat_flow.cdfl --nx 4 --ny 4 --out outputs/run.json

Optional visual layer (same engine, not a separate physics stack):
  python -m webapp.run_server
"""


def _print_json(result: dict) -> None:
    print(json.dumps(clean_json(result), indent=2, sort_keys=True, allow_nan=False))


def _selected_format(args: argparse.Namespace, default: str = "table") -> str:
    return "json" if getattr(args, "json", False) else getattr(args, "format", default)


def _emit(
    result: dict,
    *,
    json_mode: bool = False,
    out: str | None = None,
    fmt: str = "table",
    save_run: bool = False,
    runs_root: str = "runs",
    run_label: str | None = None,
) -> int:
    if save_run:
        manifest = create_run_bundle(result, root=runs_root, label=run_label)
        result = dict(result)
        payload = dict(result.get("payload", {}))
        payload["run_bundle"] = manifest
        result["payload"] = payload

    if out:
        write_json(out, result)

    output_format = "json" if json_mode else fmt
    if output_format == "json":
        _print_json(result)
    elif output_format == "markdown":
        print(result_to_markdown(result))
    elif output_format == "html":
        print(result_to_html(result))
    else:
        _print_human(result, out=out)

    return 0 if result.get("status") == "ok" else 1


def _print_human(result: dict, *, out: str | None = None) -> None:
    kind = result.get("kind")
    status = result.get("status")
    payload = result.get("payload", {})

    if kind == "runtime_info":
        print("CDFD Runtime (CLI-first)")
        print(f"status: {status}")
        print(f"primary_surface: {payload.get('primary_surface')}")
        print(f"platform_order: {' -> '.join(payload.get('platform_order', []))}")
        print(f"language: {payload.get('language')}")
        print(f"domains: {payload.get('domain_count')}")
        print("commands:", ", ".join(payload.get("commands", [])))
        print("cli: python cdfd.py")
        optional = payload.get("optional_surfaces") or []
        if optional:
            print(f"optional: {', '.join(optional)} (visual layer only)")
    elif kind == "domain_list":
        print(f"{payload.get('count', 0)} domains")
        for name in payload.get("domains", []):
            print(name)
    elif kind == "domain_demo":
        print(f"status: {status}")
        print(f"domain: {payload.get('domain')}")
        final = payload.get("final", {})
        print(f"regime: {payload.get('regime')}")
        if "mean_psi" in final:
            print(f"final mean_psi: {final['mean_psi']}")
        if payload.get("interpretation"):
            print(f"interpretation: {payload['interpretation']}")
        diag = payload.get("domain_diagnostics") or {}
        if diag.get("aromatic_source_mix"):
            mix = diag["aromatic_source_mix"]
            print(
                f"aromatic_source_mix: {mix.get('scenario')} "
                f"score={mix.get('functional_score')}"
            )
        if diag.get("life_number_guardrail"):
            print(f"guardrail: {diag['life_number_guardrail']}")
        trace = payload.get("trace") or []
        if trace:
            print(f"trace_steps: {len(trace)} (last mean_psi={trace[-1].get('mean_psi')})")
    elif kind == "part_ii_diagnostics":
        print("Part II runtime diagnostics")
        print(f"status: {status}")
        best = payload.get("best_aromatic_source_mix") or {}
        print(f"best_source_mix: {best.get('scenario')} score={best.get('functional_score')}")
        print(f"guardrail: {payload.get('life_number_guardrail')}")
        status_map = payload.get("photochemical_material_status") or {}
        for key, text in status_map.items():
            print(f"{key}: {text}")
        if payload.get("selected_scenario"):
            sel = payload["selected_scenario"]
            print(f"selected: {sel.get('scenario')} score={sel.get('functional_score')}")
        demo = payload.get("origins_of_life_demo") or {}
        if demo.get("interpretation"):
            print(f"ool_demo: {demo['interpretation']}")
    elif kind == "cdfl_validation":
        print(f"status: {status}")
        print(f"file: {payload.get('file')}")
        print(f"valid: {payload.get('valid')}")
        if payload.get("node_count") is not None:
            print(f"nodes: {payload.get('node_count')} ({', '.join(payload.get('nodes', []))})")
        _print_cdfl_diagnostics(payload)
    elif kind == "cdfl_lint":
        print(f"status: {status}")
        print(f"file: {payload.get('file')}")
        print(f"valid: {payload.get('valid')}")
        print(f"tokens: {payload.get('token_count')} nodes: {payload.get('node_count')}")
        _print_cdfl_diagnostics(payload)
    elif kind == "cdfl_format":
        print(f"status: {status}")
        print(f"file: {payload.get('file')}")
        print(f"changed: {payload.get('changed')}")
        if payload.get("output"):
            print(f"output: {payload.get('output')}")
        elif payload.get("formatted"):
            print(payload["formatted"])
    elif kind == "cdfl_ast":
        print(f"status: {status}")
        print(f"file: {payload.get('file')}")
        print(f"valid: {payload.get('valid')}")
        print(f"tokens: {payload.get('token_count')} nodes: {payload.get('node_count')}")
        for index, node in enumerate(payload.get("nodes", []), start=1):
            print(f"{index}. {node.get('type')}: {json.dumps(clean_json(node.get('attributes', {})), sort_keys=True)}")
        _print_cdfl_diagnostics(payload)
    elif kind == "cdfl_sample":
        print(f"status: {status}")
        if payload.get("output"):
            print(f"output: {payload.get('output')}")
            print(f"written: {payload.get('written')}")
        else:
            print(payload.get("sample", ""))
    elif kind == "cdfl_run":
        print(f"status: {status}")
        print(f"file: {payload.get('file')}")
        print(f"nodes: {payload.get('node_count')}")
        results = payload.get("results", [])
        print(f"result_blocks: {len(results)}")
        for item in results[:5]:
            if isinstance(item, dict):
                label = item.get("type") or item.get("error") or "result"
                print(f"- {label}")
    elif kind == "export":
        print(f"status: {status}")
        print(f"input: {payload.get('input')}")
        print(f"output: {payload.get('output')}")
    elif kind == "llm_provider_status":
        print(f"status: {status}")
        print(f"provider: {payload.get('provider')}")
        print(f"provider_mode: {payload.get('provider_mode')}")
        print(f"model: {payload.get('model')}")
        print(f"base_url: {payload.get('base_url')}")
        print(f"key_required: {payload.get('key_required')}")
        print(f"key_configured: {payload.get('key_configured')}")
        print(f"key_source: {payload.get('key_source')}")
        print(f"secrets_printed: {payload.get('secrets_printed')}")
        print(f"boundary: {payload.get('boundary')}")
    elif kind == "llm_provider_inventory":
        print(f"status: {status}")
        print(f"default_provider: {payload.get('default_provider')}")
        print(f"provider_count: {payload.get('provider_count')}")
        for row in payload.get("providers", []):
            key_state = "key" if row.get("key_configured") else ("no-key-ok" if not row.get("key_required") else "needs-key")
            configured = "ready" if row.get("configured_for_call") else "needs-config"
            print(
                f"- {row.get('provider')}: {row.get('call_shape')} "
                f"base={row.get('base_url')} {key_state} {configured}"
            )
        print(f"boundary: {payload.get('boundary')}")
    elif kind == "runtime_doctor":
        summary = payload.get("summary", {})
        print("CDFD doctor")
        print(f"status: {status}")
        print(f"root: {payload.get('root')}")
        print(f"domains: {payload.get('domain_count')}")
        print(
            "checks: "
            f"{summary.get('ok', 0)} ok, {summary.get('warnings', 0)} warnings, "
            f"{summary.get('errors', 0)} errors"
        )
        for check in payload.get("checks", []):
            print(f"- {check.get('status')}: {check.get('name')} ({check.get('detail')})")
    elif kind == "runtime_gallery":
        print("CDFD gallery")
        print(f"status: {status}")
        print(payload.get("description"))
        for row in payload.get("highlights", []):
            label = row.get("domain") or row.get("kind")
            bits = [f"status={row.get('status')}", f"finite={row.get('finite')}"]
            if row.get("regime"):
                bits.append(f"regime={row.get('regime')}")
            if row.get("mean_psi") is not None:
                bits.append(f"mean_psi={row.get('mean_psi')}")
            if row.get("functional_score") is not None:
                bits.append(f"source_score={row.get('functional_score')}")
            print(f"- {label}: " + ", ".join(bits))
        vos = payload.get("vos_preview") or {}
        if vos:
            print(f"vos: {vos.get('boundary')}")
    elif kind == "runtime_compare":
        print("CDFD compare")
        print(f"status: {status}")
        print(f"domain: {payload.get('domain')}")
        for idx, row in enumerate(payload.get("ranked", []), start=1):
            print(
                f"{idx}. {row.get('scenario')} "
                f"score={row.get('score')} regime={row.get('regime')} "
                f"finite={row.get('finite')}"
            )
    elif kind == "llm_research_explanation":
        print(f"status: {status}")
        print(f"input: {payload.get('input')}")
        print(f"provider: {payload.get('provider')}")
        print(f"provider_mode: {payload.get('provider_mode')}")
        print(f"model: {payload.get('model')}")
        print(f"key_source: {payload.get('key_source')}")
        print(f"dry_run: {payload.get('dry_run')}")
        print(f"provider_call_made: {payload.get('provider_call_made')}")
        if payload.get("prompt_audit"):
            audit = payload["prompt_audit"]
            print(f"prompt_template_version: {audit.get('prompt_template_version')}")
            print(f"total_prompt_chars: {audit.get('total_prompt_chars')}")
        print(f"boundary: {payload.get('boundary')}")
        if payload.get("response_text"):
            print("")
            print(payload["response_text"])
    elif kind in {"report", "explain"}:
        print(f"status: {status}")
        print(f"input: {payload.get('input')}")
        print(f"output: {payload.get('output')}")
        print(f"format: {payload.get('format')}")
    else:
        print(f"status: {status}")
        print(json.dumps(clean_json(payload), indent=2, sort_keys=True, allow_nan=False))

    bundle = payload.get("run_bundle") if isinstance(payload, dict) else None
    if bundle:
        print(f"run_dir: {bundle.get('run_dir')}")
        print(f"manifest: {bundle.get('manifest')}")

    errors = result.get("errors") or []
    warnings = result.get("warnings") or []
    finite = result.get("finite_audit", {})
    if warnings:
        print("warnings:")
        for warning in warnings:
            print(f"- {warning}")
    if errors:
        print("errors:")
        for error in errors:
            print(f"- {error}")
    if finite and not finite.get("all_finite", True):
        print("finite_audit: failed")
        for path in finite.get("non_finite_paths", []):
            print(f"- {path}")
    if out:
        print(f"saved: {out}")


def _add_format_args(parser: argparse.ArgumentParser, *, default: str = "table") -> None:
    parser.add_argument("--format", choices=CLI_FORMATS, default=default, help="Output format")
    parser.add_argument("--json", action="store_true", help="Shortcut for --format json")
    parser.add_argument("--out", help="Write full result JSON to a file")


def _add_run_bundle_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--save-run", action="store_true", help="Persist result, reports, and manifest under runs/")
    parser.add_argument("--runs-root", default="runs", help="Run bundle root directory")


def _print_cdfl_diagnostics(payload: dict) -> None:
    summary = payload.get("diagnostic_summary") or {}
    if summary:
        print(
            "diagnostics: "
            f"{summary.get('error', 0)} errors, "
            f"{summary.get('warning', 0)} warnings, "
            f"{summary.get('info', 0)} info"
        )
    for item in payload.get("diagnostics", [])[:12]:
        print(
            f"- {item.get('severity')}: "
            f"{item.get('code')} "
            f"line={item.get('line')} col={item.get('column')}: "
            f"{item.get('message')}"
        )


def _add_llm_provider_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--provider",
        default=None,
        help="LLM provider: openai, openai-compatible, anthropic, gemini, mistral, groq, openrouter, or ollama",
    )
    parser.add_argument("--model", default=None, help="Provider model; may also use CDFD_LLM_MODEL")
    parser.add_argument("--base-url", default=None, help="Provider base URL; may also use CDFD_LLM_BASE_URL")
    parser.add_argument("--api-key", help="Provider API key value; prefer env or --api-key-file")
    parser.add_argument("--api-key-file", help="File containing the provider API key")
    parser.add_argument("--key-env", default=None, help="Environment variable containing the provider API key")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cdfd",
        description=(
            "CDFD Runtime CLI — primary interface for CDFL models, domain demos, "
            "Part II diagnostics, validation, and export."
        ),
        epilog=CLI_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    info_p = sub.add_parser("info", help="Runtime capability summary (start here)")
    _add_format_args(info_p)

    domains_p = sub.add_parser("domains", help="List registered domain adapters")
    _add_format_args(domains_p)

    doctor_p = sub.add_parser("doctor", help="Check Python, dependencies, adapters, webapp, outputs, and finite-audit support")
    _add_format_args(doctor_p)
    _add_run_bundle_args(doctor_p)

    gallery_p = sub.add_parser("gallery", help="Run curated demos across core CDFD domains")
    gallery_p.add_argument("--nx", type=int, default=4)
    gallery_p.add_argument("--ny", type=int, default=4)
    gallery_p.add_argument("--steps", type=int, default=1)
    gallery_p.add_argument("--no-cdfl", action="store_true", help="Skip validating/running examples/heat_flow.cdfl")
    _add_format_args(gallery_p)
    _add_run_bundle_args(gallery_p)

    compare_p = sub.add_parser("compare", help="Run scenario sweeps and rank outputs")
    compare_p.add_argument("domain", help="Domain key, for example origins_of_life")
    compare_p.add_argument("--scenarios", nargs="+", help="Scenario labels to sweep")
    compare_p.add_argument("--nx", type=int, default=4)
    compare_p.add_argument("--ny", type=int, default=4)
    compare_p.add_argument("--steps", type=int, default=1)
    _add_format_args(compare_p)
    _add_run_bundle_args(compare_p)

    demo_p = sub.add_parser("demo", help="Run an engine-backed domain demo")
    demo_p.add_argument("domain", help="Domain key, for example physics, origins_of_life")
    demo_p.add_argument("--payload", metavar="FILE.json", help="Optional JSON object payload")
    demo_p.add_argument(
        "--source-scenario",
        help="OOL aromatic source scenario (origins_of_life); sets payload source_scenario",
    )
    demo_p.add_argument("--nx", type=int, default=16)
    demo_p.add_argument("--ny", type=int, default=16)
    demo_p.add_argument("--steps", type=int, default=24)
    demo_p.add_argument("--dt", type=float, default=None)
    _add_format_args(demo_p)
    _add_run_bundle_args(demo_p)
    demo_p.add_argument("--traceback", action="store_true", help="Show full traceback on error")

    diag_p = sub.add_parser(
        "diagnostics",
        help="Part II runtime diagnostics (source-mix, guardrails, optional OOL demo)",
    )
    diag_p.add_argument(
        "--scenario",
        help="Named aromatic source scenario (see diagnostics output for names)",
    )
    diag_p.add_argument("--no-demo", action="store_true", help="Skip origins_of_life demo block")
    diag_p.add_argument("--demo-steps", type=int, default=12)
    diag_p.add_argument("--demo-nx", type=int, default=8)
    diag_p.add_argument("--demo-ny", type=int, default=8)
    _add_format_args(diag_p)
    _add_run_bundle_args(diag_p)

    validate_p = sub.add_parser("validate", help="Parse and validate a CDFL model")
    validate_p.add_argument("model", help="Path to .cdfl model")
    _add_format_args(validate_p)
    _add_run_bundle_args(validate_p)
    validate_p.add_argument("--traceback", action="store_true", help="Show full traceback on error")

    run_p = sub.add_parser("run", help="Run a CDFL model")
    run_p.add_argument("model", help="Path to .cdfl model")
    run_p.add_argument("--nx", type=int, default=16)
    run_p.add_argument("--ny", type=int, default=16)
    _add_format_args(run_p)
    _add_run_bundle_args(run_p)
    run_p.add_argument("--traceback", action="store_true", help="Show full traceback on error")

    simulate_p = sub.add_parser("simulate", help="Alias for run")
    simulate_p.add_argument("model", help="Path to .cdfl model")
    simulate_p.add_argument("--nx", type=int, default=16)
    simulate_p.add_argument("--ny", type=int, default=16)
    _add_format_args(simulate_p)
    _add_run_bundle_args(simulate_p)
    simulate_p.add_argument("--traceback", action="store_true", help="Show full traceback on error")

    cdfl_p = sub.add_parser("cdfl", help="CDFL language workbench commands")
    cdfl_sub = cdfl_p.add_subparsers(dest="cdfl_command", required=True)

    cdfl_validate_p = cdfl_sub.add_parser("validate", help="Parse and validate a CDFL model")
    cdfl_validate_p.add_argument("model", help="Path to .cdfl model")
    _add_format_args(cdfl_validate_p)
    _add_run_bundle_args(cdfl_validate_p)
    cdfl_validate_p.add_argument("--traceback", action="store_true", help="Show full traceback on error")

    cdfl_run_p = cdfl_sub.add_parser("run", help="Run a CDFL model")
    cdfl_run_p.add_argument("model", help="Path to .cdfl model")
    cdfl_run_p.add_argument("--nx", type=int, default=16)
    cdfl_run_p.add_argument("--ny", type=int, default=16)
    _add_format_args(cdfl_run_p)
    _add_run_bundle_args(cdfl_run_p)
    cdfl_run_p.add_argument("--traceback", action="store_true", help="Show full traceback on error")

    cdfl_lint_p = cdfl_sub.add_parser("lint", help="Lint a CDFL model and report editor-grade diagnostics")
    cdfl_lint_p.add_argument("model", help="Path to .cdfl model")
    _add_format_args(cdfl_lint_p)
    _add_run_bundle_args(cdfl_lint_p)
    cdfl_lint_p.add_argument("--traceback", action="store_true", help="Show full traceback on error")

    cdfl_format_p = cdfl_sub.add_parser("format", help="Format a CDFL model")
    cdfl_format_p.add_argument("model", help="Path to .cdfl model")
    cdfl_format_p.add_argument("--out", dest="output_path", help="Write formatted CDFL to a file")
    cdfl_format_p.add_argument("--in-place", action="store_true", help="Rewrite the input file with formatted CDFL")
    cdfl_format_p.add_argument("--indent-size", type=int, default=2, help="Spaces per indentation level")
    cdfl_format_p.add_argument("--format", choices=CLI_FORMATS, default="table", help="Output format for the command envelope")
    cdfl_format_p.add_argument("--json", action="store_true", help="Shortcut for --format json")

    cdfl_ast_p = cdfl_sub.add_parser("ast", help="Emit a JSON-safe CDFL AST summary")
    cdfl_ast_p.add_argument("model", help="Path to .cdfl model")
    _add_format_args(cdfl_ast_p)
    _add_run_bundle_args(cdfl_ast_p)
    cdfl_ast_p.add_argument("--traceback", action="store_true", help="Show full traceback on error")

    cdfl_sample_p = cdfl_sub.add_parser("sample", help="Print or write the canonical heat-flow CDFL sample")
    cdfl_sample_p.add_argument("--out", dest="output_path", help="Write sample CDFL to a file")
    cdfl_sample_p.add_argument("--force", action="store_true", help="Overwrite --out if it already exists")
    cdfl_sample_p.add_argument("--format", choices=CLI_FORMATS, default="table", help="Output format for the command envelope")
    cdfl_sample_p.add_argument("--json", action="store_true", help="Shortcut for --format json")

    export_p = sub.add_parser("export", help="Export a saved CLI result")
    export_p.add_argument("input", help="Input JSON result")
    export_p.add_argument("--format", choices=["json"], default="json")
    export_p.add_argument("--out", help="Output path")
    export_p.add_argument("--json", action="store_true", help="Print JSON")

    report_p = sub.add_parser("report", help="Render a saved run JSON as Markdown, HTML, PDF, or JSON")
    report_p.add_argument("input", help="Input JSON result")
    report_p.add_argument("--format", choices=["markdown", "html", "pdf", "json"], default="markdown")
    report_p.add_argument("--out", help="Output report path")
    report_p.add_argument("--title", default="CDFD Runtime Report")
    report_p.add_argument("--json", action="store_true", help="Print command envelope as JSON")

    explain_p = sub.add_parser("explain", help="Explain a saved result with equations and claim boundaries")
    explain_p.add_argument("input", help="Input JSON result")
    explain_p.add_argument("--format", choices=CLI_FORMATS, default="markdown")
    explain_p.add_argument("--out", help="Output explanation path")
    explain_p.add_argument("--title", default="CDFD Runtime Explanation")
    explain_p.add_argument("--json", action="store_true", help="Print command envelope as JSON")

    llm_p = sub.add_parser("llm", help="Call an optional LLM provider for research interpretation")
    llm_sub = llm_p.add_subparsers(dest="llm_command", required=True)

    llm_providers_p = llm_sub.add_parser("providers", help="List supported LLM provider profiles without making a call")
    _add_format_args(llm_providers_p)
    _add_run_bundle_args(llm_providers_p)

    llm_status_p = llm_sub.add_parser("status", help="Check provider-key configuration without making a provider call")
    _add_llm_provider_args(llm_status_p)
    _add_format_args(llm_status_p)
    _add_run_bundle_args(llm_status_p)

    llm_explain_p = llm_sub.add_parser("explain", help="Call an LLM provider to interpret a saved CDFD result")
    llm_explain_p.add_argument("input", help="Input JSON result")
    llm_explain_p.add_argument("--question", help="Research question for the provider")
    llm_explain_p.add_argument("--system-prompt", help="Override the default CDFD research-boundary system prompt")
    llm_explain_p.add_argument("--temperature", type=float, default=0.2)
    llm_explain_p.add_argument("--max-tokens", type=int, default=900)
    llm_explain_p.add_argument("--timeout", type=float, default=60.0)
    llm_explain_p.add_argument("--max-context-chars", type=int, default=12000)
    llm_explain_p.add_argument("--dry-run", action="store_true", help="Build prompt audit without calling the provider")
    llm_explain_p.add_argument("--prompt-preview-chars", type=int, default=2000)
    _add_llm_provider_args(llm_explain_p)
    _add_format_args(llm_explain_p)
    _add_run_bundle_args(llm_explain_p)

    auth_p = sub.add_parser("auth", help="Compatibility alias for `cdfd llm status`")
    _add_llm_provider_args(auth_p)
    auth_p.add_argument("--allowed-env", default=None, help=argparse.SUPPRESS)
    _add_format_args(auth_p)
    _add_run_bundle_args(auth_p)

    return parser


def _demo_payload(args: argparse.Namespace, parser: argparse.ArgumentParser) -> dict | None:
    payload = None
    if args.payload:
        try:
            payload = load_json_object(args.payload)
        except Exception as exc:
            parser.error(str(exc))
    if args.source_scenario:
        if payload is None:
            payload = {}
        payload["source_scenario"] = args.source_scenario
    return payload


def _emit_from_args(
    result: dict,
    args: argparse.Namespace,
    *,
    out: str | None = None,
    run_label: str | None = None,
    fmt: str | None = None,
) -> int:
    return _emit(
        result,
        json_mode=getattr(args, "json", False),
        out=args.out if out is None else out,
        fmt=fmt or _selected_format(args),
        save_run=getattr(args, "save_run", False),
        runs_root=getattr(args, "runs_root", "runs"),
        run_label=run_label,
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "info":
        return _emit_from_args(runtime_info(), args)

    if args.command == "domains":
        return _emit_from_args(list_domains(), args)

    if args.command == "doctor":
        return _emit_from_args(doctor(), args, run_label="doctor")

    if args.command == "gallery":
        result = gallery(nx=args.nx, ny=args.ny, steps=args.steps, include_cdfl=not args.no_cdfl)
        return _emit_from_args(result, args, run_label="gallery")

    if args.command == "compare":
        scenarios = args.scenarios
        if not scenarios:
            scenarios = [
                "mixed_source_surface_trap",
                "meteoritic_seed_retained",
                "terrestrial_synthesis",
            ]
        result = compare_domain(args.domain, scenarios, nx=args.nx, ny=args.ny, steps=args.steps)
        return _emit_from_args(result, args, run_label=f"compare-{args.domain}")

    if args.command == "demo":
        result = run_domain(
            args.domain,
            _demo_payload(args, parser),
            nx=args.nx,
            ny=args.ny,
            steps=args.steps,
            dt=args.dt,
            include_traceback=args.traceback,
        )
        return _emit_from_args(result, args, run_label=f"demo-{args.domain}")

    if args.command == "diagnostics":
        out = args.out
        if out is None and _selected_format(args) != "json":
            out = str(
                Path(__file__).resolve().parent
                / "experiments"
                / "outputs"
                / "part_ii_runtime_diagnostics.json"
            )
        result = part_ii_diagnostics(
            scenario=args.scenario,
            include_demo=not args.no_demo,
            demo_steps=args.demo_steps,
            demo_nx=args.demo_nx,
            demo_ny=args.demo_ny,
        )
        return _emit_from_args(result, args, out=out, run_label="diagnostics")

    if args.command == "validate":
        return _emit_from_args(
            validate_cdfl(args.model, include_traceback=args.traceback),
            args,
            run_label="validate",
        )

    if args.command in {"run", "simulate"}:
        return _emit_from_args(
            run_cdfl(args.model, nx=args.nx, ny=args.ny, include_traceback=args.traceback),
            args,
            run_label="run",
        )

    if args.command == "cdfl":
        if args.cdfl_command == "validate":
            return _emit_from_args(
                validate_cdfl(
                    args.model,
                    include_traceback=args.traceback,
                    command=f"cdfd cdfl validate {args.model}",
                ),
                args,
                run_label="cdfl-validate",
            )
        if args.cdfl_command == "run":
            return _emit_from_args(
                run_cdfl(
                    args.model,
                    nx=args.nx,
                    ny=args.ny,
                    include_traceback=args.traceback,
                    command=f"cdfd cdfl run {args.model}",
                ),
                args,
                run_label="cdfl-run",
            )
        if args.cdfl_command == "lint":
            return _emit_from_args(
                lint_cdfl(args.model, include_traceback=args.traceback),
                args,
                run_label="cdfl-lint",
            )
        if args.cdfl_command == "format":
            result = format_cdfl_file(
                args.model,
                output_path=args.output_path,
                in_place=args.in_place,
                indent_size=args.indent_size,
            )
            return _emit(result, json_mode=args.json, out=None, fmt=_selected_format(args))
        if args.cdfl_command == "ast":
            return _emit_from_args(
                cdfl_ast(args.model, include_traceback=args.traceback),
                args,
                run_label="cdfl-ast",
            )
        if args.cdfl_command == "sample":
            result = cdfl_sample(output_path=args.output_path, force=args.force)
            return _emit(result, json_mode=args.json, out=None, fmt=_selected_format(args))

    if args.command == "export":
        result = export_result(Path(args.input), output_path=args.out, fmt=args.format)
        return _emit(result, json_mode=args.json, out=None)

    if args.command == "report":
        result = report_result(Path(args.input), output_path=args.out, fmt=args.format, title=args.title)
        return _emit(result, json_mode=args.json, out=None, fmt="table")

    if args.command == "explain":
        result = explain_result(Path(args.input), output_path=args.out, fmt=args.format, title=args.title)
        return _emit(result, json_mode=args.json, out=None, fmt="table")

    if args.command == "llm":
        if args.llm_command == "providers":
            return _emit_from_args(llm_provider_inventory(), args, run_label="llm-providers")
        if args.llm_command == "status":
            result = llm_provider_status(
                provider=args.provider,
                model=args.model,
                base_url=args.base_url,
                api_key=args.api_key,
                api_key_file=args.api_key_file,
                key_env=args.key_env,
            )
            return _emit_from_args(result, args, run_label="llm-status")
        if args.llm_command == "explain":
            result = llm_explain_result(
                args.input,
                question=args.question,
                provider=args.provider,
                model=args.model,
                base_url=args.base_url,
                api_key=args.api_key,
                api_key_file=args.api_key_file,
                key_env=args.key_env,
                system_prompt=args.system_prompt,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
                timeout=args.timeout,
                max_context_chars=args.max_context_chars,
                dry_run=args.dry_run,
                prompt_preview_chars=args.prompt_preview_chars,
            )
            return _emit_from_args(result, args, run_label="llm-explain")

    if args.command == "auth":
        return _emit_from_args(
            app_auth_status(
                provider=args.provider,
                model=args.model,
                base_url=args.base_url,
                api_key=args.api_key,
                api_key_file=args.api_key_file,
                key_env=args.key_env,
                allowed_env=args.allowed_env,
            ),
            args,
            run_label="auth",
        )

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
