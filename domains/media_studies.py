from domains.base import DomainAdapter
class MediaStudiesAdapter(DomainAdapter):
    def map_to_engine(self, data):
        plurality    = data.get("media_plurality", 0.6)
        info_flow    = data.get("information_flow", 0.6)
        trust        = data.get("public_trust_media", 0.5)
        censorship   = data.get("censorship_index", 0.2)
        misinfo      = data.get("misinformation_index", 0.3)
        phi = max(plurality*0.4 + info_flow*0.4 + trust*0.2, 0.01)
        C   = max(censorship*0.5 + misinfo*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Information collapse — censorship or misinformation dominant"
        if psi < 0.6:  return "Degraded media ecosystem — trust and plurality weakened"
        if psi <= 1.2: return "Healthy media — plurality and information flow maintained"
        return "Vibrant media ecosystem — high trust, diverse and free"
