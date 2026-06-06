"""
CDFD Runtime Studio.

Streamlit remains a visualization and orchestration layer over the public CLI
engine. The deterministic runtime, finite audit, provenance, and reports are
shared with `cdfd.py`.
"""
from __future__ import annotations

import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Streamlit prepends webapp/ to sys.path; webapp/ontology.py used to shadow ontology/.
_ROOT = Path(__file__).resolve().parents[1]
_WEBAPP = Path(__file__).resolve().parent
_root, _webapp = str(_ROOT), str(_WEBAPP)
sys.path = [p for p in sys.path if p not in (_webapp, "")]
if sys.path[0] != _root:
    if _root in sys.path:
        sys.path.remove(_root)
    sys.path.insert(0, _root)

import altair as alt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from domains.registry import DomainRegistry
from dsl.cdfl_tools import CANONICAL_HEAT_FLOW
from engine.causal_graph import build_causal_graph
from engine.kernel import Kernel
from engine.state import State
from runtime.artifacts import create_run_bundle
from runtime.diagnostics import (
    aromatic_source_mix_scenarios,
    clean_json,
    finite_audit,
    life_number,
    photochemical_material_status,
    regime_label,
    result_envelope,
)
from runtime.reporting import result_to_html, result_to_markdown
from runtime.runner import (
    cdfl_ast,
    compare_domain,
    doctor,
    format_cdfl_file,
    lint_cdfl,
    llm_provider_status,
    part_ii_diagnostics,
    run_cdfl,
    run_domain,
    runtime_info,
    validate_cdfl,
)
from webapp.viz_helpers import (
    REGIME_COLORS,
    figure_to_bytes,
    history_to_dataframe,
    normalize_regime,
    plot_causal_graph,
    plot_field_heatmap,
    plot_snapshot_grid,
)


TRI_REGIME_DOMAIN = ["constrained", "balanced", "overload"]
TRI_REGIME_RANGE = [REGIME_COLORS[name] for name in TRI_REGIME_DOMAIN]
OOL_SCENARIOS = [
    "mixed_source_surface_trap",
    "meteoritic_seed_retained",
    "terrestrial_synthesis",
    "meteoritic_pulse_unretained",
    "high_feedstock_overload",
]


st.set_page_config(
    page_title="CDFD Runtime Studio",
    page_icon="◇",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _install_css() -> None:
    st.markdown(
        """
        <style>
        .cdfd-run-card {
            border: 1px solid #d7dde8;
            border-radius: 8px;
            padding: 0.8rem 0.9rem;
            background: #ffffff;
        }
        .cdfd-boundary {
            border-left: 4px solid #4b5563;
            background: #f8fafc;
            padding: 0.7rem 0.9rem;
            border-radius: 6px;
        }
        .cdfd-artifact {
            font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
            font-size: 0.85rem;
            background: #111827;
            color: #f8fafc;
            padding: 0.55rem 0.7rem;
            border-radius: 6px;
            overflow-wrap: anywhere;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _runtime_version() -> str:
    citation = _ROOT / "CITATION.cff"
    if not citation.exists():
        return "local"
    for line in citation.read_text().splitlines():
        if line.startswith("version:"):
            return line.split(":", 1)[1].strip().strip('"')
    return "local"


@st.cache_resource(show_spinner=False)
def _registry() -> DomainRegistry:
    return DomainRegistry.default()


@st.cache_data(show_spinner=False)
def _domain_rows() -> list[dict[str, str]]:
    names = sorted(_registry().list_domains())
    return [
        {
            "domain": name,
            "field": _domain_field(name),
            "cli": f"python cdfd.py demo {name}",
        }
        for name in names
    ]


def _domain_field(name: str) -> str:
    tokens = set(name.replace("-", "_").split("_"))
    medical = {
        "medicine",
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
    }
    earth = {
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
    }
    engineering = {
        "engineering",
        "networks",
        "robotics",
        "software",
        "data",
        "cloud",
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
    }
    social = {
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
    history = {"history", "ancient", "medieval", "modern", "empire", "war", "revolution", "civil", "diplomacy"}
    arts = {"arts", "music", "literature", "architecture", "mythology", "folklore", "heritage"}
    physics = {"physics", "quantum", "thermodynamics", "plasma", "optics", "acoustics", "cosmos", "astrophysics"}
    if name in medical or tokens & medical:
        return "Medicine"
    if tokens & earth:
        return "Earth/Biology"
    if tokens & engineering:
        return "Engineering/Tech"
    if tokens & social:
        return "Social/Economic"
    if tokens & history:
        return "History/Conflict"
    if tokens & arts:
        return "Arts/Culture"
    if tokens & physics:
        return "Physics/Cosmos"
    if "origins" in tokens or "life" in tokens:
        return "Origins of Life"
    return "General"


def _selected_result() -> dict[str, Any]:
    return st.session_state.get("selected_result") or runtime_info()


def _result_label(result: dict[str, Any]) -> str:
    payload = result.get("payload", {})
    if isinstance(payload, dict) and payload.get("domain"):
        return str(payload["domain"])
    return str(result.get("kind") or "run")


def _result_regime(result: dict[str, Any]) -> str:
    payload = result.get("payload", {})
    if isinstance(payload, dict):
        if payload.get("regime"):
            return normalize_regime(payload["regime"])
        trace = payload.get("trace")
        if isinstance(trace, list) and trace:
            return normalize_regime(trace[-1].get("regime"))
    return "balanced"


def _final_psi(result: dict[str, Any]) -> float | None:
    payload = result.get("payload", {})
    if isinstance(payload, dict):
        final = payload.get("final")
        if isinstance(final, dict) and final.get("mean_psi") is not None:
            return float(final["mean_psi"])
        trace = payload.get("trace")
        if isinstance(trace, list) and trace and trace[-1].get("psi_s") is not None:
            return float(trace[-1]["psi_s"])
    return None


def _remember_run(label: str, result: dict[str, Any]) -> None:
    record = {
        "label": label,
        "added_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "result": clean_json(result),
    }
    records = st.session_state.setdefault("run_records", [])
    records.insert(0, record)
    del records[12:]
    st.session_state["selected_result"] = result


def _run_records_table() -> pd.DataFrame:
    rows = []
    for record in st.session_state.get("run_records", []):
        result = record["result"]
        rows.append(
            {
                "label": record["label"],
                "kind": result.get("kind"),
                "status": result.get("status"),
                "regime": _result_regime(result),
                "psi_s": _final_psi(result),
                "finite": result.get("finite_audit", {}).get("all_finite"),
                "command": result.get("provenance", {}).get("command"),
            }
        )
    return pd.DataFrame(rows)


def _safe_json_bytes(result: dict[str, Any]) -> bytes:
    return (json.dumps(clean_json(result), indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def _run_cdfl_text(text: str, action: str, *, nx: int = 16, ny: int = 16) -> dict[str, Any]:
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".cdfl", prefix="cdfd-studio-", dir="/tmp", delete=False) as handle:
            handle.write(text)
            tmp_path = Path(handle.name)
        if action == "validate":
            return validate_cdfl(tmp_path, command="streamlit cdfl validate")
        if action == "lint":
            return lint_cdfl(tmp_path)
        if action == "run":
            return run_cdfl(tmp_path, nx=nx, ny=ny, command=f"streamlit cdfl run --nx {nx} --ny {ny}")
        if action == "ast":
            return cdfl_ast(tmp_path)
        if action == "format":
            return format_cdfl_file(tmp_path)
        raise ValueError(f"Unknown CDFL action: {action}")
    finally:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)


def _cdfl_diagnostics_frame(result: dict[str, Any]) -> pd.DataFrame:
    payload = result.get("payload", {})
    diagnostics = payload.get("diagnostics", []) if isinstance(payload, dict) else []
    columns = ["severity", "code", "line", "column", "message"]
    if not diagnostics:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame(diagnostics)[columns]


def _download_result_controls(result: dict[str, Any], key: str) -> None:
    c1, c2, c3 = st.columns(3)
    c1.download_button(
        "JSON",
        _safe_json_bytes(result),
        file_name=f"{key}.json",
        mime="application/json",
        key=f"{key}-json",
    )
    c2.download_button(
        "Markdown",
        result_to_markdown(result).encode("utf-8"),
        file_name=f"{key}.md",
        mime="text/markdown",
        key=f"{key}-md",
    )
    c3.download_button(
        "HTML",
        result_to_html(result).encode("utf-8"),
        file_name=f"{key}.html",
        mime="text/html",
        key=f"{key}-html",
    )


def _download_figure(fig: plt.Figure, key: str, name: str) -> None:
    c1, c2 = st.columns(2)
    c1.download_button(
        "PNG",
        figure_to_bytes(fig, "png"),
        file_name=f"{name}.png",
        mime="image/png",
        key=f"{key}-png",
    )
    c2.download_button(
        "SVG",
        figure_to_bytes(fig, "svg"),
        file_name=f"{name}.svg",
        mime="image/svg+xml",
        key=f"{key}-svg",
    )


def _run_card(result: dict[str, Any], key: str, label: str | None = None) -> None:
    payload = result.get("payload", {})
    finite = result.get("finite_audit", {})
    command = result.get("provenance", {}).get("command")
    title = label or _result_label(result)
    psi = _final_psi(result)
    with st.container(border=True):
        h1, h2, h3, h4 = st.columns([1.4, 1, 1, 1.2])
        h1.metric("Run", title)
        h2.metric("Status", result.get("status", "unknown"))
        h3.metric("Finite audit", "pass" if finite.get("all_finite") else "fail")
        h4.metric("Regime", _result_regime(result))
        if psi is not None:
            st.metric("Final Psi_s", f"{psi:.4f}")
        if isinstance(payload, dict) and payload.get("interpretation"):
            st.markdown(str(payload["interpretation"]))
        if command:
            st.code(command, language="bash")
        _download_result_controls(result, key)
        if st.button("Save run bundle", key=f"{key}-bundle"):
            manifest = create_run_bundle(result, label=title)
            st.session_state["last_manifest"] = manifest
            st.success(f"Saved run bundle: {manifest['run_dir']}")


def _evidence_block(
    title: str,
    *,
    supports: list[str],
    breaks: list[str],
    artifact: str,
    expanded: bool = False,
) -> None:
    with st.expander(f"Evidence & falsification: {title}", expanded=expanded):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**What this supports**")
            for item in supports:
                st.markdown(f"- {item}")
        with c2:
            st.markdown("**What would break it**")
            for item in breaks:
                st.markdown(f"- {item}")
        st.markdown(f"<div class='cdfd-artifact'>{artifact}</div>", unsafe_allow_html=True)


def _trace_chart(df: pd.DataFrame, *, key: str) -> alt.Chart:
    if df.empty:
        return alt.Chart(pd.DataFrame({"t": [], "psi_s": []})).mark_line()
    y_max = max(float(df["psi_s"].max()) * 1.1, 1.35)
    bands = pd.DataFrame(
        [
            {"regime": "constrained", "y1": 0.0, "y2": 0.8},
            {"regime": "balanced", "y1": 0.8, "y2": 1.2},
            {"regime": "overload", "y1": 1.2, "y2": y_max},
        ]
    )
    base = alt.Chart(df).encode(x=alt.X("t:Q", title="time"))
    band_layer = (
        alt.Chart(bands)
        .mark_rect(opacity=0.12)
        .encode(
            y=alt.Y("y1:Q", title="Psi_s"),
            y2="y2:Q",
            color=alt.Color("regime:N", scale=alt.Scale(domain=TRI_REGIME_DOMAIN, range=TRI_REGIME_RANGE), legend=None),
        )
    )
    line = base.mark_line(color="#1f2937", strokeWidth=2).encode(
        y=alt.Y("psi_s:Q", scale=alt.Scale(domain=[0, y_max])),
        tooltip=["t:Q", "psi_s:Q", "regime:N"],
    )
    markers = (
        base.transform_filter("datum.regime != 'balanced'")
        .mark_circle(size=55, opacity=0.9)
        .encode(
            y="psi_s:Q",
            color=alt.Color("regime:N", scale=alt.Scale(domain=TRI_REGIME_DOMAIN, range=TRI_REGIME_RANGE)),
            tooltip=["t:Q", "psi_s:Q", "regime:N"],
        )
    )
    chart = (band_layer + line + markers).properties(height=330).interactive()
    st.download_button(
        "HTML",
        chart.to_html().encode("utf-8"),
        file_name=f"{key}.html",
        mime="text/html",
        key=f"{key}-html-chart",
    )
    return chart


def _phase_chart(df: pd.DataFrame) -> alt.Chart:
    return (
        alt.Chart(df)
        .mark_circle(size=70, opacity=0.78)
        .encode(
            x=alt.X("phi:Q", title="mean Phi"),
            y=alt.Y("C:Q", title="mean C"),
            color=alt.Color("regime:N", scale=alt.Scale(domain=TRI_REGIME_DOMAIN, range=TRI_REGIME_RANGE)),
            tooltip=["t:Q", "phi:Q", "C:Q", "psi_s:Q", "S:Q", "Ms:Q", "regime:N"],
        )
        .properties(height=330)
        .interactive()
    )


def _life_number_chart() -> alt.Chart:
    energies = np.linspace(0.25, 4.0, 32)
    coupling = np.linspace(0.1, 1.0, 28)
    rows = []
    for energy in energies:
        for sigma in coupling:
            lam = life_number(energy, sigma, sigma, tau_relax=2.0, stabilization=1.0, maintenance_energy=1.0)
            rows.append({"input_energy": energy, "coupling": sigma, "life_number": lam, "regime": regime_label(lam, low=1.0, high=2.0)})
    df = pd.DataFrame(rows)
    return (
        alt.Chart(df)
        .mark_rect()
        .encode(
            x=alt.X("input_energy:Q", title="input energy"),
            y=alt.Y("coupling:Q", title="coupling sigma"),
            color=alt.Color("life_number:Q", scale=alt.Scale(scheme="viridis"), title="Life Number"),
            tooltip=["input_energy:Q", "coupling:Q", "life_number:Q", "regime:N"],
        )
        .properties(height=330)
        .interactive()
    )


def _source_mix_chart(rows: list[dict[str, Any]]) -> alt.Chart:
    df = pd.DataFrame(rows)
    base = alt.Chart(df).encode(
        y=alt.Y("scenario:N", sort="-x", title=None),
        tooltip=[
            "scenario:N",
            "retained_pool:Q",
            "coupling_factor:Q",
            "damage_load:Q",
            "functional_score:Q",
            "interpretation:N",
        ],
    )
    bars = base.mark_bar(size=22).encode(
        x=alt.X("functional_score:Q", title="functional source-mix score"),
        color=alt.condition(
            alt.datum.scenario == "mixed_source_surface_trap",
            alt.value("#27AE60"),
            alt.value("#6B7280"),
        ),
    )
    return bars.properties(height=260).interactive()


def _make_physics_run(
    *,
    nx: int,
    ny: int,
    dt: float,
    steps: int,
    alpha_val: float,
    beta_val: float,
    gamma_val: float,
    noise: float,
    seed: int,
) -> tuple[pd.DataFrame, list[dict[str, Any]], State, dict[str, Any]]:
    rng = np.random.default_rng(seed)
    kernel = Kernel(dt=dt)
    state = State(nx=nx, ny=ny)
    state.alpha[:] = alpha_val
    state.beta[:] = beta_val
    state.gamma[:] = gamma_val
    if noise > 0:
        state.phi += rng.normal(0, noise, (nx, ny))
        state.update_psi()

    trace: list[dict[str, Any]] = []
    snapshots: list[dict[str, Any]] = []
    for _ in range(steps):
        cycle = kernel.run_cycle(state)
        state.update_psi()
        regime = normalize_regime(state.regime())
        trace.append(
            {
                "t": float(state.t),
                "psi_s": float(state.mean_psi()),
                "phi": float(np.mean(state.phi)),
                "C": float(np.mean(state.C)),
                "S": float(np.mean(state.S)),
                "Ms": float(np.mean(state.Ms)),
                "regime": regime,
                "status": cycle.get("status", "ok"),
            }
        )
        snapshots.append(
            {
                "t": float(state.t),
                "phi": state.phi.copy(),
                "C": state.C.copy(),
                "psi_s": state.psi_s.copy(),
                "Ms": state.Ms.copy(),
                "regime": regime,
            }
        )

    state.calculate_disease_horizon()
    df = history_to_dataframe(trace)
    final = trace[-1] if trace else {}
    payload = {
        "domain": "physics_lab",
        "nx": nx,
        "ny": ny,
        "steps": steps,
        "dt": dt,
        "parameters": {
            "alpha": alpha_val,
            "beta": beta_val,
            "gamma": gamma_val,
            "noise": noise,
            "seed": seed,
        },
        "final": {
            "mean_phi": final.get("phi"),
            "mean_C": final.get("C"),
            "mean_psi": final.get("psi_s"),
        },
        "regime": final.get("regime"),
        "trace": trace,
        "finite_fields": finite_audit({"phi": state.phi, "C": state.C, "psi_s": state.psi_s, "Ms": state.Ms}),
        "collapse_horizon": clean_json(state.meta),
        "interpretation": "Physics lab run through Kernel.run_cycle using the same state equations as the CLI runtime.",
    }
    envelope = result_envelope(
        "studio_physics_run",
        f"streamlit physics --nx {nx} --ny {ny} --steps {steps} --dt {dt}",
        payload,
    )
    return df, snapshots, state, envelope


def _causal_timeline(trace: list[dict[str, Any]], threshold: float) -> pd.DataFrame:
    if len(trace) < 6:
        return pd.DataFrame()
    step = max(4, len(trace) // 18)
    rows = []
    for end in range(6, len(trace) + 1, step):
        graph = build_causal_graph(trace[:end], threshold=threshold)
        rows.append(
            {
                "t": trace[end - 1]["t"],
                "edges": len(graph.edges),
                "strongest": graph.edges[0]["strength"] if graph.edges else 0.0,
            }
        )
    if rows[-1]["t"] != trace[-1]["t"]:
        graph = build_causal_graph(trace, threshold=threshold)
        rows.append(
            {
                "t": trace[-1]["t"],
                "edges": len(graph.edges),
                "strongest": graph.edges[0]["strength"] if graph.edges else 0.0,
            }
        )
    return pd.DataFrame(rows)


def _render_cockpit() -> None:
    info = runtime_info()
    selected = _selected_result()
    domains = info["payload"]["domain_count"]
    version = _runtime_version()
    finite = selected.get("finite_audit", {})
    command = selected.get("provenance", {}).get("command") or "python cdfd.py info"

    c1, c2, c3, c4, c5 = st.columns([1.1, 1, 1, 1, 1.4])
    c1.metric("Runtime", info["status"])
    c2.metric("Version", version)
    c3.metric("Domains", domains)
    c4.metric("Finite audit", "pass" if finite.get("all_finite") else "fail")
    c5.metric("Selected run", _result_label(selected))

    st.markdown(f"<div class='cdfd-artifact'>{command}</div>", unsafe_allow_html=True)

    c_left, c_right = st.columns([1.35, 1])
    with c_left:
        st.subheader("Selected run card")
        _run_card(selected, key="cockpit-selected", label=_result_label(selected))
    with c_right:
        st.subheader("Doctor")
        if st.button("Run doctor", type="primary", key="cockpit-doctor"):
            result = doctor()
            _remember_run("doctor", result)
            st.session_state["doctor_result"] = result
        doctor_result = st.session_state.get("doctor_result") or doctor()
        summary = doctor_result["payload"]["summary"]
        m1, m2, m3 = st.columns(3)
        m1.metric("OK", summary["ok"])
        m2.metric("Warnings", summary["warnings"])
        m3.metric("Errors", summary["errors"])
        st.dataframe(pd.DataFrame(doctor_result["payload"]["checks"]), use_container_width=True, hide_index=True)

    records = _run_records_table()
    if not records.empty:
        st.subheader("Recent run cards")
        st.dataframe(records, use_container_width=True, hide_index=True)


def _render_cdfl_workbench() -> None:
    st.session_state.setdefault("cdfl_source", CANONICAL_HEAT_FLOW)

    tools, editor = st.columns([0.9, 2.4])
    with tools:
        st.subheader("Run controls")
        nx = st.slider("Grid X", 4, 64, 16, key="cdfl_nx")
        ny = st.slider("Grid Y", 4, 64, 16, key="cdfl_ny")
        b1, b2 = st.columns(2)
        validate_clicked = b1.button("Validate", type="primary", key="cdfl_validate")
        run_clicked = b2.button("Run", key="cdfl_run")
        b3, b4 = st.columns(2)
        lint_clicked = b3.button("Lint", key="cdfl_lint")
        format_clicked = b4.button("Format", key="cdfl_format")
        ast_clicked = st.button("AST", key="cdfl_ast")
        st.code(
            "python cdfd.py cdfl lint model.cdfl\n"
            "python cdfd.py cdfl run model.cdfl --nx 16 --ny 16",
            language="bash",
        )

    with editor:
        source = st.text_area("CDFL model", key="cdfl_source", height=430)

    action = None
    if validate_clicked:
        action = "validate"
    elif run_clicked:
        action = "run"
    elif lint_clicked:
        action = "lint"
    elif format_clicked:
        action = "format"
    elif ast_clicked:
        action = "ast"

    if action:
        with st.spinner(f"CDFL {action}"):
            result = _run_cdfl_text(source, action, nx=nx, ny=ny)
        st.session_state["cdfl_result"] = result
        if result.get("kind") == "cdfl_run" and result.get("status") == "ok":
            _remember_run("cdfl_workbench", result)

    result = st.session_state.get("cdfl_result")
    if not result:
        return

    payload = result.get("payload", {})
    summary = payload.get("diagnostic_summary", {}) if isinstance(payload, dict) else {}
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Status", result.get("status", "unknown"))
    c2.metric("Kind", result.get("kind", "cdfl"))
    c3.metric("Nodes", payload.get("node_count", "-") if isinstance(payload, dict) else "-")
    c4.metric("Diagnostics", f"{summary.get('error', 0)} / {summary.get('warning', 0)} / {summary.get('info', 0)}")

    diagnostics_df = _cdfl_diagnostics_frame(result)
    if diagnostics_df.empty:
        st.success("No CDFL diagnostics.")
    else:
        st.dataframe(diagnostics_df, use_container_width=True, hide_index=True)

    if result.get("kind") == "cdfl_format" and isinstance(payload, dict):
        formatted = payload.get("formatted", "")
        st.code(formatted, language="cdfl")
        st.download_button(
            "CDFL",
            formatted.encode("utf-8"),
            file_name="formatted.cdfl",
            mime="text/plain",
            key="cdfl-formatted-download",
        )
    elif result.get("kind") == "cdfl_ast" and isinstance(payload, dict):
        st.json(clean_json(payload.get("nodes", [])))
    elif result.get("kind") == "cdfl_run" and isinstance(payload, dict):
        st.json(clean_json(payload.get("results", [])))

    _download_result_controls(result, "cdfl-workbench-result")


def _render_physics_lab() -> None:
    col_side, col_main = st.columns([0.95, 2.6])
    with col_side:
        st.subheader("Grid & time")
        nx = st.slider("Grid X", 4, 48, 16, key="phys_nx")
        ny = st.slider("Grid Y", 4, 48, 16, key="phys_ny")
        dt = st.number_input("dt", value=0.01, min_value=0.0001, format="%.4f", key="phys_dt")
        steps = st.slider("Steps", 10, 400, 120, key="phys_steps")
        st.subheader("Scalars")
        alpha_val = st.slider("alpha feedback", 0.0, 0.5, 0.1, key="phys_alpha")
        beta_val = st.slider("beta relaxation", 0.0, 0.5, 0.05, key="phys_beta")
        gamma_val = st.slider("gamma spread", 0.0, 0.2, 0.1, key="phys_gamma")
        noise = st.slider("Initial Phi noise", 0.0, 0.3, 0.08, key="phys_noise")
        seed = st.number_input("Seed", value=42, step=1, key="phys_seed")
        run_phys = st.button("Run physics kernel", type="primary", key="phys_run")

    with col_main:
        if run_phys:
            with st.spinner("Running kernel"):
                df, snapshots, state, result = _make_physics_run(
                    nx=nx,
                    ny=ny,
                    dt=dt,
                    steps=steps,
                    alpha_val=alpha_val,
                    beta_val=beta_val,
                    gamma_val=gamma_val,
                    noise=noise,
                    seed=int(seed),
                )
            st.session_state["phys_df"] = df
            st.session_state["phys_snapshots"] = snapshots
            st.session_state["phys_state"] = state
            st.session_state["phys_result"] = result
            _remember_run("physics_lab", result)

        df = st.session_state.get("phys_df")
        snapshots = st.session_state.get("phys_snapshots")
        state = st.session_state.get("phys_state")
        result = st.session_state.get("phys_result")

        if df is None or state is None or not snapshots:
            st.info("Run the physics kernel to populate the Studio panels.")
            return

        final_psi = float(df["psi_s"].iloc[-1])
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Final Psi_s", f"{final_psi:.3f}")
        m2.metric("Regime", normalize_regime(df["regime"].iloc[-1]))
        m3.metric("Mean Phi", f"{float(df['phi'].iloc[-1]):.3f}")
        m4.metric("Collapse horizon", str(state.meta.get("t_collapse_min", "-")))

        c1, c2 = st.columns(2)
        with c1:
            st.altair_chart(_trace_chart(df, key="physics-trajectory"), use_container_width=True)
            _evidence_block(
                "Psi_s trajectory",
                supports=[
                    "The run stayed in the recorded tri-regime path for the selected parameters.",
                    "Collapse/overload markers come from the same scalar trace stored in the result envelope.",
                ],
                breaks=[
                    "A failed finite audit or non-finite Psi_s trace breaks the panel.",
                    "Changing nx, ny, dt, seed, or scalar coefficients changes the replay artifact.",
                ],
                artifact="phys_result.payload.trace + streamlit physics command",
            )
        with c2:
            st.altair_chart(_phase_chart(df), use_container_width=True)
            _evidence_block(
                "Phase-space trace",
                supports=["Mean Phi/C movement is visible over the same timesteps as the replay."],
                breaks=["Flat traces, nonnumeric fields, or missing provenance make this only a UI artifact."],
                artifact="phys_result.payload.trace",
            )

        frame = st.slider("Replay timestep", 0, len(snapshots) - 1, len(snapshots) - 1, key="phys_replay")
        snapshot = snapshots[frame]
        st.caption(f"t={float(snapshot['t']):.4f} | regime={snapshot['regime']}")

        f1, f2, f3, f4 = st.columns(4)
        figs = [
            (f1, plot_field_heatmap(snapshot["phi"], "Phi flow"), "phi"),
            (f2, plot_field_heatmap(snapshot["C"], "C constraint", cmap="magma"), "constraint"),
            (f3, plot_field_heatmap(snapshot["psi_s"], "Psi_s", cmap="RdYlGn_r"), "psi_s"),
            (f4, plot_field_heatmap(snapshot["Ms"], "M_s memory", cmap="cividis"), "memory"),
        ]
        for column, fig, _name in figs:
            with column:
                st.pyplot(fig, clear_figure=True)
        grid_fig = plot_snapshot_grid(snapshot)
        _download_figure(grid_fig, key="physics-snapshot-grid", name="cdfd-physics-replay-snapshot")
        plt.close(grid_fig)
        for _column, fig, _name in figs:
            plt.close(fig)

        with st.expander("Scalar trace table"):
            st.dataframe(df, use_container_width=True, hide_index=True)

        if result:
            _run_card(result, key="physics-result", label="physics_lab")


def _render_origins_lab() -> None:
    rows = aromatic_source_mix_scenarios()
    c1, c2 = st.columns([1.25, 1])
    with c1:
        st.subheader("Source-mix comparison")
        st.altair_chart(_source_mix_chart(rows), use_container_width=True)
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        _evidence_block(
            "Aromatic source mix",
            supports=[
                "The ranking is a guarded supply/coupling diagnostic from runtime.diagnostics.",
                "The top row is not treated as an origin proof.",
            ],
            breaks=[
                "Empirical chemistry would be required before promoting the source mix to a historical claim.",
                "Changing retention, coupling, or damage formulas changes the ranking.",
            ],
            artifact="runtime.diagnostics.aromatic_source_mix_scenarios()",
        )
    with c2:
        st.subheader("Life Number map")
        st.altair_chart(_life_number_chart(), use_container_width=True)
        status = photochemical_material_status()
        st.markdown("**Photochemical guardrails**")
        for key, text in status.items():
            st.markdown(f"- `{key}`: {text}")

    scenario = st.selectbox("Scenario", OOL_SCENARIOS, index=0, key="ool_scenario")
    c_run, c_cmp = st.columns(2)
    with c_run:
        if st.button("Run OOL scenario", type="primary", key="ool_run"):
            result = run_domain(
                "origins_of_life",
                {"source_scenario": scenario},
                nx=8,
                ny=8,
                steps=12,
            )
            st.session_state["ool_result"] = result
            _remember_run(f"ool:{scenario}", result)
    with c_cmp:
        if st.button("Compare OOL scenarios", key="ool_compare"):
            result = compare_domain("origins_of_life", OOL_SCENARIOS, nx=6, ny=6, steps=6)
            st.session_state["ool_compare_result"] = result
            _remember_run("ool_compare", result)

    diag = part_ii_diagnostics(scenario=scenario, include_demo=False)
    with st.expander("Part II diagnostic envelope", expanded=False):
        st.json(diag)

    for state_key, label in (("ool_result", "origins_of_life"), ("ool_compare_result", "ool_compare")):
        result = st.session_state.get(state_key)
        if result:
            _run_card(result, key=state_key, label=label)

    st.markdown(
        """
        **Paper links:** `papers/07_Autonomous_Discovery_Hypothesis_Triage_and_Falsification.tex`
        and `papers/11_Validation_Precision_and_Falsifiability.tex`
        """
    )


def _render_domain_atlas() -> None:
    rows = pd.DataFrame(_domain_rows())
    fields = ["All"] + sorted(rows["field"].unique())
    c1, c2, c3 = st.columns([1.1, 1, 0.9])
    search = c1.text_input("Search", value="", key="atlas_search")
    field = c2.selectbox("Field", fields, key="atlas_field")
    limit = c3.slider("Rows", 10, 200, 60, key="atlas_limit")

    filtered = rows.copy()
    if field != "All":
        filtered = filtered[filtered["field"] == field]
    if search:
        q = search.lower()
        filtered = filtered[filtered["domain"].str.lower().str.contains(q) | filtered["field"].str.lower().str.contains(q)]
    filtered = filtered.sort_values(["field", "domain"]).head(limit)
    m1, m2, m3 = st.columns(3)
    m1.metric("Registered domains", len(rows))
    m2.metric("Visible", len(filtered))
    m3.metric("Fields", rows["field"].nunique())
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    st.download_button(
        "Atlas CSV",
        filtered.to_csv(index=False).encode("utf-8"),
        file_name="cdfd-domain-atlas.csv",
        mime="text/csv",
        key="atlas-csv",
    )

    names = sorted(rows["domain"].tolist())
    c_run, c_compare = st.columns(2)
    with c_run:
        domain = st.selectbox("Run adapter", names, index=names.index("origins_of_life") if "origins_of_life" in names else 0)
        scenario = st.selectbox("OOL source scenario", OOL_SCENARIOS, disabled=domain != "origins_of_life")
        nx = st.slider("nx", 4, 32, 12, key="atlas_nx")
        ny = st.slider("ny", 4, 32, 12, key="atlas_ny")
        steps = st.slider("steps", 1, 80, 24, key="atlas_steps")
        if st.button("Run adapter", type="primary", key="atlas_run"):
            payload = {"source_scenario": scenario} if domain == "origins_of_life" else {}
            result = run_domain(domain, payload, nx=nx, ny=ny, steps=steps)
            st.session_state["atlas_result"] = result
            _remember_run(f"atlas:{domain}", result)
    with c_compare:
        pair = st.multiselect(
            "Side-by-side domains",
            names,
            default=[name for name in ("physics", "origins_of_life") if name in names],
            max_selections=2,
            key="atlas_pair",
        )
        if st.button("Run side-by-side", key="atlas_side") and pair:
            results = [run_domain(name, {"source_scenario": scenario} if name == "origins_of_life" else {}, nx=8, ny=8, steps=8) for name in pair]
            st.session_state["atlas_pair_results"] = results
            for result in results:
                _remember_run(f"atlas:{_result_label(result)}", result)

    result = st.session_state.get("atlas_result")
    if result:
        _run_card(result, key="atlas-result", label=_result_label(result))

    pair_results = st.session_state.get("atlas_pair_results") or []
    if pair_results:
        cols = st.columns(len(pair_results))
        for idx, result in enumerate(pair_results):
            with cols[idx]:
                _run_card(result, key=f"atlas-pair-{idx}", label=_result_label(result))


def _render_evidence() -> None:
    result = _selected_result()
    st.subheader("Selected result")
    _run_card(result, key="evidence-selected", label=_result_label(result))

    payload = result.get("payload", {})
    trace = payload.get("trace") if isinstance(payload, dict) else None
    if isinstance(trace, list) and len(trace) >= 6:
        threshold = st.slider("Causal threshold", 0.1, 0.9, 0.3, 0.05, key="evidence_thr")
        numeric_trace = [
            {k: v for k, v in row.items() if k in {"t", "psi_s", "phi", "C", "S", "Ms"}}
            for row in trace
        ]
        graph = build_causal_graph(numeric_trace, threshold=threshold)
        timeline = _causal_timeline(numeric_trace, threshold)
        c1, c2 = st.columns(2)
        with c1:
            if graph.edges:
                fig = plot_causal_graph(graph.edges, graph.nodes)
                st.pyplot(fig, clear_figure=True)
                _download_figure(fig, key="evidence-causal-graph", name="cdfd-causal-graph")
                plt.close(fig)
            else:
                st.warning("No causal edges above threshold.")
        with c2:
            if not timeline.empty:
                chart = (
                    alt.Chart(timeline)
                    .mark_line(point=True, color="#7C3AED")
                    .encode(
                        x=alt.X("t:Q", title="time"),
                        y=alt.Y("edges:Q", title="edge count"),
                        tooltip=["t:Q", "edges:Q", "strongest:Q"],
                    )
                    .properties(height=330)
                    .interactive()
                )
                st.altair_chart(chart, use_container_width=True)
        if graph.edges:
            st.dataframe(pd.DataFrame(graph.strongest(12)), use_container_width=True, hide_index=True)
        st.download_button(
            "DOT",
            graph.to_dot().encode("utf-8"),
            file_name="cdfd-causal-graph.dot",
            mime="text/vnd.graphviz",
            key="evidence-dot",
        )
        _evidence_block(
            "Causal graph timeline",
            supports=["Edges are lagged-correlation diagnostics generated from the selected run trace."],
            breaks=[
                "Short histories, nonnumeric series, or high thresholds can erase all graph edges.",
                "A lagged correlation edge is not proof of physical causality outside the simulation.",
            ],
            artifact="engine.causal_graph.build_causal_graph(selected_result.payload.trace)",
            expanded=True,
        )
    else:
        st.info("Select a run with a scalar trace to render causal evidence.")

    st.markdown("<div class='cdfd-boundary'>CDFD Runtime output is deterministic modeling and hypothesis triage. It is not empirical proof, clinical advice, engineering certification, or a deployed safety, financial, or medical decision system.</div>", unsafe_allow_html=True)


def _render_vos_preview() -> None:
    selected = _selected_result()
    llm = llm_provider_status()
    c1, c2, c3 = st.columns(3)
    c1.metric("LLM provider", llm["payload"].get("provider") or "openai")
    c2.metric("Provider key", "configured" if llm["payload"].get("key_configured") else "not configured")
    c3.metric("Provider call", "available" if llm["payload"].get("key_configured") else "needs key")
    st.markdown("<div class='cdfd-boundary'>VOS remains above the runtime: queueing, provider keys, saved experiments, and optional LLM research calls do not enter the deterministic engine.</div>", unsafe_allow_html=True)

    queue = st.session_state.setdefault("vos_queue", [])
    q1, q2 = st.columns(2)
    with q1:
        if st.button("Queue selected run", type="primary", key="vos_queue_add"):
            queue.append(
                {
                    "queued_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "label": _result_label(selected),
                    "command": selected.get("provenance", {}).get("command"),
                    "status": selected.get("status"),
                    "finite": selected.get("finite_audit", {}).get("all_finite"),
                }
            )
    with q2:
        if st.button("Save selected experiment", key="vos_save"):
            manifest = create_run_bundle(selected, label=f"vos-{_result_label(selected)}")
            st.session_state["last_manifest"] = manifest
            st.success(f"Saved: {manifest['run_dir']}")

    if queue:
        st.dataframe(pd.DataFrame(queue), use_container_width=True, hide_index=True)
    else:
        st.info("Queue is empty.")

    manifest = st.session_state.get("last_manifest")
    if manifest:
        st.subheader("Last saved experiment")
        st.json(manifest)


def main() -> None:
    _install_css()
    st.title("CDFD Runtime Studio")
    st.caption(
        "Runtime cockpit over the same deterministic engine, CLI envelopes, finite audit, and report generator."
    )
    st.session_state.setdefault("run_records", [])

    with st.sidebar:
        st.subheader("CLI parity")
        st.code(
            "python cdfd.py doctor\n"
            "python cdfd.py gallery --save-run\n"
            "python cdfd.py cdfl lint examples/heat_flow.cdfl\n"
            "python cdfd.py cdfl run examples/heat_flow.cdfl --nx 16 --ny 16\n"
            "python cdfd.py compare origins_of_life --scenarios mixed_source_surface_trap meteoritic_seed_retained\n"
            "python cdfd.py report runs/<run>/result.json --format html",
            language="bash",
        )
        st.markdown("---")
        st.markdown("**Run root:** `runs/`")
        st.markdown("**DOI:** `10.5281/zenodo.20343160`")

    tab_cockpit, tab_cdfl, tab_physics, tab_ool, tab_atlas, tab_evidence, tab_vos = st.tabs(
        [
            "Runtime Cockpit",
            "CDFL Workbench",
            "Physics Lab",
            "Origins Lab",
            "Domain Atlas",
            "Evidence & Falsification",
            "VOS Preview",
        ]
    )

    with tab_cockpit:
        _render_cockpit()
    with tab_cdfl:
        _render_cdfl_workbench()
    with tab_physics:
        _render_physics_lab()
    with tab_ool:
        _render_origins_lab()
    with tab_atlas:
        _render_domain_atlas()
    with tab_evidence:
        _render_evidence()
    with tab_vos:
        _render_vos_preview()


main()
