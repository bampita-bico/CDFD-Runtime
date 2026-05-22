import json
from pathlib import Path

import numpy as np

import cdfd
from runtime.diagnostics import adaptive_ratio, finite_stats, life_number, operating_ratio
from runtime.runner import app_auth_status, run_cdfl, run_domain, validate_cdfl


def test_paper_aligned_runtime_diagnostics_are_available():
    psi = adaptive_ratio(np.array([2.0]), np.array([4.0]), S=2.0, M_s=1.0)
    assert float(psi[0]) == 1.0
    assert operating_ratio(2.0, 4.0, s=2.0, m_s=1.0) == 1.0
    assert life_number(2.0, 0.5, 0.5, 2.0, 1.0) == 1.0
    assert finite_stats([1.0, 2.0])["all_finite"] is True


def test_runner_domain_demo_returns_enveloped_result():
    result = run_domain("physics", nx=4, ny=4, steps=1)
    assert result["status"] == "ok"
    assert result["kind"] == "domain_demo"
    assert result["payload"]["domain"] == "physics"
    assert result["finite_audit"]["all_finite"] is True


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

    run = run_cdfl(model, nx=4, ny=4)
    assert run["status"] == "ok"
    assert run["kind"] == "cdfl_run"
    assert run["payload"]["node_count"] == 4
    assert run["finite_audit"]["all_finite"] is True


def test_cli_main_can_write_json(tmp_path):
    output = tmp_path / "domains.json"
    code = cdfd.main(["domains", "--json", "--out", str(output)])
    assert code == 0
    data = json.loads(output.read_text())
    assert data["status"] == "ok"
    assert data["payload"]["count"] > 0


def test_app_auth_boundary_redacts_keys(monkeypatch, tmp_path):
    monkeypatch.setenv("CDFD_RUNTIME_API_KEYS", "runtime-secret")
    key_file = tmp_path / "app_key.txt"
    key_file.write_text("runtime-secret\n")

    result = app_auth_status(api_key_file=key_file)
    assert result["status"] == "ok"
    assert result["payload"]["accepted"] is True
    assert result["payload"]["key_fingerprint"]
    assert "runtime-secret" not in json.dumps(result)

    rejected = app_auth_status(api_key="wrong-key")
    assert rejected["status"] == "error"
    assert rejected["payload"]["accepted"] is False
