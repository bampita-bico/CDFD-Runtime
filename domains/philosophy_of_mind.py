from domains.base import DomainAdapter
class PhilosophyOfMindAdapter(DomainAdapter):
    def map_to_engine(self, data):
        explanatory_gap  = data.get("explanatory_gap_index", 0.5)
        theory_coherence = data.get("theory_coherence", 0.6)
        empirical_support= data.get("empirical_support", 0.5)
        hard_problem     = data.get("hard_problem_index", 0.7)
        reductionism_tension = data.get("reductionism_tension", 0.4)
        phi = max(theory_coherence*0.4 + empirical_support*0.4 + (1.0-explanatory_gap)*0.2, 0.01)
        C   = max(hard_problem*0.5 + reductionism_tension*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Mind-body problem intractable — no coherent theory"
        if psi < 0.6:  return "Explanatory gap dominant — theory fragmentary"
        if psi <= 1.2: return "Productive philosophy of mind — theories advancing"
        return "Strong theory of mind — explanatory power and empirical support high"
