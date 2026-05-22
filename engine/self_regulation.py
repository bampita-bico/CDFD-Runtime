"""Level 8 — Self-Regulation Engine.

The system reads its own Ψ field and autonomously adjusts alpha/beta/gamma
to stay near equilibrium. No external AI — pure closed-loop dynamics.

Biological analogue: homeostasis.
Physical analogue: negative feedback in control systems.
"""
import numpy as np


class RegulationParams:
    def __init__(self, alpha, beta, gamma):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

    def __repr__(self):
        return f"RegulationParams(α={self.alpha:.4f}, β={self.beta:.4f}, γ={self.gamma:.4f})"


class SelfRegulator:
    """Continuously adjusts engine parameters to keep Ψ near target."""

    def __init__(self, params, target_psi=1.0,
                 sensitivity=0.05, max_step=0.01,
                 alpha_bounds=(1e-4, 2.0),
                 beta_bounds=(1e-4, 1.0),
                 gamma_bounds=(1e-4, 1.0)):
        self.params = params
        self.target = target_psi
        self.sensitivity = sensitivity
        self.max_step = max_step
        self.alpha_bounds = alpha_bounds
        self.beta_bounds = beta_bounds
        self.gamma_bounds = gamma_bounds
        self._error_integral = 0.0

    def regulate(self, state):
        """One regulation step — call after each engine cycle."""
        try:
            mean_psi = state.mean_psi()
            error = mean_psi - self.target
            self._error_integral += error

            delta = self.sensitivity * abs(error)
            delta = float(np.clip(delta, 0.0, self.max_step))

            if error < 0:
                # Ψ too low: reduce new constraint and increase relaxation.
                self.params.alpha = float(np.clip(
                    self.params.alpha - delta,
                    *self.alpha_bounds
                ))
                self.params.beta = float(np.clip(
                    self.params.beta + delta * 0.5,
                    *self.beta_bounds
                ))
            else:
                # Ψ too high: form and retain more constraint.
                self.params.alpha = float(np.clip(
                    self.params.alpha + delta,
                    *self.alpha_bounds
                ))
                self.params.beta = float(np.clip(
                    self.params.beta - delta * 0.3,
                    *self.beta_bounds
                ))

            # Diffusion nudge: spread regulation smoothly
            if abs(error) > 0.3:
                self.params.gamma = float(np.clip(
                    self.params.gamma + 0.001,
                    *self.gamma_bounds
                ))

            state.alpha[...] = self.params.alpha
            state.beta[...] = self.params.beta
            state.gamma[...] = self.params.gamma

        except Exception:
            pass

        return self.params

    def reset_integral(self):
        self._error_integral = 0.0

    def status(self, state):
        psi = state.mean_psi()
        return {
            "psi": psi,
            "error": self.target - psi,
            "alpha": self.params.alpha,
            "beta": self.params.beta,
            "gamma": self.params.gamma,
            "integral": self._error_integral,
        }


def regulate_step(state, params, target_psi=1.0, sensitivity=0.05):
    """Stateless single-step regulation — convenience wrapper."""
    regulator = SelfRegulator(params, target_psi=target_psi, sensitivity=sensitivity)
    return regulator.regulate(state)
