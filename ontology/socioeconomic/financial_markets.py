from ontology.meta.entity import Entity
from ontology.meta.process import Process
from ontology.meta.flow import Flow
from ontology.meta.constraint import Constraint

class FinancialMarketProcess(Process):
    """
    Socioeconomic Systems - GhostFlow Financial Dynamics.
    """
    def __init__(self, name="SocioEcon_GhostFlow"):
        super().__init__(name)

    def add_market_sector(self, sector_id: str, liquidity_responsiveness: float) -> Entity:
        """
        S = How quickly the market can absorb/process capital.
        """
        sector = Entity(sector_id, f"Market Sector {sector_id}", base_s=liquidity_responsiveness, base_ms=1.0)
        self.register(sector)
        return sector

    def capital_injection(self, source_id: str, target: Entity, volume: float):
        """
        Phi = Capital inflow (e.g. Quantitative Easing or retail investment).
        """
        f = Flow(f"cap_{source_id}_{target.node_id}", source_id, target.node_id, volume, "capital")
        target.add_in_flow(f)
        return f

    def apply_interest_rate(self, target: Entity, rate: float):
        """
        C = Central bank interest rate or transaction friction.
        """
        c = Constraint(f"rate_{target.node_id}", target.node_id, rate, is_chronic=False)
        target.add_constraint(c)
        return c
        
    def trigger_panic(self, target: Entity):
        """
        A panic locks the market memory (M_s), dropping effective responsiveness.
        """
        target.M_s = 0.1
