from domains.base import DomainAdapter
class HybridWarfareAdapter(DomainAdapter):
    def map_to_engine(self, data):
        deniable_ops     = data.get("deniable_operations_intensity", 0.3)
        proxy_strength   = data.get("proxy_strength", 0.3)
        economic_coercion= data.get("economic_coercion_index", 0.3)
        resilience       = data.get("societal_resilience", 0.6)
        attribution_cap  = data.get("attribution_capability", 0.5)
        phi = max(deniable_ops*0.4 + proxy_strength*0.3 + economic_coercion*0.3, 0.01)
        C   = max(resilience*0.5 + attribution_cap*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Hybrid campaign failing — operations attributed and countered"
        if psi < 0.6:  return "Limited hybrid impact — resilience containing effects"
        if psi <= 1.2: return "Hybrid warfare active — significant grey-zone pressure"
        return "Hybrid campaign succeeding — target society and institutions destabilised"
