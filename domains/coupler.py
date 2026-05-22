class Coupler:
    def __init__(self, coupling_strength=0.1):
        self.coupling_strength = coupling_strength

    def couple(self, state_a, state_b):
        """Transfer a fraction of phi from state_a into state_b."""
        transfer = self.coupling_strength * state_a.phi.mean()
        state_b.phi += transfer

    def bidirectional(self, state_a, state_b):
        diff = state_a.phi.mean() - state_b.phi.mean()
        state_a.phi -= self.coupling_strength * diff * 0.5
        state_b.phi += self.coupling_strength * diff * 0.5


class MultiDomainCoupler:
    """Couple an arbitrary number of domain states."""

    def __init__(self, coupling_strength=0.05):
        self.strength = coupling_strength

    def couple_all(self, states):
        if len(states) < 2:
            return
        means = [s.phi.mean() for s in states]
        global_mean = sum(means) / len(means)
        for state in states:
            state.phi += self.strength * (global_mean - state.phi.mean())
