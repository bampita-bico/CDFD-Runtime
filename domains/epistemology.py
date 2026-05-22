from domains.base import DomainAdapter
class EpistemologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        evidence_quality = data.get("evidence_quality", 0.7)
        justification    = data.get("justification_strength", 0.6)
        scepticism_load  = data.get("radical_scepticism", 0.2)
        bias_load        = data.get("epistemic_bias", 0.25)
        phi = max(evidence_quality*0.5 + justification*0.5, 0.01)
        C   = max(scepticism_load*0.5 + bias_load*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Epistemic collapse — knowledge unjustifiable, scepticism total"
        if psi < 0.6:  return "Weak epistemics — evidence and justification poor"
        if psi <= 1.2: return "Knowledge well-grounded — evidence and justification adequate"
        return "Epistemic excellence — strong evidence, rigorous justification"
