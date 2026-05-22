from domains.base import DomainAdapter

class SleepMedicineAdapter(DomainAdapter):
    def map_to_engine(self, data):
        sleep_efficiency = data.get("sleep_efficiency", 0.85)
        rem_fraction     = data.get("rem_fraction", 0.2)
        ahi              = data.get("ahi_events_per_hour", 5) / 30.0
        sleep_debt_hours = data.get("sleep_debt_hours", 0) / 10.0
        phi = max(sleep_efficiency * 0.5 + rem_fraction * 0.5, 0.01)
        C   = max(min(ahi, 1.0) * 0.5 + min(sleep_debt_hours, 1.0) * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Severe sleep disorder — apnoea or insomnia critically disrupting health"
        if psi < 0.6:  return "Sleep impaired — fragmented architecture, daytime dysfunction"
        if psi <= 1.2: return "Adequate sleep — restorative cycles maintained"
        return "Excellent sleep health — optimal REM and deep sleep"
