from domains.base import DomainAdapter

class PoliticsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        participation = data.get("voter_turnout", 0.6)    # 0-1
        press_freedom = data.get("press_freedom_index", 0.6) # 0-1
        corruption    = data.get("corruption_index", 0.4) # 0=clean,1=corrupt
        polarisation  = data.get("polarisation_index", 0.4) # 0-1
        phi = max(participation * 0.4 + press_freedom * 0.6, 0.01)
        C   = max(corruption * 0.6 + polarisation * 0.4, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Authoritarian collapse — democratic institutions failing"
        if psi < 0.6:  return "Democratic erosion — civil society mobilisation needed"
        if psi <= 1.2: return "Functioning democratic governance"
        return "High civic energy — potential for rapid political change"
