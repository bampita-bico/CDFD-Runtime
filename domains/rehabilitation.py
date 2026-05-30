from domains.base import DomainAdapter

class RehabilitationAdapter(DomainAdapter):
    def map_to_engine(self, data):
        functional_recovery = data.get("functional_recovery_norm", 0.5)
        session_intensity   = data.get("sessions_per_week", 3) / 7.0
        disability_load     = data.get("disability_index", 0.4)
        comorbidity_burden  = data.get("comorbidity_burden", 0.3)
        phi = max(min(functional_recovery, 1.0) * 0.5 + min(session_intensity, 1.0) * 0.5, 0.01)
        C   = max(disability_load * 0.5 + comorbidity_burden * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Rehabilitation-failure signal - function declining"
        if psi < 0.6:  return "Slow recovery — significant functional deficit remains"
        if psi <= 1.2: return "Good rehabilitation progress — function being restored"
        return "Excellent recovery — returning to full independence"
