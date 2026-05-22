from domains.base import DomainAdapter

class SeismologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        tectonic_stress  = data.get("tectonic_stress_norm", 0.4)
        fault_slip_rate  = data.get("fault_slip_rate_mm_yr", 10) / 100.0
        crustal_rigidity = data.get("crustal_rigidity", 0.7)
        seismic_gap      = data.get("seismic_gap_years", 50) / 200.0
        phi = max(min(fault_slip_rate, 1.0) * 0.5 + tectonic_stress * 0.5, 0.01)
        C   = max(crustal_rigidity * 0.5 + min(seismic_gap, 1.0) * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Seismically quiet — stress locked in rigid crust"
        if psi < 0.6:  return "Moderate seismic activity — stress accumulating"
        if psi <= 1.2: return "Active seismic zone — regular stress release"
        return "Major seismic risk — stress exceeding fault capacity"
