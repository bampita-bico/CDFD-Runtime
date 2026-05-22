from ontology.meta.entity import Entity
from ontology.meta.process import Process
from ontology.meta.flow import Flow
from ontology.meta.constraint import Constraint

class QuantumVacuumProcess(Process):
    """
    Maps the physical Adaptive Vacuum to the Universal Ontology.
    The Vacuum is an active surface that responds to energy throughput (Phi) 
    and generates Topological Constraints (C).
    """
    def __init__(self, name="QuantumVacuum_Dynamics"):
        super().__init__(name)
        
    def initialize_vacuum_surface(self) -> Entity:
        """
        Creates the base ontological entity representing the vacuum state.
        """
        vacuum = Entity("vacuum_0", "Adaptive Vacuum Surface", base_s=1.0, base_ms=1.0)
        vacuum.metadata["type"] = "fundamental_field"
        self.register(vacuum)
        return vacuum

    def apply_vacuum_flux(self, vacuum: Entity, intensity: float):
        """
        Applies a chiral energy flux to the vacuum.
        """
        f = Flow(f"flux_{len(vacuum.in_flows)}", "external_field", vacuum.node_id, intensity, "chiral_flux")
        vacuum.add_in_flow(f)
        return f

    def apply_density_constraint(self, vacuum: Entity, magnitude: float, chronic=False):
        """
        Applies a density or geometric constraint (e.g., from knot structures).
        """
        c = Constraint(f"const_{len(vacuum.constraints)}", vacuum.node_id, magnitude, is_chronic=chronic)
        vacuum.add_constraint(c)
        return c
