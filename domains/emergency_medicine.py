from domains.base import DomainAdapter

class EmergencyMedicineAdapter(DomainAdapter):
    def map_to_engine(self, data):
        gcs       = data.get("GCS", 15)          # 3-15
        sbp       = data.get("SBP", 120)
        spo2      = data.get("SpO2", 98)
        rr        = data.get("RR", 16)
        news2     = data.get("NEWS2", 0)          # 0-20
        phi = max(gcs/15.0 * 0.3 + sbp/120.0 * 0.2 + spo2/100.0 * 0.3 +
                  (1.0 - abs(rr-16)/30.0) * 0.2, 0.01)
        C   = max(min(news2/20.0, 1.0), 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.2:  return "Extreme instability signal - critical-event band"
        if psi < 0.4:  return "Critical instability signal - immediate-review flag"
        if psi < 0.6:  return "Emergent instability signal - urgent-review flag"
        if psi < 0.8:  return "Urgent instability signal - timely-review flag"
        if psi <= 1.2: return "Stable emergency-medicine model band"
        return "Low-acuity model band"
