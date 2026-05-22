from domains.base import DomainAdapter
class NuclearDeterrenceAdapter(DomainAdapter):
    def map_to_engine(self, data):
        second_strike = data.get("second_strike_capacity", 0.7)
        cc_reliability= data.get("command_control_reliability", 0.8)
        delivery      = data.get("delivery_system_readiness", 0.7)
        misperception = data.get("misperception_risk", 0.1)
        arms_race     = data.get("arms_race_intensity", 0.2)
        crisis_stab   = data.get("crisis_stability", 0.6)
        phi = max(second_strike*0.4 + cc_reliability*0.3 + delivery*0.3, 0.01)
        C   = max(misperception*0.4 + arms_race*0.3 + (1.0-crisis_stab)*0.3, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Deterrence stable — second strike assured, no first-strike incentive"
        if psi < 0.6:  return "Deterrence fragile — misperception risk elevated"
        if psi <= 1.2: return "Crisis on the brink — deterrence logic under strain"
        return "Deterrence breakdown — nuclear use possible"
