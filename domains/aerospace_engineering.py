from domains.base import DomainAdapter

class AerospaceEngineeringAdapter(DomainAdapter):
    def map_to_engine(self, data):
        lift_to_drag     = data.get("lift_drag_ratio_norm", 0.7)
        thrust_margin    = data.get("thrust_margin_norm", 0.6)
        fatigue_cycles   = data.get("fatigue_fraction_used", 0.3)
        failure_mode_risk= data.get("failure_mode_risk", 0.1)
        phi = max(lift_to_drag * 0.5 + thrust_margin * 0.5, 0.01)
        C   = max(fatigue_cycles * 0.5 + failure_mode_risk * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Airworthiness critical — fatigue or failure risk unacceptable"
        if psi < 0.6:  return "Below performance targets — aerodynamic or propulsion deficit"
        if psi <= 1.2: return "Aircraft within normal operating envelope"
        return "High-performance aircraft — excellent margins, superior aerodynamics"
