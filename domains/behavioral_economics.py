from domains.base import DomainAdapter
class BehavioralEconomicsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        rational    = data.get("rational_decision_norm", 0.6)
        market_part = data.get("market_participation", 0.6)
        bias_load   = data.get("cognitive_bias_load", 0.3)
        info_asym   = data.get("information_asymmetry", 0.3)
        phi = max(rational*0.5 + market_part*0.5, 0.01)
        C   = max(bias_load*0.5 + info_asym*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Market irrationality — biases and asymmetry collapsing allocation"
        if psi < 0.6:  return "Behavioural-distortion signal"
        if psi <= 1.2: return "Markets reasonably rational — biases offset"
        return "Highly efficient decision-making — well-informed, low bias"
