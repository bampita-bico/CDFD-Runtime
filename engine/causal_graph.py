"""Level 14 — Causal Graph.

From simulation history alone, builds a directed graph of what drives what.
Uses lagged correlation (Granger-style) to infer causality between parameters
and outcomes — no AI, pure statistics.

Question answered: "Which parameter CAUSED which outcome in this run?"
"""
import numpy as np


def lagged_correlation(series_x, series_y, lag=1):
    """Correlation of x[t] with y[t+lag] — does x predict y?"""
    if len(series_x) <= lag:
        return 0.0
    x = series_x[:-lag]
    y = series_y[lag:]
    n = len(x)
    if n < 2:
        return 0.0
    mx, my = sum(x)/n, sum(y)/n
    num = sum((a-mx)*(b-my) for a, b in zip(x, y))
    dx = sum((a-mx)**2 for a in x)**0.5
    dy = sum((b-my)**2 for b in y)**0.5
    if dx < 1e-12 or dy < 1e-12:
        return 0.0
    return num / (dx * dy)


def granger_test(cause, effect, max_lag=3):
    """Returns the max absolute lagged correlation across lags 1..max_lag."""
    scores = [abs(lagged_correlation(cause, effect, lag=k))
              for k in range(1, max_lag + 1)]
    return max(scores) if scores else 0.0


class CausalGraph:
    def __init__(self, threshold=0.3):
        self.threshold = threshold
        self.nodes = []
        self.edges = []

    def build(self, series_dict, max_lag=3):
        """
        series_dict: {name: [values over time], ...}
        Adds a directed edge A→B if A Granger-causes B above threshold.
        """
        self.nodes = list(series_dict.keys())
        self.edges = []
        keys = self.nodes

        for cause in keys:
            for effect in keys:
                if cause == effect:
                    continue
                score = granger_test(series_dict[cause], series_dict[effect], max_lag)
                if score >= self.threshold:
                    self.edges.append({
                        "from": cause,
                        "to": effect,
                        "strength": round(score, 4),
                    })

        self.edges.sort(key=lambda e: -e["strength"])
        return self

    def strongest(self, n=5):
        return self.edges[:n]

    def causes_of(self, effect):
        return [e for e in self.edges if e["to"] == effect]

    def effects_of(self, cause):
        return [e for e in self.edges if e["from"] == cause]

    def summary(self):
        return {
            "nodes": self.nodes,
            "n_edges": len(self.edges),
            "strongest": self.strongest(5),
        }

    def to_dot(self):
        """Returns the graph in Graphviz DOT format for professional visualization."""
        lines = ["digraph CausalGraph {", "    rankdir=LR;", "    node [shape=box, style=filled, fillcolor=lightblue];"]
        for edge in self.edges:
            weight = edge["strength"]
            label = f"{weight:.2f}"
            penwidth = weight * 5
            lines.append(f'    "{edge["from"]}" -> "{edge["to"]}" [label="{label}", penwidth={penwidth:.2f}];')
        lines.append("}")
        return "\n".join(lines)

    def to_json(self):
        """Returns the graph structure in standard JSON format."""
        import json
        return json.dumps({
            "nodes": self.nodes,
            "edges": self.edges
        }, indent=2)


def extract_series(history):
    """Pull numeric time series out of a history list of dicts."""
    if not history:
        return {}
    keys = [k for k in history[0] if k != "t"]
    series = {}
    for key in keys:
        values = []
        for row in history:
            value = row.get(key)
            try:
                number = float(value)
            except (TypeError, ValueError):
                values = []
                break
            if not np.isfinite(number):
                values = []
                break
            values.append(number)
        if len(values) == len(history):
            series[key] = values
    return series


def build_causal_graph(history, extra_series=None, threshold=0.3):
    series = extract_series(history)
    if extra_series:
        series.update(extra_series)
    graph = CausalGraph(threshold=threshold)
    graph.build(series)
    return graph
