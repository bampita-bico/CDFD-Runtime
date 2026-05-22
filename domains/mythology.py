from domains.base import DomainAdapter
class MythologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        narrative_vitality = data.get("narrative_vitality", 0.5)
        ritual_practice    = data.get("ritual_practice_index", 0.4)
        scholarly_interest = data.get("scholarly_interest", 0.5)
        secularisation     = data.get("secularisation_index", 0.4)
        narrative_fragm    = data.get("narrative_fragmentation", 0.2)
        phi = max(narrative_vitality*0.4 + ritual_practice*0.3 + scholarly_interest*0.3, 0.01)
        C   = max(secularisation*0.5 + narrative_fragm*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Mythology extinct — narratives lost, no living tradition"
        if psi < 0.6:  return "Mythology fading — academic interest only, no living practice"
        if psi <= 1.2: return "Mythology alive — narratives shaping culture"
        return "Mythological renaissance — stories actively shaping identity and art"
