import numpy as np
from numba import njit
from engine.config import DEFAULT_DT

# Mujjabi Vacuum Constants
CHI_ATTRACTOR = 137.035999177  # χ* = 1/α, CODATA 2022 (α⁻¹ = 137.035999177)
KAPPA_S = 0.05       # kept for backward compat; replaced by VE_* below in step()
MU_HYSTERESIS = 0.05
TAU_M = 100.0

# Surface evolution constants — VE Paper II §7: ∂S/∂t = a·Φ − b·C + c·M_s − d·S + ξ·∇²S
VE_A_S  = 0.10   # flow-driven activation
VE_B_S  = 0.05   # constraint suppression
VE_C_S  = 0.02   # memory reinforcement
VE_D_S  = 0.12   # surface decay  (> VE_A_S so S* < ∞ at equilibrium)
VE_XI_S = 0.01   # adaptive spatial spreading

# Mujjabi Hysteresis Kernel — spatial extension
LAMBDA_MS = 0.005  # spatial diffusion coefficient for M_s field
MS_MAX    = 50.0   # solid-vacuum clamp (VPT threshold from Discovery 23)

@njit(fastmath=True)
def _njit_laplacian(field):
    """Numba-accelerated 5-point Laplacian."""
    res = np.empty_like(field)
    nx, ny = field.shape
    for i in range(nx):
        for j in range(ny):
            im = (i - 1) % nx
            ip = (i + 1) % nx
            jm = (j - 1) % ny
            jp = (j + 1) % ny
            res[i, j] = field[im, j] + field[ip, j] + field[i, jm] + field[i, jp] - 4.0 * field[i, j]
    return res

@njit(fastmath=True)
def _njit_compute_derivatives(phi, C, alpha, beta, gamma, S, D, J_in=0.0):
    """Numba-accelerated derivative computation."""
    nx, ny = phi.shape
    dphi_dt = np.full_like(phi, J_in + S - D)
    dC_dt = np.empty_like(C)

    # 5-point stencil for flux and laplacian
    for i in range(nx):
        for j in range(ny):
            im = (i - 1) % nx
            ip = (i + 1) % nx
            jm = (j - 1) % ny
            jp = (j + 1) % ny

            # Flux calculation
            c_val = max(C[i, j], 1e-9)
            cr = (C[ip, j] + c_val) / 2.0
            cl = (C[im, j] + c_val) / 2.0
            cd = (C[i, jp] + c_val) / 2.0
            cu = (C[i, jm] + c_val) / 2.0

            fr = (phi[ip, j] - phi[i, j]) / cr
            fl = (phi[im, j] - phi[i, j]) / cl
            fd = (phi[i, jp] - phi[i, j]) / cd
            fu = (phi[i, jm] - phi[i, j]) / cu

            dphi_dt[i, j] += fr + fl + fd + fu

            # Constraint evolution
            lap_c = C[im, j] + C[ip, j] + C[i, jm] + C[i, jp] - 4.0 * C[i, j]
            dC_dt[i, j] = alpha[i, j] * abs(dphi_dt[i, j]) - beta[i, j] * C[i, j] + gamma[i, j] * lap_c

    return dphi_dt, dC_dt

def update_psi(state):
    """Synchronize Ψ_s with the current Φ/C/S/Ms fields and return the tensor."""
    updater = getattr(state, "update_psi", None)
    if callable(updater):
        return updater()
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    state.psi_s = (state.phi / safe_C) * getattr(state, "S", 1.0) * getattr(state, "Ms", 1.0)
    return state.psi_s

def _parameter_field(value, fallback):
    if value is None:
        return fallback
    arr = np.asarray(value, dtype=float)
    if arr.shape == ():
        return np.full_like(fallback, float(arr), dtype=float)
    return np.broadcast_to(arr, fallback.shape).astype(float, copy=False)

def laplacian(field):
    return _njit_laplacian(field)

def compute_derivatives(phi, C, alpha, beta, gamma, S, D, J_in=0.0):
    """
    Computes the instantaneous time derivatives d(phi)/dt and d(C)/dt
    using the rigorous CDFD Runtime master equations with Acceleration-driven constraints.
    Now Numba-accelerated for high performance.
    """
    return _njit_compute_derivatives(phi, C, alpha, beta, gamma, S, D, J_in)

def step(state, dt=DEFAULT_DT, S=0.0, D=0.0, alpha=None, beta=None, gamma=None, J_in=0.0):
    """
    Advances the state by dt using Runge-Kutta 4th Order (RK4) integration.
    Also updates Adaptive Surface Dynamics (S and Ms).
    """
    phi_0 = state.phi.copy()
    C_0 = state.C.copy()
    alpha = _parameter_field(alpha, state.alpha)
    beta = _parameter_field(beta, state.beta)
    gamma = _parameter_field(gamma, state.gamma)
    
    # RK4 - Step 1
    k1_phi, k1_C = compute_derivatives(phi_0, C_0, alpha, beta, gamma, S, D, J_in)
    
    # RK4 - Step 2
    phi_1 = phi_0 + 0.5 * dt * k1_phi
    C_1 = np.clip(C_0 + 0.5 * dt * k1_C, 1e-9, 1e6)
    k2_phi, k2_C = compute_derivatives(phi_1, C_1, alpha, beta, gamma, S, D, J_in)
    
    # RK4 - Step 3
    phi_2 = phi_0 + 0.5 * dt * k2_phi
    C_2 = np.clip(C_0 + 0.5 * dt * k2_C, 1e-9, 1e6)
    k3_phi, k3_C = compute_derivatives(phi_2, C_2, alpha, beta, gamma, S, D, J_in)
    
    # RK4 - Step 4
    phi_3 = phi_0 + dt * k3_phi
    C_3 = np.clip(C_0 + dt * k3_C, 1e-9, 1e6)
    k4_phi, k4_C = compute_derivatives(phi_3, C_3, alpha, beta, gamma, S, D, J_in)
    
    # Combine RK4 stages
    state.phi = phi_0 + (dt / 6.0) * (k1_phi + 2*k2_phi + 2*k3_phi + k4_phi)
    state.C = C_0 + (dt / 6.0) * (k1_C + 2*k2_C + 2*k3_C + k4_C)
    
    # Enforce physical bounds
    state.phi = np.clip(state.phi, -1e6, 1e6)
    state.C = np.clip(state.C, 1e-9, 1e6)
    
    # --- Surface Evolution: VE Paper II §7 — ∂S/∂t = a·Φ − b·C + c·M_s − d·S + ξ·∇²S ---
    try:
        dS_dt = (VE_A_S * state.phi
                 - VE_B_S * state.C
                 + VE_C_S * state.Ms
                 - VE_D_S * state.S
                 + VE_XI_S * laplacian(state.S))
        state.S = np.clip(state.S + dt * dS_dt, 0.01, 20.0)
    except Exception:
        mean_psi = state.mean_psi()
        state.S = np.clip(state.S + dt * KAPPA_S * (mean_psi - state.S), 0.01, 20.0)

    # --- Mujjabi Hysteresis Kernel — spatial, with diffusion and VPT clamp ---
    try:
        safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
        J_crit = getattr(state, "J", 1.0)
        J_crit = J_crit if J_crit > 1e-9 else 1e-9
        overload_field = np.maximum(0.0, (state.phi / safe_C) / J_crit - 1.0)
        decay = np.exp(-dt / TAU_M)
        state.Ms = (1.0
                    + (state.Ms - 1.0) * decay
                    + MU_HYSTERESIS * overload_field * TAU_M * (1.0 - decay)
                    + dt * LAMBDA_MS * laplacian(state.Ms))
        state.Ms = np.clip(state.Ms, 1.0, MS_MAX)
    except Exception:
        state.Ms = np.clip(state.Ms, 1.0, MS_MAX)
    
    chi_attractor_feedback(state, dt)
    update_psi(state)
    state.t += dt


def chi_attractor_feedback(state, dt, chi=CHI_ATTRACTOR, threshold=0.01, boost=0.001):
    """Gentle beta recovery when Φ/C mean is within 1% of the Mujjabi Attractor χ*=137.035999177."""
    try:
        local_ratio = np.mean(state.phi / np.maximum(state.C, 1e-9))
        chi_dist = abs(float(local_ratio) - chi) / chi
        if chi_dist < threshold:
            state.beta = np.clip(state.beta + boost * dt, 1e-4, 1.0)
    except Exception:
        pass

def _scalar_history_row(state):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    return {
        "t": state.t,
        "phi": mean_phi,
        "C": mean_C,
        "psi_s": state.mean_psi(),
        "S": float(np.mean(state.S)),
        "Ms": float(np.mean(state.Ms))
    }

def run(state, steps, dt=DEFAULT_DT, S=0.0, D=0.0, record=False, record_interval=1, alpha=None, beta=None, gamma=None, J_in=0.0):
    history = []
    for i in range(steps):
        step(state, dt=dt, S=S, D=D, alpha=alpha, beta=beta, gamma=gamma, J_in=J_in)
        if record and i % record_interval == 0:
            history.append(state.snapshot())
            state.record()
        elif not record:
            history.append(_scalar_history_row(state))
    return history

def stability_dt(state, dx=1.0):
    max_c = float(np.max(state.C))
    if max_c < 1e-9:
        return DEFAULT_DT
    return 0.5 * dx ** 2 / max_c


class VortexRingSolver:
    @staticmethod
    def total_energy(chi, beta, kappa):
        return chi * (np.log(8*chi) - beta) + kappa / chi

    @staticmethod
    def dE_dchi(chi, beta, kappa):
        return (np.log(8*chi) - beta + 1) - kappa / (chi**2)

    @staticmethod
    def find_equilibrium(beta, kappa, chi_min=10.0, chi_max=200.0, tol=1e-6):
        # Bisection method to find where dE_dchi = 0
        left, right = chi_min, chi_max
        if VortexRingSolver.dE_dchi(left, beta, kappa) * VortexRingSolver.dE_dchi(right, beta, kappa) > 0:
            return CHI_ATTRACTOR # Fallback
            
        while (right - left) / 2.0 > tol:
            mid = (left + right) / 2.0
            if VortexRingSolver.dE_dchi(mid, beta, kappa) == 0.0:
                return mid
            elif VortexRingSolver.dE_dchi(left, beta, kappa) * VortexRingSolver.dE_dchi(mid, beta, kappa) < 0:
                right = mid
            else:
                left = mid
        return (left + right) / 2.0

    @staticmethod
    def stability_index(phi_c_ratio, chi_local=CHI_ATTRACTOR):
        # Calculates how close the local flux ratio is to the stability attractor
        return np.abs(phi_c_ratio - chi_local) / chi_local
