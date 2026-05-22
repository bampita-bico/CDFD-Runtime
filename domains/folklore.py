from domains.base import DomainAdapter
class FolkloreAdapter(DomainAdapter):
    def map_to_engine(self, data):
        transmission= data.get("oral_transmission_rate", 0.5)
        community   = data.get("community_participation", 0.6)
        documentation= data.get("documentation_index", 0.4)
        urbanisation= data.get("urbanisation_disruption", 0.3)
        globalisation= data.get("globalisation_erosion", 0.2)
        phi = max(transmission*0.4 + community*0.4 + documentation*0.2, 0.01)
        C   = max(urbanisation*0.5 + globalisation*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Folklore dying — no transmission to younger generations"
        if psi < 0.6:  return "Folk traditions weakening — urbanisation and globalisation eroding"
        if psi <= 1.2: return "Folklore living — traditions transmitted and practiced"
        return "Folklore flourishing — rich cultural expression and strong community"
