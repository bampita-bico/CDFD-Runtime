from domains.base import DomainAdapter
class DigitalArtsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        creative    = data.get("creative_output_norm", 0.6)
        platform    = data.get("platform_access", 0.7)
        engagement  = data.get("audience_engagement", 0.5)
        censorship  = data.get("platform_censorship", 0.1)
        monetis     = data.get("monetisation_barriers", 0.3)
        phi = max(creative*0.4 + platform*0.3 + engagement*0.3, 0.01)
        C   = max(censorship*0.5 + monetis*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Digital art suppressed — platform restrictions or access collapse"
        if psi < 0.6:  return "Constrained digital creativity — monetisation and censorship barriers"
        if psi <= 1.2: return "Thriving digital arts — creative output and audiences healthy"
        return "Digital cultural explosion — global reach, diverse creation"
