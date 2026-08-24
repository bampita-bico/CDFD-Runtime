import json
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_exposes_installed_cli_and_optional_extras():
    data = tomllib.loads((ROOT / "pyproject.toml").read_text())
    project = data["project"]
    assert project["scripts"]["cdfd"] == "cdfd:main"
    assert project["requires-python"] == ">=3.10"
    assert project["license"] == "AGPL-3.0-or-later"
    assert project["license-files"] == ["LICENSE"]
    assert {"dev", "docs", "experiments"} <= set(project["optional-dependencies"])
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
    assert "*.bib" in package_data["docs"]


def test_core_requirements_do_not_pull_web_or_dev_stack():
    requirements = (ROOT / "requirements.txt").read_text()
    for heavy in ("streamlit", "altair", "matplotlib", "pandas", "pytest", "h5py"):
        assert heavy not in requirements


def test_machine_readable_metadata_is_parseable_and_doi_aligned():
    codemeta = json.loads((ROOT / "codemeta.json").read_text())
    crate = json.loads((ROOT / "ro-crate-metadata.json").read_text())
    assert codemeta["identifier"] == "https://doi.org/10.5281/zenodo.20343160"
    crate_root = next(item for item in crate["@graph"] if item["@id"] == "./")
    assert crate_root["identifier"] == "https://doi.org/10.5281/zenodo.20343160"
    assert any(part["@id"] == "docs/paper.md" for part in crate_root["hasPart"])


def test_slim_release_surfaces_are_documented():
    readme = (ROOT / "README.md").read_text()
    paper = (ROOT / "docs" / "paper.md").read_text()
    assert "ARCHIVE_NOTICE_2026-08-25.md" in readme
    assert "docs/paper.md" in readme
    assert "experiments/run_cdfl_smoke.py" in readme
    assert "cdfd cdfl lint" in readme
    assert "ARCHIVE_NOTICE_2026-08-25.md" in paper
    assert "domain-maturity matrix" not in paper.lower()
    assert "runtime studio" not in paper.lower()
    assert (ROOT / "CLAIM_BOUNDARY.md").exists()
    assert (ROOT / "experiments" / "run_cdfl_smoke.py").exists()
    assert not (ROOT / "requirements-web.txt").exists()
