from domains.base import DomainAdapter

class ClimateAdapter(DomainAdapter):
    def map_to_engine(self, data):
        temp_anom = data.get("temp_anomaly_C", 1.1)    # above pre-industrial
        co2_ppm   = data.get("CO2_ppm", 420)
        arctic_ice= data.get("arctic_ice_extent", 0.7)  # relative to 1980s
        renewables= data.get("renewable_pct", 0.3)      # fraction of energy
        phi = max((1.0 - min(temp_anom/4.0,1.0)) * 0.4 + arctic_ice * 0.3 + renewables * 0.3, 0.01)
        C   = max(min(co2_ppm/600.0,1.0) * 0.5 + min(temp_anom/4.0,1.0) * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.2:  return "Catastrophic climate breakdown — 4°C+ trajectory"
        if psi < 0.5:  return "High-risk climate state — emergency decarbonisation"
        if psi < 0.8:  return "Climate stress — accelerate net-zero transition"
        if psi <= 1.2: return "Climate within manageable bounds"
        return "Climate stabilising — continue current trajectory"
