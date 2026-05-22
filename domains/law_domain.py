from domains.base import DomainAdapter

class LawAdapter(DomainAdapter):
    def map_to_engine(self, data):
        case_clearance= data.get("case_clearance_rate", 0.8)  # 0-1
        access_justice= data.get("access_to_justice", 0.6)    # 0-1
        court_backlog = data.get("court_backlog_years", 1.0)
        rule_of_law   = data.get("rule_of_law_index", 0.6)    # 0-1
        phi = max(case_clearance * 0.4 + access_justice * 0.3 + rule_of_law * 0.3, 0.01)
        C   = max(min(court_backlog/5.0,1.0) * 0.5 + (1.0-rule_of_law) * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Justice system collapse — impunity and lawlessness"
        if psi < 0.6:  return "Overburdened courts — access to justice severely limited"
        if psi <= 1.2: return "Functioning rule of law"
        return "High legal activity — reform or transformation underway"
