from domains.base import DomainAdapter
class EthicsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        moral_consensus   = data.get("moral_consensus_index", 0.5)
        institutional_ethics = data.get("institutional_ethics_norm", 0.6)
        applied_effectiveness = data.get("applied_ethics_effectiveness", 0.5)
        moral_relativism  = data.get("moral_relativism_index", 0.3)
        enforcement_gap   = data.get("enforcement_gap", 0.3)
        phi = max(moral_consensus*0.3 + institutional_ethics*0.3 + applied_effectiveness*0.4, 0.01)
        C   = max(moral_relativism*0.5 + enforcement_gap*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Ethical collapse — moral framework absent, institutions corrupt"
        if psi < 0.6:  return "Ethical weakness — norms unenforced, relativism dominant"
        if psi <= 1.2: return "Ethics functioning — norms upheld and applied"
        return "Strong ethical culture — high consensus, robust institutions, effective enforcement"
