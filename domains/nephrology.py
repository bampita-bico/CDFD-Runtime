from domains.base import DomainAdapter

class NephrologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        egfr       = data.get("eGFR", 60)
        creatinine = data.get("creatinine", 90)   # umol/L
        proteinuria= data.get("proteinuria", 0.1) # g/day
        bp         = data.get("bp", 120)
        phi = max(egfr / 120.0, 0.01)
        C   = max(creatinine / 90.0 * 0.4 + proteinuria * 0.4 + bp / 120.0 * 0.2, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "End-stage renal disease — dialysis likely required"
        if psi < 0.6:  return "Severe CKD — aggressive nephroprotection needed"
        if psi < 0.8:  return "Moderate CKD — optimise BP and proteinuria control"
        if psi <= 1.2: return "Compensated renal function"
        return "Hyperfiltration — early diabetic nephropathy pattern"
