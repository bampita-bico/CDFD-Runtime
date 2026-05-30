from domains.base import DomainAdapter

class SurgeryAdapter(DomainAdapter):
    def map_to_engine(self, data):
        healing   = data.get("wound_healing_score", 1.0)  # 0-1
        infection = data.get("surgical_site_infection", 0)  # 0=no,1=yes
        blood_loss= data.get("blood_loss_ml", 200)
        post_op_d = data.get("post_op_days", 1)
        phi = max(healing * 0.5 + (1.0 - infection) * 0.3 + min(post_op_d/14.0,1.0)*0.2, 0.01)
        C   = max(infection * 0.5 + min(blood_loss/2000.0,1.0) * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Post-operative crisis signal"
        if psi < 0.6:  return "Complicated post-operative signal"
        if psi < 0.8:  return "Slow-healing model band"
        if psi <= 1.2: return "Normal post-operative recovery"
        return "Rapid-healing model band"
