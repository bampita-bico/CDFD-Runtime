from domains.base import DomainAdapter
class OtolaryngologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        hearing_index    = data.get("hearing_index", 0.8)
        airway_patency   = data.get("airway_patency", 0.9)
        vestibular_func  = data.get("vestibular_function", 0.8)
        hearing_loss_db  = data.get("hearing_loss_dB", 10) / 100.0
        obstruction      = data.get("airway_obstruction_index", 0.05)
        phi = max(hearing_index*0.3 + airway_patency*0.4 + vestibular_func*0.3, 0.01)
        C   = max(hearing_loss_db*0.5 + obstruction*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "ENT emergency — airway compromise or profound hearing loss"
        if psi < 0.6:  return "Significant ENT dysfunction — hearing and balance impaired"
        if psi <= 1.2: return "ENT function adequate — hearing and airway maintained"
        return "Excellent ENT health — full hearing, clear airway, good balance"
