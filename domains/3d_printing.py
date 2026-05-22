from domains.base import DomainAdapter
class ThreeDPrintingAdapter(DomainAdapter):
    def map_to_engine(self, data):
        resolution_norm  = data.get("print_resolution_norm", 0.7)
        material_diversity = data.get("material_diversity_norm", 0.5)
        print_speed_norm = data.get("print_speed_norm", 0.5)
        defect_rate      = data.get("print_defect_rate", 0.05)
        material_cost    = data.get("material_cost_norm", 0.4)
        phi = max(resolution_norm*0.3 + material_diversity*0.3 + print_speed_norm*0.4, 0.01)
        C   = max(defect_rate*0.5 + material_cost*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "3D printing impractical — defects and costs prohibitive"
        if psi < 0.6:  return "Limited 3D printing — resolution or speed constraining applications"
        if psi <= 1.2: return "3D printing functional — reliable production in target applications"
        return "Advanced additive manufacturing — high resolution, diverse materials, fast"
