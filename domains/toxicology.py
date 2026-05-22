from domains.base import DomainAdapter

class ToxicologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        detox_capacity   = data.get("hepatic_detox_norm", 0.7)
        renal_clearance  = data.get("renal_clearance_norm", 0.7)
        toxin_load       = data.get("toxin_load_norm", 0.2)
        organ_damage     = data.get("organ_damage_index", 0.1)
        phi = max(detox_capacity * 0.5 + renal_clearance * 0.5, 0.01)
        C   = max(toxin_load * 0.5 + organ_damage * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Toxicological emergency — clearance overwhelmed, organ failure"
        if psi < 0.6:  return "Significant toxicity — detoxification strained"
        if psi <= 1.2: return "Toxin load manageable — clearance adequate"
        return "Excellent detoxification capacity — toxins rapidly cleared"
