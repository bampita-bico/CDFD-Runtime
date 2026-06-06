import json
from pathlib import Path

import numpy as np

import cdfd
import runtime.llm as llm_module
from dsl.cdfl_tools import CANONICAL_HEAT_FLOW, analyze_cdfl_text, format_cdfl_text
from engine.causal_graph import build_causal_graph
from runtime.diagnostics import (
    adaptive_ratio,
    aromatic_source_mix_scenario,
    best_aromatic_source_mix,
    finite_stats,
    life_number,
    operating_ratio,
    photochemical_material_status,
    write_json,
)
from runtime.decision import classify_operating_state
from runtime.artifacts import create_run_bundle
from runtime.reporting import result_to_html, result_to_markdown
from runtime.runner import (
    app_auth_status,
    cdfl_ast,
    cdfl_sample,
    compare_domain,
    doctor,
    explain_result,
    gallery,
    format_cdfl_file,
    lint_cdfl,
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


def test_paper_aligned_runtime_diagnostics_are_available():
    psi = adaptive_ratio(np.array([2.0]), np.array([4.0]), S=2.0, M_s=1.0)
    assert float(psi[0]) == 1.0
    assert operating_ratio(2.0, 4.0, s=2.0, m_s=1.0) == 1.0
    assert life_number(2.0, 0.5, 0.5, 2.0, 1.0) == 1.0
    assert finite_stats([1.0, 2.0])["all_finite"] is True


def test_part_ii_source_mix_and_endpoint_guardrails_are_available():
    best = best_aromatic_source_mix()
    assert best["scenario"] == "mixed_source_surface_trap"
    assert abs(best["functional_score"] - 0.6096551724137931) < 1e-12

    retained = aromatic_source_mix_scenario("meteoritic_seed_retained")
    assert abs(retained["retained_pool"] - 0.9750000000000001) < 1e-12

    status = photochemical_material_status()
    assert "not an origin requirement" in status["melanin_status"]


def test_runtime_info_is_cli_first():
    result = runtime_info()
    assert result["status"] == "ok"
    assert result["payload"]["primary_surface"] == "cli"
    assert result["payload"]["platform_order"][1] == "cli"
    assert "diagnostics" in result["payload"]["commands"]
    assert "cdfl" in result["payload"]["commands"]
    assert "webapp" in result["payload"]["optional_surfaces"]
    assert "vscode_extension" in result["payload"]["optional_surfaces"]
    assert result["payload"]["entrypoints"]["vscode_extension_optional"] == "tools/cdfl-vscode"


def test_runtime_guidance_is_domain_neutral():
    guidance = classify_operating_state(1.3333333333333333, domain="physics")
    assert guidance["state"] == "overloaded"
    serialized = json.dumps(guidance)
    assert "dietary" not in serialized
    assert "clinical" not in serialized


def test_part_ii_diagnostics_command_surface():
    result = part_ii_diagnostics(include_demo=False)
    assert result["status"] == "ok"
    assert result["kind"] == "part_ii_diagnostics"
    assert result["payload"]["best_aromatic_source_mix"]["scenario"] == "mixed_source_surface_trap"


def test_cli_diagnostics_main(tmp_path):
    out = tmp_path / "diag.json"
    code = cdfd.main(["diagnostics", "--no-demo", "--json", "--out", str(out)])
    assert code == 0
    data = json.loads(out.read_text())
    assert data["kind"] == "part_ii_diagnostics"
    assert data["finite_audit"]["all_finite"] is True


def test_cli_demo_source_scenario_flag():
    code = cdfd.main(
        [
            "demo",
            "origins_of_life",
            "--source-scenario",
            "mixed_source_surface_trap",
            "--steps",
            "1",
            "--nx",
            "4",
            "--ny",
            "4",
            "--json",
        ]
    )
    assert code == 0


def test_causal_graph_ignores_nonnumeric_trace_fields():
    history = [
        {"t": i, "phi": float(i), "C": float(i + 1), "psi_s": float(i) / 10.0, "regime": "balanced"}
        for i in range(8)
    ]
    graph = build_causal_graph(history, threshold=0.1)
    assert "regime" not in graph.nodes
    assert {"phi", "C", "psi_s"} <= set(graph.nodes)


def test_runner_domain_demo_returns_enveloped_result():
    result = run_domain("physics", nx=4, ny=4, steps=1)
    assert result["status"] == "ok"
    assert result["kind"] == "domain_demo"
    assert result["payload"]["domain"] == "physics"
    assert result["finite_audit"]["all_finite"] is True


def test_origins_of_life_demo_exposes_source_mix_guardrail():
    result = run_domain(
        "origins_of_life",
        {"source_scenario": "mixed_source_surface_trap"},
        nx=4,
        ny=4,
        steps=1,
    )
    assert result["status"] == "ok"
    diagnostics = result["payload"]["domain_diagnostics"]
    assert diagnostics["aromatic_source_mix"]["scenario"] == "mixed_source_surface_trap"
    assert "not itself a Life Number gate" in diagnostics["life_number_guardrail"]
    assert "eumelanin" in result["payload"]["interpretation"]


def test_runner_validates_and_runs_cdfl(tmp_path):
    model = tmp_path / "model.cdfl"
    model.write_text(
        """
SET domain: physics
SYSTEM Channel {
  flux: 1.2
  constraint: 0.9
  state: psi
}
RUN Engine {
  duration: 0.02
  dt: 0.01
}
OBSERVE {
  metrics: [psi]
}
"""
    )

    validation = validate_cdfl(model)
    assert validation["status"] == "ok"
    assert validation["payload"]["valid"] is True
    assert validation["payload"]["node_count"] == 4
    assert validation["payload"]["diagnostic_summary"]["error"] == 0

    run = run_cdfl(model, nx=4, ny=4)
    assert run["status"] == "ok"
    assert run["kind"] == "cdfl_run"
    assert run["payload"]["node_count"] == 4
    assert run["finite_audit"]["all_finite"] is True
    system = run["payload"]["results"][0]
    assert "runtime_guidance" in system
    assert not [key for key in system if key.startswith("reco")]


def test_cdfl_tooling_lint_format_ast_sample_and_cli(tmp_path):
    model = tmp_path / "model.cdfl"
    model.write_text(CANONICAL_HEAT_FLOW)

    analysis = analyze_cdfl_text(model.read_text())
    assert analysis["valid"] is True
    assert analysis["node_count"] == 5
    assert analysis["diagnostic_summary"] == {"error": 0, "warning": 0, "info": 0}

    lint = lint_cdfl(model)
    assert lint["status"] == "ok"
    assert lint["kind"] == "cdfl_lint"
    assert lint["payload"]["diagnostic_summary"]["error"] == 0

    ast = cdfl_ast(model)
    assert ast["status"] == "ok"
    assert ast["payload"]["nodes"][1]["type"] == "SystemNode"
    assert ast["payload"]["nodes"][1]["attributes"]["name"] == "HeatChannel"

    messy = tmp_path / "messy.cdfl"
    messy.write_text("SET domain: physics\nSYSTEM Messy {\nflux: 1.2\nconstraint: 0.9\nstate: psi\n}\n")
    formatted_text = format_cdfl_text(messy.read_text())
    assert "  flux: 1.2" in formatted_text

    formatted_out = tmp_path / "formatted.cdfl"
    formatted = format_cdfl_file(messy, output_path=formatted_out)
    assert formatted["status"] == "ok"
    assert formatted["payload"]["changed"] is True
    assert "  state: psi" in formatted_out.read_text()

    sample_out = tmp_path / "sample.cdfl"
    sample = cdfl_sample(output_path=sample_out)
    assert sample["status"] == "ok"
    assert sample_out.read_text() == CANONICAL_HEAT_FLOW

    bad = tmp_path / "bad.cdfl"
    bad.write_text("RUN Engine {\n  duration: 0.05\n")
    bad_lint = lint_cdfl(bad)
    assert bad_lint["status"] == "error"
    assert bad_lint["payload"]["diagnostic_summary"]["error"] == 1

    lint_json = tmp_path / "lint.json"
    assert cdfd.main(["cdfl", "lint", str(model), "--json", "--out", str(lint_json)]) == 0
    assert json.loads(lint_json.read_text())["kind"] == "cdfl_lint"

    cli_formatted = tmp_path / "cli-formatted.cdfl"
    assert cdfd.main(["cdfl", "format", str(messy), "--out", str(cli_formatted), "--json"]) == 0
    assert "  constraint: 0.9" in cli_formatted.read_text()

    assert cdfd.main(["cdfl", "ast", str(model), "--json"]) == 0
    assert cdfd.main(["cdfl", "sample", "--out", str(tmp_path / "cli-sample.cdfl"), "--json"]) == 0


def test_cli_main_can_write_json(tmp_path):
    output = tmp_path / "domains.json"
    code = cdfd.main(["domains", "--json", "--out", str(output)])
    assert code == 0
    data = json.loads(output.read_text())
    assert data["status"] == "ok"
    assert data["payload"]["count"] > 0


def test_llm_provider_key_status_does_not_print_keys(monkeypatch, tmp_path):
    key_file = tmp_path / "provider_key.txt"
    key_file.write_text("provider-secret\n")

    result = app_auth_status(api_key_file=key_file, provider="openai", model="test-model")
    assert result["status"] == "ok"
    assert result["kind"] == "llm_provider_status"
    assert result["payload"]["key_configured"] is True
    assert result["payload"]["key_source"] == "file"
    assert "provider-secret" not in json.dumps(result)
    assert "key_fingerprint" not in result["payload"]

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("CDFD_LLM_API_KEY", raising=False)
    missing = llm_provider_status(provider="openai", model="test-model", key_env="CDFD_TEST_MISSING_KEY")
    assert missing["status"] == "ok"
    assert missing["payload"]["key_configured"] is False
    assert missing["warnings"]

    unsupported = llm_provider_status(provider="unknown-provider", api_key="provider-secret")
    assert unsupported["status"] == "error"
    assert "provider-secret" not in json.dumps(unsupported)


def test_llm_provider_inventory_lists_supported_shapes_without_calls(monkeypatch):
    for profile in llm_module.PROVIDER_PROFILES.values():
        for env_name in profile["key_envs"]:
            monkeypatch.delenv(env_name, raising=False)
    for provider in llm_module.SUPPORTED_PROVIDERS:
        prefix = provider.upper().replace("-", "_")
        monkeypatch.delenv(f"{prefix}_MODEL", raising=False)
        monkeypatch.delenv(f"{prefix}_BASE_URL", raising=False)
    monkeypatch.delenv("CDFD_LLM_MODEL", raising=False)
    monkeypatch.delenv("CDFD_LLM_BASE_URL", raising=False)

    result = llm_provider_inventory()

    assert result["status"] == "ok"
    providers = {row["provider"]: row for row in result["payload"]["providers"]}
    assert {"openai", "anthropic", "gemini", "mistral", "groq", "openrouter", "ollama"} <= set(providers)
    assert providers["gemini"]["provider_mode"] == "gemini-generate-content"
    assert providers["ollama"]["key_required"] is False
    assert result["payload"]["call_mode"] == "inventory only; no provider call made"


def test_llm_explain_requires_runtime_model_without_calling_provider(monkeypatch, tmp_path):
    src = tmp_path / "result.json"
    write_json(src, run_domain("physics", nx=4, ny=4, steps=1))

    def fail_post(*args, **kwargs):
        raise AssertionError("provider call should not happen without a model")

    monkeypatch.setattr(llm_module.requests, "post", fail_post)
    result = llm_explain_result(src, provider="openai", api_key="provider-secret")

    assert result["status"] == "error"
    assert "No model supplied" in result["errors"][0]
    assert "provider-secret" not in json.dumps(result)


def test_llm_explain_dry_run_builds_prompt_without_provider_call(monkeypatch, tmp_path):
    src = tmp_path / "result.json"
    write_json(src, run_domain("physics", nx=4, ny=4, steps=1))

    def fail_post(*args, **kwargs):
        raise AssertionError("dry-run must not call provider")

    monkeypatch.setattr(llm_module.requests, "post", fail_post)
    result = llm_explain_result(
        src,
        provider="openai",
        model="test-model",
        api_key="provider-secret",
        question="Explain for research.",
        dry_run=True,
        prompt_preview_chars=500,
    )

    assert result["status"] == "ok"
    assert result["payload"]["dry_run"] is True
    assert result["payload"]["provider_call_made"] is False
    assert result["payload"]["prompt_template_version"] == "cdfd-llm-explain-v1"
    assert "CDFD context" in result["payload"]["prompt_audit"]["prompt_preview"]
    assert "provider-secret" not in json.dumps(result)


def test_llm_explain_result_calls_openai_compatible_provider_without_leaking_key(monkeypatch, tmp_path):
    src = tmp_path / "result.json"
    write_json(src, run_domain("physics", nx=4, ny=4, steps=1))
    captured = {}

    class FakeResponse:
        status_code = 200
        text = "{}"

        def raise_for_status(self):
            return None

        def json(self):
            return {
                "id": "chatcmpl-test",
                "choices": [{"message": {"content": "Research interpretation with claim boundaries."}}],
                "usage": {"prompt_tokens": 12, "completion_tokens": 7, "total_tokens": 19},
            }

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(llm_module.requests, "post", fake_post)
    result = llm_explain_result(
        src,
        provider="openai",
        model="test-model",
        base_url="https://provider.test/v1",
        api_key="provider-secret",
        question="Explain for research.",
    )

    assert result["status"] == "ok"
    assert result["kind"] == "llm_research_explanation"
    assert result["payload"]["response_text"] == "Research interpretation with claim boundaries."
    assert result["payload"]["secrets_printed"] is False
    assert "provider-secret" not in json.dumps(result)
    assert captured["url"] == "https://provider.test/v1/chat/completions"
    assert captured["headers"]["Authorization"] == "Bearer provider-secret"
    assert captured["json"]["model"] == "test-model"
    assert captured["json"]["messages"][0]["role"] == "system"
    assert "CDFD context" in captured["json"]["messages"][1]["content"]


def test_llm_explain_result_calls_anthropic_provider_without_leaking_key(monkeypatch, tmp_path):
    src = tmp_path / "result.json"
    write_json(src, run_domain("physics", nx=4, ny=4, steps=1))
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "id": "msg-test",
                "content": [{"type": "text", "text": "Anthropic research note."}],
                "usage": {"input_tokens": 11, "output_tokens": 4},
            }

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(llm_module.requests, "post", fake_post)
    result = llm_explain_result(
        src,
        provider="anthropic",
        model="test-anthropic-model",
        base_url="https://anthropic.test/v1",
        api_key="provider-secret",
        question="Explain for research.",
    )

    assert result["status"] == "ok"
    assert result["payload"]["response_text"] == "Anthropic research note."
    assert result["payload"]["provider"] == "anthropic"
    assert "provider-secret" not in json.dumps(result)
    assert captured["url"] == "https://anthropic.test/v1/messages"
    assert captured["headers"]["x-api-key"] == "provider-secret"
    assert captured["json"]["model"] == "test-anthropic-model"
    assert captured["json"]["messages"][0]["role"] == "user"


def test_llm_explain_result_calls_gemini_provider_without_leaking_key(monkeypatch, tmp_path):
    src = tmp_path / "result.json"
    write_json(src, run_domain("physics", nx=4, ny=4, steps=1))
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "responseId": "gemini-test-response",
                "candidates": [
                    {"content": {"parts": [{"text": "Gemini research interpretation."}]}}
                ],
                "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 5},
            }

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(llm_module.requests, "post", fake_post)
    result = llm_explain_result(
        src,
        provider="gemini",
        model="gemini-test-model",
        api_key="provider-secret",
        question="Explain for research.",
    )

    assert result["status"] == "ok"
    assert result["payload"]["response_text"] == "Gemini research interpretation."
    assert result["payload"]["provider_mode"] == "gemini-generate-content"
    assert "provider-secret" not in json.dumps(result)
    assert captured["url"] == "https://generativelanguage.googleapis.com/v1beta/models/gemini-test-model:generateContent"
    assert captured["headers"]["x-goog-api-key"] == "provider-secret"
    assert captured["json"]["generationConfig"]["maxOutputTokens"] == 900
    assert captured["json"]["systemInstruction"]["parts"][0]["text"]


def test_llm_provider_errors_redact_keys(monkeypatch, tmp_path):
    src = tmp_path / "result.json"
    write_json(src, run_domain("physics", nx=4, ny=4, steps=1))

    def fake_post(*args, **kwargs):
        raise llm_module.requests.RequestException("provider-secret appeared in provider failure")

    monkeypatch.setattr(llm_module.requests, "post", fake_post)
    result = llm_explain_result(
        src,
        provider="openai",
        model="test-model",
        api_key="provider-secret",
    )

    assert result["status"] == "error"
    assert "provider-secret" not in json.dumps(result)
    assert "[REDACTED]" in result["errors"][0]


def test_llm_provider_error_language_is_friendly(monkeypatch, tmp_path):
    src = tmp_path / "result.json"
    write_json(src, run_domain("physics", nx=4, ny=4, steps=1))

    def run_with_exception(exc):
        def fake_post(*args, **kwargs):
            raise exc

        monkeypatch.setattr(llm_module.requests, "post", fake_post)
        return llm_explain_result(
            src,
            provider="openai",
            model="test-model",
            api_key="provider-secret",
        )

    timeout = run_with_exception(llm_module.requests.Timeout("provider-secret timed out"))
    assert timeout["status"] == "error"
    assert timeout["errors"] == ["Provider request timed out."]

    auth_error = llm_module.requests.HTTPError("provider-secret was rejected")
    auth_error.response = type("Response", (), {"status_code": 401})()
    auth = run_with_exception(auth_error)
    assert auth["status"] == "error"
    assert "Provider authentication failed (401)" in auth["errors"][0]
    assert "provider-secret" not in json.dumps(auth)

    rate_error = llm_module.requests.HTTPError("provider-secret was rate limited")
    rate_error.response = type("Response", (), {"status_code": 429})()
    rate = run_with_exception(rate_error)
    assert rate["status"] == "error"
    assert "Provider rate limit reached (429)" in rate["errors"][0]
    assert "provider-secret" not in json.dumps(rate)


def test_llm_malformed_provider_response_is_error(monkeypatch, tmp_path):
    src = tmp_path / "result.json"
    write_json(src, run_domain("physics", nx=4, ny=4, steps=1))

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {}}]}

    monkeypatch.setattr(llm_module.requests, "post", lambda *args, **kwargs: FakeResponse())
    result = llm_explain_result(
        src,
        provider="openai",
        model="test-model",
        api_key="provider-secret",
    )

    assert result["status"] == "error"
    assert "Malformed provider response" in result["errors"][0]
    assert "provider-secret" not in json.dumps(result)


def test_llm_redaction_covers_prompts_reports_and_run_bundles(monkeypatch, tmp_path):
    secret = "provider-secret"
    source_result = run_domain("physics", nx=4, ny=4, steps=1)
    source_result["payload"]["debug_note"] = f"input accidentally had {secret}"
    src = tmp_path / "result.json"
    write_json(src, source_result)

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "id": f"chatcmpl-{secret}",
                "choices": [{"message": {"content": f"Provider echoed {secret}."}}],
                "usage": {"prompt_tokens": 12, "completion_tokens": 7, "total_tokens": 19},
            }

    def fake_post(url, headers=None, json=None, timeout=None):
        assert secret not in json["messages"][1]["content"]
        assert "[REDACTED]" in json["messages"][1]["content"]
        return FakeResponse()

    monkeypatch.setattr(llm_module.requests, "post", fake_post)
    result = llm_explain_result(
        src,
        provider="openai",
        model="test-model",
        base_url="https://provider.test/v1",
        api_key=secret,
        question=f"Explain without leaking {secret}.",
    )

    assert result["status"] == "ok"
    assert secret not in json.dumps(result)
    assert "[REDACTED]" in json.dumps(result)
    assert secret not in result_to_markdown(result)
    assert secret not in result_to_html(result)

    bundle = create_run_bundle(result, root=tmp_path / "runs", label="llm-redaction")
    paths = [
        Path(bundle["result"]),
        Path(bundle["reports"]["markdown"]),
        Path(bundle["reports"]["html"]),
        Path(bundle["manifest"]),
        Path(bundle["artifacts"]["llm_interpretation_json"]),
        Path(bundle["artifacts"]["llm_interpretation_markdown"]),
    ]
    for path in paths:
        assert secret not in path.read_text()

    llm_artifact = json.loads(Path(bundle["artifacts"]["llm_interpretation_json"]).read_text())
    assert llm_artifact["artifact_boundary"].startswith("Interpretive LLM output only")
    assert llm_artifact["temperature"] == 0.2
    assert llm_artifact["max_tokens"] == 900
    assert llm_artifact["context_chars"] > 0


def test_doctor_gallery_and_compare_surfaces_are_enveloped():
    doctor_result = doctor()
    assert doctor_result["status"] == "ok"
    assert doctor_result["kind"] == "runtime_doctor"
    assert doctor_result["payload"]["summary"]["errors"] == 0

    gallery_result = gallery(nx=4, ny=4, steps=1, include_cdfl=False)
    assert gallery_result["status"] == "ok"
    domains = {row.get("domain") for row in gallery_result["payload"]["highlights"]}
    assert {"physics", "origins_of_life", "medicine", "networks", "climate", "economics"} <= domains
    assert "VOS" in gallery_result["payload"]["vos_preview"]["boundary"]

    compare_result = compare_domain(
        "origins_of_life",
        ["mixed_source_surface_trap", "meteoritic_seed_retained"],
        nx=4,
        ny=4,
        steps=1,
    )
    assert compare_result["status"] == "ok"
    ranked = compare_result["payload"]["ranked"]
    assert ranked[0]["scenario"] == "mixed_source_surface_trap"
    assert ranked[0]["score"] >= ranked[1]["score"]


def test_run_bundles_reports_and_explanations(tmp_path):
    result = run_domain("physics", nx=4, ny=4, steps=1)
    src = tmp_path / "result.json"
    write_json(src, result)

    bundle = create_run_bundle(result, root=tmp_path / "runs", label="physics")
    assert Path(bundle["manifest"]).exists()
    assert Path(bundle["result"]).exists()
    assert Path(bundle["reports"]["markdown"]).exists()
    assert Path(bundle["reports"]["html"]).exists()
    assert Path(bundle["plots_dir"]).is_dir()
    assert bundle["command"] == "cdfd demo physics"

    md = tmp_path / "report.md"
    html = tmp_path / "report.html"
    pdf = tmp_path / "report.pdf"
    assert report_result(src, output_path=md, fmt="markdown")["status"] == "ok"
    assert report_result(src, output_path=html, fmt="html")["status"] == "ok"
    assert report_result(src, output_path=pdf, fmt="pdf")["status"] == "ok"
    assert "Claim Boundary" in md.read_text()
    assert html.read_text().startswith("<!doctype html>")
    assert pdf.exists() and pdf.stat().st_size > 0

    explanation = tmp_path / "explain.md"
    explain = explain_result(src, output_path=explanation, fmt="markdown")
    assert explain["status"] == "ok"
    text = explanation.read_text()
    assert "Psi_s = (Phi / C) S M_s" in text
    assert "not empirical proof" in text


def test_llm_run_bundle_writes_separate_interpretation_artifacts(monkeypatch, tmp_path):
    src = tmp_path / "result.json"
    write_json(src, run_domain("physics", nx=4, ny=4, steps=1))

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "id": "chatcmpl-test",
                "choices": [{"message": {"content": "Saved research interpretation."}}],
                "usage": {"prompt_tokens": 12, "completion_tokens": 7, "total_tokens": 19},
            }

    monkeypatch.setattr(llm_module.requests, "post", lambda *args, **kwargs: FakeResponse())
    result = llm_explain_result(
        src,
        provider="openai",
        model="test-model",
        base_url="https://provider.test/v1",
        api_key="provider-secret",
    )

    bundle = create_run_bundle(result, root=tmp_path / "runs", label="llm")
    artifacts = bundle["artifacts"]
    llm_json = Path(artifacts["llm_interpretation_json"])
    llm_md = Path(artifacts["llm_interpretation_markdown"])

    assert llm_json.exists()
    assert llm_md.exists()
    assert json.loads(llm_json.read_text())["response_text"] == "Saved research interpretation."
    assert "Saved research interpretation." in llm_md.read_text()
    assert "provider-secret" not in json.dumps(bundle)
    assert "provider-secret" not in llm_json.read_text()
    assert "provider-secret" not in llm_md.read_text()


def test_cli_new_commands_main(tmp_path):
    run_out = tmp_path / "demo.json"
    code = cdfd.main(
        [
            "demo",
            "physics",
            "--steps",
            "1",
            "--nx",
            "4",
            "--ny",
            "4",
            "--format",
            "json",
            "--out",
            str(run_out),
        ]
    )
    assert code == 0
    assert json.loads(run_out.read_text())["kind"] == "domain_demo"

    compare_out = tmp_path / "compare.json"
    code = cdfd.main(
        [
            "compare",
            "origins_of_life",
            "--scenarios",
            "mixed_source_surface_trap",
            "meteoritic_seed_retained",
            "--json",
            "--out",
            str(compare_out),
        ]
    )
    assert code == 0
    assert json.loads(compare_out.read_text())["kind"] == "runtime_compare"

    report_out = tmp_path / "report.md"
    assert cdfd.main(["report", str(run_out), "--format", "markdown", "--out", str(report_out)]) == 0
    assert "CDFD Runtime Report" in report_out.read_text()

    explain_out = tmp_path / "explain.md"
    assert cdfd.main(["explain", str(run_out), "--format", "markdown", "--out", str(explain_out)]) == 0
    assert "Claim Boundary" in explain_out.read_text()

    llm_status_out = tmp_path / "llm-status.json"
    assert (
        cdfd.main(
            [
                "llm",
                "status",
                "--provider",
                "openai",
                "--model",
                "test-model",
                "--key-env",
                "CDFD_TEST_MISSING_KEY",
                "--json",
                "--out",
                str(llm_status_out),
            ]
        )
        == 0
    )
    assert json.loads(llm_status_out.read_text())["kind"] == "llm_provider_status"

    llm_providers_out = tmp_path / "llm-providers.json"
    assert cdfd.main(["llm", "providers", "--json", "--out", str(llm_providers_out)]) == 0
    providers = json.loads(llm_providers_out.read_text())
    assert providers["kind"] == "llm_provider_inventory"
    assert providers["payload"]["provider_count"] >= 8
