from domains.base import DomainAdapter

class EducationAdapter(DomainAdapter):
    def map_to_engine(self, data):
        literacy    = data.get("literacy_rate", 0.85)      # 0-1
        enrolment   = data.get("enrolment_rate", 0.9)      # 0-1
        dropout     = data.get("dropout_rate", 0.1)        # 0-1
        pupil_ratio = data.get("pupil_teacher_ratio", 30)
        phi = max(literacy * 0.4 + enrolment * 0.4 + (1.0-dropout) * 0.2, 0.01)
        C   = max(dropout * 0.5 + min(pupil_ratio/60.0,1.0) * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Education system failing — generational knowledge gap"
        if psi < 0.6:  return "Low educational-attainment signal"
        if psi <= 1.2: return "Education system in equilibrium"
        return "High educational flow — knowledge economy emerging"
