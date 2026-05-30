"""Shared plotting helpers for the CDFD Runtime Streamlit dashboard."""
from __future__ import annotations

import io
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REGIME_LOW = 0.8
REGIME_HIGH = 1.2
REGIME_COLORS = {
    "constrained": "#3498DB",
    "balanced": "#27AE60",
    "stable": "#27AE60",
    "overload": "#E74C3C",
}


def normalize_regime(value: Any) -> str:
    text = str(value or "").strip().lower()
    if text == "stable":
        return "balanced"
    if text in REGIME_COLORS:
        return text
    return "balanced"


def history_to_dataframe(history: list[dict[str, Any]]) -> pd.DataFrame:
    if not history:
        return pd.DataFrame()
    df = pd.DataFrame(history)
    if "regime" in df:
        df["regime"] = df["regime"].map(normalize_regime)
    return df


def add_regime_bands(ax: plt.Axes, t_min: float, t_max: float, y_top: float | None = None) -> None:
    top = y_top if y_top is not None else max(REGIME_HIGH * 1.5, 2.0)
    ax.axhspan(0, REGIME_LOW, alpha=0.08, color=REGIME_COLORS["constrained"], label="constrained (<0.8)")
    ax.axhspan(REGIME_LOW, REGIME_HIGH, alpha=0.08, color=REGIME_COLORS["stable"], label="balanced (0.8–1.2)")
    ax.axhspan(REGIME_HIGH, top, alpha=0.08, color=REGIME_COLORS["overload"], label="overload (>1.2)")
    ax.set_xlim(t_min, t_max)


def plot_psi_trajectory(df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 3.5))
    if df.empty or "psi_s" not in df.columns:
        ax.set_title("No trajectory data")
        return fig
    t = df["t"] if "t" in df.columns else df.index
    ax.plot(t, df["psi_s"], color="#2E75B6", lw=2, label=r"$\Psi_s$")
    t_min, t_max = float(t.min()), float(t.max())
    y_max = max(float(df["psi_s"].max()) * 1.1, REGIME_HIGH * 1.2)
    add_regime_bands(ax, t_min, t_max, y_top=y_max)
    ax.set_ylim(0, y_max)
    ax.set_xlabel("Time")
    ax.set_ylabel(r"$\Psi_s$")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_title("Operating ratio trajectory")
    fig.tight_layout()
    return fig


def plot_flux_constraint(df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 3.5))
    if df.empty:
        ax.set_title("No flux data")
        return fig
    t = df["t"] if "t" in df.columns else df.index
    if "phi" in df.columns:
        ax.plot(t, df["phi"], color="#C0392B", lw=2, label=r"$\Phi$ (mean)")
    if "C" in df.columns:
        ax.plot(t, df["C"], color="#8E44AD", lw=2, label=r"$C$ (mean)")
    ax.set_xlabel("Time")
    ax.legend()
    ax.set_title("Mean flux vs constraint")
    fig.tight_layout()
    return fig


def plot_field_heatmap(field: np.ndarray, title: str, cmap: str = "viridis") -> plt.Figure:
    fig, ax = plt.subplots(figsize=(5, 4))
    im = ax.imshow(field.T, origin="lower", cmap=cmap, aspect="auto")
    ax.set_title(title)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    return fig


def plot_snapshot_grid(snapshot: dict[str, Any]) -> plt.Figure:
    fields = [
        ("phi", r"$\Phi$ flow", "viridis"),
        ("C", r"$C$ constraint", "magma"),
        ("psi_s", r"$\Psi_s$", "RdYlGn_r"),
        ("Ms", r"$M_s$ memory", "cividis"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(9, 7))
    for ax, (key, title, cmap) in zip(axes.flat, fields):
        data = np.asarray(snapshot.get(key, np.zeros((2, 2))), dtype=float)
        im = ax.imshow(data.T, origin="lower", cmap=cmap, aspect="auto")
        ax.set_title(title)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        fig.colorbar(im, ax=ax, fraction=0.046)
    fig.suptitle(f"Replay snapshot t={float(snapshot.get('t', 0.0)):.4f}")
    fig.tight_layout()
    return fig


def figure_to_bytes(fig: plt.Figure, fmt: str = "png") -> bytes:
    buffer = io.BytesIO()
    fig.savefig(buffer, format=fmt, bbox_inches="tight", dpi=180)
    return buffer.getvalue()


def plot_aromatic_source_mix(rows: list[dict[str, Any]]) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(9, 4))
    labels = [r["scenario"] for r in rows]
    scores = [float(r["functional_score"]) for r in rows]
    colors = ["#27AE60" if s == max(scores) else "#7F8C8D" for s in scores]
    ax.barh(labels, scores, color=colors)
    ax.set_xlabel("Functional score (retained pool × coupling / (1 + damage))")
    ax.set_title("Part II Paper 7 — aromatic source-mix scenarios")
    fig.tight_layout()
    return fig


def plot_causal_graph(edges: list[dict[str, Any]], nodes: list[str]) -> plt.Figure:
    """Simple circular layout when Graphviz is unavailable."""
    fig, ax = plt.subplots(figsize=(7, 7))
    if not nodes:
        ax.text(0.5, 0.5, "No causal edges above threshold", ha="center", va="center")
        ax.axis("off")
        return fig

    n = len(nodes)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    pos = {node: (np.cos(a), np.sin(a)) for node, a in zip(nodes, angles)}

    for edge in edges[:12]:
        x0, y0 = pos[edge["from"]]
        x1, y1 = pos[edge["to"]]
        strength = float(edge.get("strength", 0.3))
        ax.annotate(
            "",
            xy=(x1, y1),
            xytext=(x0, y0),
            arrowprops=dict(arrowstyle="->", lw=1 + 3 * strength, color="#34495E", alpha=0.7),
        )
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        ax.text(mx, my, f"{strength:.2f}", fontsize=7, ha="center")

    for node, (x, y) in pos.items():
        ax.scatter([x], [y], s=400, c="#AED6F1", edgecolors="#2E86C1", zorder=3)
        ax.text(x, y, node, ha="center", va="center", fontsize=8, fontweight="bold")

    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.4, 1.4)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Granger-style causal edges (simulation history)")
    fig.tight_layout()
    return fig
