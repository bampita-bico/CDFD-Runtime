from ontology.meta.entity import Entity
from ontology.meta.process import Process
from ontology.meta.flow import Flow
from ontology.meta.constraint import Constraint

class AIEmergenceProcess(Process):
    """
    Abstract - Machine learning and intelligence scaling.
    """
    def __init__(self, name="AIEmergenceProcess"):
        super().__init__(name)

    def add_neural_architecture(self, node_id: str, name: str, capacity: float) -> Entity:
        """
        S = Capacity or responsiveness of the Neural Architecture.
        """
        node = Entity(node_id, name, base_s=capacity, base_ms=1.0)
        self.register(node)
        return node

    def apply_learning_gradients_flow(self, source_id: str, target: Entity, intensity: float):
        """
        Phi = Flow of learning_gradients.
        """
        f = Flow(f"flow_{source_id}_{target.node_id}", source_id, target.node_id, intensity, "learning_gradients")
        target.add_in_flow(f)
        return f

    def apply_compute_limit_constraint(self, target: Entity, magnitude: float):
        """
        C = Constraint representing compute_limit.
        """
        c = Constraint(f"const_{target.node_id}", target.node_id, magnitude, is_chronic=True)
        target.add_constraint(c)
        return c
