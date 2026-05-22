from ontology.meta.entity import Entity
from ontology.meta.process import Process
from ontology.meta.flow import Flow
from ontology.meta.constraint import Constraint

class MetabolismProcess(Process):
    """
    AFL Biology & Medicine - Metabolic Regulation.
    Models tissues reacting to glucose flow and insulin constraints.
    """
    def __init__(self, name="AFL_Metabolism"):
        super().__init__(name)

    def define_tissue(self, tissue_id: str, name: str) -> Entity:
        """
        Creates a physiological tissue surface.
        """
        tissue = Entity(tissue_id, name, base_s=1.0, base_ms=1.0)
        self.register(tissue)
        return tissue

    def inject_glucose_flow(self, tissue: Entity, source_id: str, intensity: float):
        """
        Represents glucose / energy throughput (Phi).
        """
        f = Flow(f"gluc_{tissue.node_id}", source_id, tissue.node_id, intensity, "glucose")
        tissue.add_in_flow(f)
        return f

    def apply_insulin_resistance(self, tissue: Entity, severity: float):
        """
        Insulin resistance acts as a pathological constraint (C) on energy utilization.
        Chronically high constraints force Psi_s < 1, leading to tissue failure (Diabetes).
        """
        c = Constraint(f"ir_{tissue.node_id}", tissue.node_id, magnitude=severity, is_chronic=True)
        tissue.add_constraint(c)
        
        # In chronic AFL disease, maladaptive memory locks the tissue
        tissue.M_s = max(0.1, 1.0 - (severity / 100.0))
        return c
