from ontology.meta.entity import Entity
from ontology.meta.process import Process
from ontology.meta.flow import Flow
from ontology.meta.constraint import Constraint

class BlackHoleThermodynamicsProcess(Process):
    """
    Cosmos - Information and entropy dynamics.
    """
    def __init__(self, name="BlackHoleThermodynamicsProcess"):
        super().__init__(name)

    def add_black_hole(self, node_id: str, name: str, capacity: float) -> Entity:
        """
        S = Capacity or responsiveness of the Black Hole.
        """
        node = Entity(node_id, name, base_s=capacity, base_ms=1.0)
        self.register(node)
        return node

    def apply_entropy_flow(self, source_id: str, target: Entity, intensity: float):
        """
        Phi = Flow of entropy.
        """
        f = Flow(f"flow_{source_id}_{target.node_id}", source_id, target.node_id, intensity, "entropy")
        target.add_in_flow(f)
        return f

    def apply_event_horizon_constraint(self, target: Entity, magnitude: float):
        """
        C = Constraint representing event_horizon.
        """
        c = Constraint(f"const_{target.node_id}", target.node_id, magnitude, is_chronic=True)
        target.add_constraint(c)
        return c
