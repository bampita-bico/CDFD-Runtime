from domains.base import DomainAdapter
class PeacekeepingAdapter(DomainAdapter):
    def map_to_engine(self, data):
        troop_strength   = data.get("troop_strength_norm", 0.5)
        mandate_clarity  = data.get("mandate_clarity", 0.6)
        local_support    = data.get("local_population_support", 0.5)
        spoiler_activity = data.get("spoiler_activity", 0.2)
        political_backing= data.get("international_backing", 0.6)
        phi = max(troop_strength*0.3 + mandate_clarity*0.3 + local_support*0.2 + political_backing*0.2, 0.01)
        C   = max(spoiler_activity*0.5 + (1.0-local_support)*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Peacekeeping failing — spoilers and lack of support undermining mission"
        if psi < 0.6:  return "Mission struggling — insufficient mandate or troops"
        if psi <= 1.2: return "Peacekeeping effective — violence reduced, peace holding"
        return "Mission success — durable peace established, handover possible"
