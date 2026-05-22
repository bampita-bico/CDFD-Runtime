from domains.base import DomainAdapter

class InterstateWarAdapter(DomainAdapter):
    def map_to_engine(self, data):
        mil_capability = data.get("military_capability", 0.5)
        alliance_str   = data.get("alliance_strength", 0.4)
        deterrence     = data.get("deterrence_index", 0.6)
        diplomacy      = data.get("diplomatic_relations", 0.5)
        phi = max(mil_capability*0.6 + alliance_str*0.4, 0.01)
        C   = max(deterrence*0.6 + diplomacy*0.4, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.4:  return "Stable deterrence — military balance preventing conflict"
        if psi < 0.7:  return "Armed peace — deterrence holding, tension remains"
        if psi <= 1.2: return "Crisis escalation — diplomatic channels breaking down"
        return "War imminent — military capability overwhelming deterrence"
