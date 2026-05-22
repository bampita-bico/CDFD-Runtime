from ontology.meta.entity import Entity
from ontology.meta.process import Process
from ontology.meta.flow import Flow
from ontology.meta.constraint import Constraint

class NuclearDynamicsProcess(Process):
    """
    Physics - Nucleon interactions and decay.
    """
    def __init__(self, name="NuclearDynamicsProcess"):
        super().__init__(name)

    def add_nucleus(self, node_id: str, name: str, capacity: float) -> Entity:
        """
        S = Capacity or responsiveness of the Nucleus.
        """
        node = Entity(node_id, name, base_s=capacity, base_ms=1.0)
        self.register(node)
        return node

    def apply_nucleon_exchange_flow(self, source_id: str, target: Entity, intensity: float):
        """
        Phi = Flow of nucleon_exchange.
        """
        f = Flow(f"flow_{source_id}_{target.node_id}", source_id, target.node_id, intensity, "nucleon_exchange")
        target.add_in_flow(f)
        return f

    def apply_strong_force_constraint(self, target: Entity, magnitude: float):
        """
        C = Constraint representing strong_force.
        """
        c = Constraint(f"const_{target.node_id}", target.node_id, magnitude, is_chronic=True)
        target.add_constraint(c)
        return c
