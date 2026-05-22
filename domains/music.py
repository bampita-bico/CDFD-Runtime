from domains.base import DomainAdapter
class MusicAdapter(DomainAdapter):
    def map_to_engine(self, data):
        creative    = data.get("creative_output_norm", 0.6)
        audience    = data.get("audience_reach_norm", 0.5)
        innovation  = data.get("innovation_index", 0.4)
        censorship  = data.get("censorship_index", 0.1)
        funding_s   = data.get("funding_scarcity", 0.3)
        phi = max(creative*0.4 + audience*0.3 + innovation*0.3, 0.01)
        C   = max(censorship*0.5 + funding_s*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Music culture suppressed — censorship or economic collapse"
        if psi < 0.6:  return "Declining music scene — funding and innovation constrained"
        if psi <= 1.2: return "Vibrant music culture — active creation and audiences"
        return "Musical renaissance — innovation and reach extraordinary"
