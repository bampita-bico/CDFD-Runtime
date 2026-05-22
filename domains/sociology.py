from domains.base import DomainAdapter

class SociologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        social_cohesion  = data.get("social_cohesion", 0.6)
        mobility_index   = data.get("social_mobility", 0.5)
        inequality       = data.get("inequality_index", 0.3)
        social_trust     = data.get("social_trust", 0.5)
        phi = max(social_cohesion * 0.4 + mobility_index * 0.3 + social_trust * 0.3, 0.01)
        C   = max(inequality * 0.5 + (1.0 - social_trust) * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Social breakdown — inequality and distrust fragmenting society"
        if psi < 0.6:  return "Social stress — mobility blocked, cohesion weakening"
        if psi <= 1.2: return "Functioning society — cohesion and mobility balanced"
        return "Strong social fabric — high trust, mobility and cohesion"
