from domains.base import DomainAdapter

class OphthalmologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        va        = data.get("visual_acuity", 1.0)  # decimal 0-1
        iop       = data.get("IOP", 15)             # mmHg
        retinal_s = data.get("retinal_score", 1.0)  # 0=degenerate,1=normal
        cup_disc  = data.get("cup_disc_ratio", 0.3) # glaucoma indicator
        phi = max(va * 0.5 + retinal_s * 0.5, 0.01)
        C   = max(min(iop/30.0,1.0) * 0.5 + cup_disc * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Severe visual loss — urgent ophthalmological intervention"
        if psi < 0.6:  return "Significant visual impairment — active treatment required"
        if psi < 0.8:  return "Mild visual dysfunction — close monitoring"
        if psi <= 1.2: return "Visual function preserved"
        return "Ocular hypertension — glaucoma surveillance"
