"""
Coherence Field Ω(x,t) — VE Paper IV §2-3 & Paper XII §4

Governs synchronization of the Ψ_s field across space.
Superconductivity is the limit Ω → 1 (constraint reallocation: C_diss → 0, C_phase → ρ_s).

Evolution: ∂Ω/∂t = κ_Ω·(Ψ_target − |∇Ψ_s|) − λ_Ω·Ω + η_Ω·∇²Ω
"""
import numpy as np
from engine.physics import laplacian

KAPPA_OMEGA = 0.05   # growth rate when Ψ_s is spatially flat
LAMBDA_OMEGA = 0.02  # natural decoherence
ETA_OMEGA = 0.01     # spatial synchronization spread
PSI_TARGET = 1.0     # target equilibrium Ψ_s


class CoherenceField:
    def __init__(self, nx, ny, init=0.5):
        self.Omega = np.full((nx, ny), init, dtype=float)

    def update(self, state, dt):
        try:
            psi = state.psi_s
            grad_psi_mag = np.sqrt(
                ((np.roll(psi, -1, 0) - np.roll(psi, 1, 0)) / 2) ** 2
                + ((np.roll(psi, -1, 1) - np.roll(psi, 1, 1)) / 2) ** 2
            )
            dOmega = (
                KAPPA_OMEGA * (PSI_TARGET - grad_psi_mag)
                - LAMBDA_OMEGA * self.Omega
                + ETA_OMEGA * laplacian(self.Omega)
            )
            self.Omega = np.clip(self.Omega + dt * dOmega, 0.0, 1.0)
        except Exception:
            pass

    def mean_coherence(self):
        return float(np.mean(self.Omega))

    def coherence_efficiency(self, state):
        return float(np.mean(self.Omega) * np.mean(state.phi))
