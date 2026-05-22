from ontology.meta.entity import Entity
from ontology.meta.process import Process
from ontology.meta.flow import Flow
from ontology.meta.constraint import Constraint

class PlasmaDynamicsProcess(Process):
    """
    Physics - Charged particle flow and confinement.
    """
    def __init__(self, name="PlasmaDynamicsProcess"):
        super().__init__(name)

    def add_plasma_field(self, node_id: str, name: str, capacity: float) -> Entity:
        """
        S = Capacity or responsiveness of the Plasma Field.
        """
        node = Entity(node_id, name, base_s=capacity, base_ms=1.0)
        self.register(node)
        return node

    def apply_charged_particles_flow(self, source_id: str, target: Entity, intensity: float):
        """
        Phi = Flow of charged_particles.
        """
        f = Flow(f"flow_{source_id}_{target.node_id}", source_id, target.node_id, intensity, "charged_particles")
        target.add_in_flow(f)
        return f

    def apply_magnetic_confinement_constraint(self, target: Entity, magnitude: float):
        """
        C = Constraint representing magnetic_confinement.
        """
        c = Constraint(f"const_{target.node_id}", target.node_id, magnitude, is_chronic=True)
        target.add_constraint(c)
        return c
