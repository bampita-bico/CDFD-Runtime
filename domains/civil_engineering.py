from domains.base import DomainAdapter

class CivilEngineeringAdapter(DomainAdapter):
    def map_to_engine(self, data):
        structural_integrity = data.get("structural_integrity", 0.8)
        load_capacity_norm   = data.get("load_capacity_norm", 0.7)
        material_degradation = data.get("material_degradation", 0.15)
        seismic_vulnerability= data.get("seismic_vulnerability", 0.2)
        phi = max(structural_integrity * 0.5 + load_capacity_norm * 0.5, 0.01)
        C   = max(material_degradation * 0.5 + seismic_vulnerability * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Structural failure risk — critical degradation or overload"
        if psi < 0.6:  return "Below safety margins - structural-renewal flag"
        if psi <= 1.2: return "Structure within safe operational limits"
        return "Over-engineered — large safety margin, excellent longevity"
