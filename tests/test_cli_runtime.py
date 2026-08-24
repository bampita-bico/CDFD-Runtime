import json
from pathlib import Path

import numpy as np

import cdfd
import runtime.llm as llm_module
from dsl.cdfl_tools import CANONICAL_HEAT_FLOW, analyze_cdfl_text, format_cdfl_text
from engine.causal_graph import build_causal_graph
from runtime.diagnostics import adaptive_ratio, finite_stats, operating_ratio, write_json
from runtime.decision import classify_operating_state
from runtime.artifacts import create_run_bundle
from runtime.reporting import result_to_html, result_to_markdown
from runtime.runner import (
    app_auth_status,
    cdfl_ast,
    cdfl_sample,
    doctor,
    explain_result,
    gallery,
    format_cdfl_file,
    lint_cdfl,
    llm_explain_result,
    llm_provider_inventory,
    llm_provider_status,
    report_result,
    run_cdfl,
    runtime_info,
    validate_cdfl,
)


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_MODEL = ROOT / "examples" / "heat_flow.cdfl"


def _sample_result():
    return run_cdfl(SAMPLE_MODEL, nx=4, ny=4)


def test_generic_runtime_diagnostics_helpers():
    psi = adaptive_ratio(np.array([2.0]), np.array([4.0]), S=2.0, M_s=1.0)
    assert float(psi[0]) == 1.0
    assert operating_ratio(2.0, 4.0, s=2.0, m_s=1.0) == 1.0
    assert finite_stats([1.0, 2.0])["all_finite"] is True


def test_runtime_info_is_cli_first():
    result = runtime_info()
    assert result["status"] == "ok"
    assert result["payload"]["primary_surface"] == "cli"
    assert result["payload"]["platform_order"] == ["engine", "cli", "api", "editor"]
    assert "gallery" in result["payload"]["commands"]
    assert "cdfl" in result["payload"]["commands"]
    assert "domains" not in result["payload"]["commands"]
    assert "vscode_extension" in result["payload"]["optional_surfaces"]


def test_runtime_guidance_is_domain_neutral():
    guidance = classify_operating_state(1.3333333333333333, domain="physics")
    assert guidance["state"] == "overloaded"
    serialized = json.dumps(guidance)
    assert "dietary" not in serialized
    assert "clinical" not in serialized


def test_causal_graph_ignores_nonnumeric_trace_fields():
    history = [
        {"t": i, "phi": float(i), "C": float(i + 1), "psi_s": float(i) / 10.0, "regime": "balanced"}
        for i in range(8)
    ]
    graph = build_causal_graph(history, threshold=0.1)
    assert "regime" not in graph.nodes
    assert {"phi", "C", "psi_s"} <= set(graph.nodes)


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


def test_doctor_and_gallery_surfaces_are_enveloped():
    doctor_result = doctor()
    assert doctor_result["status"] == "ok"
    assert doctor_result["kind"] == "runtime_doctor"
    assert doctor_result["payload"]["summary"]["errors"] == 0

    gallery_result = gallery(nx=4, ny=4, steps=1, include_cdfl=True)
    assert gallery_result["status"] == "ok"
    kinds = {row.get("kind") for row in gallery_result["payload"]["highlights"]}
    assert "runtime_info" in kinds
    assert "cdfl_validation" in kinds or "cdfl_run" in kinds


def test_run_bundles_reports_and_explanations(tmp_path):
    result = _sample_result()
    src = tmp_path / "result.json"
    write_json(src, result)

    bundle = create_run_bundle(result, root=tmp_path / "runs", label="cdfl")
    assert Path(bundle["manifest"]).exists()
    assert Path(bundle["result"]).exists()
    assert Path(bundle["reports"]["markdown"]).exists()
    assert Path(bundle["reports"]["html"]).exists()
    assert Path(bundle["plots_dir"]).is_dir()

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
    assert "not empirical proof" in text


def test_llm_provider_key_status_does_not_print_keys(monkeypatch, tmp_path):
    key_file = tmp_path / "provider_key.txt"
    key_file.write_text("provider-secret\n")

    result = app_auth_status(api_key_file=key_file, provider="openai", model="test-model")
    assert result["status"] == "ok"
    assert result["kind"] == "llm_provider_status"
    assert result["payload"]["key_configured"] is True
    assert result["payload"]["key_source"] == "file"
    assert "provider-secret" not in json.dumps(result)

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    missing = llm_provider_status(provider="openai", model="test-model", key_env="CDFD_TEST_MISSING_KEY")
    assert missing["status"] == "ok"
    assert missing["payload"]["key_configured"] is False
    assert missing["warnings"]


def test_llm_provider_inventory_lists_supported_shapes_without_calls(monkeypatch):
    for profile in llm_module.PROVIDER_PROFILES.values():
        for env_name in profile["key_envs"]:
            monkeypatch.delenv(env_name, raising=False)

    result = llm_provider_inventory()
    assert result["status"] == "ok"
    providers = {row["provider"]: row for row in result["payload"]["providers"]}
    assert {"openai", "anthropic", "gemini", "mistral", "groq", "openrouter", "ollama"} <= set(providers)


def test_llm_explain_dry_run_builds_prompt_without_provider_call(monkeypatch, tmp_path):
    src = tmp_path / "result.json"
    write_json(src, _sample_result())

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
    assert "provider-secret" not in json.dumps(result)


def test_llm_explain_result_calls_openai_compatible_provider_without_leaking_key(monkeypatch, tmp_path):
    src = tmp_path / "result.json"
    write_json(src, _sample_result())
    captured = {}

    class FakeResponse:
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
    assert result["payload"]["response_text"] == "Research interpretation with claim boundaries."
    assert "provider-secret" not in json.dumps(result)
    assert captured["url"] == "https://provider.test/v1/chat/completions"


def test_cli_gallery_and_report_main(tmp_path):
    gallery_out = tmp_path / "gallery.json"
    assert cdfd.main(["gallery", "--json", "--out", str(gallery_out)]) == 0
    assert json.loads(gallery_out.read_text())["kind"] == "runtime_gallery"

    report_out = tmp_path / "report.md"
    assert cdfd.main(["report", str(gallery_out), "--format", "markdown", "--out", str(report_out)]) == 0
    assert "CDFD Runtime Report" in report_out.read_text()

    explain_out = tmp_path / "explain.md"
    assert cdfd.main(["explain", str(gallery_out), "--format", "markdown", "--out", str(explain_out)]) == 0
    assert "Claim Boundary" in explain_out.read_text()
