from ontology.meta.entity import Entity
from ontology.meta.process import Process
from ontology.meta.flow import Flow
from ontology.meta.constraint import Constraint

class BiodiversityProcess(Process):
    """
    Earth - Genetic and species flow.
    """
    def __init__(self, name="BiodiversityProcess"):
        super().__init__(name)

    def add_biome(self, node_id: str, name: str, capacity: float) -> Entity:
        """
        S = Capacity or responsiveness of the Biome.
        """
        node = Entity(node_id, name, base_s=capacity, base_ms=1.0)
        self.register(node)
        return node

    def apply_genetic_drift_flow(self, source_id: str, target: Entity, intensity: float):
        """
        Phi = Flow of genetic_drift.
        """
        f = Flow(f"flow_{source_id}_{target.node_id}", source_id, target.node_id, intensity, "genetic_drift")
        target.add_in_flow(f)
        return f

    def apply_niche_competition_constraint(self, target: Entity, magnitude: float):
        """
        C = Constraint representing niche_competition.
        """
        c = Constraint(f"const_{target.node_id}", target.node_id, magnitude, is_chronic=True)
        target.add_constraint(c)
        return c
