from domains.base import DomainAdapter

class HepatologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        alt       = data.get("ALT", 30)           # IU/L
        bilirubin = data.get("bilirubin", 15)     # umol/L
        albumin   = data.get("albumin", 40)       # g/L
        child_pugh= data.get("Child_Pugh", 5)     # 5-15
        phi = max(albumin / 45.0 * 0.5 + (1.0 - min(bilirubin/200.0,1.0)) * 0.5, 0.01)
        C   = max(min(alt/200.0,1.0) * 0.4 + child_pugh / 15.0 * 0.6, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Acute liver-failure signal"
        if psi < 0.6:  return "Decompensated-cirrhosis signal"
        if psi < 0.8:  return "Compensated liver-disease band"
        if psi <= 1.2: return "Hepatic function maintained"
        return "Hepatic hypermetabolism — monitor for toxicity"
