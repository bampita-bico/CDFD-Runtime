from domains.base import DomainAdapter

class DermatologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        pasi      = data.get("PASI", 0)           # psoriasis 0-72
        tewl      = data.get("TEWL", 5)           # trans-epidermal water loss g/m2/hr
        wound_area= data.get("wound_area_cm2", 0)
        itch_vas  = data.get("itch_VAS", 0)       # 0-10
        phi = max((1.0 - min(pasi/72.0,1.0)) * 0.4 + (1.0 - min(tewl/50.0,1.0)) * 0.4 +
                  (1.0 - itch_vas/10.0) * 0.2, 0.01)
        C   = max(min(pasi/72.0,1.0) * 0.4 + min(wound_area/100.0,1.0) * 0.4 +
                  min(tewl/50.0,1.0) * 0.2, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Severe skin-barrier failure signal"
        if psi < 0.6:  return "Active inflammatory skin-disease signal"
        if psi < 0.8:  return "Partial skin-remission model band"
        if psi <= 1.2: return "Skin barrier intact and stable"
        return "Reactive skin — monitor for hypersensitivity"
