from domains.base import DomainAdapter

class PaediatricsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        weight_z  = data.get("weight_z_score", 0.0)    # SD from median
        height_z  = data.get("height_z_score", 0.0)
        dev_score = data.get("developmental_score", 1.0) # 0-1
        vaccine_c = data.get("vaccination_coverage", 1.0) # 0-1
        phi = max((1.0 - abs(weight_z)/3.0) * 0.3 + (1.0 - abs(height_z)/3.0) * 0.3 +
                  dev_score * 0.4, 0.01)
        C   = max((1.0 - vaccine_c) * 0.4 + max(-weight_z, 0)/3.0 * 0.6, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Severe malnutrition/failure to thrive — urgent nutritional support"
        if psi < 0.6:  return "Developmental concern — multi-disciplinary assessment"
        if psi < 0.8:  return "Mild growth or developmental lag — watchful optimisation"
        if psi <= 1.2: return "Healthy child development trajectory"
        return "Above-average development — maintain stimulation"
