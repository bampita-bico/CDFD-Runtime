from domains.base import DomainAdapter

class CivilWarAdapter(DomainAdapter):
    def map_to_engine(self, data):
        grievance  = data.get("grievance_index", 0.4)
        faction_str= data.get("faction_strength", 0.3)
        state_cap  = data.get("state_capacity", 0.6)
        legitimacy = data.get("government_legitimacy", 0.6)
        phi = max(grievance*0.5 + faction_str*0.5, 0.01)
        C   = max(state_cap*0.5 + legitimacy*0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.4:  return "Stable — state contains all pressures, grievances manageable"
        if psi < 0.7:  return "Tense peace — grievances rising, state still holds"
        if psi <= 1.2: return "High instability — armed groups mobilising, conflict likely"
        return "Civil war — grievances and factions overwhelming state capacity"
