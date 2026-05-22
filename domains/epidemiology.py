from domains.base import DomainAdapter

class EpidemiologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        r0          = data.get("R0", 2.5)
        vaccination = data.get("vaccination_rate", 0.5)   # 0-1
        cfr         = data.get("case_fatality_rate", 0.01)
        contacts    = data.get("daily_contacts", 10)
        phi = max(r0 * (1.0 - vaccination) * 0.5 + min(contacts/20.0,1.0) * 0.5, 0.01)
        C   = max(vaccination * 0.6 + (1.0 - cfr * 10) * 0.4, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.5:  return "Epidemic controlled — Reff < 1, cases declining"
        if psi <= 1.0: return "Endemic equilibrium — sustained low-level transmission"
        if psi <= 2.0: return "Active outbreak — intervention scale-up needed"
        return "Epidemic surge — declare public health emergency"
