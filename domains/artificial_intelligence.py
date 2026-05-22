from domains.base import DomainAdapter

class ArtificialIntelligenceAdapter(DomainAdapter):
    def map_to_engine(self, data):
        model_accuracy   = data.get("model_accuracy", 0.8)
        compute_norm     = data.get("compute_norm", 0.5)
        data_quality     = data.get("data_quality", 0.7)
        bias_index       = data.get("bias_index", 0.2)
        overfitting      = data.get("overfitting_index", 0.1)
        phi = max(model_accuracy * 0.4 + compute_norm * 0.3 + data_quality * 0.3, 0.01)
        C   = max(bias_index * 0.5 + overfitting * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "AI system failing — bias or overfitting rendering results unreliable"
        if psi < 0.6:  return "Underperforming model — data or compute constraints limiting capability"
        if psi <= 1.2: return "AI system functional — reliable predictions"
        return "High-capability AI — accurate, generalising well"
