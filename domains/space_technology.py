from domains.base import DomainAdapter

class SpaceTechnologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        launch_reliability = data.get("launch_reliability", 0.95)
        mission_power      = data.get("power_budget_norm", 0.7)
        radiation_exposure = data.get("radiation_dose_norm", 0.2)
        orbital_debris     = data.get("debris_collision_risk", 0.05)
        phi = max(launch_reliability * 0.5 + mission_power * 0.5, 0.01)
        C   = max(radiation_exposure * 0.5 + orbital_debris * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Mission failure — launch or power systems critical"
        if psi < 0.6:  return "Mission at risk — radiation or debris threatening systems"
        if psi <= 1.2: return "Mission nominal — spacecraft operating within parameters"
        return "Excellent mission performance — full capability in orbit"
