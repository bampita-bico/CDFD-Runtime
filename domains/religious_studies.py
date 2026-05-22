from domains.base import DomainAdapter
class ReligiousStudiesAdapter(DomainAdapter):
    def map_to_engine(self, data):
        participation = data.get("religious_participation", 0.5)
        interfaith    = data.get("interfaith_harmony", 0.6)
        inst_trust    = data.get("institutional_trust", 0.5)
        sectarian     = data.get("sectarian_conflict", 0.15)
        radical       = data.get("radicalisation_index", 0.1)
        phi = max(participation*0.4 + interfaith*0.4 + inst_trust*0.2, 0.01)
        C   = max(sectarian*0.5 + radical*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Religious crisis — sectarianism destabilising society"
        if psi < 0.6:  return "Religious tension — interfaith friction significant"
        if psi <= 1.2: return "Religious coexistence — diversity respected"
        return "Flourishing spiritual life — harmony and high participation"
