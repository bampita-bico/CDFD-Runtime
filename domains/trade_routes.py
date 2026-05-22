from domains.base import DomainAdapter

class TradeRoutesAdapter(DomainAdapter):
    def map_to_engine(self, data):
        trade_volume  = data.get("trade_volume_index", 0.6)
        route_density = data.get("route_density", 0.5)
        tariff_burden = data.get("tariff_burden", 0.3)
        piracy_index  = data.get("piracy_index", 0.1)
        phi = max(trade_volume*0.5 + route_density*0.5, 0.01)
        C   = max(tariff_burden*0.5 + piracy_index*0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Route collapse — trade severed by piracy, war or tariffs"
        if psi < 0.6:  return "Severely disrupted — merchants rerouting, losses mounting"
        if psi <= 1.2: return "Active trade — goods flowing, route viable"
        return "Flourishing trade routes — wealth accumulating, cities growing along path"
