from domains.base import DomainAdapter
class EthicsTheoryAdapter(DomainAdapter):
    def map_to_engine(self, data):
        normative_clarity    = data.get("normative_theory_clarity", 0.6)
        metaethical_grounding= data.get("metaethical_grounding", 0.5)
        applied_scope        = data.get("applied_scope", 0.5)
        moral_disagreement   = data.get("persistent_moral_disagreement", 0.3)
        is_ought_gap         = data.get("is_ought_problem_index", 0.4)
        phi = max(normative_clarity*0.4 + metaethical_grounding*0.3 + applied_scope*0.3, 0.01)
        C   = max(moral_disagreement*0.5 + is_ought_gap*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Ethical theory in crisis — no normative consensus or grounding"
        if psi < 0.6:  return "Weak ethical theory — disagreement and is-ought gap blocking progress"
        if psi <= 1.2: return "Productive ethical theory — frameworks guiding applied ethics"
        return "Ethical theory advancing — clear normative guidance, broad applied reach"
