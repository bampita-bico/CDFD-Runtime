from domains.base import DomainAdapter
class CognitiveScienceAdapter(DomainAdapter):
    def map_to_engine(self, data):
        proc_speed   = data.get("processing_speed_norm", 0.6)
        working_mem  = data.get("working_memory_norm", 0.6)
        learning_rate= data.get("learning_rate", 0.5)
        cog_load     = data.get("cognitive_load", 0.4)
        attn_frag    = data.get("attention_fragmentation", 0.3)
        phi = max(proc_speed*0.3 + working_mem*0.3 + learning_rate*0.4, 0.01)
        C   = max(cog_load*0.5 + attn_frag*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Cognitive impairment — processing and memory severely limited"
        if psi < 0.6:  return "Cognitive strain — load exceeding capacity"
        if psi <= 1.2: return "Normal cognitive function — learning and memory adequate"
        return "Optimal cognition — high capacity, focused, rapid learning"
