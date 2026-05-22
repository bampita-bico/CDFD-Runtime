"""
Civilization Dynamics — Archeology, Migrations, Settlements, and Empires.
Applying the CDFT framework to anthropology and human history.
"""
import numpy as np


def apply_civilization(state, dt=0.01):
    try:
        _migrations_and_settlements(state, dt)
        _rise_and_fall_of_empires(state, dt)
        _archaeological_stratigraphy(state, dt)
    except Exception:
        raise


def _migrations_and_settlements(state, dt):
    """
    Models human migration and settlement formation.
    Phi (J) = Population density / migratory flux.
    Lambda (C) = Geographic carrying capacity / resource friction.
    """
    # Populations migrate away from Overload (Psi > 1.2, overpopulation)
    # or Depletion (Psi < 0.5, famine) toward stable regimes (Psi ~ 1.0)

    grad_psi_y, grad_psi_x = np.gradient(state.psi)

    # Migratory flux: flow moves down the gradient of Psi-stress
    # (i.e., away from |Psi - 1.0|)
    stress = np.abs(state.psi - 1.0)
    grad_stress_y, grad_stress_x = np.gradient(stress)

    # Advect population (Phi) away from stress
    migratory_flow_x = -grad_stress_x * state.phi
    migratory_flow_y = -grad_stress_y * state.phi

    # Divergence of migratory flow
    div_mig_y, _ = np.gradient(migratory_flow_y, axis=0)
    _, div_mig_x = np.gradient(migratory_flow_x, axis=1)

    state.phi += dt * 0.1 * (div_mig_x + div_mig_y)

    # Settlements form where population stabilizes (low stress, high Phi)
    settlements = (stress < 0.2) & (state.phi > float(np.mean(state.phi)))
    if np.any(settlements):
        # Infrastructure building: population actively lowers local survival constraint
        # (e.g., agriculture, irrigation, housing)
        state.C[settlements] = np.maximum(state.C[settlements] - dt * 0.05 * state.phi[settlements], 0.1)


def _rise_and_fall_of_empires(state, dt):
    """
    Models the lifecycle of empires (Turchin/Ibn Khaldun dynamics via AFL).
    Rise: State lowers internal C, captures external Phi.
    Peak: Psi ~ 1.0 (Pax Romana).
    Fall: Administrative burden (alpha * |J|) accumulates faster than Phi generation.
    """
    # High capacity regions (high Phi, optimized C) become imperial cores
    imperial_cores = (state.phi > float(np.mean(state.phi)) * 2.0)

    if np.any(imperial_cores):
        # 1. Expansion (Rise)
        # Cores project power, synchronizing neighboring regions by lowering trade/military constraints
        grad_C_y, grad_C_x = np.gradient(state.C)
        state.C -= dt * 0.02 * (grad_C_x**2 + grad_C_y**2) * state.phi

        # 2. Institutional Decay (Fall)
        # Maintaining the empire requires bureaucracy and military overhead.
        # This is the AFL alpha term: high continuous flux breeds systemic constraints.
        # Over time, maintenance costs (C) rise inevitably.
        state.C[imperial_cores] += dt * 0.08 * state.phi[imperial_cores]

        # 3. Collapse (Fragmentation)
        # When C eclipses Phi (Psi << 1.0), the empire can no longer maintain its complexity.
        collapse = (state.C > state.phi * 1.5) & imperial_cores
        if np.any(collapse):
            # Population/wealth (Phi) plummets, borders (C) shatter into high-friction local warlords
            state.phi[collapse] *= (1.0 - dt * 0.5)
            state.C[collapse] += dt * 2.0


def _archaeological_stratigraphy(state, dt):
    """
    Models the formation of the archaeological record.
    When a settlement or empire collapses, its optimized constraints (infrastructure)
    don't vanish—they become ruins (fossilized C).
    """
    if not hasattr(state, 'ruins_layer'):
        state.ruins_layer = np.zeros_like(state.C)

    # Regions that lost massive population (abandoned cities)
    # If Phi is low but C was previously altered
    abandoned = (state.phi < 0.1) & (state.C < 1.0)

    if np.any(abandoned):
        # The infrastructure becomes ruins, permanently recorded in the stratigraphic layer
        state.ruins_layer[abandoned] += dt * 0.01
        # Over time, natural constraints (forests, sand) reclaim the area, raising C back up
        state.C[abandoned] += dt * 0.05
