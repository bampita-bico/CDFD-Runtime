import json
import tomllib
from pathlib import Path

from domains.registry import DomainRegistry


ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_exposes_installed_cli_and_optional_extras():
    data = tomllib.loads((ROOT / "pyproject.toml").read_text())
    project = data["project"]
    assert project["scripts"]["cdfd"] == "cdfd:main"
    assert project["requires-python"] == ">=3.10"
    assert project["license"] == "AGPL-3.0-or-later"
    assert project["license-files"] == ["LICENSE"]
    assert {"web", "dev", "docs", "experiments"} <= set(project["optional-dependencies"])
    assert "streamlit>=1.32" in project["optional-dependencies"]["web"]
    assert "pytest>=8.0" in project["optional-dependencies"]["dev"]
    assert "wheel>=0.43" in project["optional-dependencies"]["dev"]


def test_wheel_asset_configuration_carries_runtime_examples_and_docs():
    data = tomllib.loads((ROOT / "pyproject.toml").read_text())
    package_includes = set(data["tool"]["setuptools"]["packages"]["find"]["include"])
    package_data = data["tool"]["setuptools"]["package-data"]
    assert {"examples*", "docs*"} <= package_includes
    assert "*.cdfl" in package_data["examples"]
    assert "*.json" in package_data["docs"]
    assert "*.md" in package_data["docs"]


def test_core_requirements_do_not_pull_web_or_dev_stack():
    requirements = (ROOT / "requirements.txt").read_text()
    for heavy in ("streamlit", "altair", "matplotlib", "pandas", "pytest", "h5py"):
        assert heavy not in requirements


def test_domain_maturity_matrix_matches_registry():
    matrix = json.loads((ROOT / "docs" / "domain_maturity_matrix.json").read_text())
    registry_domains = sorted(DomainRegistry.default().list_domains())
    matrix_domains = sorted(row["name"] for row in matrix["domains"])
    assert matrix["domain_count"] == len(registry_domains)
    assert matrix_domains == registry_domains
    assert matrix["summary"]["risk_counts"]["medical-risk"] > 0
    assert matrix["summary"]["risk_counts"]["engineering-risk"] > 0
    for row in matrix["domains"]:
        assert row["maturity"] in {"core", "paper-backed", "experimental", "demo-only"}
        assert row["expected_inputs"]
        assert row["outputs"]
        assert row["validation_level"]
        assert row["references"]


def test_machine_readable_metadata_is_parseable_and_doi_aligned():
    codemeta = json.loads((ROOT / "codemeta.json").read_text())
    crate = json.loads((ROOT / "ro-crate-metadata.json").read_text())
    assert codemeta["identifier"] == "https://doi.org/10.5281/zenodo.20343160"
    crate_root = next(item for item in crate["@graph"] if item["@id"] == "./")
    assert crate_root["identifier"] == "https://doi.org/10.5281/zenodo.20343160"
    assert any(part["@id"] == "docs/domain_maturity_matrix.json" for part in crate_root["hasPart"])


def test_webapp_is_documented_as_optional_release_surface():
    assert (ROOT / "webapp" / "run_server.py").exists()
    assert (ROOT / "webapp" / "README.md").exists()
    readme = (ROOT / "README.md").read_text()
    assert "python -m webapp.run_server" in readme
    assert ".[web]" in readme
