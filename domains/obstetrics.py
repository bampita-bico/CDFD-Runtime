from domains.base import DomainAdapter

class ObstetricsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        bp_sys    = data.get("bp_systolic", 110)
        proteinuria=data.get("proteinuria", 0.0) # g/day
        fetal_hr  = data.get("fetal_HR", 140)    # bpm
        gestation = data.get("gestation_weeks", 36)
        phi = max(min(gestation/40.0,1.0) * 0.4 + (1.0-abs(fetal_hr-140)/60.0) * 0.6, 0.01)
        C   = max(min(bp_sys/160.0,1.0) * 0.5 + min(proteinuria/5.0,1.0) * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Maternal-foetal emergency signal"
        if psi < 0.6:  return "Pre-eclampsia/foetal-distress signal"
        if psi < 0.8:  return "High-risk pregnancy band"
        if psi <= 1.2: return "Normal pregnancy progression"
        return "Hyperactive uterine/foetal-state signal"
