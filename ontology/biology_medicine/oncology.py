from ontology.meta.entity import Entity
from ontology.meta.process import Process
from ontology.meta.flow import Flow
from ontology.meta.constraint import Constraint

class OncologyProcess(Process):
    """
    AFL Biology & Medicine - Oncology & Constraint Escape.
    Tumors emerge by hacking their Surface Responsiveness (S) and evading 
    local biological constraints (C), allowing unrestricted local growth (Psi_s >> 1).
    """
    def __init__(self, name="AFL_Oncology"):
        super().__init__(name)

    def spawn_tumor(self, tissue_node_id: str) -> Entity:
        """
        A tumor is an entity that emerges from a host tissue.
        It starts with hyper-responsiveness (high S) and ignores normal constraints.
        """
        tumor = Entity(f"tumor_on_{tissue_node_id}", "Malignant Neoplasm", base_s=5.0, base_ms=0.2)
        self.register(tumor)
        return tumor

    def angiogenetic_flow(self, tumor: Entity, host_blood_id: str, intensity: float):
        """
        Tumor hijacks blood flow (angiogenesis), artificially increasing its incoming Phi.
        """
        f = Flow(f"angio_{tumor.node_id}", host_blood_id, tumor.node_id, intensity, "vascular_nutrient")
        tumor.add_in_flow(f)
        return f

    def host_immune_response(self, tumor: Entity, immune_strength: float):
        """
        The immune system attempts to place a constraint (C) on the tumor.
        """
        c = Constraint(f"immune_{tumor.node_id}", tumor.node_id, magnitude=immune_strength, is_chronic=False)
        tumor.add_constraint(c)
        return c
