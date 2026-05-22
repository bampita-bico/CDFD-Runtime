from domains.base import DomainAdapter
class AutonomousVehiclesAdapter(DomainAdapter):
    def map_to_engine(self, data):
        perception_accuracy = data.get("perception_accuracy", 0.9)
        decision_latency    = data.get("decision_latency_norm", 0.1)
        safety_record       = data.get("safety_record_norm", 0.95)
        regulatory_clearance= data.get("regulatory_clearance", 0.5)
        edge_case_handling  = data.get("edge_case_handling", 0.6)
        phi = max(perception_accuracy*0.3 + safety_record*0.4 + edge_case_handling*0.3, 0.01)
        C   = max(decision_latency*0.4 + (1.0-regulatory_clearance)*0.6, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Autonomous system unsafe — perception or edge case failures"
        if psi < 0.6:  return "Limited autonomy — regulatory and safety barriers constraining deployment"
        if psi <= 1.2: return "Autonomous vehicles operational — safe in defined conditions"
        return "Full autonomy achieved — safe in all conditions, regulatory approved"
