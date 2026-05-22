#!/usr/bin/env python3
"""Top-level command line interface for CDFD Runtime."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from runtime.diagnostics import clean_json, write_json
from runtime.runner import (
    app_auth_status,
    export_result,
    list_domains,
    load_json_object,
    run_cdfl,
    run_domain,
    runtime_info,
    validate_cdfl,
)


def _print_json(result: dict) -> None:
    print(json.dumps(clean_json(result), indent=2, sort_keys=True, allow_nan=False))


def _emit(result: dict, *, json_mode: bool = False, out: str | None = None) -> int:
    if out:
        write_json(out, result)

    if json_mode:
        _print_json(result)
    else:
        _print_human(result, out=out)

    return 0 if result.get("status") == "ok" else 1


def _print_human(result: dict, *, out: str | None = None) -> None:
    kind = result.get("kind")
    status = result.get("status")
    payload = result.get("payload", {})

    if kind == "runtime_info":
        print("CDFD Runtime")
        print(f"status: {status}")
        print(f"language: {payload.get('language')}")
        print(f"domains: {payload.get('domain_count')}")
        print("cli: python cdfd.py")
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
    elif kind == "cdfl_validation":
        print(f"status: {status}")
        print(f"file: {payload.get('file')}")
        print(f"valid: {payload.get('valid')}")
        if payload.get("node_count") is not None:
            print(f"nodes: {payload.get('node_count')} ({', '.join(payload.get('nodes', []))})")
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
    elif kind == "app_auth":
        print(f"status: {status}")
        print(f"auth_configured: {payload.get('auth_configured')}")
        print(f"key_supplied: {payload.get('key_supplied')}")
        print(f"accepted: {payload.get('accepted')}")
        if payload.get("key_fingerprint"):
            print(f"key_fingerprint: {payload.get('key_fingerprint')}")
        print(f"llm_boundary: {payload.get('llm_boundary')}")
    else:
        print(f"status: {status}")
        print(json.dumps(clean_json(payload), indent=2, sort_keys=True, allow_nan=False))

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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cdfd",
        description="CDFD Runtime CLI for CDFL models, domain demos, validation, and export.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    info_p = sub.add_parser("info", help="Show runtime capability summary")
    info_p.add_argument("--json", action="store_true", help="Print JSON")
    info_p.add_argument("--out", help="Write full result JSON to a file")

    domains_p = sub.add_parser("domains", help="List registered domain adapters")
    domains_p.add_argument("--json", action="store_true", help="Print JSON")
    domains_p.add_argument("--out", help="Write full result JSON to a file")

    demo_p = sub.add_parser("demo", help="Run an engine-backed domain demo")
    demo_p.add_argument("domain", help="Domain key, for example physics, medicine, origins_of_life")
    demo_p.add_argument("--payload", metavar="FILE.json", help="Optional JSON object payload")
    demo_p.add_argument("--nx", type=int, default=16)
    demo_p.add_argument("--ny", type=int, default=16)
    demo_p.add_argument("--steps", type=int, default=24)
    demo_p.add_argument("--dt", type=float, default=None)
    demo_p.add_argument("--json", action="store_true", help="Print JSON")
    demo_p.add_argument("--out", help="Write full result JSON to a file")

    validate_p = sub.add_parser("validate", help="Parse and validate a CDFL model")
    validate_p.add_argument("model", help="Path to .cdfl model")
    validate_p.add_argument("--json", action="store_true", help="Print JSON")
    validate_p.add_argument("--out", help="Write full result JSON to a file")

    run_p = sub.add_parser("run", help="Run a CDFL model")
    run_p.add_argument("model", help="Path to .cdfl model")
    run_p.add_argument("--nx", type=int, default=16)
    run_p.add_argument("--ny", type=int, default=16)
    run_p.add_argument("--json", action="store_true", help="Print JSON")
    run_p.add_argument("--out", help="Write full result JSON to a file")

    simulate_p = sub.add_parser("simulate", help="Alias for run")
    simulate_p.add_argument("model", help="Path to .cdfl model")
    simulate_p.add_argument("--nx", type=int, default=16)
    simulate_p.add_argument("--ny", type=int, default=16)
    simulate_p.add_argument("--json", action="store_true", help="Print JSON")
    simulate_p.add_argument("--out", help="Write full result JSON to a file")

    export_p = sub.add_parser("export", help="Export a saved CLI result")
    export_p.add_argument("input", help="Input JSON result")
    export_p.add_argument("--format", choices=["json"], default="json")
    export_p.add_argument("--out", help="Output path")
    export_p.add_argument("--json", action="store_true", help="Print JSON")

    auth_p = sub.add_parser("auth", help="Check app API-key boundary without storing the secret")
    auth_p.add_argument("--api-key", help="App API key value; prefer --api-key-file or env in scripts")
    auth_p.add_argument("--api-key-file", help="File containing the app API key")
    auth_p.add_argument("--key-env", default="CDFD_APP_API_KEY", help="Environment variable for caller key")
    auth_p.add_argument("--allowed-env", default="CDFD_RUNTIME_API_KEYS", help="Environment variable with allowed keys")
    auth_p.add_argument("--json", action="store_true", help="Print JSON")
    auth_p.add_argument("--out", help="Write full result JSON to a file")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "info":
        return _emit(runtime_info(), json_mode=args.json, out=args.out)

    if args.command == "domains":
        return _emit(list_domains(), json_mode=args.json, out=args.out)

    if args.command == "demo":
        payload = None
        if args.payload:
            try:
                payload = load_json_object(args.payload)
            except Exception as exc:
                parser.error(str(exc))
        result = run_domain(
            args.domain,
            payload,
            nx=args.nx,
            ny=args.ny,
            steps=args.steps,
            dt=args.dt,
        )
        return _emit(result, json_mode=args.json, out=args.out)

    if args.command == "validate":
        return _emit(validate_cdfl(args.model), json_mode=args.json, out=args.out)

    if args.command in {"run", "simulate"}:
        return _emit(run_cdfl(args.model, nx=args.nx, ny=args.ny), json_mode=args.json, out=args.out)

    if args.command == "export":
        result = export_result(Path(args.input), output_path=args.out, fmt=args.format)
        return _emit(result, json_mode=args.json, out=None)

    if args.command == "auth":
        return _emit(
            app_auth_status(
                api_key=args.api_key,
                api_key_file=args.api_key_file,
                key_env=args.key_env,
                allowed_env=args.allowed_env,
            ),
            json_mode=args.json,
            out=args.out,
        )

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
