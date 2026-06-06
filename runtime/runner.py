"""Command backend for the CDFD CLI and future web interfaces."""
from __future__ import annotations

import html
import importlib.util
import json
import os
import traceback
from pathlib import Path
from typing import Any

from domains.demo_runner import run_domain_demo
from domains.registry import DomainRegistry
from dsl.cdfl_tools import CANONICAL_HEAT_FLOW, analyze_cdfl_text, format_cdfl_text
from dsl.executor import Executor
from dsl.lexer import tokenize
from dsl.parser import ParseError, parse
from runtime.diagnostics import (
    LIFE_NUMBER_SUPPLY_GUARDRAIL,
    aromatic_source_mix_scenario,
    aromatic_source_mix_scenarios,
    best_aromatic_source_mix,
    clean_json,
    photochemical_material_status,
    result_envelope,
    write_json,
)
from runtime.llm import llm_explain_result, llm_provider_inventory, llm_provider_status
from runtime.reporting import explanation_for_result, explanation_to_markdown, write_report


CRITICAL_IMPORTS = ("numpy",)
OPTIONAL_IMPORTS = ("matplotlib", "pandas", "streamlit")
GALLERY_SCENARIOS = (
    "mixed_source_surface_trap",
    "meteoritic_seed_retained",
    "terrestrial_synthesis",
)


def load_json_object(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text())
    if not isinstance(data, dict):
        raise ValueError("JSON payload must be an object")
    return data


def list_domains() -> dict[str, Any]:
    names = sorted(DomainRegistry.default().list_domains())
    return result_envelope(
        "domain_list",
        "cdfd domains",
        {"count": len(names), "domains": names},
    )


def runtime_info() -> dict[str, Any]:
    domains = sorted(DomainRegistry.default().list_domains())
    return result_envelope(
        "runtime_info",
        "cdfd info",
        {
            "name": "CDFD Runtime",
            "language": "CDFL",
            "platform_order": ["engine", "cli", "api", "webapp", "editor"],
            "primary_surface": "cli",
            "cli_status": "available",
            "domain_count": len(domains),
            "commands": [
                "info",
                "domains",
                "demo",
                "diagnostics",
                "doctor",
                "gallery",
                "compare",
                "report",
                "explain",
                "llm",
                "cdfl",
                "validate",
                "run",
                "export",
                "auth",
            ],
            "entrypoints": {
                "cli": "python cdfd.py",
                "cdfl_tooling": "python cdfd.py cdfl lint examples/heat_flow.cdfl",
                "legacy_domain_cli": "python -m domains",
                "diagnostics_export": "python cdfd.py diagnostics --out experiments/outputs/part_ii_runtime_diagnostics.json",
                "webapp_optional": "python -m webapp.run_server",
                "vscode_extension_optional": "tools/cdfl-vscode",
            },
            "app_boundary": {
                "provider_inventory": "python cdfd.py llm providers",
                "provider_key_status": "python cdfd.py llm status",
                "provider_key_envs": [
                    "OPENAI_API_KEY",
                    "ANTHROPIC_API_KEY",
                    "GEMINI_API_KEY",
                    "MISTRAL_API_KEY",
                    "GROQ_API_KEY",
                    "OPENROUTER_API_KEY",
                    "CDFD_LLM_API_KEY",
                ],
                "llm_research_call": "python cdfd.py llm explain runs/<run>/result.json",
                "llm_layer": "optional provider calls above the deterministic runtime engine",
                "vos": "Vacuum OS orchestration layer above CDFD Runtime",
            },
            "core_surfaces": [
                "engine",
                "domains",
                "dsl",
                "runtime",
                "validation",
                "discovery",
            ],
            "optional_surfaces": ["webapp", "vscode_extension"],
        },
    )


def doctor() -> dict[str, Any]:
    """Check the public runtime surfaces without mutating repository state."""
    root = Path(__file__).resolve().parents[1]
    domains = sorted(DomainRegistry.default().list_domains())
    checks: list[dict[str, Any]] = []
    warnings: list[str] = []
    errors: list[str] = []

    def add(name: str, ok: bool, detail: str, *, critical: bool = True) -> None:
        status = "ok" if ok else ("error" if critical else "warning")
        checks.append({"name": name, "status": status, "detail": detail, "critical": critical})
        if not ok and critical:
            errors.append(f"{name}: {detail}")
        elif not ok:
            warnings.append(f"{name}: {detail}")

    add("python", True, f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}")
    for module in CRITICAL_IMPORTS:
        add(f"import:{module}", importlib.util.find_spec(module) is not None, "module importable")
    for module in OPTIONAL_IMPORTS:
        add(
            f"import:{module}",
            importlib.util.find_spec(module) is not None,
            "module importable",
            critical=module != "streamlit",
        )

    add("cli_entrypoint", (root / "cdfd.py").exists(), "cdfd.py present")
    add("example_model", (root / "examples" / "heat_flow.cdfl").exists(), "examples/heat_flow.cdfl present")
    add("webapp_entrypoint", (root / "webapp" / "run_server.py").exists(), "python -m webapp.run_server present", critical=False)
    add("domain_registry", len(domains) > 0, f"{len(domains)} domain adapters")

    try:
        info = runtime_info()
        add("result_envelope", bool(info.get("finite_audit", {}).get("all_finite")), "strict JSON envelope finite audit")
    except Exception as exc:  # pragma: no cover - defensive doctor surface
        add("result_envelope", False, str(exc))

    run_root = root / "runs"
    add("run_root", os.access(run_root.parent, os.W_OK), f"{run_root} parent writable", critical=False)

    payload = {
        "root": str(root),
        "domain_count": len(domains),
        "checks": checks,
        "summary": {
            "ok": sum(1 for item in checks if item["status"] == "ok"),
            "warnings": sum(1 for item in checks if item["status"] == "warning"),
            "errors": sum(1 for item in checks if item["status"] == "error"),
        },
    }
    return result_envelope(
        "runtime_doctor",
        "cdfd doctor",
        payload,
        status="error" if errors else "ok",
        warnings=warnings,
        errors=errors,
    )


def gallery(*, nx: int = 4, ny: int = 4, steps: int = 1, include_cdfl: bool = True) -> dict[str, Any]:
    """Run a curated, quick CDFD gallery for demos and public smoke checks."""
    root = Path(__file__).resolve().parents[1]
    runs: list[dict[str, Any]] = [
        runtime_info(),
        run_domain("physics", nx=nx, ny=ny, steps=steps),
        run_domain(
            "origins_of_life",
            {"source_scenario": "mixed_source_surface_trap"},
            nx=nx,
            ny=ny,
            steps=steps,
        ),
        run_domain("medicine", nx=nx, ny=ny, steps=steps),
        run_domain("networks", nx=nx, ny=ny, steps=steps),
        run_domain("climate", nx=nx, ny=ny, steps=steps),
        run_domain("economics", nx=nx, ny=ny, steps=steps),
        part_ii_diagnostics(include_demo=False),
    ]
    model = root / "examples" / "heat_flow.cdfl"
    if include_cdfl and model.exists():
        runs.append(validate_cdfl(model))
        runs.append(run_cdfl(model, nx=nx, ny=ny))

    highlights = []
    for item in runs:
        payload = item.get("payload", {})
        highlight: dict[str, Any] = {
            "kind": item.get("kind"),
            "status": item.get("status"),
            "finite": item.get("finite_audit", {}).get("all_finite"),
        }
        if isinstance(payload, dict):
            if "domain" in payload:
                highlight["domain"] = payload["domain"]
                highlight["regime"] = payload.get("regime")
                highlight["mean_psi"] = (payload.get("final") or {}).get("mean_psi")
            if "best_aromatic_source_mix" in payload:
                best = payload["best_aromatic_source_mix"]
                highlight["best_source_mix"] = best.get("scenario")
                highlight["functional_score"] = best.get("functional_score")
        highlights.append(highlight)

    return result_envelope(
        "runtime_gallery",
        "cdfd gallery",
        {
            "description": "Curated quick tour of physics, origins of life, medicine, networks, climate, economics, Part II diagnostics, and CDFL runtime surfaces.",
            "vos_preview": {
                "boundary": "VOS and optional LLM provider calls sit above the deterministic runtime engine.",
                "future_hooks": ["run queue", "provider-key status", "saved experiments", "research-assistant LLM calls"],
            },
            "parameters": {"nx": nx, "ny": ny, "steps": steps, "include_cdfl": include_cdfl},
            "highlights": highlights,
            "runs": runs,
        },
    )


def compare_domain(
    domain: str,
    scenarios: list[str],
    *,
    nx: int = 4,
    ny: int = 4,
    steps: int = 1,
) -> dict[str, Any]:
    """Run scenario comparisons through the same domain adapter path as `demo`."""
    rows: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    for scenario in scenarios:
        payload = {"source_scenario": scenario} if domain == "origins_of_life" else {"scenario": scenario}
        result = run_domain(domain, payload, nx=nx, ny=ny, steps=steps)
        results.append(result)
        body = result.get("payload", {})
        final = body.get("final", {}) if isinstance(body, dict) else {}
        diag = body.get("domain_diagnostics", {}) if isinstance(body, dict) else {}
        source_mix = diag.get("aromatic_source_mix", {}) if isinstance(diag, dict) else {}
        mean_psi = final.get("mean_psi")
        functional_score = source_mix.get("functional_score")
        score = functional_score if functional_score is not None else (
            -abs(float(mean_psi) - 1.0) if mean_psi is not None else None
        )
        rows.append(
            {
                "label": f"{domain}:{scenario}",
                "domain": domain,
                "scenario": scenario,
                "status": result.get("status"),
                "finite": result.get("finite_audit", {}).get("all_finite"),
                "regime": body.get("regime") if isinstance(body, dict) else None,
                "mean_psi": mean_psi,
                "functional_score": functional_score,
                "score": score,
                "interpretation": body.get("interpretation") if isinstance(body, dict) else None,
            }
        )
    ranked = sorted(rows, key=lambda row: (row["score"] is not None, row["score"]), reverse=True)
    return result_envelope(
        "runtime_compare",
        f"cdfd compare {domain}",
        {
            "domain": domain,
            "parameters": {"nx": nx, "ny": ny, "steps": steps, "scenarios": scenarios},
            "ranked": ranked,
            "results": results,
        },
    )


def part_ii_diagnostics(
    *,
    scenario: str | None = None,
    include_demo: bool = True,
    demo_steps: int = 12,
    demo_nx: int = 8,
    demo_ny: int = 8,
) -> dict[str, Any]:
    """Part II-aligned runtime diagnostics (Paper 7 source-mix, Paper 11 guardrails)."""
    payload: dict[str, Any] = {
        "life_number_guardrail": LIFE_NUMBER_SUPPLY_GUARDRAIL,
        "photochemical_material_status": photochemical_material_status(),
        "aromatic_source_mix_scenarios": aromatic_source_mix_scenarios(),
        "best_aromatic_source_mix": best_aromatic_source_mix(),
    }
    if scenario:
        payload["selected_scenario"] = aromatic_source_mix_scenario(scenario)
    if include_demo:
        payload["origins_of_life_demo"] = run_domain_demo(
            "origins_of_life",
            {"source_scenario": scenario or "mixed_source_surface_trap"},
            nx=demo_nx,
            ny=demo_ny,
            steps=demo_steps,
        )
    command = f"cdfd diagnostics{f' --scenario {scenario}' if scenario else ''}"
    return result_envelope("part_ii_diagnostics", command, payload)


def app_auth_status(
    *,
    provider: str | None = None,
    model: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    api_key_file: str | Path | None = None,
    key_env: str | None = None,
    allowed_env: str | None = None,
) -> dict[str, Any]:
    """Compatibility wrapper: `cdfd auth` now reports LLM provider-key status."""
    _ = allowed_env
    return llm_provider_status(
        provider=provider,
        model=model,
        base_url=base_url,
        api_key=api_key,
        api_key_file=api_key_file,
        key_env=key_env,
    )


def run_domain(
    domain: str,
    payload: dict[str, Any] | None = None,
    *,
    nx: int = 16,
    ny: int = 16,
    steps: int = 24,
    dt: float | None = None,
    include_traceback: bool = False,
) -> dict[str, Any]:
    try:
        result = run_domain_demo(domain, payload or {}, nx=nx, ny=ny, steps=steps, dt=dt)
        return result_envelope("domain_demo", f"cdfd demo {domain}", result)
    except Exception as exc:
        errors = [str(exc)]
        if include_traceback:
            errors.append(traceback.format_exc())
        return result_envelope(
            "domain_demo",
            f"cdfd demo {domain}",
            {"domain": domain},
            status="error",
            errors=errors,
        )


def _read_cdfl(path: str | Path) -> str:
    return Path(path).read_text()


def analyze_cdfl(path: str | Path) -> dict[str, Any]:
    return analyze_cdfl_text(_read_cdfl(path))


def compile_cdfl(path: str | Path) -> tuple[list[Any], list[Any]]:
    code = _read_cdfl(path)
    tokens = tokenize(code)
    nodes = parse(tokens)
    return tokens, nodes


def validate_cdfl(path: str | Path, include_traceback: bool = False, command: str | None = None) -> dict[str, Any]:
    model_path = Path(path)
    command_label = command or f"cdfd validate {model_path}"
    try:
        analysis = analyze_cdfl(model_path)
        payload = {
            "file": str(model_path),
            "valid": analysis["valid"],
            "token_count": analysis["token_count"],
            "node_count": analysis["node_count"],
            "nodes": [node["type"] for node in analysis["nodes"]],
            "diagnostics": analysis["diagnostics"],
            "diagnostic_summary": analysis["diagnostic_summary"],
        }
        errors = [row["message"] for row in analysis["diagnostics"] if row.get("severity") == "error"]
        return result_envelope(
            "cdfl_validation",
            command_label,
            payload,
            status="ok" if analysis["valid"] else "error",
            errors=errors if errors else None,
        )
    except (OSError, ParseError, Exception) as exc:
        errors = [str(exc)]
        if include_traceback:
            errors.append(traceback.format_exc())
        return result_envelope(
            "cdfl_validation",
            command_label,
            {"file": str(model_path), "valid": False},
            status="error",
            errors=errors,
        )


def lint_cdfl(path: str | Path, include_traceback: bool = False) -> dict[str, Any]:
    model_path = Path(path)
    try:
        analysis = analyze_cdfl(model_path)
        summary = analysis["diagnostic_summary"]
        errors = [row["message"] for row in analysis["diagnostics"] if row.get("severity") == "error"]
        payload = {
            "file": str(model_path),
            "valid": analysis["valid"],
            "token_count": analysis["token_count"],
            "node_count": analysis["node_count"],
            "diagnostics": analysis["diagnostics"],
            "diagnostic_summary": summary,
        }
        return result_envelope(
            "cdfl_lint",
            f"cdfd cdfl lint {model_path}",
            payload,
            status="ok" if summary.get("error", 0) == 0 else "error",
            errors=errors if errors else None,
        )
    except Exception as exc:
        errors = [str(exc)]
        if include_traceback:
            errors.append(traceback.format_exc())
        return result_envelope(
            "cdfl_lint",
            f"cdfd cdfl lint {model_path}",
            {"file": str(model_path), "valid": False},
            status="error",
            errors=errors,
        )


def format_cdfl_file(
    path: str | Path,
    *,
    output_path: str | Path | None = None,
    in_place: bool = False,
    indent_size: int = 2,
) -> dict[str, Any]:
    model_path = Path(path)
    try:
        if in_place and output_path is not None:
            return result_envelope(
                "cdfl_format",
                f"cdfd cdfl format {model_path}",
                {"file": str(model_path), "output": str(output_path), "in_place": in_place},
                status="error",
                errors=["Use either --in-place or --out, not both."],
            )
        original = _read_cdfl(model_path)
        formatted = format_cdfl_text(original, indent_size=indent_size)
        changed = formatted != original
        output = None
        if in_place:
            model_path.write_text(formatted)
            output = model_path
        elif output_path is not None:
            output = Path(output_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(formatted)

        return result_envelope(
            "cdfl_format",
            f"cdfd cdfl format {model_path}",
            {
                "file": str(model_path),
                "output": str(output) if output else None,
                "in_place": in_place,
                "indent_size": indent_size,
                "changed": changed,
                "formatted": formatted,
            },
        )
    except Exception as exc:
        return result_envelope(
            "cdfl_format",
            f"cdfd cdfl format {model_path}",
            {"file": str(model_path), "output": str(output_path) if output_path else None, "in_place": in_place},
            status="error",
            errors=[str(exc)],
        )


def cdfl_ast(path: str | Path, include_traceback: bool = False) -> dict[str, Any]:
    model_path = Path(path)
    try:
        analysis = analyze_cdfl(model_path)
        errors = [row["message"] for row in analysis["diagnostics"] if row.get("severity") == "error"]
        return result_envelope(
            "cdfl_ast",
            f"cdfd cdfl ast {model_path}",
            {
                "file": str(model_path),
                "valid": analysis["valid"],
                "token_count": analysis["token_count"],
                "node_count": analysis["node_count"],
                "nodes": analysis["nodes"],
                "diagnostics": analysis["diagnostics"],
                "diagnostic_summary": analysis["diagnostic_summary"],
            },
            status="ok" if analysis["valid"] else "error",
            errors=errors if errors else None,
        )
    except Exception as exc:
        errors = [str(exc)]
        if include_traceback:
            errors.append(traceback.format_exc())
        return result_envelope(
            "cdfl_ast",
            f"cdfd cdfl ast {model_path}",
            {"file": str(model_path), "valid": False},
            status="error",
            errors=errors,
        )


def cdfl_sample(*, output_path: str | Path | None = None, force: bool = False) -> dict[str, Any]:
    output = Path(output_path) if output_path else None
    try:
        if output and output.exists() and not force:
            return result_envelope(
                "cdfl_sample",
                "cdfd cdfl sample",
                {"output": str(output), "written": False, "sample": CANONICAL_HEAT_FLOW},
                status="error",
                errors=[f"{output} already exists; pass --force to overwrite it."],
            )
        if output:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(CANONICAL_HEAT_FLOW)
        return result_envelope(
            "cdfl_sample",
            "cdfd cdfl sample",
            {"output": str(output) if output else None, "written": bool(output), "sample": CANONICAL_HEAT_FLOW},
        )
    except Exception as exc:
        return result_envelope(
            "cdfl_sample",
            "cdfd cdfl sample",
            {"output": str(output) if output else None, "written": False, "sample": CANONICAL_HEAT_FLOW},
            status="error",
            errors=[str(exc)],
        )


def run_cdfl(
    path: str | Path,
    *,
    nx: int = 16,
    ny: int = 16,
    include_traceback: bool = False,
    command: str | None = None,
) -> dict[str, Any]:
    model_path = Path(path)
    command_label = command or f"cdfd run {model_path}"
    try:
        _tokens, nodes = compile_cdfl(model_path)
        executor = Executor(nx=nx, ny=ny)
        results = executor.execute(nodes)
        return result_envelope(
            "cdfl_run",
            command_label,
            {
                "file": str(model_path),
                "nx": nx,
                "ny": ny,
                "node_count": len(nodes),
                "results": clean_json(results),
            },
        )
    except (OSError, ParseError, Exception) as exc:
        errors = [str(exc)]
        if include_traceback:
            errors.append(traceback.format_exc())
        return result_envelope(
            "cdfl_run",
            command_label,
            {"file": str(model_path), "nx": nx, "ny": ny},
            status="error",
            errors=errors,
        )


def export_result(input_path: str | Path, *, output_path: str | Path | None = None, fmt: str = "json") -> dict[str, Any]:
    src = Path(input_path)
    if fmt != "json":
        return result_envelope(
            "export",
            f"cdfd export {src}",
            {"input": str(src), "format": fmt},
            status="error",
            errors=["Only JSON export is currently implemented."],
        )
    try:
        payload = json.loads(src.read_text())
        out = Path(output_path) if output_path else src.with_suffix(".export.json")
        write_json(out, payload)
        return result_envelope(
            "export",
            f"cdfd export {src}",
            {"input": str(src), "output": str(out), "format": fmt},
        )
    except Exception as exc:
        return result_envelope(
            "export",
            f"cdfd export {src}",
            {"input": str(src), "format": fmt},
            status="error",
            errors=[str(exc)],
        )


def report_result(
    input_path: str | Path,
    *,
    output_path: str | Path | None = None,
    fmt: str = "markdown",
    title: str = "CDFD Runtime Report",
) -> dict[str, Any]:
    src = Path(input_path)
    try:
        payload = json.loads(src.read_text())
        suffix = {"markdown": ".md", "html": ".html", "pdf": ".pdf", "json": ".json"}[fmt]
        out = Path(output_path) if output_path else src.with_suffix(suffix)
        write_report(payload, out, fmt=fmt, title=title)
        return result_envelope(
            "report",
            f"cdfd report {src}",
            {"input": str(src), "output": str(out), "format": fmt, "title": title},
        )
    except KeyError:
        return result_envelope(
            "report",
            f"cdfd report {src}",
            {"input": str(src), "format": fmt},
            status="error",
            errors=[f"unsupported report format: {fmt}"],
        )
    except Exception as exc:
        return result_envelope(
            "report",
            f"cdfd report {src}",
            {"input": str(src), "format": fmt},
            status="error",
            errors=[str(exc)],
        )


def explain_result(
    input_path: str | Path,
    *,
    output_path: str | Path | None = None,
    fmt: str = "markdown",
    title: str = "CDFD Runtime Explanation",
) -> dict[str, Any]:
    src = Path(input_path)
    try:
        saved = json.loads(src.read_text())
        explanation = explanation_for_result(saved)
        if fmt == "json":
            content = json.dumps(clean_json(explanation), indent=2, sort_keys=True, allow_nan=False) + "\n"
            suffix = ".explain.json"
        elif fmt == "markdown":
            content = explanation_to_markdown(explanation, title=title)
            suffix = ".explain.md"
        elif fmt == "html":
            markdown = explanation_to_markdown(explanation, title=title)
            content = (
                "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
                f"<title>{html.escape(title)}</title></head><body><pre>"
                f"{html.escape(markdown)}</pre></body></html>\n"
            )
            suffix = ".explain.html"
        elif fmt == "table":
            lines = [explanation["headline"], ""]
            for key in ("interpretation", "what_this_supports", "what_would_break_it"):
                lines.append(key)
                lines.extend(f"- {item}" for item in explanation[key])
                lines.append("")
            content = "\n".join(lines)
            suffix = ".explain.txt"
        else:
            raise ValueError(f"unsupported explanation format: {fmt}")
        out = Path(output_path) if output_path else src.with_suffix(suffix)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content)
        return result_envelope(
            "explain",
            f"cdfd explain {src}",
            {"input": str(src), "output": str(out), "format": fmt, "explanation": explanation},
        )
    except Exception as exc:
        return result_envelope(
            "explain",
            f"cdfd explain {src}",
            {"input": str(src), "format": fmt},
            status="error",
            errors=[str(exc)],
        )
