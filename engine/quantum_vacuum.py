"""
Conditional CDFT torus-knot amplitude toy model.

The equations below are postulated parametrisations for internal numerical
experiments. They do not derive vacuum properties or particle masses.
"""

import numpy as np
import math

class QuantumVacuum:
    def __init__(self, m_e=0.51099895, alpha=1/137.035999177):
        """
        Initialize a conditional amplitude ansatz from supplied values.
        It does not provide a Z3 uniqueness theorem or derive other masses.
        """
        self.m_e = m_e
        self.alpha = alpha
        self.c_n = np.sqrt(2)

        # Z3 (lepton sector) is algebraic
        self.theta_3 = 2.0 / 9.0  # Exact radians

        # Compute M_3 scale
        amps_sq_3 = sorted([(1 + self.c_n * np.cos(self.theta_3 + 2 * np.pi * k / 3))**2 for k in range(3)])
        self.m_3 = self.m_e / amps_sq_3[0]  # Normalizing to the lightest mode (electron)

        self.knots = {}

    def _q_tilde(self, n, theta):
        """Modified Koide ratio: 2n / (sum |A_k|)^2."""
        amps = [1 + self.c_n * np.cos(theta + 2 * np.pi * k / n) for k in range(n)]
        sq = sum(a**2 for a in amps)  # Flow (Phi)
        sa = sum(abs(a) for a in amps) # Capacity Limit (C)
        return sq / sa**2

    def solve_theta_n(self, n, ngrid=10_000):
        """
        Solves the postulated ansatz relation n*theta_n = Q_tilde(n, theta_n).
        Returns theta_n in radians.
        """
        if n == 3:
            return self.theta_3
        if n % 2 == 0 and n < 4:
            raise ValueError("n=2 is excluded by this postulated Fourier ansatz.")

        thetas = np.linspace(1e-9, np.pi/n - 1e-9, ngrid)
        lhs = n * thetas
        rhs = np.array([self._q_tilde(n, t) for t in thetas])
        diff = lhs - rhs

        sc = np.where(np.diff(np.sign(diff)))[0]
        if len(sc) == 0:
            raise ValueError(f"No self-consistency solution found for n={n}")

        idx = sc[0]
        t_lo, t_hi = thetas[idx], thetas[idx + 1]

        # Bisection refinement
        for _ in range(80):
            t_mid = (t_lo + t_hi) / 2
            if n * t_mid - self._q_tilde(n, t_mid) < 0:
                t_lo = t_mid
            else:
                t_hi = t_mid

        return (t_lo + t_hi) / 2

    def spawn_knot(self, n):
        """
        Evaluate a T(2,n) conditional amplitude construction.
        The returned scales and modes are model output, not physical particles.
        """
        if n in self.knots:
            return self.knots[n]

        theta_n = self.solve_theta_n(n)
        m_n = self.m_3 * (n / 3)**(0.75) # Faddeev-Niemi scaling

        amps = [(1 + self.c_n * np.cos(theta_n + 2 * np.pi * k / n)) for k in range(n)]

        masses = sorted([m_n * a**2 for a in amps])

        # Anti-phase boundary modes (A_k < 0) vs Co-phase observable modes (A_k > 0)
        n_neg = sum(1 for a in amps if a < 0)
        n_pos = n - n_neg

        # Conditional amplitude split calculation (Paper VIII archive).
        split_formula_neg = math.floor(5*n/8) - math.ceil(3*n/8) + 1
        # Correction for boundary integers (Paper IX)
        if (3*n) % 8 == 0 or (5*n) % 8 == 0:
            split_formula_neg -= 1

        self.knots[n] = {
            "n": n,
            "theta_n_rad": theta_n,
            "theta_n_deg": np.degrees(theta_n),
            "M_n": m_n,
            "masses": masses,
            "sum_masses": sum(masses),
            "conditional_sum": 2 * n * m_n,
            "claim_status": "postulated amplitude ansatz; not a particle prediction",
            "n_pos": n_pos,
            "n_neg": n_neg,
            "split_formula_neg": split_formula_neg
        }

        return self.knots[n]

    def verify_vacuum_eos(self, n):
        """
        Explicitly verify that the knot state satisfies the fundamental axiom:
        Psi = Phi / C
        """
        knot = self.knots.get(n)
        if not knot:
            knot = self.spawn_knot(n)

        theta = knot["theta_n_rad"]
        amps = [1 + self.c_n * np.cos(theta + 2 * np.pi * k / n) for k in range(n)]

        phi = sum(a**2 for a in amps)
        c = sum(abs(a) for a in amps)**2
        psi = n * theta

        return {
            "Phi": phi,
            "C": c,
            "Psi": psi,
            "Ratio": phi / c,
            "Delta": abs((phi / c) - psi)
        }


class VacuumPhaseDetector:
    """
    Detects first-order Vacuum Phase Transitions (VPT) — Discovery 23.
    When flux/capacity ratio > VPT_J_THRESHOLD and Ms_max > VPT_MS_THRESHOLD,
    the medium enters "Solid Vacuum": Ms diverges and C stiffens.
    """
    VPT_J_THRESHOLD = 0.90
    VPT_MS_THRESHOLD = 25.0

    def __init__(self):
        self.events = []

    def check(self, state):
        try:
            J = getattr(state, "J", 1.0)
            ms_max = float(np.max(state.Ms))
            mean_ratio = float(np.mean(state.phi / np.maximum(state.C, 1e-9)))
            j_ratio = mean_ratio / max(float(J), 1e-9)

            if j_ratio > self.VPT_J_THRESHOLD and ms_max > self.VPT_MS_THRESHOLD:
                state.Ms = np.clip(state.Ms, 1.0, self.VPT_MS_THRESHOLD)
                state.C = np.clip(state.C * 1.05, 1e-9, 1e6)
                event = {"t": state.t, "j_ratio": j_ratio, "ms_max": ms_max, "type": "VPT"}
                self.events.append(event)
                if hasattr(state, "meta") and isinstance(state.meta, dict):
                    state.meta["vpt_event"] = event
                return True
        except Exception:
            pass
        return False

    def stability_index(self, state, chi=137.035999177):
        """Geometric Recovery Index: SI = |mean(Φ/C) − χ*| / χ* (Discovery 35)."""
        try:
            local_ratio = float(np.mean(state.phi / np.maximum(state.C, 1e-9)))
            return abs(local_ratio - chi) / chi
        except Exception:
            return float("inf")


def measure_stability_index(state, chi=137.035999177):
    """Standalone helper — same as VacuumPhaseDetector.stability_index()."""
    try:
        local_ratio = float(np.mean(state.phi / np.maximum(state.C, 1e-9)))
        return abs(local_ratio - chi) / chi
    except Exception:
        return float("inf")
