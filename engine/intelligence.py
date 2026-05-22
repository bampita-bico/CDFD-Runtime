"""
Intelligence module (Emergent pattern analysis).
Detects coherent features and oscillatory behaviors in the flow/constraint
system without making external model calls.
"""
import numpy as np
import logging
from engine.config import LOG_FAILURES

logger = logging.getLogger(__name__)


def apply_intelligence(state, dt=0.01):
    """
    Performs pattern detection on the current state.
    Runs non-blocking checks to identify if macroscopic 'intelligence' 
    (stable homeostatic loops or coherent signal propagation) is emerging.
    """
    try:
        # Calculate gradients of Psi to find regions of high information density
        grad_y, grad_x = np.gradient(state.psi)
        grad_mag = np.sqrt(grad_x**2 + grad_y**2)
        
        # Coherence is high where Psi is near 1 (equilibrium) but flow is active
        # Intelligence emerges at the boundary of chaos (high phi, balanced psi)
        coherence = np.where(np.abs(state.psi - 1.0) < 0.1, state.phi, 0)
        
        mean_coherence = float(np.mean(coherence))
        max_grad = float(np.max(grad_mag))
        
        # Add intelligence metrics directly to state tracking without making LLM calls
        if not hasattr(state, "intelligence_metrics"):
            state.intelligence_metrics = []
            
        state.intelligence_metrics.append({
            "t": state.t,
            "mean_coherence": mean_coherence,
            "max_gradient": max_grad,
            "is_emergent": mean_coherence > float(np.mean(state.phi)) * 0.5
        })
        
        # Let the system slightly reinforce coherent regions
        # Intelligence acts to optimize constraint to match flow
        if mean_coherence > 0.1:
            coherent_mask = coherence > 0
            # Nudge C toward Phi so Psi approaches the balanced regime.
            state.C[coherent_mask] += dt * 0.01 * (state.phi[coherent_mask] - state.C[coherent_mask])

    except Exception as e:
        if LOG_FAILURES:
            logger.warning("intelligence analysis failed: %s", e)
