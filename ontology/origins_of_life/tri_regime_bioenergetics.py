from ontology.meta.base_types import Agent
from ontology.meta.process import Process
from ontology.meta.flow import Flow
from ontology.meta.constraint import Constraint

class TriRegimeBioenergeticsProcess(Process):
    """
    CRITICAL DOMAIN: Origins of Life Master Synthesis.
    Maps the physical components of pre-biotic life to the Universal Ontology.
    Implements the 4-Capacity Life Number (Lambda).
    """
    def __init__(self, name="TriRegime_Bioenergetics"):
        super().__init__(name)
        self.tau_relax = 1.0
        self.E_maintenance = 0.25

    def spawn_protocell(self, cell_id: str) -> Agent:
        cell = Agent(cell_id, "Mineral Scaffold / Proto-Cell", base_s=1.0, base_ms=0.5)
        cell.C_input = 0.0
        cell.C_electron = 0.0
        cell.C_proton = 0.0
        cell.C_stability = 0.0
        self.register(cell)
        return cell

    def compute_lambda(self, cell: Agent) -> float:
        """
        Calculates the 4-Capacity Life Number (Lambda).
        Lambda = (C_input * C_electron * C_proton * tau_relax) / (S * E_maintenance)
        """
        numerator = cell.C_input * cell.C_electron * cell.C_proton * self.tau_relax
        denominator = cell.S * self.E_maintenance
        if denominator <= 0: return 0.0
        return numerator / denominator

    def apply_energy_input(self, cell: Agent, capture_efficiency: float, source_id: str = "sun"):
        f = Flow(f"energy_{cell.node_id}", source_id, cell.node_id, intensity=capture_efficiency)
        cell.add_in_flow(f)
        cell.C_input += capture_efficiency
        return f

    def apply_transport_efficiency(self, cell: Agent, sigma_e: float, sigma_p: float):
        cell.C_electron = sigma_e
        cell.C_proton = sigma_p
        cell.S = cell.S * (sigma_e * sigma_p)

    def apply_maintenance_load(self, cell: Agent, load_magnitude: float):
        c = Constraint(f"maint_{cell.node_id}", cell.node_id, magnitude=load_magnitude)
        cell.add_constraint(c)
        cell.C_stability = 1.0 / cell.S if cell.S > 0 else 0
        return c

    def evaluate_life_regime(self, cell: Agent) -> str:
        lam = self.compute_lambda(cell)
        if lam < 1.0:
            return "Decay-dominated (< 1.0)"
        elif lam < 1.2:
            return "Near-critical proto-biological (~ 1.0)"
        else:
            return "Sustained life-like regime (> 1.0)"
