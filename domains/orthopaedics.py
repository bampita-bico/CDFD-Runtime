from domains.base import DomainAdapter

class OrthopaedicsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        bone_density     = data.get("bone_density_T_score", 0) / 2.0 + 0.5
        joint_function   = data.get("joint_function_norm", 0.7)
        fracture_risk    = data.get("fracture_risk_index", 0.2)
        inflammation     = data.get("joint_inflammation", 0.15)
        phi = max(min(bone_density, 1.0) * 0.5 + joint_function * 0.5, 0.01)
        C   = max(fracture_risk * 0.5 + inflammation * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Severe musculoskeletal failure — fracture or joint destruction"
        if psi < 0.6:  return "Significant orthopaedic impairment — mobility restricted"
        if psi <= 1.2: return "Musculoskeletal system functional"
        return "Excellent bone and joint health — high mechanical reserve"
