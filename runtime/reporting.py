"""Report rendering for CDFD Runtime result envelopes."""
from __future__ import annotations

import html
import json
import textwrap
from pathlib import Path
from typing import Any, Mapping

from runtime.diagnostics import clean_json

RUNTIME_CITATION = (
    "Mujjabi, S. B. (2026). CDFD Runtime: Constraint-Driven Flux Dynamics "
    "and CDFL Execution Engine. Zenodo. https://doi.org/10.5281/zenodo.20343160"
)
CLAIM_BOUNDARY = (
    "CDFD Runtime output is deterministic toy-model execution and hypothesis "
    "triage. It is not empirical proof or other empirical evidence, a calibrated forecast, clinical "
    "advice, engineering certification, or a deployed safety, financial, or "
    "medical decision system."
)


def _payload_summary(payload: Mapping[str, Any]) -> list[str]:
    lines: list[str] = []
    if payload.get("file"):
        lines.append(f"- Model file: `{payload.get('file')}`")
    if "valid" in payload:
        lines.append(f"- CDFL valid: `{payload.get('valid')}`")
    if "node_count" in payload:
        lines.append(f"- AST nodes: `{payload.get('node_count')}`")
    if "description" in payload:
        lines.append(f"- Summary: {payload.get('description')}")
    if "highlights" in payload and isinstance(payload["highlights"], list):
        kinds = [row.get("kind") for row in payload["highlights"] if isinstance(row, Mapping)]
        if kinds:
            lines.append(f"- Gallery kinds: `{', '.join(str(k) for k in kinds if k)}`")
    if "checks" in payload:
        checks = payload["checks"]
        if isinstance(checks, list):
            ok = sum(1 for item in checks if isinstance(item, Mapping) and item.get("status") == "ok")
            lines.append(f"- Doctor checks: `{ok}/{len(checks)}` passing")
    if "run_bundle" in payload:
        bundle = payload["run_bundle"]
        if isinstance(bundle, Mapping):
            lines.append(f"- Run bundle: `{bundle.get('run_dir')}`")
    return lines


def _equation_notes(result: Mapping[str, Any]) -> list[str]:
    notes = [
        "- Adaptive operating ratio: `Psi_s = (Phi / C) S M_s` (bookkeeping notation only).",
        "- Regime grammar: constrained below the lower guardrail, balanced near the guardrail window, overload above it.",
        "- A finite JSON audit shows only that recorded values were finite, not that the model is calibrated or empirically adequate.",
    ]
    kind = result.get("kind")
    if kind in {"cdfl_run", "cdfl_validation", "runtime_gallery"}:
        notes.append(
            "- CDFL outputs are software execution records for declared toy models, not domain validation."
        )
    return notes


def explanation_for_result(result: Mapping[str, Any]) -> dict[str, Any]:
    """Return deterministic plain-language interpretation for a result envelope."""
    data = clean_json(dict(result))
    payload = data.get("payload", {})
    kind = data.get("kind")
    status = data.get("status")
    finite = data.get("finite_audit", {})

    result_notes: list[str] = []
    if isinstance(payload, Mapping):
        if payload.get("valid") is not None:
            result_notes.append(f"CDFL validation valid={payload.get('valid')}.")
        if payload.get("node_count") is not None:
            result_notes.append(f"Model parsed {payload.get('node_count')} AST nodes.")
        if payload.get("description"):
            result_notes.append(str(payload["description"]))
        if payload.get("highlights") and isinstance(payload["highlights"], list):
            kinds = [row.get("kind") for row in payload["highlights"] if isinstance(row, Mapping)]
            if kinds:
                result_notes.append(f"Gallery covered: {', '.join(str(k) for k in kinds if k)}.")
        if payload.get("checks"):
            checks = payload["checks"]
            if isinstance(checks, list):
                bad = [item for item in checks if isinstance(item, Mapping) and item.get("status") != "ok"]
                result_notes.append(
                    f"Doctor reported {len(checks) - len(bad)} passing checks and {len(bad)} warnings/errors."
                )

    would_break = [
        "A failed finite audit, non-finite path, exception, or missing provenance breaks the result as a reusable artifact.",
        "External empirical validation would be required before treating a toy-model pattern as a real-world claim.",
    ]
    if finite.get("all_finite") is False:
        would_break.insert(0, f"Finite audit failed at: {finite.get('non_finite_paths')}")

    return {
        "headline": f"{kind or 'runtime result'} finished with status {status}.",
        "equations": _equation_notes(data),
        "interpretation": result_notes or ["No additional interpretation fields were present in the saved result."],
        "what_this_supports": [
            "The run exercises the public runtime path recorded in provenance.",
            "The finite audit records whether JSON-visible numeric output stayed finite.",
        ],
        "what_would_break_it": would_break,
        "claim_boundary": CLAIM_BOUNDARY,
        "citation": RUNTIME_CITATION,
    }


def explanation_to_markdown(explanation: Mapping[str, Any], *, title: str = "CDFD Runtime Explanation") -> str:
    lines = [f"# {title}", "", str(explanation.get("headline", "")), ""]
    sections = [
        ("Equations", explanation.get("equations", [])),
        ("Interpretation", explanation.get("interpretation", [])),
        ("What This Supports", explanation.get("what_this_supports", [])),
        ("What Would Break It", explanation.get("what_would_break_it", [])),
    ]
    for heading, items in sections:
        lines.extend([f"## {heading}", ""])
        for item in items if isinstance(items, list) else [items]:
            text = str(item)
            lines.append(text if text.startswith("- ") else f"- {text}")
        lines.append("")
    lines.extend(
        [
            "## Claim Boundary",
            "",
            str(explanation.get("claim_boundary", CLAIM_BOUNDARY)),
            "",
            "## Citation",
            "",
            str(explanation.get("citation", RUNTIME_CITATION)),
            "",
        ]
    )
    return "\n".join(lines)


def result_to_markdown(result: Mapping[str, Any], *, title: str = "CDFD Runtime Report") -> str:
    """Render a strict result envelope as a compact Markdown report."""
    data = clean_json(dict(result))
    payload = data.get("payload", {})
    provenance = data.get("provenance", {})
    finite = data.get("finite_audit", {})
    warnings = data.get("warnings", [])
    errors = data.get("errors", [])

    lines = [
        f"# {title}",
        "",
        "## Status",
        "",
        f"- Status: `{data.get('status')}`",
        f"- Kind: `{data.get('kind')}`",
        f"- Command: `{provenance.get('command')}`",
        f"- Timestamp UTC: `{provenance.get('timestamp_utc')}`",
        f"- Finite audit: `{'pass' if finite.get('all_finite') else 'fail'}`",
    ]
    if finite.get("non_finite_paths"):
        lines.append(f"- Non-finite paths: `{finite.get('non_finite_paths')}`")

    summary = _payload_summary(payload if isinstance(payload, Mapping) else {})
    if summary:
        lines.extend(["", "## Summary", ""])
        lines.extend(summary)

    if warnings:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {item}" for item in warnings)
    if errors:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {item}" for item in errors)

    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            CLAIM_BOUNDARY,
            "",
            "## Equation Notes",
            "",
        ]
    )
    lines.extend(_equation_notes(data))
    explanation = explanation_for_result(data)
    lines.extend(
        [
            "",
            "## Explanation",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in explanation["interpretation"])
    lines.extend(
        [
            "",
            "## What This Supports",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in explanation["what_this_supports"])
    lines.extend(
        [
            "",
            "## What Would Break It",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in explanation["what_would_break_it"])
    lines.extend(
        [
            "",
            "## Citation",
            "",
            RUNTIME_CITATION,
            "",
            "## Full Result JSON",
            "",
            "```json",
            json.dumps(data, indent=2, sort_keys=True, allow_nan=False),
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def result_to_html(result: Mapping[str, Any], *, title: str = "CDFD Runtime Report") -> str:
    """Render a self-contained HTML report with the same content as Markdown."""
    markdown = result_to_markdown(result, title=title)
    escaped = html.escape(markdown)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; background: #f6f7f9; color: #111827; }}
    main {{ max-width: 980px; margin: 0 auto; padding: 32px 20px 48px; }}
    pre {{ white-space: pre-wrap; background: #111827; color: #f9fafb; padding: 18px; border-radius: 8px; overflow-x: auto; }}
  </style>
</head>
<body>
<main>
<pre>{escaped}</pre>
</main>
</body>
</html>
"""


def write_report(
    result: Mapping[str, Any],
    path: str | Path,
    *,
    fmt: str = "markdown",
    title: str = "CDFD Runtime Report",
) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "markdown":
        out.write_text(result_to_markdown(result, title=title))
    elif fmt == "html":
        out.write_text(result_to_html(result, title=title))
    elif fmt == "pdf":
        write_pdf_report(result, out, title=title)
    elif fmt == "json":
        out.write_text(json.dumps(clean_json(dict(result)), indent=2, sort_keys=True, allow_nan=False) + "\n")
    else:
        raise ValueError(f"unsupported report format: {fmt}")
    return out


def write_pdf_report(
    result: Mapping[str, Any],
    path: str | Path,
    *,
    title: str = "CDFD Runtime Report",
) -> Path:
    """Write a text-first PDF report without adding a new dependency."""
    import os
    import tempfile

    mpl_config = Path(tempfile.gettempdir()) / "cdfd-matplotlib"
    mpl_config.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(mpl_config))

    from matplotlib.backends.backend_pdf import PdfPages
    import matplotlib.pyplot as plt

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    markdown = result_to_markdown(result, title=title)
    wrapped: list[str] = []
    for line in markdown.splitlines():
        if not line:
            wrapped.append("")
            continue
        wrapped.extend(textwrap.wrap(line, width=98, replace_whitespace=False) or [""])

    page_lines = 48
    with PdfPages(out) as pdf:
        for start in range(0, len(wrapped), page_lines):
            fig = plt.figure(figsize=(8.5, 11))
            fig.text(
                0.06,
                0.96,
                "\n".join(wrapped[start : start + page_lines]),
                va="top",
                ha="left",
                family="monospace",
                fontsize=8,
            )
            fig.patch.set_facecolor("white")
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)
    return out
