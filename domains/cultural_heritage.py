from domains.base import DomainAdapter
class CulturalHeritageAdapter(DomainAdapter):
    def map_to_engine(self, data):
        preservation= data.get("preservation_index", 0.6)
        docs        = data.get("documentation_quality", 0.6)
        community   = data.get("community_engagement", 0.5)
        destruction = data.get("destruction_risk", 0.2)
        neglect     = data.get("neglect_index", 0.2)
        phi = max(preservation*0.4 + docs*0.3 + community*0.3, 0.01)
        C   = max(destruction*0.5 + neglect*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Heritage at critical risk — destruction or irreversible neglect"
        if psi < 0.6:  return "Heritage threatened — inadequate preservation"
        if psi <= 1.2: return "Heritage maintained — sites and traditions preserved"
        return "Heritage thriving — well-documented, community-owned, celebrated"
