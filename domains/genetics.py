from domains.base import DomainAdapter

class GeneticsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        expression  = data.get("expression_level", 1.0)   # relative
        mutation_l  = data.get("mutation_load", 0.1)      # 0-1
        epigenetic_s= data.get("epigenetic_silencing", 0.1) # 0-1
        repair_eff  = data.get("DNA_repair_efficiency", 0.9) # 0-1
        phi = max(expression * 0.5 + repair_eff * 0.5, 0.01)
        C   = max(mutation_l * 0.6 + epigenetic_s * 0.4, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Genomic instability — cancer or genetic disease risk high"
        if psi < 0.6:  return "Elevated mutation burden — monitor for somatic evolution"
        if psi <= 1.2: return "Genomic stability maintained"
        return "Hyperexpression — oncogene activation possible"
