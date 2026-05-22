from domains.base import DomainAdapter
class ConsciousnessAdapter(DomainAdapter):
    def map_to_engine(self, data):
        neural_integration = data.get("neural_integration_norm", 0.6)
        arousal_level      = data.get("arousal_level", 0.5)
        attention_focus    = data.get("attention_focus", 0.6)
        anaesthetic_depth  = data.get("anaesthetic_depth", 0.0)
        disorder_index     = data.get("consciousness_disorder", 0.0)
        phi = max(neural_integration*0.4 + arousal_level*0.3 + attention_focus*0.3, 0.01)
        C   = max(anaesthetic_depth*0.5 + disorder_index*0.5 + 0.01, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Unconscious — anaesthesia, coma or vegetative state"
        if psi < 0.6:  return "Diminished consciousness — sedated or severely impaired"
        if psi <= 1.2: return "Normal waking consciousness — aware and integrated"
        return "Heightened consciousness — peak focus and integration"
