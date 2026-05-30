"""Optional LLM provider calls for research interpretation above CDFD Runtime."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

from runtime.diagnostics import clean_json, result_envelope
from runtime.reporting import explanation_for_result, explanation_to_markdown


DEFAULT_PROVIDER = "openai"
PROMPT_TEMPLATE_VERSION = "cdfd-llm-explain-v1"
PROVIDER_PROFILES: dict[str, dict[str, Any]] = {
    "openai": {
        "mode": "openai-chat",
        "default_base_url": "https://api.openai.com/v1",
        "key_envs": ("OPENAI_API_KEY", "CDFD_LLM_API_KEY"),
        "key_required": True,
        "description": "OpenAI Chat Completions-compatible endpoint.",
    },
    "openai-compatible": {
        "mode": "openai-chat",
        "default_base_url": None,
        "key_envs": ("CDFD_LLM_API_KEY", "OPENAI_API_KEY"),
        "key_required": False,
        "description": "Generic /v1/chat/completions server; set --base-url and --model.",
    },
    "anthropic": {
        "mode": "anthropic-messages",
        "default_base_url": "https://api.anthropic.com/v1",
        "key_envs": ("ANTHROPIC_API_KEY", "CDFD_LLM_API_KEY"),
        "key_required": True,
        "description": "Anthropic Messages API endpoint.",
    },
    "gemini": {
        "mode": "gemini-generate-content",
        "default_base_url": "https://generativelanguage.googleapis.com/v1beta",
        "key_envs": ("GEMINI_API_KEY", "GOOGLE_API_KEY", "CDFD_LLM_API_KEY"),
        "key_required": True,
        "description": "Google Gemini generateContent REST endpoint.",
    },
    "mistral": {
        "mode": "openai-chat",
        "default_base_url": "https://api.mistral.ai/v1",
        "key_envs": ("MISTRAL_API_KEY", "CDFD_LLM_API_KEY"),
        "key_required": True,
        "description": "Mistral chat completions endpoint.",
    },
    "groq": {
        "mode": "openai-chat",
        "default_base_url": "https://api.groq.com/openai/v1",
        "key_envs": ("GROQ_API_KEY", "CDFD_LLM_API_KEY"),
        "key_required": True,
        "description": "Groq OpenAI-compatible chat completions endpoint.",
    },
    "openrouter": {
        "mode": "openai-chat",
        "default_base_url": "https://openrouter.ai/api/v1",
        "key_envs": ("OPENROUTER_API_KEY", "CDFD_LLM_API_KEY"),
        "key_required": True,
        "description": "OpenRouter OpenAI-compatible chat completions endpoint.",
    },
    "ollama": {
        "mode": "openai-chat",
        "default_base_url": "http://localhost:11434/v1",
        "key_envs": ("OLLAMA_API_KEY", "CDFD_LLM_API_KEY"),
        "key_required": False,
        "description": "Local Ollama OpenAI-compatible endpoint; no key is normally required.",
    },
}
SUPPORTED_PROVIDERS = tuple(PROVIDER_PROFILES)
DEFAULT_MODELS = {provider: None for provider in SUPPORTED_PROVIDERS}
DEFAULT_BASE_URLS = {
    provider: profile["default_base_url"] for provider, profile in PROVIDER_PROFILES.items()
}
PROVIDER_KEY_ENVS = {
    provider: profile["key_envs"] for provider, profile in PROVIDER_PROFILES.items()
}

SYSTEM_PROMPT = """You are a research assistant connected to CDFD Runtime outputs.
Interpret only the supplied runtime result. Do not invent measurements, citations,
or validation status. Keep deterministic CDFD results separate from your own
interpretive text. State claim boundaries and falsification checks clearly.
Do not provide clinical advice, engineering certification, financial advice,
legal advice, or deployed safety decisions."""


def _normalized_provider(provider: str | None = None) -> str:
    return (provider or os.environ.get("CDFD_LLM_PROVIDER") or DEFAULT_PROVIDER).strip().lower()


def _provider_profile(provider: str) -> dict[str, Any] | None:
    return PROVIDER_PROFILES.get(provider)


def _provider_mode(provider: str) -> str | None:
    profile = _provider_profile(provider)
    return profile.get("mode") if profile else None


def _base_url_host(base_url: str | None) -> str | None:
    if not base_url:
        return None
    parsed = urlparse(base_url)
    return parsed.netloc or parsed.path.split("/")[0] or None


def _unsupported_provider_result(
    *,
    kind: str,
    command: str,
    provider: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body = {
        "provider": provider,
        "supported_providers": list(SUPPORTED_PROVIDERS),
        "key_configured": False,
        "key_required": True,
        "secrets_printed": False,
    }
    if payload:
        body.update(payload)
    return result_envelope(
        kind,
        command,
        body,
        status="error",
        errors=[f"Unsupported LLM provider: {provider}"],
    )


def _load_provider_key(
    *,
    provider: str,
    api_key: str | None = None,
    api_key_file: str | Path | None = None,
    key_env: str | None = None,
) -> tuple[str | None, str | None]:
    if api_key_file:
        return Path(api_key_file).read_text().strip(), "file"
    if api_key:
        return api_key.strip(), "argument"

    env_names = (key_env,) if key_env else PROVIDER_KEY_ENVS.get(provider, ("CDFD_LLM_API_KEY",))
    for env_name in env_names:
        value = os.environ.get(env_name)
        if value:
            return value.strip(), f"env:{env_name}"
    return None, None


def _redact_secret(text: str, *secrets: str | None) -> str:
    redacted = text
    for secret in secrets:
        if secret:
            redacted = redacted.replace(secret, "[REDACTED]")
    return redacted


def _redact_data(value: Any, *secrets: str | None) -> Any:
    if isinstance(value, dict):
        return {key: _redact_data(item, *secrets) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact_data(item, *secrets) for item in value]
    if isinstance(value, tuple):
        return tuple(_redact_data(item, *secrets) for item in value)
    if isinstance(value, str):
        return _redact_secret(value, *secrets)
    return value


def _provider_error(exc: Exception, api_key: str | None) -> str:
    if isinstance(exc, requests.Timeout):
        return "Provider request timed out."
    if isinstance(exc, ValueError):
        message = str(exc) or "provider returned invalid or unexpected JSON"
        if not message.startswith("Malformed provider response:"):
            message = f"Malformed provider response: {message}"
        return _redact_secret(message, api_key)
    if isinstance(exc, requests.HTTPError):
        response = getattr(exc, "response", None)
        status = getattr(response, "status_code", None)
        if status in {401, 403}:
            return f"Provider authentication failed ({status}). Check the provider key and model access."
        if status == 429:
            return "Provider rate limit reached (429). Retry later or use a different model/provider."
        if status:
            return _redact_secret(f"Provider HTTP error {status}: {exc}", api_key)
    if isinstance(exc, requests.RequestException):
        return _redact_secret(f"Provider request failed: {exc}", api_key)
    return _redact_secret(str(exc), api_key)


def _resolve_model(provider: str, model: str | None = None) -> str | None:
    return (
        model
        or os.environ.get("CDFD_LLM_MODEL")
        or os.environ.get(f"{provider.upper().replace('-', '_')}_MODEL")
        or DEFAULT_MODELS.get(provider)
    )


def _resolve_base_url(provider: str, base_url: str | None = None) -> str | None:
    return (
        base_url
        or os.environ.get("CDFD_LLM_BASE_URL")
        or os.environ.get(f"{provider.upper().replace('-', '_')}_BASE_URL")
        or DEFAULT_BASE_URLS.get(provider)
    )


def _provider_status_payload(
    *,
    provider: str,
    model: str | None,
    base_url: str | None,
    key_configured: bool,
    key_source: str | None,
) -> dict[str, Any]:
    profile = _provider_profile(provider) or {}
    return {
        "provider": provider,
        "provider_mode": profile.get("mode"),
        "supported_providers": list(SUPPORTED_PROVIDERS),
        "model": model,
        "base_url": base_url,
        "base_url_host": _base_url_host(base_url),
        "key_configured": key_configured,
        "key_required": bool(profile.get("key_required", True)),
        "key_source": key_source,
        "key_envs": list(profile.get("key_envs", ())),
        "secrets_printed": False,
        "description": profile.get("description"),
    }


def llm_provider_status(
    *,
    provider: str | None = None,
    model: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    api_key_file: str | Path | None = None,
    key_env: str | None = None,
) -> dict[str, Any]:
    """Report whether an LLM provider key is available without printing it."""
    resolved_provider = _normalized_provider(provider)
    resolved_model = _resolve_model(resolved_provider, model)
    resolved_base_url = _resolve_base_url(resolved_provider, base_url)
    if resolved_provider not in SUPPORTED_PROVIDERS:
        return _unsupported_provider_result(
            kind="llm_provider_status",
            command="cdfd llm status",
            provider=resolved_provider,
            payload={"model": resolved_model, "base_url": resolved_base_url},
        )
    try:
        key, key_source = _load_provider_key(
            provider=resolved_provider,
            api_key=api_key,
            api_key_file=api_key_file,
            key_env=key_env,
        )
    except OSError as exc:
        return result_envelope(
            "llm_provider_status",
            "cdfd llm status",
            _provider_status_payload(
                provider=resolved_provider,
                model=resolved_model,
                base_url=resolved_base_url,
                key_configured=False,
                key_source="file",
            ),
            status="error",
            errors=[str(exc)],
        )

    warnings: list[str] = []
    profile = _provider_profile(resolved_provider) or {}
    key_required = bool(profile.get("key_required", True))
    if key_required and not key:
        warnings.append(
            "No LLM provider key configured. Set one of the provider key env vars, "
            "CDFD_LLM_API_KEY, or pass --api-key-file."
        )
    if not resolved_model:
        warnings.append("Provider calls need --model or CDFD_LLM_MODEL.")
    if not resolved_base_url:
        warnings.append("No provider base URL resolved.")

    return result_envelope(
        "llm_provider_status",
        "cdfd llm status",
        {
            **_provider_status_payload(
                provider=resolved_provider,
                model=resolved_model,
                base_url=resolved_base_url,
                key_configured=bool(key),
                key_source=key_source,
            ),
            "call_mode": "status only; no provider call made",
            "boundary": "Provider calls are optional research interpretation above deterministic CDFD execution.",
        },
        warnings=warnings,
    )


def llm_provider_inventory() -> dict[str, Any]:
    """List supported LLM provider profiles without making provider calls."""
    providers: list[dict[str, Any]] = []
    for provider in SUPPORTED_PROVIDERS:
        profile = _provider_profile(provider) or {}
        key, key_source = _load_provider_key(provider=provider)
        base_url = _resolve_base_url(provider)
        model = _resolve_model(provider)
        providers.append(
            {
                **_provider_status_payload(
                    provider=provider,
                    model=model,
                    base_url=base_url,
                    key_configured=bool(key),
                    key_source=key_source,
                ),
                "call_shape": profile.get("mode"),
                "configured_for_call": bool(base_url and model and (key or not profile.get("key_required", True))),
            }
        )
    return result_envelope(
        "llm_provider_inventory",
        "cdfd llm providers",
        {
            "default_provider": DEFAULT_PROVIDER,
            "providers": providers,
            "provider_count": len(providers),
            "secrets_printed": False,
            "call_mode": "inventory only; no provider call made",
            "boundary": "Only listed provider shapes are supported directly; other LLMs need compatible endpoints or new adapters.",
        },
    )


def _compact_runtime_context(saved: dict[str, Any], *, max_context_chars: int) -> str:
    try:
        explanation = explanation_to_markdown(explanation_for_result(saved), title="Deterministic CDFD Explanation")
    except Exception:
        explanation = "Deterministic CDFD Explanation\n\nNo structured explanation could be generated."

    excerpt = {
        "kind": saved.get("kind"),
        "status": saved.get("status"),
        "finite_audit": saved.get("finite_audit"),
        "warnings": saved.get("warnings"),
        "errors": saved.get("errors"),
        "provenance": saved.get("provenance"),
        "payload": saved.get("payload"),
    }
    payload_text = json.dumps(clean_json(excerpt), indent=2, sort_keys=True, allow_nan=False)
    context = f"{explanation}\n\nRuntime JSON excerpt:\n{payload_text}"
    if len(context) <= max_context_chars:
        return context
    return context[:max_context_chars] + "\n\n[context truncated by CDFD Runtime before provider call]"


def _openai_chat_url(base_url: str) -> str:
    trimmed = base_url.rstrip("/")
    if trimmed.endswith("/chat/completions"):
        return trimmed
    return f"{trimmed}/chat/completions"


def _call_openai_compatible(
    *,
    provider: str,
    base_url: str,
    api_key: str | None,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
    timeout: float,
) -> dict[str, Any]:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    response = requests.post(
        _openai_chat_url(base_url),
        headers=headers,
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError("Malformed provider response: expected a JSON object.")
    choices = data.get("choices") or []
    text = ""
    if choices:
        message = choices[0].get("message") or {}
        text = message.get("content") or ""
    if not text:
        raise ValueError("Malformed provider response: missing chat completion message content.")
    return {
        "provider": provider,
        "model": model,
        "response_text": text,
        "usage": data.get("usage"),
        "provider_response_id": data.get("id"),
    }


def _call_anthropic(
    *,
    base_url: str,
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
    timeout: float,
) -> dict[str, Any]:
    response = requests.post(
        f"{base_url.rstrip('/')}/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError("Malformed provider response: expected a JSON object.")
    parts = []
    for item in data.get("content") or []:
        if isinstance(item, dict) and item.get("type") == "text":
            parts.append(item.get("text", ""))
    if not parts:
        raise ValueError("Malformed provider response: missing Anthropic text content.")
    return {
        "provider": "anthropic",
        "model": model,
        "response_text": "\n".join(part for part in parts if part),
        "usage": data.get("usage"),
        "provider_response_id": data.get("id"),
    }


def _gemini_generate_url(base_url: str, model: str) -> str:
    trimmed = base_url.rstrip("/")
    if trimmed.endswith(":generateContent"):
        return trimmed
    model_name = model if model.startswith("models/") else f"models/{model}"
    return f"{trimmed}/{model_name}:generateContent"


def _call_gemini(
    *,
    base_url: str,
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
    timeout: float,
) -> dict[str, Any]:
    response = requests.post(
        _gemini_generate_url(base_url, model),
        headers={
            "x-goog-api-key": api_key,
            "Content-Type": "application/json",
        },
        json={
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        },
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError("Malformed provider response: expected a JSON object.")
    parts: list[str] = []
    for candidate in data.get("candidates") or []:
        content = candidate.get("content") if isinstance(candidate, dict) else None
        for item in (content or {}).get("parts") or []:
            if isinstance(item, dict) and item.get("text"):
                parts.append(item["text"])
    if not parts:
        raise ValueError("Malformed provider response: missing Gemini text content.")
    return {
        "provider": "gemini",
        "model": model,
        "response_text": "\n".join(parts),
        "usage": data.get("usageMetadata"),
        "provider_response_id": data.get("responseId"),
    }


def _prompt_audit(
    *,
    system_prompt: str,
    user_prompt: str,
    context: str,
    preview_chars: int,
) -> dict[str, Any]:
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    preview = full_prompt[:preview_chars]
    if len(full_prompt) > preview_chars:
        preview += "\n\n[prompt preview truncated by CDFD Runtime]"
    return {
        "prompt_template_version": PROMPT_TEMPLATE_VERSION,
        "system_prompt_chars": len(system_prompt),
        "user_prompt_chars": len(user_prompt),
        "context_chars": len(context),
        "total_prompt_chars": len(full_prompt),
        "prompt_preview_chars": min(len(full_prompt), preview_chars),
        "prompt_preview": preview,
    }


def llm_explain_result(
    input_path: str | Path,
    *,
    question: str | None = None,
    provider: str | None = None,
    model: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    api_key_file: str | Path | None = None,
    key_env: str | None = None,
    system_prompt: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 900,
    timeout: float = 60.0,
    max_context_chars: int = 12000,
    dry_run: bool = False,
    prompt_preview_chars: int = 2000,
) -> dict[str, Any]:
    """Call an LLM provider to interpret a saved CDFD result for research use."""
    src = Path(input_path)
    resolved_provider = _normalized_provider(provider)
    resolved_model = _resolve_model(resolved_provider, model)
    resolved_base_url = _resolve_base_url(resolved_provider, base_url)
    profile = _provider_profile(resolved_provider) or {}
    provider_mode = profile.get("mode")
    if resolved_provider not in SUPPORTED_PROVIDERS:
        return _unsupported_provider_result(
            kind="llm_research_explanation",
            command=f"cdfd llm explain {src}",
            provider=resolved_provider,
            payload={"input": str(src), "model": resolved_model, "base_url": resolved_base_url},
        )

    try:
        saved = json.loads(src.read_text())
    except Exception as exc:
        return result_envelope(
            "llm_research_explanation",
            f"cdfd llm explain {src}",
            {"input": str(src), "provider": resolved_provider},
            status="error",
            errors=[str(exc)],
        )

    try:
        key, key_source = _load_provider_key(
            provider=resolved_provider,
            api_key=api_key,
            api_key_file=api_key_file,
            key_env=key_env,
        )
    except OSError as exc:
        return result_envelope(
            "llm_research_explanation",
            f"cdfd llm explain {src}",
            {"input": str(src), "provider": resolved_provider, "key_source": "file"},
            status="error",
            errors=[str(exc)],
        )

    payload_base = {
        **_provider_status_payload(
            provider=resolved_provider,
            model=resolved_model,
            base_url=resolved_base_url,
            key_configured=bool(key),
            key_source=key_source,
        ),
        "input": str(src),
        "key_configured": bool(key),
        "provider_call_made": False,
        "dry_run": dry_run,
        "boundary": "LLM output is interpretive research assistance, not deterministic CDFD evidence.",
    }

    context = _redact_secret(_compact_runtime_context(saved, max_context_chars=max_context_chars), key)
    prompt = _redact_secret(question or (
        "Explain this CDFD Runtime result for a research notebook. Identify what the "
        "deterministic result supports, what it does not prove, and the next "
        "falsification checks."
    ), key)
    user_prompt = f"{prompt}\n\nCDFD context:\n{context}"
    active_system_prompt = _redact_secret(system_prompt or SYSTEM_PROMPT, key)
    audit = _prompt_audit(
        system_prompt=active_system_prompt,
        user_prompt=user_prompt,
        context=context,
        preview_chars=prompt_preview_chars,
    )
    payload_base.update(
        {
            "question": prompt,
            "prompt_template_version": PROMPT_TEMPLATE_VERSION,
            "prompt_audit": _redact_data(audit, key),
            "context_chars": len(context),
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
    )

    warnings: list[str] = []
    key_required = bool(profile.get("key_required", True))
    if key_required and not key:
        warnings.append(
            "No LLM provider key supplied. Set one of the provider key env vars, "
            "CDFD_LLM_API_KEY, or pass --api-key-file."
        )
    if not resolved_base_url:
        warnings.append("No provider base URL resolved.")
    if not resolved_model:
        warnings.append("No model supplied. Use --model or CDFD_LLM_MODEL.")

    if dry_run:
        return result_envelope(
            "llm_research_explanation",
            f"cdfd llm explain {src}",
            payload_base,
            warnings=warnings,
        )

    if key_required and not key:
        return result_envelope(
            "llm_research_explanation",
            f"cdfd llm explain {src}",
            payload_base,
            status="error",
            errors=[warnings[0]],
        )
    if not resolved_base_url:
        return result_envelope(
            "llm_research_explanation",
            f"cdfd llm explain {src}",
            payload_base,
            status="error",
            errors=["No provider base URL resolved."],
        )
    if not resolved_model:
        return result_envelope(
            "llm_research_explanation",
            f"cdfd llm explain {src}",
            payload_base,
            status="error",
            errors=["No model supplied. Use --model or CDFD_LLM_MODEL."],
        )

    try:
        if provider_mode == "openai-chat":
            provider_result = _call_openai_compatible(
                provider=resolved_provider,
                base_url=resolved_base_url,
                api_key=key,
                model=resolved_model,
                system_prompt=active_system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout,
            )
        elif provider_mode == "anthropic-messages":
            provider_result = _call_anthropic(
                base_url=resolved_base_url,
                api_key=key or "",
                model=resolved_model,
                system_prompt=active_system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout,
            )
        elif provider_mode == "gemini-generate-content":
            provider_result = _call_gemini(
                base_url=resolved_base_url,
                api_key=key or "",
                model=resolved_model,
                system_prompt=active_system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout,
            )
        else:  # pragma: no cover - provider validation happens before key loading.
            return _unsupported_provider_result(
                kind="llm_research_explanation",
                command=f"cdfd llm explain {src}",
                provider=resolved_provider,
                payload=payload_base,
            )
    except Exception as exc:
        return result_envelope(
            "llm_research_explanation",
            f"cdfd llm explain {src}",
            payload_base,
            status="error",
            errors=[_provider_error(exc, key)],
        )

    provider_result = _redact_data(provider_result, key)
    payload = dict(payload_base)
    payload.update(
        {
            "question": prompt,
            "provider_call_made": True,
            "response_text": provider_result.get("response_text"),
            "usage": provider_result.get("usage"),
            "provider_response_id": provider_result.get("provider_response_id"),
        }
    )
    return result_envelope(
        "llm_research_explanation",
        f"cdfd llm explain {src}",
        payload,
    )
