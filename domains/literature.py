from domains.base import DomainAdapter
class LiteratureAdapter(DomainAdapter):
    def map_to_engine(self, data):
        publication = data.get("publication_rate_norm", 0.5)
        literacy    = data.get("literacy_rate", 0.8)
        diversity   = data.get("diversity_of_voices", 0.5)
        censorship  = data.get("censorship_index", 0.1)
        lang_barrier= data.get("language_barrier", 0.2)
        phi = max(publication*0.3 + literacy*0.3 + diversity*0.4, 0.01)
        C   = max(censorship*0.5 + lang_barrier*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Literature suppressed — censorship eliminating voices"
        if psi < 0.6:  return "Literature constrained — limited voices and readership"
        if psi <= 1.2: return "Healthy literary culture — diverse voices and readers"
        return "Literary renaissance — extraordinary diversity and reach"
