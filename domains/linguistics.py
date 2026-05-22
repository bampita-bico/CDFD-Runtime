from domains.base import DomainAdapter

class LinguisticsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        speakers      = data.get("speaker_count_millions", 1.0)
        literacy      = data.get("literacy_rate", 0.8)        # 0-1
        media_presence= data.get("media_presence", 0.5)       # 0-1
        endangerment  = data.get("endangerment_level", 0.1)   # 0=safe, 1=extinct
        phi = max(min(speakers/100.0,1.0) * 0.3 + literacy * 0.3 + media_presence * 0.4, 0.01)
        C   = max(endangerment * 0.7 + (1.0 - media_presence) * 0.3, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Language critically endangered — documentation urgent"
        if psi < 0.6:  return "Language under threat — revitalisation programmes needed"
        if psi <= 1.2: return "Language in healthy use"
        return "Dominant language — monitor for displacement of minority languages"
