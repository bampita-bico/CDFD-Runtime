from domains.base import DomainAdapter

class MaterialsScienceAdapter(DomainAdapter):
    def map_to_engine(self, data):
        strength_index   = data.get("tensile_strength_norm", 0.6)
        ductility        = data.get("ductility_index", 0.5)
        defect_density   = data.get("defect_density", 0.2)
        corrosion_index  = data.get("corrosion_index", 0.1)
        phi = max(strength_index * 0.5 + ductility * 0.5, 0.01)
        C   = max(defect_density * 0.5 + corrosion_index * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Material failure — defects and corrosion dominant"
        if psi < 0.6:  return "Degraded material — reduced performance and lifespan"
        if psi <= 1.2: return "Material in service — acceptable performance"
        return "High-performance material — exceptional strength and durability"
