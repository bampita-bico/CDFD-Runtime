from ontology.meta.entity import Entity
from ontology.meta.process import Process
from ontology.meta.flow import Flow
from ontology.meta.constraint import Constraint

class DistributedComputeProcess(Process):
    """
    Engineered - Compute task flow.
    """
    def __init__(self, name="DistributedComputeProcess"):
        super().__init__(name)

    def add_cluster(self, node_id: str, name: str, capacity: float) -> Entity:
        """
        S = Capacity or responsiveness of the Cluster.
        """
        node = Entity(node_id, name, base_s=capacity, base_ms=1.0)
        self.register(node)
        return node

    def apply_tasks_flow(self, source_id: str, target: Entity, intensity: float):
        """
        Phi = Flow of tasks.
        """
        f = Flow(f"flow_{source_id}_{target.node_id}", source_id, target.node_id, intensity, "tasks")
        target.add_in_flow(f)
        return f

    def apply_cpu_memory_limit_constraint(self, target: Entity, magnitude: float):
        """
        C = Constraint representing cpu_memory_limit.
        """
        c = Constraint(f"const_{target.node_id}", target.node_id, magnitude, is_chronic=True)
        target.add_constraint(c)
        return c
