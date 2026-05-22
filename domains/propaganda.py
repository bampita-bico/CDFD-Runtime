from domains.base import DomainAdapter
class PropagandaAdapter(DomainAdapter):
    def map_to_engine(self, data):
        reach       = data.get("message_reach_norm", 0.5)
        coherence   = data.get("narrative_coherence", 0.6)
        repetition  = data.get("repetition_saturation", 0.4)
        counter_n   = data.get("counter_narrative_strength", 0.5)
        media_lit   = data.get("media_literacy", 0.5)
        phi = max(reach*0.4 + coherence*0.3 + repetition*0.3, 0.01)
        C   = max(counter_n*0.5 + media_lit*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Propaganda ineffective — narrative not believed or reaching audience"
        if psi < 0.6:  return "Moderate influence — competing narratives limiting reach"
        if psi <= 1.2: return "Effective propaganda — narrative establishing itself"
        return "Total information dominance — counter-narrative eliminated"
