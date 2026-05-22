from domains.base import DomainAdapter

class DentistryAdapter(DomainAdapter):
    def map_to_engine(self, data):
        oral_hygiene     = data.get("oral_hygiene_index", 0.7)
        tooth_integrity  = data.get("tooth_integrity", 0.8)
        caries_index     = data.get("caries_index", 0.1)
        periodontal_loss = data.get("periodontal_attachment_loss", 0.1)
        phi = max(oral_hygiene * 0.5 + tooth_integrity * 0.5, 0.01)
        C   = max(caries_index * 0.5 + periodontal_loss * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Severe oral disease — tooth loss and systemic risk"
        if psi < 0.6:  return "Active dental disease — caries and periodontal disease"
        if psi <= 1.2: return "Acceptable oral health — maintenance required"
        return "Excellent oral health — optimal dental function"
