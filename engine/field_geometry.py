"""Level 12 — Field Geometry.

Runs Φ/C/Ψ dynamics on arbitrary graph topologies instead of flat grids.
Nodes carry scalar Φ and C values. Edges carry flux.

This lets the same equations model:
  - blood vessel networks
  - neural graphs
  - social networks
  - power grids
  - road systems
"""
import numpy as np


class FieldNode:
    def __init__(self, node_id, phi=1.0, C=1.0):
        self.id = node_id
        self.phi = phi
        self.C = C
        self.psi = phi / max(C, 1e-9)


class FieldGraph:
    def __init__(self):
        self.nodes = {}
        self.adjacency = {}

    def add_node(self, node_id, phi=1.0, C=1.0):
        self.nodes[node_id] = FieldNode(node_id, phi, C)
        self.adjacency.setdefault(node_id, [])

    def add_edge(self, a, b, weight=1.0):
        self.adjacency.setdefault(a, []).append((b, weight))
        self.adjacency.setdefault(b, []).append((a, weight))

    def neighbors(self, node_id):
        return self.adjacency.get(node_id, [])

    def _flux(self, src, dst, weight):
        src_node = self.nodes[src]
        dst_node = self.nodes[dst]
        mean_C = (src_node.C + dst_node.C) / 2.0 + 1e-9
        return weight * (src_node.phi - dst_node.phi) / mean_C

    def step(self, dt=0.01, alpha=0.1, beta=0.05, S=0.0, D=0.0):
        dphi = {}
        dC = {}

        for nid, node in self.nodes.items():
            flux_in = 0.0
            for neighbor_id, weight in self.neighbors(nid):
                nb = self.nodes[neighbor_id]
                mean_C = (node.C + nb.C) / 2.0 + 1e-9
                flux_in += weight * (nb.phi - node.phi) / mean_C
            dphi[nid] = dt * (flux_in + S - D)
            dC[nid] = dt * (alpha * abs(node.phi) - beta * node.C)

        for nid in self.nodes:
            self.nodes[nid].phi = float(np.clip(
                self.nodes[nid].phi + dphi[nid], -1e6, 1e6
            ))
            self.nodes[nid].C = float(np.clip(
                self.nodes[nid].C + dC[nid], 1e-9, 1e6
            ))
            self.nodes[nid].psi = (
                self.nodes[nid].phi / max(self.nodes[nid].C, 1e-9)
            )

    def run(self, steps=50, dt=0.01, alpha=0.1, beta=0.05):
        history = []
        for _ in range(steps):
            self.step(dt=dt, alpha=alpha, beta=beta)
            psi_vals = [n.psi for n in self.nodes.values()]
            history.append({
                "mean_psi": float(np.mean(psi_vals)),
                "max_psi": float(np.max(psi_vals)),
                "min_psi": float(np.min(psi_vals)),
            })
        return history

    def summary(self):
        psi_vals = [n.psi for n in self.nodes.values()]
        phi_vals = [n.phi for n in self.nodes.values()]
        return {
            "n_nodes": len(self.nodes),
            "n_edges": sum(len(v) for v in self.adjacency.values()) // 2,
            "mean_psi": float(np.mean(psi_vals)),
            "mean_phi": float(np.mean(phi_vals)),
        }

    def bottlenecks(self, threshold=0.5):
        """Nodes where Ψ < threshold — choke points in the system."""
        return [nid for nid, n in self.nodes.items() if n.psi < threshold]

    def hubs(self, threshold=1.5):
        """Nodes where Ψ > threshold — overloaded flow concentrations."""
        return [nid for nid, n in self.nodes.items() if n.psi > threshold]


def make_chain(n, phi=1.0, C=1.0):
    g = FieldGraph()
    for i in range(n):
        g.add_node(i, phi=phi, C=C)
    for i in range(n - 1):
        g.add_edge(i, i + 1)
    return g


def make_ring(n, phi=1.0, C=1.0):
    g = make_chain(n, phi, C)
    g.add_edge(0, n - 1)
    return g


def make_star(n_leaves, phi=1.0, C=1.0):
    g = FieldGraph()
    g.add_node(0, phi=phi * 2, C=C)
    for i in range(1, n_leaves + 1):
        g.add_node(i, phi=phi, C=C)
        g.add_edge(0, i)
    return g


def make_grid_graph(nx, ny, phi=1.0, C=1.0):
    g = FieldGraph()
    for i in range(nx):
        for j in range(ny):
            g.add_node((i, j), phi=phi, C=C)
    for i in range(nx):
        for j in range(ny):
            if i + 1 < nx:
                g.add_edge((i, j), (i + 1, j))
            if j + 1 < ny:
                g.add_edge((i, j), (i, j + 1))
    return g
