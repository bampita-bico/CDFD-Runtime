from domains.base import DomainAdapter
class TerrorismAdapter(DomainAdapter):
    def map_to_engine(self, data):
        attack_freq = data.get("attack_frequency_norm", 0.1)
        radical     = data.get("ideological_radicalisation", 0.2)
        capability  = data.get("operational_capability", 0.2)
        ct_effect   = data.get("counter_terrorism_effectiveness", 0.7)
        deradical   = data.get("deradicalisation_programmes", 0.4)
        phi = max(attack_freq*0.4 + radical*0.3 + capability*0.3, 0.01)
        C   = max(ct_effect*0.5 + deradical*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Terrorism negligible — threat contained, radicalisation low"
        if psi < 0.6:  return "Elevated threat — radicalisation growing"
        if psi <= 1.2: return "Active terrorism — attacks frequent, security response maximal"
        return "Terrorism crisis — state capacity overwhelmed by insurgency"
