"""Shared CDFL editor, CLI, and web tooling helpers."""
from __future__ import annotations

import re
from typing import Any

from dsl.ast_nodes import Node
from dsl.lexer import tokenize
from dsl.parser import ParseError, parse


CANONICAL_HEAT_FLOW = """SET domain: physics

SYSTEM HeatChannel {
  flux: 1.2
  constraint: 0.9
  state: psi
}

RULE HeatOverload {
  IF psi > 1.1
  ACTION reduce_flux
}

RUN Engine {
  duration: 0.05
  dt: 0.01
}

OBSERVE {
  metrics: [psi]
}
"""

KEYWORDS = {
    "DEFINE",
    "SET",
    "LINK",
    "RUN",
    "SCENARIO",
    "OBSERVE",
    "SWEEP",
    "DISCOVER",
    "PATIENT",
    "APPLY",
    "TO",
    "MODIFY",
    "ANALYZE",
    "BIFURCATE",
    "EMERGE",
    "ATTRACTOR",
    "INFOFLOW",
    "VACUUM",
    "KNOT",
    "SPAWN",
    "RESOLVE",
    "SPECTRUM",
    "SYSTEM",
    "RULE",
    "IF",
    "ACTION",
}
TYPES = {"Engine", "Field", "Constraint", "Vacuum", "Knot", "Spectrum"}
TOP_LEVEL = KEYWORDS | TYPES
NAMED_BLOCKS = {"SYSTEM", "RULE", "SCENARIO", "PATIENT"}
BLOCK_KEYWORDS = {
    "DEFINE",
    "PATIENT",
    "SCENARIO",
    "RUN",
    "OBSERVE",
    "DISCOVER",
    "ANALYZE",
    "BIFURCATE",
    "EMERGE",
    "ATTRACTOR",
    "INFOFLOW",
    "SPAWN",
    "SYSTEM",
    "RULE",
    "MODIFY",
}

IDENTIFIER_RE = r"[A-Za-z_\u0370-\u03FF][\w.\u0370-\u03FF]*"


def strip_comment(line: str) -> str:
    """Remove a CDFL hash comment while preserving hashes inside strings."""
    quote = None
    for index, char in enumerate(line):
        if char in {"'", '"'} and (index == 0 or line[index - 1] != "\\"):
            quote = None if quote == char else quote or char
            continue
        if char == "#" and quote is None:
            return line[:index]
    return line


def cdfl_diagnostics(text: str) -> list[dict[str, Any]]:
    diagnostics: list[dict[str, Any]] = []
    stack: list[dict[str, Any]] = []
    rule_depth = 0

    for line_index, raw in enumerate(text.splitlines(), start=1):
        stripped = strip_comment(raw).strip()
        if not stripped:
            continue

        depth_before = len(stack)
        first = _first_word(stripped)
        column = max(raw.find(first), 0) + 1 if first else 1

        if depth_before == 0 and first and first not in TOP_LEVEL and first != "}":
            diagnostics.append(
                _diagnostic(
                    "warning",
                    line_index,
                    column,
                    column + len(first),
                    "UNKNOWN_STATEMENT",
                    f"Unknown CDFL statement '{first}'.",
                )
            )

        if first == "SET":
            _check_set_line(diagnostics, line_index, raw, stripped)
        elif first == "RUN":
            _check_run_line(diagnostics, line_index, raw, stripped)
        elif first in NAMED_BLOCKS:
            _check_named_block_line(diagnostics, line_index, raw, stripped, first)
        elif first == "IF":
            if rule_depth == 0:
                diagnostics.append(
                    _diagnostic("info", line_index, column, column + 2, "IF_OUTSIDE_RULE", "`IF` is only meaningful inside a RULE block.")
                )
            if not re.search(rf"\bIF\s+{IDENTIFIER_RE}\s*(?:>|<|>=|<=|==|!=)\s*\d+(?:\.\d+)?\b", stripped):
                diagnostics.append(
                    _diagnostic("warning", line_index, 1, max(2, len(raw) + 1), "MALFORMED_IF", "Expected rule condition like `IF psi > 1.1`.")
                )
        elif first == "ACTION" and not re.match(rf"^ACTION\s+{IDENTIFIER_RE}\s*$", stripped):
            diagnostics.append(
                _diagnostic("warning", line_index, 1, max(2, len(raw) + 1), "MALFORMED_ACTION", "Expected action line like `ACTION reduce_flux`.")
            )

        if depth_before > 0 and first and _should_look_like_key_value(first, stripped):
            diagnostics.append(
                _diagnostic(
                    "warning",
                    line_index,
                    column,
                    column + len(first),
                    "MALFORMED_KEY_VALUE",
                    "Expected `key: value` inside this CDFL block.",
                )
            )

        for event in _bracket_events(raw):
            char = event["char"]
            if char == "{":
                stack.append({"char": "{", "line": line_index, "column": event["column"], "first": first})
                if first == "RULE":
                    rule_depth += 1
            elif char == "[":
                stack.append({"char": "[", "line": line_index, "column": event["column"], "first": None})
            elif char == "}":
                opened = stack.pop() if stack else None
                if not opened or opened["char"] != "{":
                    diagnostics.append(
                        _diagnostic("error", line_index, event["column"], event["column"] + 1, "UNMATCHED_CLOSING_BRACE", "Unmatched closing brace.")
                    )
                elif opened.get("first") == "RULE":
                    rule_depth = max(0, rule_depth - 1)
            elif char == "]":
                opened = stack.pop() if stack else None
                if not opened or opened["char"] != "[":
                    diagnostics.append(
                        _diagnostic("error", line_index, event["column"], event["column"] + 1, "UNMATCHED_CLOSING_BRACKET", "Unmatched closing bracket.")
                    )

    for opened in stack:
        code = "UNCLOSED_BLOCK" if opened["char"] == "{" else "UNCLOSED_LIST"
        label = "block" if opened["char"] == "{" else "list"
        diagnostics.append(
            _diagnostic("error", opened["line"], opened["column"], opened["column"] + 1, code, f"Unclosed {label}.")
        )

    return diagnostics


def diagnostic_summary(diagnostics: list[dict[str, Any]]) -> dict[str, int]:
    summary = {"error": 0, "warning": 0, "info": 0}
    for item in diagnostics:
        severity = str(item.get("severity", "info"))
        summary[severity] = summary.get(severity, 0) + 1
    return summary


def format_cdfl_text(text: str, *, indent_size: int = 2) -> str:
    indent_unit = " " * max(0, indent_size)
    lines: list[str] = []
    depth = 0

    for raw in text.splitlines():
        original = raw.strip()
        if not original:
            lines.append("")
            continue
        starts_closing = original.startswith("}") or original.startswith("]")
        current_depth = max(0, depth - (1 if starts_closing else 0))
        lines.append(f"{indent_unit * current_depth}{original}")
        for event in _bracket_events(original):
            if event["char"] in {"{", "["}:
                depth += 1
            elif event["char"] in {"}", "]"}:
                depth = max(0, depth - 1)

    if not lines:
        return ""
    return "\n".join(lines).rstrip() + "\n"


def analyze_cdfl_text(text: str) -> dict[str, Any]:
    diagnostics = cdfl_diagnostics(text)
    try:
        tokens = tokenize(text)
        nodes = parse(tokens)
    except ParseError as exc:
        diagnostics.append(_diagnostic("error", 0, 0, 0, "PARSE_ERROR", str(exc)))
        return _analysis_payload(text, diagnostics, tokens=[], nodes=[])

    return _analysis_payload(text, diagnostics, tokens=tokens, nodes=nodes)


def summarize_nodes(nodes: list[Any]) -> list[dict[str, Any]]:
    return [_node_summary(node) for node in nodes]


def _analysis_payload(text: str, diagnostics: list[dict[str, Any]], *, tokens: list[Any], nodes: list[Any]) -> dict[str, Any]:
    summary = diagnostic_summary(diagnostics)
    return {
        "valid": summary.get("error", 0) == 0,
        "diagnostics": diagnostics,
        "diagnostic_summary": summary,
        "token_count": max(0, len(tokens) - 1) if tokens else 0,
        "node_count": len(nodes),
        "nodes": summarize_nodes(nodes),
        "formatted": format_cdfl_text(text),
    }


def _node_summary(node: Any) -> dict[str, Any]:
    attrs = {}
    for key, value in vars(node).items():
        attrs[key] = _clean_value(value)
    return {"type": type(node).__name__, "attributes": attrs}


def _clean_value(value: Any) -> Any:
    if isinstance(value, Node):
        return _node_summary(value)
    if isinstance(value, list):
        return [_clean_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _clean_value(item) for key, item in value.items()}
    return value


def _check_set_line(diagnostics: list[dict[str, Any]], line: int, raw: str, text: str) -> None:
    if not re.match(rf"^SET\s+{IDENTIFIER_RE}\s*:\s*\S+", text):
        diagnostics.append(
            _diagnostic("warning", line, 1, max(2, len(raw) + 1), "MALFORMED_SET", "Expected `SET key: value`, for example `SET domain: physics`.")
        )


def _check_run_line(diagnostics: list[dict[str, Any]], line: int, raw: str, text: str) -> None:
    if not re.match(r"^RUN\s+Engine\b", text):
        diagnostics.append(
            _diagnostic("warning", line, 1, max(2, len(raw) + 1), "MALFORMED_RUN", "The current parser expects `RUN Engine { ... }`.")
        )
    if "{" not in text:
        diagnostics.append(
            _diagnostic("warning", line, 1, max(2, len(raw) + 1), "MISSING_RUN_BLOCK", "`RUN Engine` needs a parameter block.")
        )


def _check_named_block_line(diagnostics: list[dict[str, Any]], line: int, raw: str, text: str, keyword: str) -> None:
    if not re.match(rf"^{keyword}\s+{IDENTIFIER_RE}\s*{{?", text):
        diagnostics.append(
            _diagnostic("warning", line, 1, max(2, len(raw) + 1), "MALFORMED_BLOCK", f"Expected `{keyword} Name {{ ... }}`.")
        )
    if "{" not in text:
        diagnostics.append(
            _diagnostic("warning", line, 1, max(2, len(raw) + 1), "MISSING_BLOCK_BRACE", f"{keyword} declarations need an opening block brace.")
        )


def _should_look_like_key_value(first: str, text: str) -> bool:
    if first in BLOCK_KEYWORDS or first in {"IF", "ACTION", "}"}:
        return False
    if ":" in text:
        return False
    return re.match(rf"^{IDENTIFIER_RE}\s+\S+", text) is not None


def _first_word(text: str) -> str:
    match = re.match(IDENTIFIER_RE, text)
    return match.group(0) if match else ""


def _bracket_events(line: str) -> list[dict[str, Any]]:
    events = []
    quote = None
    for index, char in enumerate(line):
        if char in {"'", '"'} and (index == 0 or line[index - 1] != "\\"):
            quote = None if quote == char else quote or char
            continue
        if char == "#" and quote is None:
            break
        if quote is None and char in "{}[]":
            events.append({"char": char, "column": index + 1})
    return events


def _diagnostic(severity: str, line: int, column: int, end_column: int, code: str, message: str) -> dict[str, Any]:
    return {
        "severity": severity,
        "line": line,
        "column": column,
        "end_column": max(column + 1, end_column),
        "code": code,
        "message": message,
    }
