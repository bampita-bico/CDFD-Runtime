"""Run artifact helpers for CLI and webapp surfaces."""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from runtime.diagnostics import clean_json, write_json
from runtime.reporting import write_report
from runtime.session import RuntimeSession


def _slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-")
    return slug[:80] or "run"


def _run_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def create_run_bundle(
    result: Mapping[str, Any],
    *,
    root: str | Path = "runs",
    label: str | None = None,
) -> dict[str, Any]:
    """Persist a result envelope plus report under a timestamped run directory."""
    session = RuntimeSession.from_result(result, label=label)
    run_label = _slug(label or session.command)
    stamp = _run_stamp()
    run_dir = Path(root) / f"{stamp}-{run_label}"
    run_dir.mkdir(parents=True, exist_ok=True)
    plots_dir = run_dir / "plots"
    plots_dir.mkdir(exist_ok=True)

    result_path = write_json(run_dir / "result.json", result)
    report_paths = {
        "markdown": write_report(result, run_dir / "report.md", fmt="markdown"),
        "html": write_report(result, run_dir / "report.html", fmt="html"),
    }
    llm_artifacts: dict[str, str] = {}
    if isinstance(result, Mapping) and result.get("kind") == "llm_research_explanation":
        payload = result.get("payload") if isinstance(result.get("payload"), Mapping) else {}
        interpretation = {
            "kind": "llm_interpretation",
            "status": result.get("status"),
            "provider": payload.get("provider"),
            "provider_mode": payload.get("provider_mode"),
            "model": payload.get("model"),
            "base_url_host": payload.get("base_url_host"),
            "prompt_template_version": payload.get("prompt_template_version"),
            "dry_run": payload.get("dry_run"),
            "provider_call_made": payload.get("provider_call_made"),
            "temperature": payload.get("temperature"),
            "max_tokens": payload.get("max_tokens"),
            "context_chars": payload.get("context_chars"),
            "boundary": payload.get("boundary"),
            "artifact_boundary": "Interpretive LLM output only; not deterministic CDFD evidence.",
            "question": payload.get("question"),
            "response_text": payload.get("response_text"),
            "usage": payload.get("usage"),
            "provider_response_id": payload.get("provider_response_id"),
            "secrets_printed": False,
        }
        llm_json = write_json(run_dir / "llm_interpretation.json", interpretation)
        response_text = payload.get("response_text") or ""
        llm_md = run_dir / "llm_interpretation.md"
        llm_md.write_text(
            "\n".join(
                [
                    "# CDFD LLM Research Interpretation",
                    "",
                    f"Provider: {payload.get('provider')}",
                    f"Provider mode: {payload.get('provider_mode')}",
                    f"Model: {payload.get('model')}",
                    f"Base URL host: {payload.get('base_url_host')}",
                    f"Prompt template version: {payload.get('prompt_template_version')}",
                    f"Temperature: {payload.get('temperature')}",
                    f"Max tokens: {payload.get('max_tokens')}",
                    f"Context chars: {payload.get('context_chars')}",
                    f"Provider call made: {payload.get('provider_call_made')}",
                    "",
                    "## Boundary",
                    "",
                    str(payload.get("boundary") or ""),
                    "",
                    "Interpretive LLM output only; not deterministic CDFD evidence.",
                    "",
                    "## Question",
                    "",
                    str(payload.get("question") or ""),
                    "",
                    "## Response",
                    "",
                    response_text or "No provider response text recorded.",
                    "",
                ]
            ),
        )
        llm_artifacts = {
            "llm_interpretation_json": str(llm_json),
            "llm_interpretation_markdown": str(llm_md),
        }
    manifest = session.manifest(
        run_dir=run_dir,
        result_path=result_path,
        report_paths=report_paths,
        plots_dir=plots_dir,
    )
    manifest["artifacts"] = {
        "result_json": str(result_path),
        "report_markdown": str(report_paths["markdown"]),
        "report_html": str(report_paths["html"]),
        "plots_dir": str(plots_dir),
    }
    manifest["artifacts"].update(llm_artifacts)
    manifest["result_preview"] = {
        "kind": result.get("kind") if isinstance(result, Mapping) else None,
        "status": result.get("status") if isinstance(result, Mapping) else None,
        "finite_audit": clean_json(result.get("finite_audit", {})) if isinstance(result, Mapping) else {},
    }
    manifest_path = write_json(run_dir / "manifest.json", manifest)
    manifest["manifest"] = str(manifest_path)
    return manifest
