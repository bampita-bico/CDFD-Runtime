from ontology.meta.entity import Entity
from ontology.meta.process import Process
from ontology.meta.flow import Flow
from ontology.meta.constraint import Constraint

class VolcanologyProcess(Process):
    """
    Earth - Magma ascent and eruption.
    """
    def __init__(self, name="VolcanologyProcess"):
        super().__init__(name)

    def add_magma_chamber(self, node_id: str, name: str, capacity: float) -> Entity:
        """
        S = Capacity or responsiveness of the Magma Chamber.
        """
        node = Entity(node_id, name, base_s=capacity, base_ms=1.0)
        self.register(node)
        return node

    def apply_magma_flow(self, source_id: str, target: Entity, intensity: float):
        """
        Phi = Flow of magma.
        """
        f = Flow(f"flow_{source_id}_{target.node_id}", source_id, target.node_id, intensity, "magma")
        target.add_in_flow(f)
        return f

    def apply_vent_pressure_constraint(self, target: Entity, magnitude: float):
        """
        C = Constraint representing vent_pressure.
        """
        c = Constraint(f"const_{target.node_id}", target.node_id, magnitude, is_chronic=True)
        target.add_constraint(c)
        return c
