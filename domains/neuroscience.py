from domains.base import DomainAdapter

class NeuroscienceAdapter(DomainAdapter):
    def map_to_engine(self, data):
        firing_rate = data.get("mean_firing_rate_Hz", 20)
        inhibitory  = data.get("inhibitory_tone", 0.5)    # 0-1
        plasticity  = data.get("synaptic_plasticity", 0.7) # 0-1
        connectivity= data.get("connectivity_index", 0.8)
        phi = max(min(firing_rate/100.0,1.0) * 0.3 + plasticity * 0.4 + connectivity * 0.3, 0.01)
        C   = max(inhibitory * 0.5 + (1.0 - connectivity) * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Neural silence — severe suppression or brain death"
        if psi < 0.6:  return "Hypofrontality — depression or anaesthetic state"
        if psi <= 1.2: return "Balanced neural activity"
        return "Hyperexcitability — seizure or mania risk"
