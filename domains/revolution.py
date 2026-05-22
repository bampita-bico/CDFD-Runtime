from domains.base import DomainAdapter
class RevolutionAdapter(DomainAdapter):
    def map_to_engine(self, data):
        mobilisation= data.get("popular_mobilisation", 0.3)
        opposition  = data.get("opposition_organisation", 0.3)
        legitimacy  = data.get("regime_legitimacy", 0.6)
        security_l  = data.get("security_apparatus_loyalty", 0.7)
        elite_def   = data.get("elite_defection", 0.1)
        phi = max(mobilisation*0.5 + opposition*0.5, 0.01)
        C   = max(legitimacy*0.4 + security_l*0.4 + (1.0-elite_def)*0.2, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Regime stable — mobilisation insufficient to challenge power"
        if psi < 0.6:  return "Political instability — protests growing, regime nervous"
        if psi <= 1.2: return "Revolutionary situation — regime losing control of streets"
        return "Revolution — regime collapsing, power vacuum forming"
