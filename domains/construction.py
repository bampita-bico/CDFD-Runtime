from domains.base import DomainAdapter

class ConstructionAdapter(DomainAdapter):
    def map_to_engine(self, data):
        project_progress = data.get("project_progress", 0.5)
        resource_availability = data.get("resource_availability", 0.7)
        cost_overrun     = data.get("cost_overrun_fraction", 0.1)
        safety_incidents = data.get("safety_incident_rate", 0.05)
        phi = max(project_progress * 0.5 + resource_availability * 0.5, 0.01)
        C   = max(cost_overrun * 0.5 + safety_incidents * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Project failure — cost overrun and safety failures critical"
        if psi < 0.6:  return "Project in trouble — delays and resource shortfalls"
        if psi <= 1.2: return "Construction on track — within budget and schedule"
        return "Project excelling — ahead of schedule, under budget"
