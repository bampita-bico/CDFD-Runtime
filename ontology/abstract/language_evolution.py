from ontology.meta.entity import Entity
from ontology.meta.process import Process
from ontology.meta.flow import Flow
from ontology.meta.constraint import Constraint

class LanguageEvolutionProcess(Process):
    """
    Abstract - Memetic and linguistic transmission.
    """
    def __init__(self, name="LanguageEvolutionProcess"):
        super().__init__(name)

    def add_culture(self, node_id: str, name: str, capacity: float) -> Entity:
        """
        S = Capacity or responsiveness of the Culture.
        """
        node = Entity(node_id, name, base_s=capacity, base_ms=1.0)
        self.register(node)
        return node

    def apply_memes_flow(self, source_id: str, target: Entity, intensity: float):
        """
        Phi = Flow of memes.
        """
        f = Flow(f"flow_{source_id}_{target.node_id}", source_id, target.node_id, intensity, "memes")
        target.add_in_flow(f)
        return f

    def apply_cultural_barrier_constraint(self, target: Entity, magnitude: float):
        """
        C = Constraint representing cultural_barrier.
        """
        c = Constraint(f"const_{target.node_id}", target.node_id, magnitude, is_chronic=True)
        target.add_constraint(c)
        return c
