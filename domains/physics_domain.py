from domains.base import DomainAdapter


class PhysicsAdapter(DomainAdapter):
    def map_to_engine(self, system):
        phi = system.get("energy", 1.0)
        C = system.get("resistance", 1.0)
        return max(phi, 0.01), max(C, 0.01)

    def interpret(self, state):
        psi = state.mean_psi()
        if psi > 1.5:
            return "high propagation efficiency — low resistance medium"
        if psi < 0.5:
            return "poor propagation — high resistance"
        return "balanced field propagation"
