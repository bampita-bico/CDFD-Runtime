from domains.base import DomainAdapter
class LogicAdapter(DomainAdapter):
    def map_to_engine(self, data):
        validity    = data.get("argument_validity", 0.7)
        completeness= data.get("proof_completeness", 0.6)
        paradox     = data.get("paradox_load", 0.15)
        undecidable = data.get("undecidability_index", 0.2)
        phi = max(validity*0.5 + completeness*0.5, 0.01)
        C   = max(paradox*0.5 + undecidable*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Logical collapse — system inconsistent or trivially true"
        if psi < 0.6:  return "Weak logic — paradoxes and gaps undermining reasoning"
        if psi <= 1.2: return "Sound logical system — valid inference and proof"
        return "Complete and consistent — maximal formal rigour"
