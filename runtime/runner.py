"""Command backend for the CDFD CLI and future web interfaces."""
from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import Any

from domains.demo_runner import run_domain_demo
from domains.registry import DomainRegistry
from dsl.executor import Executor
from dsl.lexer import tokenize
from dsl.parser import ParseError, parse
from runtime.diagnostics import clean_json, result_envelope, write_json


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
            "cli_status": "available",
            "domain_count": len(domains),
            "entrypoints": {
                "cli": "python cdfd.py",
                "legacy_domain_cli": "python -m domains",
                "webapp": "python -m webapp.run_server",
            },
            "app_boundary": {
                "api_key_check": "python cdfd.py auth",
                "allowed_keys_env": "CDFD_RUNTIME_API_KEYS",
                "caller_key_env": "CDFD_APP_API_KEY",
                "llm_layer": "applications only; not inside the runtime engine",
                "vos": "Vacuum OS orchestration layer above CDFD Runtime",
            },
            "core_surfaces": [
                "engine",
                "domains",
                "dsl",
                "runtime",
                "validation",
                "discovery",
                "webapp",
            ],
        },
    )


def _key_fingerprint(secret: str) -> str:
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()[:12]


def _split_keys(raw: str | None) -> list[str]:
    if not raw:
        return []
    normalized = raw.replace("\n", ",")
    return [item.strip() for item in normalized.split(",") if item.strip()]


def _load_app_key(
    api_key: str | None = None,
    api_key_file: str | Path | None = None,
    *,
    key_env: str = "CDFD_APP_API_KEY",
) -> tuple[str | None, str | None]:
    if api_key_file:
        return Path(api_key_file).read_text().strip(), "file"
    if api_key:
        return api_key.strip(), "argument"
    env_value = os.environ.get(key_env)
    if env_value:
        return env_value.strip(), f"env:{key_env}"
    return None, None


def app_auth_status(
    *,
    api_key: str | None = None,
    api_key_file: str | Path | None = None,
    key_env: str = "CDFD_APP_API_KEY",
    allowed_env: str = "CDFD_RUNTIME_API_KEYS",
) -> dict[str, Any]:
    """Validate an app API key without exposing the secret in runtime output."""
    try:
        supplied_key, key_source = _load_app_key(api_key, api_key_file, key_env=key_env)
    except OSError as exc:
        return result_envelope(
            "app_auth",
            "cdfd auth",
            {"key_supplied": False, "accepted": False, "key_source": "file"},
            status="error",
            errors=[str(exc)],
        )

    allowed = _split_keys(os.environ.get(allowed_env))
    payload: dict[str, Any] = {
        "auth_configured": bool(allowed),
        "allowed_env": allowed_env,
        "key_env": key_env,
        "key_supplied": bool(supplied_key),
        "key_source": key_source,
        "accepted": False,
        "llm_boundary": "LLM providers and their keys belong in apps/VOS, not in CDFD Runtime.",
    }
    if supplied_key:
        payload["key_fingerprint"] = _key_fingerprint(supplied_key)

    if not allowed:
        return result_envelope(
            "app_auth",
            "cdfd auth",
            payload,
            warnings=[
                f"No app-key allowlist configured in {allowed_env}; runtime command execution is not gated."
            ],
        )

    if not supplied_key:
        return result_envelope(
            "app_auth",
            "cdfd auth",
            payload,
            status="error",
            errors=["No app API key supplied."],
        )

    if any(hmac.compare_digest(supplied_key, candidate) for candidate in allowed):
        payload["accepted"] = True
        return result_envelope("app_auth", "cdfd auth", payload)

    return result_envelope(
        "app_auth",
        "cdfd auth",
        payload,
        status="error",
        errors=["App API key rejected."],
    )


def run_domain(
    domain: str,
    payload: dict[str, Any] | None = None,
    *,
    nx: int = 16,
    ny: int = 16,
    steps: int = 24,
    dt: float | None = None,
) -> dict[str, Any]:
    try:
        result = run_domain_demo(domain, payload or {}, nx=nx, ny=ny, steps=steps, dt=dt)
        return result_envelope("domain_demo", f"cdfd demo {domain}", result)
    except Exception as exc:
        return result_envelope(
            "domain_demo",
            f"cdfd demo {domain}",
            {"domain": domain},
            status="error",
            errors=[str(exc)],
        )


def _read_cdfl(path: str | Path) -> str:
    return Path(path).read_text()


def compile_cdfl(path: str | Path) -> tuple[list[Any], list[Any]]:
    code = _read_cdfl(path)
    tokens = tokenize(code)
    nodes = parse(tokens)
    return tokens, nodes


def validate_cdfl(path: str | Path) -> dict[str, Any]:
    model_path = Path(path)
    try:
        tokens, nodes = compile_cdfl(model_path)
        token_count = max(0, len(tokens) - 1)
        return result_envelope(
            "cdfl_validation",
            f"cdfd validate {model_path}",
            {
                "file": str(model_path),
                "valid": True,
                "token_count": token_count,
                "node_count": len(nodes),
                "nodes": [type(node).__name__ for node in nodes],
            },
        )
    except (OSError, ParseError, Exception) as exc:
        return result_envelope(
            "cdfl_validation",
            f"cdfd validate {model_path}",
            {"file": str(model_path), "valid": False},
            status="error",
            errors=[str(exc)],
        )


def run_cdfl(path: str | Path, *, nx: int = 16, ny: int = 16) -> dict[str, Any]:
    model_path = Path(path)
    try:
        _tokens, nodes = compile_cdfl(model_path)
        executor = Executor(nx=nx, ny=ny)
        results = executor.execute(nodes)
        return result_envelope(
            "cdfl_run",
            f"cdfd run {model_path}",
            {
                "file": str(model_path),
                "nx": nx,
                "ny": ny,
                "node_count": len(nodes),
                "results": clean_json(results),
            },
        )
    except (OSError, ParseError, Exception) as exc:
        return result_envelope(
            "cdfl_run",
            f"cdfd run {model_path}",
            {"file": str(model_path), "nx": nx, "ny": ny},
            status="error",
            errors=[str(exc)],
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
