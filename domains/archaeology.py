from domains.base import DomainAdapter

class ArchaeologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        trade_flux    = data.get("trade_network_density", 0.5)  # 0-1
        site_integrity= data.get("site_integrity", 0.7)         # 0-1
        time_depth_kyr= data.get("time_depth_kyr", 2.0)
        looting_index = data.get("looting_index", 0.2)          # 0-1
        phi = max(trade_flux * 0.5 + site_integrity * 0.5, 0.01)
        C   = max(looting_index * 0.5 + min(time_depth_kyr/50.0,1.0) * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Civilisational collapse — cultural discontinuity"
        if psi < 0.6:  return "Cultural stress — fragmented trade and knowledge transfer"
        if psi <= 1.2: return "Stable civilisational flow"
        return "Cultural florescence — peak exchange and innovation"
