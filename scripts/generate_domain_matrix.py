#!/usr/bin/env python3
"""Generate the CDFD domain maturity matrix from the registered adapters."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from domains.registry import DomainRegistry

MATRIX_JSON = ROOT / "docs" / "domain_maturity_matrix.json"
MATRIX_MD = ROOT / "docs" / "DOMAIN_MATURITY.md"
GENERATED_DATE = "2026-05-30"

CORE_DOMAINS = {
    "physics",
    "origins_of_life",
    "medicine",
    "networks",
    "climate",
    "economics",
    "society",
    "cosmos",
}

PAPER_BACKED_DOMAINS = {
    "physics",
    "origins_of_life",
    "thermodynamics",
    "chemistry",
    "biology",
    "evolution",
    "ecology",
    "climate",
    "cosmos",
    "astrophysics",
    "quantum_mechanics",
    "plasma_physics",
    "medicine",
    "epidemiology",
    "pharmacology",
    "networks",
}

MEDICAL_TERMS = {
    "medicine",
    "medical",
    "cardiology",
    "oncology",
    "neurology",
    "nephrology",
    "surgery",
    "pharmacology",
    "epidemiology",
    "immunology",
    "radiology",
    "pathology",
    "paediatrics",
    "obstetrics",
    "psychiatry",
    "dermatology",
    "geriatrics",
    "urology",
    "dentistry",
    "haematology",
    "hepatology",
    "endocrinology",
    "pulmonology",
    "rheumatology",
    "neurosurgery",
    "rehabilitation",
    "palliative",
    "neonatology",
    "toxicology",
    "anaesthesia",
    "orthopaedics",
}

ENGINEERING_TERMS = {
    "engineering",
    "infrastructure",
    "networks",
    "robotics",
    "software",
    "data",
    "cloud",
    "cybersecurity",
    "semiconductors",
    "telecommunications",
    "energy",
    "construction",
    "aerospace",
    "civil",
    "electrical",
    "mechanical",
    "nuclear",
    "biomedical",
    "iot",
    "vehicles",
    "railway",
    "marine",
    "space",
    "nanotechnology",
    "biotechnology",
    "printing",
}

EARTH_TERMS = {
    "climate",
    "ecology",
    "geology",
    "hydrology",
    "oceanography",
    "agriculture",
    "soil",
    "forest",
    "water",
    "biodiversity",
    "drought",
    "flooding",
    "wildfire",
    "pollution",
    "marine",
    "freshwater",
    "desert",
    "arctic",
}

SOCIAL_TERMS = {
    "economics",
    "politics",
    "law",
    "education",
    "psychology",
    "sociology",
    "demography",
    "policy",
    "finance",
    "markets",
    "migration",
    "governance",
}

HISTORY_TERMS = {
    "history",
    "ancient",
    "medieval",
    "modern",
    "empire",
    "war",
    "revolution",
    "civil",
    "diplomacy",
}

ART_TERMS = {
    "arts",
    "music",
    "literature",
    "architecture",
    "mythology",
    "folklore",
    "heritage",
}

PHYSICS_TERMS = {
    "physics",
    "quantum",
    "thermodynamics",
    "plasma",
    "optics",
    "acoustics",
    "cosmos",
    "astrophysics",
}


def _tokens(name: str) -> set[str]:
    return set(name.replace("-", "_").split("_"))


def _field(name: str) -> str:
    tokens = _tokens(name)
    if name in MEDICAL_TERMS or tokens & MEDICAL_TERMS:
        return "medicine-health"
    if tokens & ENGINEERING_TERMS:
        return "engineering-technology"
    if tokens & EARTH_TERMS:
        return "earth-biology"
    if tokens & SOCIAL_TERMS:
        return "social-economic"
    if tokens & HISTORY_TERMS:
        return "history-conflict"
    if tokens & ART_TERMS:
        return "arts-culture"
    if tokens & PHYSICS_TERMS:
        return "physics-cosmos"
    if {"origins", "life"} & tokens:
        return "origins-of-life"
    return "general"


def _risk_class(name: str) -> list[str]:
    tokens = _tokens(name)
    risks: list[str] = []
    if name in MEDICAL_TERMS or tokens & MEDICAL_TERMS:
        risks.append("medical-risk")
    if tokens & ENGINEERING_TERMS:
        risks.append("engineering-risk")
    if not risks:
        risks.append("none")
    return risks


def _maturity(name: str) -> str:
    risks = set(_risk_class(name))
    if name in CORE_DOMAINS:
        return "core"
    if name in PAPER_BACKED_DOMAINS:
        return "paper-backed"
    if risks & {"medical-risk", "engineering-risk"}:
        return "experimental"
    return "demo-only"


def _validation_level(name: str, maturity: str, risks: list[str]) -> str:
    if maturity == "core":
        return "focused runtime tests plus CLI smoke coverage"
    if maturity == "paper-backed":
        return "runtime-paper or release-paper backed adapter diagnostics"
    if "medical-risk" in risks or "engineering-risk" in risks:
        return "risk-flagged demo adapter; no deployment validation"
    return "adapter import and demo-run surface only"


def _references(name: str) -> list[str]:
    refs = [
        "README.md#runtime-papers",
        "papers/10_Multi_Domain_Isomorphism_and_Adapter_Evidence.tex",
        "papers/11_Validation_Precision_and_Falsifiability.tex",
    ]
    if name == "origins_of_life":
        refs.append("https://doi.org/10.5281/zenodo.20264779")
    if name in {"physics", "thermodynamics", "quantum_mechanics", "plasma_physics", "cosmos"}:
        refs.append("https://doi.org/10.5281/zenodo.20250821")
    return refs


def _row(name: str) -> dict[str, Any]:
    risks = _risk_class(name)
    maturity = _maturity(name)
    classifications = [maturity] + [risk for risk in risks if risk != "none"]
    if risks == ["none"]:
        classifications.append("no-deployment-risk-flag")
    expected_inputs = [
        "optional JSON payload accepted by the adapter",
        "nx, ny, steps, and optional dt through cdfd demo",
        "adapter-specific scalar fields mapped into Phi, C, S, and M_s",
    ]
    if name == "origins_of_life":
        expected_inputs.append("source_scenario for aromatic source-mix diagnostics")
    return {
        "name": name,
        "field": _field(name),
        "maturity": maturity,
        "risk_class": risks,
        "classifications": classifications,
        "expected_inputs": expected_inputs,
        "outputs": [
            "strict result envelope with status, kind, provenance, and finite_audit",
            "domain payload with regime, final mean Phi/C/Psi_s values when available",
            "trace and human interpretation when the adapter exposes them",
        ],
        "validation_level": _validation_level(name, maturity, risks),
        "references": _references(name),
    }


def build_matrix() -> dict[str, Any]:
    domains = sorted(DomainRegistry.default().list_domains())
    rows = [_row(name) for name in domains]
    maturity_counts = Counter(row["maturity"] for row in rows)
    risk_counts = Counter(risk for row in rows for risk in row["risk_class"])
    return {
        "schema_version": "cdfd-domain-maturity-matrix-1",
        "generated_on": GENERATED_DATE,
        "generated_from": "DomainRegistry.default().list_domains()",
        "domain_count": len(rows),
        "classification_legend": {
            "core": "First-path runtime adapters with focused CLI smoke coverage.",
            "paper-backed": "Adapters tied directly to runtime papers or CDFD release-paper diagnostics.",
            "experimental": "Risk-flagged adapters retained for modeling exploration only.",
            "demo-only": "Breadth adapters with import/demo coverage but no independent validation.",
            "medical-risk": "No clinical advice, diagnosis, treatment, triage, or deployment claim.",
            "engineering-risk": "No safety certification, design approval, or deployment claim.",
        },
        "summary": {
            "maturity_counts": dict(sorted(maturity_counts.items())),
            "risk_counts": dict(sorted(risk_counts.items())),
        },
        "domains": rows,
    }


def render_markdown(matrix: dict[str, Any]) -> str:
    summary = matrix["summary"]
    lines = [
        "# Domain Maturity Matrix",
        "",
        f"Generated from `{matrix['generated_from']}` on {matrix['generated_on']}.",
        f"Registered domains: {matrix['domain_count']}.",
        "",
        "The machine-readable source is `docs/domain_maturity_matrix.json`.",
        "",
        "## Maturity Counts",
        "",
    ]
    for key, value in summary["maturity_counts"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Risk Counts", ""])
    for key, value in summary["risk_counts"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "The matrix describes release maturity and risk flags. It is not an empirical validation claim.",
            "Medical-risk and engineering-risk adapters are modeling surfaces only.",
            "",
            "## First-Path Domains",
            "",
        ]
    )
    core_rows = [row for row in matrix["domains"] if row["maturity"] == "core"]
    for row in core_rows:
        risks = ", ".join(row["risk_class"])
        lines.append(f"- {row['name']}: {row['field']}; risk={risks}; {row['validation_level']}.")
    lines.append("")
    return "\n".join(lines)


def _json_text(matrix: dict[str, Any]) -> str:
    return json.dumps(matrix, indent=2, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Exit nonzero if generated files are stale.")
    args = parser.parse_args(argv)

    matrix = build_matrix()
    json_text = _json_text(matrix)
    md_text = render_markdown(matrix)

    if args.check:
        stale = []
        if not MATRIX_JSON.exists() or MATRIX_JSON.read_text() != json_text:
            stale.append(str(MATRIX_JSON.relative_to(ROOT)))
        if not MATRIX_MD.exists() or MATRIX_MD.read_text() != md_text:
            stale.append(str(MATRIX_MD.relative_to(ROOT)))
        if stale:
            print("stale generated files:", ", ".join(stale), file=sys.stderr)
            return 1
        print("domain matrix is current")
        return 0

    MATRIX_JSON.parent.mkdir(parents=True, exist_ok=True)
    MATRIX_JSON.write_text(json_text)
    MATRIX_MD.write_text(md_text)
    print(f"wrote {MATRIX_JSON.relative_to(ROOT)}")
    print(f"wrote {MATRIX_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
