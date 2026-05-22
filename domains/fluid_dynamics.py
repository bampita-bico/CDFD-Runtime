from domains.base import DomainAdapter

class FluidDynamicsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        velocity     = data.get("flow_velocity_m_s", 1.0) / 10.0
        reynolds     = data.get("reynolds_number", 1000) / 10000.0
        viscosity    = data.get("dynamic_viscosity", 0.1)
        turbulence   = data.get("turbulence_intensity", 0.1)
        phi = max(min(velocity, 1.0) * 0.5 + min(reynolds, 1.0) * 0.5, 0.01)
        C   = max(viscosity * 0.5 + turbulence * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Stagnant flow — viscosity or turbulence blocking motion"
        if psi < 0.6:  return "Laminar but sluggish — low Reynolds regime"
        if psi <= 1.2: return "Smooth efficient flow — optimal fluid dynamics"
        return "High-velocity turbulent flow — energy transport maximal"
