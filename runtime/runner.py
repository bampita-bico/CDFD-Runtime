"""Command backend for the CDFD CLI and future web interfaces."""
from __future__ import annotations

import html
import importlib.util
import json
import os
import traceback
from pathlib import Path
from typing import Any

from dsl.cdfl_tools import CANONICAL_HEAT_FLOW, analyze_cdfl_text, format_cdfl_text
from dsl.executor import Executor
from dsl.lexer import tokenize
from dsl.parser import ParseError, parse
from runtime.diagnostics import clean_json, result_envelope, write_json
from runtime.llm import llm_explain_result, llm_provider_inventory, llm_provider_status
from runtime.reporting import explanation_for_result, explanation_to_markdown, write_report


CRITICAL_IMPORTS = ("numpy",)
OPTIONAL_IMPORTS = ("matplotlib", "pandas")


def load_json_object(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text())
    if not isinstance(data, dict):
        raise ValueError("JSON payload must be an object")
    return data


def runtime_info() -> dict[str, Any]:
    return result_envelope(
        "runtime_info",
        "cdfd info",
        {
            "name": "CDFD Runtime",
            "language": "CDFL",
            "platform_order": ["engine", "cli", "api", "editor"],
            "primary_surface": "cli",
            "cli_status": "available",
            "commands": [
                "info",
                "doctor",
                "gallery",
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
            },
            "core_surfaces": [
                "engine",
                "dsl",
                "runtime",
                "validation",
            ],
            "optional_surfaces": ["vscode_extension"],
        },
    )


def doctor() -> dict[str, Any]:
    """Check the public runtime surfaces without mutating repository state."""
    root = Path(__file__).resolve().parents[1]
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
            critical=False,
        )

    add("cli_entrypoint", (root / "cdfd.py").exists(), "cdfd.py present")
    add("example_model", (root / "examples" / "heat_flow.cdfl").exists(), "examples/heat_flow.cdfl present")
    add("claim_boundary", (root / "CLAIM_BOUNDARY.md").exists(), "CLAIM_BOUNDARY.md present")

    try:
        info = runtime_info()
        add("result_envelope", bool(info.get("finite_audit", {}).get("all_finite")), "strict JSON envelope finite audit")
    except Exception as exc:  # pragma: no cover - defensive doctor surface
        add("result_envelope", False, str(exc))

    run_root = root / "runs"
    add("run_root", os.access(run_root.parent, os.W_OK), f"{run_root} parent writable", critical=False)

    payload = {
        "root": str(root),
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
    """Run the neutral CDFL example as a compact software smoke check."""
    root = Path(__file__).resolve().parents[1]
    runs: list[dict[str, Any]] = [runtime_info()]
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
        highlights.append(highlight)

    return result_envelope(
        "runtime_gallery",
        "cdfd gallery",
        {
            "description": "Compact CDFL parse, validation, execution, and finite-audit smoke check.",
            "parameters": {"nx": nx, "ny": ny, "steps": steps, "include_cdfl": include_cdfl},
            "highlights": highlights,
            "runs": runs,
        },
    )


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
