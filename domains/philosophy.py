from domains.base import DomainAdapter
class PhilosophyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        conceptual_clarity= data.get("conceptual_clarity", 0.6)
        argumentative_rigor = data.get("argumentative_rigour", 0.7)
        interdisciplinary_reach = data.get("interdisciplinary_reach", 0.5)
        dogmatism_index   = data.get("dogmatism_index", 0.2)
        sceptical_paralysis = data.get("sceptical_paralysis", 0.15)
        phi = max(conceptual_clarity*0.4 + argumentative_rigor*0.3 + interdisciplinary_reach*0.3, 0.01)
        C   = max(dogmatism_index*0.5 + sceptical_paralysis*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Philosophy paralysed — dogmatism or radical scepticism blocking progress"
        if psi < 0.6:  return "Philosophical stagnation — conceptual confusion and limited reach"
        if psi <= 1.2: return "Productive philosophy — clear concepts, rigorous argument"
        return "Philosophical renaissance — transforming other disciplines and culture"
